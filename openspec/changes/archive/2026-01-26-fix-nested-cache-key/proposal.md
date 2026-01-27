# Proposal: Fix Nested Route Cache Key Generation

## Summary

Fix a critical bug in `CacheListMixin` where nested route API endpoints generate identical cache keys for different parent resources, causing incorrect data to be returned.

## Problem

When accessing nested route endpoints like `/api/v1/courses/{course_pk}/chapters`:
- The cache key is generated using only `view_name` and `query_params`
- The parent resource's primary key (`course_pk`) from the URL path is NOT included
- This causes different endpoints to share the same cache key:

```
GET /api/v1/courses/1/chapters?page=1
  → cache key: "api:ChapterViewSet:page=1"

GET /api/v1/courses/2/chapters?page=1
  → cache key: "api:ChapterViewSet:page=1"  ← SAME KEY!
```

**Impact**: After accessing course 1's chapters, subsequent requests to course 2's chapters return course 1's cached data.

## Affected Endpoints

All nested route list endpoints that use `CacheListMixin`:
- `/api/v1/courses/{course_pk}/chapters`
- `/api/v1/courses/{course_pk}/chapters/{chapter_pk}/problems`
- `/api/v1/courses/{course_pk}/threads`
- `/api/v1/courses/{course_pk}/exams`
- `/api/v1/chapters/{chapter_pk}/threads`
- `/api/v1/problems/{problem_pk}/threads`
- `/api/v1/problems/{problem_pk}/submissions`
- `/api/v1/problems/{problem_pk}/drafts`
- `/api/v1/threads/{thread_pk}/replies`

## Root Cause

In `backend/common/mixins/cache_mixin.py:12-21`, the `CacheListMixin.list()` method calls `get_cache_key()` with:
- `prefix` (e.g., "api")
- `view_name` (e.g., "ChapterViewSet")
- `query_params` (e.g., {"page": "1"})

But it does NOT pass the parent resource pk from `self.kwargs` (e.g., `course_pk=1`).

## Proposed Solution

1. **Modify `CacheListMixin.list()`** to extract parent resource pks from `self.kwargs` and include them in the cache key

2. **Modify `InvalidateCacheMixin`** to properly invalidate nested route caches by including parent pks

3. **Add `parent_pks` parameter to `get_cache_key()`** in `backend/common/utils/cache.py` to support nested resource identification

## Key Changes

### Cache Key Format

**Before**:
```
api:ChapterViewSet:page=1
```

**After**:
```
api:ChapterViewSet:course_pk=1:page=1
api:ChapterViewSet:course_pk=2:page=1
```

For deeply nested routes:
```
api:ProblemViewSet:course_pk=1:chapter_pk=5:page=1
```

### Implementation Approach

1. Update `get_cache_key()` in `cache.py` to accept a `parent_pks` dict
2. Update `CacheListMixin` to extract parent lookup values from `self.kwargs`
3. Use DRF's standard pattern: `self.kwargs` contains `{parent_lookup}_{lookup_field}` for nested routes
4. Update `InvalidateCacheMixin` to support parent pk-based invalidation

## Related Specs

- **progress-cache**: This fix ensures nested route caches are correctly isolated per parent resource, which is critical for the progress caching feature

## Alternatives Considered

1. **Disable caching for nested routes**: Would fix correctness but lose performance benefits
2. **Include full URL in cache key**: Simpler but less maintainable; current approach is more explicit
3. **Use request.path in cache key**: Would work but ties cache to URL structure rather than resource identity
