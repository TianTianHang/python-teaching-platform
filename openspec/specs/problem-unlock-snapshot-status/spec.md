# Backend Specification: Problem Unlock Snapshot Status Enhancement

## Overview

This specification defines the enhancement to the Problem Unlock Snapshot feature to include problem status (solved/not_started) in the snapshot data. This enhancement eliminates the need to query the `ProblemProgress` table when serializing problem lists, further reducing database queries and improving performance.

**Strategy**: Extend the existing `ProblemUnlockSnapshot` to store problem status alongside unlock state, enabling the serializer to retrieve all user-specific data from a single source.

## Context

### Current Performance Problems

1. **Additional Query Per Problem**: Even with snapshot optimization, `ProblemSerializer.get_status()` queries `ProblemProgress` for each problem
2. **Unnecessary Database Load**: Problem status is static data that changes infrequently, making it ideal for snapshot storage
3. **Inefficient Data Access**: The serializer already has access to snapshot data but still queries separately for status

### Performance Impact (Estimated)

For a course with 50 algorithm problems:
- **Base queries with snapshot**: 1 (problems) + 1 (snapshot) = 2 queries
- **Status queries**: 50 problems × 1 query = **50 extra queries**
- **Total**: **~52 queries/request**
- **With this enhancement**: **~2 queries/request** (96% reduction)

### Solution Strategy

**Extend Snapshot Data Structure**:
- Add `status` field to `unlock_states` JSON
- Batch query `ProblemProgress` during snapshot computation
- Update serializer to prioritize snapshot data for status
- Maintain backward compatibility with old snapshots

**Impact**:
- Snapshot computation: +100ms (one-time batch query)
- Request performance: -50 queries/request
- Backward compatibility: 100% (fallback to database query)

## Requirements

### Requirement: Snapshot Must Store Problem Status

**Status**: ADDED

The `ProblemUnlockSnapshot.unlock_states` JSONField MUST store both the unlock state (`unlocked`) and the problem progress status (`status`) for each problem, enabling the serializer to retrieve all user-specific data from the snapshot.

#### Scenario: Snapshot Includes Status Field

**GIVEN** a course has 10 problems, user has completed 3
**WHEN** the system recomputes the problem unlock snapshot
**THEN** `unlock_states` JSON MUST include:
- For completed 3 problems: `{"unlocked": true, "status": "solved", "reason": null}`
- For incomplete 7 problems: `{"unlocked": true, "status": "not_started", "reason": null}` or `{"unlocked": false, "status": "not_started", "reason": "prerequisite"}`

#### Scenario: Snapshot Batch Queries ProblemProgress

**GIVEN** a course has 100 problems, user has completed 50
**WHEN** the system recomputes the problem unlock snapshot
**THEN** the system MUST use a single batch query to fetch all 50 `ProblemProgress` records
**AND** snapshot computation time MUST be <600ms (increase <100ms)

#### Scenario: Backward Compatible with Old Snapshots

**GIVEN** an old snapshot with `unlock_states` format `{"10": {"unlocked": true, "reason": null}}` (no `status` field)
**WHEN** the serializer reads that snapshot
**THEN** the serializer MUST fall back to querying `ProblemProgress` table for `status`
**AND** MUST NOT throw `KeyError` or other exceptions

### Requirement: Serializer Must Prioritize Snapshot for Status

**Status**: ADDED

The `ProblemSerializer.get_status()` method MUST read from `context['unlock_states']` first, only querying the database when the snapshot doesn't exist or lacks the `status` field.

#### Scenario: Direct Return When Snapshot Has Status

**GIVEN** `context['unlock_states'] = {"10": {"unlocked": true, "status": "solved"}}`
**WHEN** the serializer serializes problem with ID=10
**THEN** `get_status()` method MUST return `"solved"`
**AND** MUST NOT query `ProblemProgress` table

#### Scenario: Query Database When Snapshot Lacks Status

