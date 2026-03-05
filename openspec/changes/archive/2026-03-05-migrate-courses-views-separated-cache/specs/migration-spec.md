# Migration Spec: courses/views.py Separated Cache

## Overview

This change migrates the separated cache implementation in `courses/views.py` from direct `cache.get/set` usage to the unified service layer (`SeparatedCacheService`) created in Phase 1.

**Type**: Migration (refactoring, no new capabilities)

**Scope**: 
- 4 ViewSet methods in `courses/views.py`
- ChapterViewSet.list(), ChapterViewSet.retrieve()
- ProblemViewSet.list(), ProblemViewSet.retrieve()

## No New Capabilities

This is a migration of existing functionality to a new API. No new capabilities are added.

**Existing capabilities used** (from Phase 1):
- `separated-cache-service`: Provides `SeparatedCacheService.get_global_data()`
- `cache-invalidation-api`: Provides `CacheInvalidator` for cache invalidation

## Migration Details

### Key Changes

| Aspect | Before | After |
|--------|--------|-------|
| Cache API | `cache.get(key)`, `cache.set(key, value, timeout)` | `SeparatedCacheService.get_global_data()` |
| Key Format | `chapter:global:list:{course_id}` | `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk={course_id}` |
| Metrics | None | Auto-recorded via `get_cache(return_result=True)` |
| Penetration Protection | None | Uses `CacheResult.is_null_value` |
| Logging | Manual debug logs | Automatic hit/miss logging |

### Compatibility

- **API Compatible**: Request/response format unchanged
- **Cache Compatible**: Dual-write during transition period (1 week)
- **Test Compatible**: Existing tests updated to mock new service

## ADDED Requirements

### Requirement: ViewSet methods use SeparatedCacheService for global data caching

The ChapterViewSet and ProblemViewSet SHALL use `SeparatedCacheService.get_global_data()` for caching global data instead of direct `cache.get/set` calls.

#### Scenario: ChapterViewSet.list() cache hit
- **WHEN** user requests chapter list with valid cache
- **THEN** system returns cached data with cache key `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk={course_id}`
- **AND** Prometheus metric `cache_requests_total` is incremented with status="hit"

#### Scenario: ChapterViewSet.list() cache miss
- **WHEN** user requests chapter list with no valid cache
- **THEN** system fetches data from database
- **AND** data is cached with TTL=1800 seconds
- **AND** Prometheus metric `cache_requests_total` is incremented with status="miss"

#### Scenario: ChapterViewSet.retrieve() cache hit
- **WHEN** user requests single chapter with valid cache
- **THEN** system returns cached data with cache key `courses:ChapterViewSet:SEPARATED:GLOBAL:pk={chapter_id}:parent_pk={course_id}`
- **AND** Prometheus metric is recorded

#### Scenario: ChapterViewSet.retrieve() cache miss
- **WHEN** user requests single chapter with no valid cache
- **THEN** system fetches data from database
- **AND** data is cached with TTL=1800 seconds

#### Scenario: ProblemViewSet.list() cache hit
- **WHEN** user requests problem list with valid cache
- **THEN** system returns cached data with cache key `courses:ProblemViewSet:SEPARATED:GLOBAL:parent_pk={chapter_id}`

#### Scenario: ProblemViewSet.list() cache miss
- **WHEN** user requests problem list with no valid cache
- **THEN** system fetches data from database
- **AND** data is cached with TTL=1800 seconds

#### Scenario: ProblemViewSet.retrieve() cache hit
- **WHEN** user requests single problem with valid cache
- **THEN** system returns cached data with cache key `courses:ProblemViewSet:SEPARATED:GLOBAL:pk={problem_id}:parent_pk={chapter_id}`

#### Scenario: ProblemViewSet.retrieve() cache miss
- **WHEN** user requests single problem with no valid cache
- **THEN** system fetches data from database
- **AND** data is cached with TTL=1800 seconds

### Requirement: Dual-write during transition period

During the transition period (1 week), the system SHALL write to both old and new cache keys to maintain backward compatibility.

#### Scenario: Dual-write on cache miss
- **WHEN** cache miss occurs
- **THEN** data is written to new key format `courses:ChapterViewSet:SEPARATED:GLOBAL:...`
- **AND** data is written to old key format `chapter:global:list:{course_id}`

#### Scenario: Old key expiration
- **WHEN** TTL (30 minutes) expires
- **THEN** old key is automatically deleted
- **AND** only new key format remains

### Requirement: Cache hit/miss logging

The system SHALL log cache hit/miss events for debugging purposes.

#### Scenario: Cache hit logged
- **WHEN** cache hit occurs
- **THEN** debug log message "Global cache HIT for course {course_id}" is emitted

#### Scenario: Cache miss logged
- **WHEN** cache miss occurs
- **THEN** debug log message "Global cache MISS for course {course_id}, data fetched from DB" is emitted

### Requirement: Cache penetration protection

The system SHALL use `CacheResult.is_null_value` to prevent cache penetration attacks.

#### Scenario: Null value protection
- **WHEN** data_fetcher returns None or empty result
- **THEN** system marks value as null in cache
- **AND** subsequent requests return null value without calling data_fetcher
- **AND** cache penetration is prevented

## Migration Notes

### Rollback Plan

If cache hit rate drops > 10% or response time increases > 20%:
1. Revert code changes with `git revert <commit>`
2. Old cache keys remain valid (dual-write)
3. No data loss

### Performance Impact

- Service layer overhead: < 1μs (verified in Phase 1)
- No degradation expected
- Metrics auto-recorded for monitoring

### Test Coverage

- Unit tests: Mock `SeparatedCacheService.get_global_data()`
- Integration tests: Verify Redis key creation
- Manual tests: Verify API response correctness