# Backend Specification: Problem Unlock Query Optimization

## Overview

This specification defines the implementation requirements for optimizing problem unlock state queries in the courses application. The optimization addresses severe N+1 query performance problems in the `/api/v1/courses/{id}/problems/` and `/api/v1/chapters/{id}/problems/` endpoints.

**Strategy**: Directly reuse the proven Chapter unlock snapshot optimization pattern, minimizing design and implementation complexity.

## Context

### Current Performance Problems

1. **True N+1 Query Issue**: `ProblemSerializer.get_is_unlocked()` calls `unlock_condition.is_unlocked(user)` for **each** problem
2. **Python Layer Processing**: All unlock checks happen in Python loops, not database layer
3. **Complex Nested Logic**: For each prerequisite problem, queries `ProblemProgress` and `Submission` tables
4. **No Database Optimization**: Unlike Chapter's EXISTS subqueries, Problem has no database-level optimization

### Performance Impact (Estimated)

For a course with 50 algorithm problems:
- **Base queries**: 1 (problems table) + 2 (prefetch_related) = 3 queries
- **N+1 queries**: 50 problems × average 3 prerequisites × 2 checks = **300 extra queries**
- **Total**: **~353 queries/request**
- **25 concurrent**: **8825 queries/second**

### Solution Strategy

**Copy-Paste-Adapt** from Chapter optimization:
- Add `ProblemUnlockSnapshot` model (reference `CourseUnlockSnapshot`)
- Use `ProblemUnlockSnapshotService` (reference `UnlockSnapshotService`)
- Use Celery async refresh (reuse task pattern)
- ViewSet and Serializer integration (reference Chapter implementation)

**Reuse ratio**: ~85% of logic directly copied from Chapter
**Specialization**: ~15% adapted for Problem-specific needs

## Requirements

### Requirement: ProblemUnlockSnapshot Model

**Status**: ADDED

The system MUST include a `ProblemUnlockSnapshot` model to store pre-computed unlock states.

#### Attributes

- `course`: ForeignKey to Course (CASCADE)
- `enrollment`: OneToOneField to Enrollment (unique=True, CASCADE)
- `unlock_states`: JSONField storing `{"problem_id": {"unlocked": bool, "reason": str|null}}`
- `computed_at`: DateTimeField (auto_now=True)
- `is_stale`: BooleanField (default=False, db_index=True)
- `version`: PositiveIntegerField (default=1)

#### Methods

- `recompute()`: Recompute unlock states for all problems using existing logic
- `save_with_timestamps()`: Work with `update_fields` for atomic updates

#### Requirements

1. **Indexes**:
   - Composite: `(course, enrollment)`
   - Composite: `(is_stale, computed_at)`
   - Single: `(enrollment)`
2. **Default Values**: JSONField default must be `dict()`, not `{}`
3. **Migration**: Must include migration file

### Requirement: ProblemUnlockSnapshotService

**Status**: ADDED

The system MUST include a `ProblemUnlockSnapshotService` class with the following methods:

#### `get_or_create_snapshot(enrollment: Enrollment) -> ProblemUnlockSnapshot`

**WHEN** getting a snapshot for an enrollment
**THEN** it MUST:
- Attempt to fetch existing snapshot
- If not found, create and trigger async computation
- Return the snapshot instance (possibly stale/empty)

#### `mark_stale(enrollment: Enrollment)`

**WHEN** a problem is solved or conditions change
**THEN** it MUST:
- Set `is_stale=True` for the enrollment's snapshot
- Not trigger immediate computation
- Handle non-existent snapshots gracefully

#### `get_unlock_status_hybrid(course: Course, enrollment: Enrollment) -> dict`

**WHEN** requesting unlock status for a course enrollment
**THEN** it MUST return:

```python
{
    'unlock_states': dict,  # {problem_id: {'unlocked': bool, 'reason': str|null}}
    'source': 'snapshot' | 'snapshot_stale' | 'realtime',
    'snapshot_version': int  # if source is snapshot or snapshot_stale
}
```

**IMPLEMENTATION RULES**:

1. **Fresh Snapshot**: If snapshot exists and `is_stale=False`, use it
2. **Stale Snapshot**: If snapshot exists and `is_stale=True`:
   - Trigger async refresh
   - Return stale data with `source='snapshot_stale'`
   - Log the staleness event
