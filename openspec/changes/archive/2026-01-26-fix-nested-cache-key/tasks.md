# Tasks: Fix Nested Route Cache Key Generation

## Implementation Tasks

### 1. Update cache utility to support parent pks
**File**: `backend/common/utils/cache.py`

- [x] Add `parent_pks` parameter to `get_cache_key()` function signature
- [x] Implement parent pk serialization: sort alphabetically and format as `key=value` pairs
- [x] Include parent pks in cache key between `view_name` and `pk`/query_params components
- [x] Add unit tests for `get_cache_key()` with parent_pks argument
- [x] Verify backward compatibility (calls without parent_pks still work)

### 2. Update CacheListMixin to extract parent pks from kwargs
**File**: `backend/common/mixins/cache_mixin.py`

- [x] Add `_get_parent_pks()` method to extract parent lookup values from `self.kwargs`
- [x] Filter for keys matching DRF nested router pattern (keys ending in `_pk`)
- [x] Sort parent pks alphabetically for consistent key generation
- [x] Update `list()` method to pass parent_pks to `get_cache_key()`
- [x] Add unit tests verifying cache keys differ for different parent resources

### 3. Update InvalidateCacheMixin to support nested routes
**File**: `backend/common/mixins/cache_mixin.py`

- [x] Add `parent_pks` parameter to `_get_base_cache_key()` method
- [x] Update `_invalidate_all_list_cache()` to include parent pks in invalidation pattern
- [x] Ensure invalidation patterns are specific to the nested route context
- [x] Add tests verifying only relevant caches are invalidated

### 4. Add integration tests for nested route caching
**File**: `backend/common/tests/test_cache_mixin.py` (created)

- [x] Test `/api/v1/courses/1/chapters` and `/api/v1/courses/2/chapters` return different data
- [x] Test doubly-nested routes `/api/v1/courses/1/chapters/5/problems` have correct cache keys
- [x] Test cache invalidation on nested routes doesn't affect other parent resources
- [x] Test top-level (non-nested) routes still work correctly

### 5. Update existing test that may be affected
**File**: `backend/courses/tests/test_signals.py`

- [x] Review existing tests that hit nested endpoints
- [x] Verify tests still pass with new cache key format
- [x] Add assertions to verify cache isolation between parent resources

## Validation Tasks

### 6. Manual verification
- [x] Start Redis and Django dev server
- [x] Create two courses with different chapters
- [x] Request `/api/v1/courses/1/chapters` and verify response
- [x] Request `/api/v1/courses/2/chapters` and verify different data is returned
- [x] Verify Redis keys show different cache keys for each course

### 7. Performance verification
- [x] Run benchmark before and after changes
- [x] Verify cache hit/miss ratios remain similar
- [x] Confirm no performance regression from additional cache key processing

## Dependencies

- Task 2 depends on Task 1 (cache utility must be updated first)
- Task 3 depends on Task 1
- Tasks 4 and 5 can run in parallel after Task 1 and 2 are complete
- Tasks 6 and 7 depend on all implementation tasks being complete

## Testing Strategy

1. **Unit tests**: Test `get_cache_key()` with various parent_pks combinations
2. **Mixin tests**: Test CacheListMixin and InvalidateCacheMixin with mocked kwargs
3. **Integration tests**: Test actual API endpoints with nested routes
4. **Regression tests**: Ensure non-nested routes continue working
