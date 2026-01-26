# Spec: Nested Route Cache Isolation

## ADDED Requirements

### Requirement: Nested route cache keys must include parent resource primary keys

To ensure cache correctness for nested API endpoints, the cache key generation MUST include all parent resource primary keys from the URL path.

#### Scenario: Different parent resources produce different cache keys

**Given** a nested route endpoint `/api/v1/courses/{course_pk}/chapters`
**When** a request is made to `/api/v1/courses/1/chapters?page=1`
**Then** the cache key must include `course_pk=1`
**And** the cache key must be unique from `/api/v1/courses/2/chapters?page=1`

#### Scenario: Deeply nested routes include all ancestor pks

**Given** a doubly-nested route `/api/v1/courses/{course_pk}/chapters/{chapter_pk}/problems`
**When** a request is made to `/api/v1/courses/1/chapters/5/problems?page=1`
**Then** the cache key must include both `course_pk=1` AND `chapter_pk=5`
**And** the cache key format must be: `api:ProblemViewSet:course_pk=1:chapter_pk=5:page=1`

#### Scenario: Non-nested routes work as before

**Given** a top-level endpoint `/api/v1/courses`
**When** a request is made to `/api/v1/courses?page=1`
**Then** the cache key must NOT include any parent pk component
**And** the cache key format must be: `api:CourseViewSet:page=1`

### Requirement: Parent pks are extracted from view kwargs using DRF nested router convention

The cache mixin MUST extract parent primary keys from `self.kwargs` using the Django REST Framework nested router naming pattern.

#### Scenario: Parent lookup kwarg is extracted correctly

**Given** a view with `self.kwargs = {'course_pk': '1', 'pk': '5'}`
**When** generating a cache key
**Then** `course_pk='1'` must be included in the cache key
**And** `pk` (the resource's own lookup) must be handled separately for retrieve operations
**And** only parent lookup keys (those ending in `_pk`) must be used for list operations

#### Scenario: Multiple parent pks are sorted for consistency

**Given** a view with `self.kwargs = {'chapter_pk': '5', 'course_pk': '1'}`
**When** generating a cache key for a list endpoint
**Then** parent pks must be sorted alphabetically to ensure consistent key generation
**And** the cache key must be: `api:ProblemViewSet:course_pk=1:chapter_pk=5`

### Requirement: Cache invalidation respects nested route structure

When invalidating caches for nested routes, the invalidation MUST include parent resource primary keys to avoid clearing unrelated caches.

#### Scenario: Invalidating nested route list cache

**Given** a chapter under course 1 is modified
**When** the chapter's cache is invalidated
**Then** only caches with `course_pk=1` should be invalidated
**And** caches for `course_pk=2` must remain intact

#### Scenario: InvalidateCacheMixin supports parent pk context

**Given** an InvalidateCacheMixin used on a nested route viewset
**When** `_invalidate_all_list_cache()` is called
**Then** the invalidation pattern must include parent pks if present
**And** the pattern must match only the specific nested route's caches

## Related Capabilities

- **progress-cache**: Nested route progress caching depends on correct cache key isolation

## Implementation Notes

The `get_cache_key()` utility function signature should be extended to support:
```python
def get_cache_key(prefix, view_name=None, pk=None, query_params=None, allowed_params=None, parent_pks=None):
    """
    Args:
        parent_pks: Dict of parent resource pks (e.g., {'course_pk': '1', 'chapter_pk': '5'})
    """
```

The `CacheListMixin` should extract parent pks from `self.kwargs` by filtering for keys matching the pattern `{parent_lookup}_pk`.
