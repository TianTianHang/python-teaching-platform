# Backend Specification: Chapter Unlock Query Optimization

## Overview

This specification defines the implementation requirements for optimizing chapter unlock state queries in the courses application. The optimization addresses performance bottlenecks in the `/api/v1/courses/{id}/chapters/` endpoint under high concurrency (25+ requests).

## Context

### Current Performance Problems

1. **Complex EXISTS Subqueries**: The `_annotate_is_locked()` method executes 60+ EXISTS subqueries per course (30 chapters × 2 conditions)
2. **Many-to-Many JOIN Overhead**: Each subquery joins `chapter_unlock_condition_prerequisite_chapters` table
3. **Array Matching Issues**: `prerequisite_chapters__id__in=completed_chapter_ids` has poor performance with large arrays
4. **Database Connection Pool Pressure**: 25 concurrent requests > MAX_CONNS=20, causing queue delays

### Solution Strategy

Implement a **Course-level Unlock Snapshot Table** with hybrid query strategy:
- Pre-compute unlock states for each (course, enrollment) combination
- Asynchronous refresh using Celery tasks
- Graceful degradation when snapshots are stale or unavailable

## Requirements

### Requirement: CourseUnlockSnapshot Model

**Status**: ADDED

The system MUST include a `CourseUnlockSnapshot` model to store pre-computed unlock states.

#### Attributes

- `course`: ForeignKey to Course (CASCADE)
- `enrollment`: OneToOneField to Enrollment (unique=True, CASCADE)
- `unlock_states`: JSONField storing `{"chapter_id": {"locked": bool, "reason": str|null}}`
- `computed_at`: DateTimeField (auto_now=True)
- `is_stale`: BooleanField (default=False, db_index=True)
- `version`: PositiveIntegerField (default=1)

#### Methods

- `recompute()`: Recompute unlock states for all chapters using existing logic
- `save_with_timestamps()`: Updated to work with `update_fields` for atomic updates

#### Requirements

1. **Indexes**:
   - Composite: `(course, enrollment)`
   - Composite: `(is_stale, computed_at)`
   - Single: `(enrollment)`
2. **Default Values**: JSONField default must be `dict()`, not `{}`
3. **Migration**: Must include `makes_migrations=True` flag

### Requirement: UnlockSnapshotService

**Status**: ADDED

The system MUST include an `UnlockSnapshotService` class with the following methods:

#### `get_or_create_snapshot(enrollment: Enrollment) -> CourseUnlockSnapshot`

**WHEN** getting a snapshot for an enrollment
**THEN** it MUST:
- Attempt to fetch existing snapshot
- If not found, create and trigger async computation
- Return the snapshot instance (possibly stale/empty)

#### `mark_stale(enrollment: Enrollment)`

**WHEN** a chapter is completed or conditions change
**THEN** it MUST:
- Set `is_stale=True` for the enrollment's snapshot
- Not trigger immediate computation
- Handle non-existent snapshots gracefully

#### `get_unlock_status_hybrid(course: Course, enrollment: Enrollment) -> dict`

**WHEN** requesting unlock status for a course enrollment
**THEN** it MUST return:

```python
{
    'unlock_states': dict,  # {chapter_id: {'locked': bool, 'reason': str|null}}
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
- Replicate existing `ChapterUnlockService.is_unlocked()` logic
- Return format compatible with snapshot format
- Be identical in behavior to original implementation

### Requirement: Celery Tasks

**Status**: ADDED

The system MUST include Celery tasks for asynchronous snapshot management.

#### `refresh_unlock_snapshot(self, enrollment_id: int)`

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

#### `batch_refresh_stale_snapshots(batch_size: int = 100)`

**WHEN** needing to refresh multiple stale snapshots
**THEN** it MUST:

1. **Query**: Fetch `batch_size` snapshots with `is_stale=True`
2. **Optimization**: Use `select_related('enrollment__user', 'course')`
3. **Processing**: Trigger individual `refresh_unlock_snapshot` tasks
4. **Logging**: Log number of snapshots processed
5. **Return**: Return count of snapshots processed

#### `scheduled_snapshot_refresh()`

**WHEN** needing scheduled refreshes
**THEN** it MUST:
- Be a simple wrapper calling `batch_refresh_stale_snapshots.delay()`
- Be configured to run every minute via Celery Beat

### Requirement: Signal Integration

**Status**: ADDED

The system MUST integrate signals to update snapshots when progress changes.

#### Signal Handler: `mark_snapshot_stale_on_progress_update`

**WHEN** a `ChapterProgress` is saved with `completed=True`
**THEN** it MUST:

1. **Trigger**: Call `UnlockSnapshotService.mark_stale()`
2. **Safety**:
   - Never raise exceptions (use try/except)
   - Log errors without crashing
   - Handle non-existent snapshots gracefully
3. **Logging**: Include debug log with enrollment_id, chapter_id, completed

#### App Configuration

**WHEN** the courses app starts
**THEN** it MUST:
- Import `courses.signals` in `ready()` method
- Ensure signals are connected at startup

### Requirement: ChapterViewSet Integration

**Status**: ADDED

The system MUST modify `ChapterViewSet.get_queryset()` to support snapshot-based queries.

#### Modified Query Logic

**WHEN** processing a chapter list request
**THEN** it MUST:

1. **Enrollment Check**: Use `select_related` for enrollment query
2. **Snapshot Detection**:
   - Try to fetch snapshot
   - If fresh snapshot exists:
     - Set `self._use_snapshot = True`
     - Set `self._unlock_states = snapshot.unlock_states`
     - Return simple queryset without complex annotations
   - If stale/no snapshot:
     - Set `self._use_snapshot = False`
     - Pre-calculate `_completed_chapter_ids`
     - Use existing `_annotate_is_locked()` logic
     - Keep prefetch_related for annotation mode

3. **Query Optimization**:
   - Fresh snapshot: Skip `prefetch_related` (reduce 2 queries)
   - Annotation mode: Keep prefetch_related

#### Required Attributes

The view MUST set these instance attributes:
- `self._enrollment`: The enrollment instance
- `self._use_snapshot`: bool (True if using snapshot)
- `self._unlock_states`: dict (if using snapshot)
- `self._completed_chapter_ids`: set (if using annotation)

### Requirement: Serializer Integration

**Status**: ADDED

The system MUST update `ChapterSerializer` to use snapshot data.

#### Modified `get_is_locked()` Method

**WHEN** getting the is_locked field
**THEN** it MUST:

1. **Snapshot Mode**:
   - Check `view._use_snapshot` is True
   - Look up chapter in `view._unlock_states`
   - Return `state['locked']` value

2. **Fallback Chain**:
   - Use annotation `obj.is_locked_db` if available
   - Fallback to `ChapterUnlockService.is_unlocked()` with context enrollment

#### Key Requirements

1. **Format Compatibility**: Return boolean, not string
2. **Error Handling**: Handle missing keys gracefully
3. **Performance**: No additional queries in snapshot mode

### Requirement: Performance Guarantees

**Status**: MODIFIED

The system MUST achieve the following performance improvements:

#### Query Counts

**WHEN** processing chapter list requests
**THEN** the total database queries MUST be:
- Fresh snapshot mode: 2 queries (enrollment + chapters)
- Annotation mode: 5 queries (enrollment + progress + chapters + prefetches)

#### Response Times

**WHEN** processing 25 concurrent requests
**THEN** response times MUST be:
- Fresh snapshot mode: < 50ms (median)
- Annotation mode: < 200ms (median)
- Maximum: 300ms (99th percentile)

#### Throughput Improvements

The system MUST achieve:
- Query reduction: 60%+ (from 5 queries to 2)
- Subquery elimination: 100% (from 60+ EXISTS to 0)
- Concurrency support: 100+ requests (from 25)

### Requirement: Consistency Guarantees

**Status**: MODIFIED

The system MUST ensure eventual consistency with bounded staleness.

#### Consistency Model

1. **Update Pattern**:
   - User completes chapter → Signal marks snapshot stale → Async refresh
   - Maximum staleness: 1 minute (configurable)

2. **Freshness Guarantees**:
   - Fresh snapshot: Immediate consistency (read from DB)
   - Stale snapshot: Latest known state (realtime as fallback)

3. **Validation**:
   - MUST include `source` field in response
   - MUST log staleness events for monitoring
   - MUST use pessimistic concurrent updating in `recompute()`

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
   snapshot_hit_rate = snapshot_requests / total_requests
   ```

2. **Stale Rate**:
   ```python
   stale_snapshot_rate = stale_snapshots / total_snapshots
   ```

3. **Task Duration**:
   ```python
   refresh_task_duration_histogram = histogram of task completion times
   ```

4. **API Latency**:
   ```python
   chapter_list_api_latency_histogram = histogram of response times
   ```

#### Logging Requirements

**WHEN** critical operations occur
**THEN** the system MUST log:

1. **Snapshot Operations**:
   ```python
   logger.info(
       "Chapter unlock snapshot query",
       extra={
           'course_id': course.id,
           'enrollment_id': enrollment.id,
           'source': result['source'],
           'snapshot_version': result.get('snapshot_version'),
           'latency_ms': (end - start) * 1000
       }
   )
   ```