3. **No Snapshot**: If no snapshot exists:
   - Trigger async creation
   - Use `_compute_realtime()` as fallback
   - Return `source='realtime'`

#### `_compute_realtime(course: Course, enrollment: Enrollment) -> dict`

**WHEN** needing to compute unlock status without snapshot
**THEN** it MUST:
- Replicate existing `ProblemUnlockCondition.is_unlocked()` logic
- Return format compatible with snapshot format
- Be identical in behavior to original implementation

### Requirement: Celery Tasks

**Status**: ADDED

The system MUST include Celery tasks for asynchronous snapshot management.

#### `refresh_problem_unlock_snapshot(self, enrollment_id: int)`

**WHEN** needing to refresh a single snapshot
**THEN** it MUST:

1. **Parameters**:
   - Use `@shared_task(bind=True)`
   - `max_retries=3`
   - `default_retry_delay=60`
   - `autoretry_for=(Exception,)`

2. **Error Handling**:
   - Retry on any exception
   - Log retry attempts with enrollment_id
   - Include structured logging (enrollment_id, user_id, course_id, snapshot_version)

3. **Implementation**:
   - Use `select_related` for enrollment query
   - Call `snapshot.recompute()` method
   - Update `update_fields=['unlock_states', 'is_stale', 'version']`
   - Handle `Enrollment.DoesNotExist` gracefully

#### `batch_refresh_stale_problem_snapshots(batch_size: int = 200)`

**WHEN** needing to refresh multiple stale snapshots
**THEN** it MUST:

1. **Query**: Fetch `batch_size` snapshots with `is_stale=True`
2. **Optimization**: Use `select_related('enrollment__user', 'course')`
3. **Processing**: Trigger individual `refresh_problem_unlock_snapshot` tasks
4. **Logging**: Log number of snapshots processed
5. **Return**: Return count of snapshots processed

**Note**: `batch_size` is larger than Chapter (200 vs 100) because Problem has more items.

#### `scheduled_problem_snapshot_refresh()`

**WHEN** needing scheduled refreshes
**THEN** it MUST:
- Be a simple wrapper calling `batch_refresh_stale_problem_snapshots.delay()`
- Be configured to run every 30 seconds via Celery Beat

**Note**: Frequency is higher than Chapter (30s vs 60s) because Problem is accessed more frequently.

### Requirement: Signal Integration

**Status**: ADDED

The system MUST integrate signals to update snapshots when progress changes.

#### Signal Handler: `mark_problem_snapshot_stale_on_progress_update`

**WHEN** a `ProblemProgress` is saved with `status='solved'`
**THEN** it MUST:

1. **Trigger**: Call `ProblemUnlockSnapshotService.mark_stale()`
2. **Safety**:
   - Never raise exceptions (use try/except)
   - Log errors without crashing
   - Handle non-existent snapshots gracefully
3. **Logging**: Include debug log with enrollment_id, problem_id, status

### Requirement: ProblemViewSet Integration

**Status**: MODIFIED

The system MUST modify `ProblemViewSet.get_queryset()` to support snapshot-based queries.

#### Modified Query Logic

**WHEN** processing a problem list request
**THEN** it MUST:

1. **Enrollment Check**: Use `select_related` for enrollment query
2. **Snapshot Detection**:
   - Try to fetch snapshot
   - If fresh snapshot exists:
     - Set `self._use_snapshot = True`
     - Set `self._unlock_states = snapshot.unlock_states`
     - Return queryset (keep existing prefetch_related for other fields)
   - If stale/no snapshot:
     - Set `self._use_snapshot = False`
     - Keep existing logic

3. **Prefetch Related**:
   - Keep existing prefetch_related (other fields need it)
   - No need to remove complex annotations (Problem has none)

#### Required Attributes

The view MUST set these instance attributes:
- `self._enrollment`: The enrollment instance
- `self._use_snapshot`: bool (True if using snapshot)
- `self._unlock_states`: dict (if using snapshot)

### Requirement: Serializer Integration

**Status**: MODIFIED

The system MUST update `ProblemSerializer` to use snapshot data.

#### Modified `get_is_unlocked()` Method

**WHEN** getting the is_unlocked field
**THEN** it MUST:

1. **Snapshot Mode**:
   - Check `view._use_snapshot` is True
   - Look up problem in `view._unlock_states`
   - Return `state['unlocked']` value