**GIVEN** `context['unlock_states'] = {"10": {"unlocked": true}}` (missing `status` field)
**WHEN** the serializer serializes problem with ID=10
**THEN** `get_status()` method MUST query `ProblemProgress` table for `status`
**AND** return query result or `"not_started"` (if record doesn't exist)

#### Scenario: Query Database When Snapshot Doesn't Exist

**GIVEN** `context` doesn't have `unlock_states`
**WHEN** the serializer serializes a problem
**THEN** `get_status()` method MUST use the original logic to query `ProblemProgress` table

### Requirement: Serializer Must Read unlock_states Directly from Context

**Status**: MODIFIED

The `ProblemSerializer.get_is_unlocked()` method MUST read directly from `context['unlock_states']`, removing the dependency on `view._use_snapshot` flag to decouple the serializer from the view instance.

#### Scenario: Prioritize Reading unlock_states from Context

**GIVEN** `context['unlock_states'] = {"10": {"unlocked": true, "status": "solved"}}`
**WHEN** `get_is_unlocked()` serializes problem with ID=10
**THEN** the method MUST get data from `context['unlock_states']`
**AND** return `problem_state['unlocked']` = `true`
**AND** MUST NOT check `view._use_snapshot` flag

#### Scenario: Fallback When unlock_states Doesn't Exist

**GIVEN** `context` doesn't have `unlock_states`
**WHEN** `get_is_unlocked()` executes
**THEN** the method MUST fall back to calling `unlock_condition.is_unlocked(user)`
**AND** return calculation result or `true` (if no unlock condition)

### Requirement: get_next_problem Must Use Snapshot Data

**Status**: ADDED

The `ProblemViewSet.get_next_problem()` method MUST prioritize snapshot data (`view._unlock_states`), only falling back to real-time computation `unlock_condition.is_unlocked(user)` when the snapshot doesn't exist or is stale.

#### Scenario: Use Snapshot Data in Snapshot Mode

**GIVEN** user has visited problem list, `view._unlock_states` is set
**AND** `view._use_snapshot = true`
**WHEN** user requests `/problems/next?type=algorithm&id=10`
**THEN** the system MUST read unlock states from `view._unlock_states` for subsequent problems
**AND** MUST NOT call `unlock_condition.is_unlocked(user)` method
**AND** database query count MUST be 0 (except for getting queryset)

#### Scenario: Fallback to Real-time Calculation When Snapshot Stale

**GIVEN** `view._use_snapshot = false` (snapshot stale or doesn't exist)
**WHEN** user requests `/problems/next?type=algorithm&id=10`
**THEN** the system MUST call `unlock_condition.is_unlocked(user)` to check each problem
**AND** return the first unlocked problem

#### Scenario: Default to Unlocked When Problem Not in Snapshot

**GIVEN** `view._unlock_states = {"11": {"unlocked": true}}` (doesn't contain problem ID=12)
**WHEN** iterating to problem with ID=12
**THEN** the system MUST assume the problem is unlocked
**AND** return it as the next problem

### Requirement: ViewSet Must Pass unlock_states to Serializer Context

**Status**: ADDED

The `ProblemViewSet.get_serializer_context()` method MUST pass `view._unlock_states` to `context['unlock_states']` when calling the serializer, enabling direct access to snapshot data.

#### Scenario: Pass unlock_states When Snapshot Exists

**GIVEN** `view._unlock_states = {"10": {"unlocked": true, "status": "solved"}}`
**WHEN** `get_serializer_context()` executes
**THEN** returned `context` MUST include `context['unlock_states']` = `view._unlock_states`

#### Scenario: Don't Pass unlock_states When Snapshot Doesn't Exist

**GIVEN** `view` doesn't have `_unlock_states` attribute
**WHEN** `get_serializer_context()` executes
**THEN** returned `context` MUST NOT include `unlock_states` key

### Requirement: Snapshot Computation Must Execute in Async Task

**Status**: MODIFIED

The `ProblemUnlockSnapshot.recompute()` MUST execute in a Celery async task, not blocking user requests, to ensure system response time is not affected.

#### Scenario: Async Snapshot Refresh After Problem Solve

**GIVEN** user completes a problem, `ProblemProgress.status` updates to `"solved"`
**WHEN** `ProblemProgress` save triggers `post_save` signal
**THEN** the system MUST mark snapshot as stale (`is_stale = true`)
**AND** trigger async task `refresh_problem_unlock_snapshot.delay(enrollment_id)`
**AND** MUST NOT block the current HTTP request

#### Scenario: Scheduled Task Batch Refreshes Stale Snapshots

**GIVEN** system has 50 stale snapshots (`is_stale = true`)
**WHEN** Celery Beat executes `batch_refresh_stale_problem_snapshots()` every minute
**THEN** the system MUST batch fetch 50 stale snapshots
**AND** trigger separate async task `refresh_problem_unlock_snapshot.delay()` for each snapshot
**AND** each task's computation time MUST be <600ms

## Implementation Notes

### Data Structure Changes

**Before**:
```json
{
  "10": {"unlocked": true, "reason": null}
}
```

**After**:
```json
{
  "10": {"unlocked": true, "status": "solved", "reason": null}
}
```

### Migration Strategy

1. **No data migration required**: Old snapshots without `status` will trigger fallback queries
2. **Gradual upgrade**: Snapshots will be regenerated on next async refresh cycle
3. **Zero downtime**: System remains fully operational during transition

### Performance Monitoring

Key metrics to track:
- Snapshot computation time (target: <600ms)
- Problem list API response time (target: <200ms for 50 problems)
- Database query count per request (target: 2-3 queries)
- Snapshot cache hit rate (target: >95%)

## Testing Requirements

### Unit Tests

1. **Snapshot.recompute()**: Verify `status` field is included in `unlock_states`
2. **Serializer.get_status()**: Test all three scenarios (snapshot with status, snapshot without status, no snapshot)
3. **Serializer.get_is_unlocked()**: Verify context-based access
4. **ViewSet integration**: Verify context passing

### Integration Tests

1. **End-to-end flow**: Submit solution → snapshot marked stale → async refresh → status included
2. **Backward compatibility**: Verify old snapshots still work correctly
3. **Performance**: Measure query count and response time with 50+ problems

### Load Tests

1. **Concurrent requests**: 25+ concurrent users viewing problem list
2. **Snapshot refresh**: 50+ snapshots recomputing simultaneously
3. **Race conditions**: Multiple problem submissions triggering snapshot refresh

## Rollback Plan

If issues occur:
1. **Immediate fallback**: Remove `status` from serializer context logic
2. **Feature flag**: Disable snapshot status inclusion via configuration
3. **Data cleanup**: No cleanup needed; old format remains compatible

No data migration rollback needed as the enhancement is backward compatible.