2. **Task Operations**:
   ```python
   logger.info(
       "Refresh unlock snapshot",
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
   - `CourseUnlockSnapshot` CRUD operations
   - `recompute()` logic with various unlock conditions
   - JSON serialization/deserialization

2. **Service Tests**:
   - `UnlockSnapshotService.get_or_create_snapshot()`
   - `UnlockSnapshotService.mark_stale()`
   - `UnlockSnapshotService.get_unlock_status_hybrid()` (all 3 paths)
   - `_compute_realtime()` accuracy

3. **Task Tests**:
   - `refresh_unlock_snapshot()` success case
   - `refresh_unlock_snapshot()` failure retry
   - `batch_refresh_stale_snapshots()` processing
   - `scheduled_snapshot_refresh()` wrapper

#### Integration Tests

**WHEN** testing the complete flow
**THEN** it MUST include:

1. **End-to-End Flow**:
   - Chapter completion → Signal → Stale marking → Refresh → Update
   - Fresh snapshot → API response with snapshot data
   - Stale snapshot → API response with stale data + async refresh

2. **Concurrency Tests**:
   - 25 concurrent requests
   - 100 concurrent requests
   - Verify no race conditions or deadlocks

3. **API Compatibility**:
   - Verify response format unchanged
   - Verify no breaking changes to existing clients

#### Performance Tests

**WHEN** validating optimizations
**THEN** it MUST include:

1. **Query Count Comparison**:
   - Baseline (current implementation): 5+ queries
   - Optimized (snapshot): 2 queries
   - 60%+ reduction target

2. **Response Time Comparison**:
   - Baseline (current): 200-500ms
   - Optimized (snapshot): 20-50ms
   - 80%+ reduction target

3. **Throughput Testing**:
   - Baseline: 25 concurrent max
   - Optimized: 100+ concurrent target

### Requirement: Deployment Strategy

**Status**: MODIFIED

The system MUST support gradual rollout and rollback.

#### Migration Strategy

**WHEN** deploying to production
**THEN** it MUST:

1. **Data Migration**:
   - Create new table `course_unlock_snapshot`
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

1. **Feature Flag Approach**:
   - Toggle `USE_UNLOCK_SNAPSHOT=False` to disable
   - System falls back to original annotation logic
   - No data loss during rollback

2. **Quick Rollback**:
   - Delete migration file (if not applied)
   - Remove new code
   - Restart services

3. **Data Cleanup** (optional):
   - Drop `course_unlock_snapshot` table
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
   - API latency > 100ms

## Constraints

### Technical Constraints

1. **Database**: PostgreSQL 15+ (required for JSONB performance)
2. **Cache**: Redis (required for Django cache and Celery)
3. **Message Queue**: Celery with Redis backend
4. **Python Version**: 3.11+ (for type hints and async)
5. **Django Version**: 5.2+ (required for JSONField index support)

### Performance Constraints

1. **Concurrency**: Must support 25+ concurrent requests
2. **Response Time**: < 300ms (99th percentile)
3. **Database Connections**: No connection pool exhaustion
4. **Memory Usage**: Snapshot table must scale linearly (not exponentially)

### Compatibility Constraints

1. **API Compatibility**: Response format must be identical
2. **Database Compatibility**: No breaking schema changes
3. **Version Compatibility**: Must work with existing frontend
4. **Cache Compatibility**: No conflict with existing cache keys

### Operational Constraints

1. **Monitoring**: Must provide sufficient observability
2. **Logging**: Must include necessary context for debugging
3. **Rollback**: Must support quick rollback (< 5 minutes)
4. **Scaling**: Must handle user growth (1000+ enrollments)

## Acceptance Criteria

### Functional Acceptance

- [ ] All unit tests pass (100% coverage)
- [ ] All integration tests pass
- [ ] API response format unchanged
- [ ] Chapter unlock logic identical to original
- [ ] Fast mode returns correct unlock states
- [ ] Stale mode returns correct data with refresh trigger

### Performance Acceptance

- [ ] Query count reduced by 60%+ (from 5 to 2)
- [ ] EXISTS subqueries eliminated (0 remaining)
- [ ] API latency reduced by 80%+ (from 500ms to 50ms)
- [ ] Supports 100+ concurrent requests
- [ ] Database connection pool not exhausted

### Consistency Acceptance

- [ ] Fresh data when using fresh snapshot
- [ ] Stale data < 1 minute old when using stale snapshot
- [ ] Real-time fallback when no snapshot
- [ ] No data loss during migration
- [ ] Version tracking for all updates

### Operational Acceptance

- [ ] Celery tasks run without errors
- [ ] Scheduled refreshes execute every minute
- [ ] Signal triggers work on chapter completion
- [ ] Monitoring metrics available
- [ ] Successful rollback path verified

## Related Artifacts

- **Proposal**: `proposal.md` - Business case and implementation overview
- **Design**: `design.md` - Architecture and implementation details
- **Tasks**: `tasks.md` - Detailed task breakdown and timeline
- **Tests**: `tasks.md` - Comprehensive test requirements

## Change History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-02-28 | Claude | Initial specification |