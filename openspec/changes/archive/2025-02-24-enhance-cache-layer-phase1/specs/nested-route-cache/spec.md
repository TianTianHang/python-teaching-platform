## MODIFIED Requirements

### Requirement: Nested route cache keys must include parent resource primary keys

To ensure cache correctness for nested API endpoints, the cache key generation MUST include all parent resource primary keys from the URL path.

#### Scenario: Different parent resources produce different cache keys

**Given** a nested route endpoint `/api/v1/courses/{course_pk}/chapters`
**WHEN** a request is made to `/api/v1/courses/1/chapters?page=1`
**THEN** the cache key must include `course_pk=1`
**AND** the cache key must be unique from `/api/v1/courses/2/chapters?page=1`

#### Scenario: Deeply nested routes include all ancestor pks

**Given** a doubly-nested route `/api/v1/courses/{course_pk}/chapters/{chapter_pk}/problems`
**WHEN** a request is made to `/api/v1/courses/1/chapters/5/problems?page=1`
**THEN** the cache key must include both `course_pk=1` AND `chapter_pk=5`
**AND** the cache key format must be: `api:ProblemViewSet:course_pk=1:chapter_pk=5:page=1`

#### Scenario: Non-nested routes work as before

**Given** a top-level endpoint `/api/v1/courses`
**WHEN** a request is made to `/api/v1/courses?page=1`
**THEN** the cache key must NOT include any parent pk component
**AND** the cache key format must be: `api:CourseViewSet:page=1`

---

### ADDED Requirement: Cache key structure must support sentinel values

Cache keys MUST be structured to properly handle sentinel values (HIT, MISS, NULL_VALUE) for penetration protection.

#### Scenario: Sentinel values don't interfere with nested key structure

**WHEN** a nested route returns NULL_VALUE (empty result)
**THEN** the cache key MUST maintain the parent pk structure
**AND** the sentinel status MUST be stored separately in cache metadata

#### Scenario: Cache invalidation works with sentinel value metadata

**WHEN** invalidating a nested route cache
**THEN** both the data cache AND metadata cache MUST be invalidated
**AND** the invalidation pattern MUST match the nested key structure

---

### MODIFIED Requirement: Parent pks are extracted from view kwargs using DRF nested router convention

The cache mixin MUST extract parent primary keys from `self.kwargs` using the Django REST Framework nested router naming pattern.

#### Scenario: Parent lookup kwarg is extracted correctly

**GIVEN** a view with `self.kwargs = {'course_pk': '1', 'pk': '5'}`
**WHEN** generating a cache key
**THEN** `course_pk='1'` must be included in the cache key
**AND** `pk` (the resource's own lookup) must be handled separately for retrieve operations
**AND** only parent lookup keys (those ending in `_pk`) must be used for list operations

#### Scenario: Multiple parent pks are sorted for consistency

**GIVEN** a view with `self.kwargs = {'chapter_pk': '5', 'course_pk': '1'}`
**WHEN** generating a cache key for a list endpoint
**THEN** parent pks must be sorted alphabetically to ensure consistent key generation
**AND** the cache key must be: `api:ProblemViewSet:course_pk=1:chapter_pk=5`

---

### MODIFIED Requirement: Cache invalidation respects nested route structure

When invalidating caches for nested routes, the invalidation MUST include parent resource primary keys to avoid clearing unrelated caches.

#### Scenario: Invalidating nested route list cache

**GIVEN** a chapter under course 1 is modified
**WHEN** the chapter's cache is invalidated
**THEN** only caches with `course_pk=1` should be invalidated
**AND** caches for `course_pk=2` must remain intact

#### Scenario: InvalidateCacheMixin supports parent pk context

**GIVEN** an InvalidateCacheMixin used on a nested route viewset
**WHEN** `_invalidate_all_list_cache()` is called
**THEN** the invalidation pattern must include parent pks if present
**AND** the pattern must match only the specific nested route's caches

---

### ADDED Requirement: Nested route cache supports short TTL for empty results

Empty results in nested routes MUST use short TTL to prevent cache bloat while maintaining proper key structure.

#### Scenario: Empty nested list has short TTL

**GIVEN** a nested route returns empty results (e.g., `/courses/1/chapters` with no chapters)
**WHEN** the result is cached
**THEN** the TTL MUST be set to 60 seconds (not the default 900 seconds)
**AND** the cache key MUST include the parent pk structure

#### Scenario: Empty nested detail has short TTL

**GIVEN** a nested route returns empty result (e.g., `/courses/1/chapters/999` for non-existent chapter)
**WHEN** the result is cached
**THEN** the TTL MUST be set to 60 seconds
**AND** the cache key MUST include parent pks for proper invalidation