2. **Fallback Chain**:
   - Use existing `unlock_condition.is_unlocked(user)` logic
   - Handle `AttributeError` (no unlock condition)

#### Key Requirements

1. **Format Compatibility**: Return boolean, not string
2. **Error Handling**: Handle missing keys gracefully
3. **Performance**: No additional queries in snapshot mode

### Requirement: Performance Guarantees

**Status**: MODIFIED

The system MUST achieve the following performance improvements:

#### Query Counts

**WHEN** processing problem list requests
**THEN** the total database queries MUST be:
- Snapshot mode: 2-5 queries (enrollment + problems + prefetches)
- Non-snapshot mode: 300+ queries (existing N+1 behavior)

#### Response Times

**WHEN** processing 25 concurrent requests
**THEN** response times MUST be:
- Snapshot mode: < 100ms (median), < 200ms (99th percentile)
- Non-snapshot mode: < 2000ms (fallback)

#### Throughput Improvements

The system MUST achieve:
- Query reduction: 98%+ (from 300+ to 2-5)
- N+1 query elimination: 100% (from 300+ to 0)
- Concurrency support: 100+ requests (from 10-15)

### Requirement: Consistency Guarantees

**Status**: MODIFIED

The system MUST ensure eventual consistency with bounded staleness.

#### Consistency Model

1. **Update Pattern**:
   - User solves problem → Signal marks snapshot stale → Async refresh
   - Maximum staleness: 30 seconds (shorter than Chapter's 60s)

2. **Freshness Guarantees**:
   - Fresh snapshot: Immediate consistency (read from DB)
   - Stale snapshot: Latest known state (realtime as fallback)

3. **Validation**:
   - MUST include `source` field in response
   - MUST log staleness events for monitoring
   - MUST use atomic updates in `recompute()`

#### Data Integrity

1. **Atomic Operations**: All snapshot writes MUST be atomic
2. **Error Recovery**: Failed refreshes MUST NOT affect snapshot integrity
3. **Version Tracking**: Each snapshot update MUST increment version

### Requirement: Monitoring Observability

**Status**: MODIFIED

The system MUST include monitoring for performance and health.

#### Key Metrics

**WHEN** the system is running
**THEN** it MUST expose:

1. **Hit Rate**:
   ```python
   problem_snapshot_hit_rate = snapshot_requests / total_requests
   ```

2. **Stale Rate**:
   ```python
   problem_stale_snapshot_rate = stale_snapshots / total_snapshots
   ```

3. **Task Duration**:
   ```python
   problem_refresh_task_duration_histogram = histogram of task completion times
   ```

4. **API Latency**:
   ```python
   problem_list_api_latency_histogram = histogram of response times
   ```

5. **Problem Count**:
   ```python
   problem_count_per_snapshot = average number of problems in unlock_states
   ```

#### Logging Requirements

**WHEN** critical operations occur
**THEN** the system MUST log:

1. **Snapshot Operations**:
   ```python
   logger.info(
       "Problem unlock snapshot query",
       extra={
           'course_id': course.id,
           'enrollment_id': enrollment.id,
           'source': result['source'],
           'snapshot_version': result.get('snapshot_version'),
           'latency_ms': (end - start) * 1000,
           'problem_count': len(result['unlock_states'])
       }
   )
   ```

2. **Task Operations**:
   ```python
   logger.info(
       "Refresh problem unlock snapshot",
       extra={
           'enrollment_id': enrollment_id,
           'user_id': enrollment.user_id,
           'course_id': enrollment.course_id,
           'snapshot_version': snapshot.version,
           'duration_ms': duration * 1000
       }
   )
   ```

### Requirement: Test Coverage

**Status**: ADDED

The system MUST include comprehensive test coverage.

#### Unit Tests

**WHEN** implementing the optimization
**THEN** it MUST include:

1. **Model Tests**:
   - `ProblemUnlockSnapshot` CRUD operations
   - `recompute()` logic with various unlock conditions
   - JSON serialization/deserialization

2. **Service Tests**:
   - `ProblemUnlockSnapshotService.get_or_create_snapshot()`
   - `ProblemUnlockSnapshotService.mark_stale()`
   - `ProblemUnlockSnapshotService.get_unlock_status_hybrid()` (all 3 paths)
   - `_compute_realtime()` accuracy

3. **Task Tests**:
   - `refresh_problem_unlock_snapshot()` success case
   - `refresh_problem_unlock_snapshot()` failure retry
   - `batch_refresh_stale_problem_snapshots()` processing
   - `scheduled_problem_snapshot_refresh()` wrapper

#### Integration Tests

**WHEN** testing the complete flow
**THEN** it MUST include:

1. **End-to-End Flow**:
   - Problem solving → Signal → Stale marking → Refresh → Update
   - Fresh snapshot → API response with snapshot data
   - Stale snapshot → API response with stale data + async refresh

2. **Concurrency Tests**:
   - 25 concurrent requests
   - 50 concurrent requests
   - 100 concurrent requests
   - Verify no race conditions or deadlocks

3. **API Compatibility**:
   - Verify response format unchanged
   - Verify no breaking changes to existing clients

#### Performance Tests

**WHEN** validating optimizations
**THEN** it MUST include:

1. **Query Count Comparison**:
   - Baseline (current implementation): 300+ queries
   - Optimized (snapshot): 2-5 queries
   - 98%+ reduction target

2. **Response Time Comparison**:
   - Baseline (current): 500-2000ms
   - Optimized (snapshot): 50-100ms
   - 90%+ reduction target

3. **Throughput Testing**:
   - Baseline: 10-15 concurrent max
   - Optimized: 100+ concurrent target

### Requirement: Deployment Strategy

**Status**: MODIFIED

The system MUST support gradual rollout and rollback.

#### Migration Strategy

**WHEN** deploying to production
**THEN** it MUST:

1. **Data Migration**:
   - Create new table `problem_unlock_snapshot`
   - No initial data needed (on-demand creation)
   - Zero downtime with concurrent operations

2. **Deployment Steps**:
   - Deploy code (new models/services)
   - Run migration `python manage.py migrate courses`
   - Restart Django app
   - Restart Celery worker
   - Restart Celery beat

#### Rollback Strategy

**WHEN** issues are detected
**THEN** it MUST support:

1. **Feature Flag Approach** (optional):
   - Toggle `USE_PROBLEM_SNAPSHOT=False` to disable
   - System falls back to original logic
   - No data loss during rollback

2. **Quick Rollback**:
   - Delete migration file (if not applied)
   - Remove new code
   - Restart services

3. **Data Cleanup** (optional):
   - Drop `problem_unlock_snapshot` table
   - No impact on existing data

#### Monitoring Deployment

**WHEN** rolling out
**THEN** it MUST monitor:

1. **Success Metrics**:
   - API latency reduction
   - Database query count reduction
   - Error rate < 1%

2. **Alerts**:
   - Hit rate < 80%
   - Stale rate > 20%
   - Task failure rate > 5%
   - API latency > 200ms

### Requirement: Reuse from Chapter Implementation

**Status**: ADDED

The implementation MUST maximize code reuse from Chapter optimization.

#### Required References

**WHEN** implementing each component
**THEN** it MUST reference the corresponding Chapter implementation:

1. **Model**:
   - Reference: `CourseUnlockSnapshot` (models.py:1158-1296)
   - Reuse: Field definitions, Meta config, recompute() structure

2. **Service**:
   - Reference: `UnlockSnapshotService` (services.py:506-656)
   - Reuse: Method signatures, hybrid query logic, fallback chain

3. **Tasks**:
   - Reference: `refresh_unlock_snapshot` (tasks.py:7-67)
   - Reuse: Task decorators, error handling, logging

4. **Signals**:
   - Reference: `mark_snapshot_stale_on_progress_update` (signals.py:234-275)
   - Reuse: Signal handler structure, safety measures

5. **ViewSet**:
   - Reference: `ChapterViewSet.get_queryset()` (views.py:99-167)
   - Reuse: Snapshot detection logic, instance variable patterns

6. **Serializer**:
   - Reference: `ChapterSerializer.get_is_locked()` (serializers.py:149-184)
   - Reuse: Priority chain (snapshot → annotation → realtime)

#### Allowed Adaptations

**WHEN** adapting Chapter code
**THEN** it MAY change:

1. **Configuration**:
   - Refresh frequency: 30s (Chapter: 60s)
   - Batch size: 200 (Chapter: 100)
   - JSON size: ~4KB (Chapter: ~2KB)

2. **Problem-Specific Logic**:
   - Use `ProblemUnlockCondition.is_unlocked()` instead of `ChapterUnlockService`
   - Check `status='solved'` instead of `completed=True`
   - Include Submission fallback logic

**MUST NOT CHANGE**:
- Core architecture and patterns
- Error handling strategies
- Logging format and structure
- Test structure and coverage

## Constraints

### Technical Constraints

1. **Database**: PostgreSQL 15+ (required for JSONB performance)
2. **Cache**: Redis (required for Django cache and Celery)
3. **Message Queue**: Celery with Redis backend
4. **Python Version**: 3.11+ (for type hints and async)
5. **Django Version**: 5.2+ (required for JSONField index support)

### Performance Constraints

1. **Concurrency**: Must support 25+ concurrent requests (target: 100+)
2. **Response Time**: < 200ms (99th percentile)
3. **Database Connections**: No connection pool exhaustion
4. **Memory Usage**: Snapshot table must scale linearly (not exponentially)

### Compatibility Constraints

1. **API Compatibility**: Response format must be identical
2. **Database Compatibility**: No breaking schema changes
3. **Version Compatibility**: Must work with existing frontend
4. **Cache Compatibility**: No conflict with existing cache keys

### Reuse Constraints

1. **Implementation Time**: Must be <= 3 days (Chapter was 5-8 days)
2. **Code Reuse**: Must reuse >= 80% of Chapter patterns
3. **Risk Level**: Must be lower than Chapter (pattern proven)
4. **Test Coverage**: Must match Chapter coverage levels

### Operational Constraints

1. **Monitoring**: Must provide sufficient observability
2. **Logging**: Must include necessary context for debugging
3. **Rollback**: Must support quick rollback (< 5 minutes)
4. **Scaling**: Must handle user growth (1000+ enrollments)

## Acceptance Criteria

### Functional Acceptance

- [ ] All unit tests pass (100% coverage target)
- [ ] All integration tests pass
- [ ] API response format unchanged
- [ ] Problem unlock logic identical to original
- [ ] Fast mode returns correct unlock states
- [ ] Stale mode returns correct data with refresh trigger

### Performance Acceptance

- [ ] Query count reduced by 98%+ (from 300+ to 2-5)
- [ ] N+1 queries eliminated (0 remaining)
- [ ] API latency reduced by 90%+ (from 500-2000ms to 50-100ms)
- [ ] Supports 100+ concurrent requests
- [ ] Database connection pool not exhausted

### Consistency Acceptance

- [ ] Fresh data when using fresh snapshot
- [ ] Stale data < 30 seconds old when using stale snapshot
- [ ] Real-time fallback when no snapshot
- [ ] No data loss during migration
- [ ] Version tracking for all updates

### Operational Acceptance

- [ ] Celery tasks run without errors
- [ ] Scheduled refreshes execute every 30 seconds
- [ ] Signal triggers work on problem solve
- [ ] Monitoring metrics available
- [ ] Successful rollback path verified

### Reuse Acceptance

- [ ] Implementation time <= 3 days
- [ ] Code reuse >= 80% from Chapter
- [ ] All Chapter references documented
- [ ] Test structure matches Chapter

## Related Artifacts

- **Chapter Optimization Proposal**: `openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/proposal.md`
- **Chapter Optimization Design**: `openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/design.md`
- **Chapter Optimization Tasks**: `openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/tasks.md`
- **Chapter Optimization Spec**: `openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/specs/backend-courses/chapter-unlock-query-spec.md`

## Implementation References

### Chapter Implementation Locations

| Component | File | Lines |
|-----------|------|-------|
| Model | `models.py` | 1158-1296 |
| Service | `services.py` | 506-656 |
| Tasks | `tasks.py` | 7-112 |
| Signals | `signals.py` | 234-275 |
| ViewSet | `views.py` | 99-190 |
| Serializer | `serializers.py` | 149-184 |

### Problem Implementation Locations (To Be Created)

| Component | File | Estimated Lines |
|-----------|------|------------------|
| Model | `models.py` | ~140 (add to end) |
| Service | `services.py` | ~150 (add new class) |
| Tasks | `tasks.py` | ~70 (add new functions) |
| Signals | `signals.py` | ~40 (add new handler) |
| ViewSet | `views.py` | ~30 (modify existing) |
| Serializer | `serializers.py` | ~30 (modify existing) |

## Change History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-02-28 | Claude | Initial specification (based on Chapter) |
