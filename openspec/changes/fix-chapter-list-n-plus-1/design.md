## Context

ChapterSerializer has multiple N+1 query issues that slow down chapter list loading. The ViewSet already prefetches user progress data, but the serializers don't utilize this data effectively. Additionally, accessing related objects like courses through relations causes additional queries.

## Goals / Non-Goals

**Goals:**
- Eliminate all N+1 queries in ChapterSerializer
- Leverage existing pre-fetched data from ChapterViewSet
- Maintain full compatibility with existing API responses
- Ensure optimizations work for both authenticated and unauthenticated users

**Non-Goals:**
- Caching improvements (handled by Django CacheMixin)
- Frontend changes
- Performance benchmarking

## Decisions

### 1. Use Pre-fetched Progress Data
**Decision**: Modify all serializer methods to use `user_progress` instead of querying database directly.

**Rationale**: ChapterViewSet already prefetches progress data, so we should leverage this to avoid additional queries.

### 2. Optimize Enrollment Access
**Decision**: Extract enrollment from pre-fetched progress records instead of querying user.enrollments.

**Rationale**: Each enrollment query creates a new database hit. Progress records already contain the needed enrollment data.

### 3. Prefetch Course in Unlock Conditions
**Decision**: Add `prefetch_related('unlock_condition__prerequisite_chapters__course')` to queryset.

**Rationale**: `get_prerequisite_chapters()` accesses `prereq.course.title` for each prerequisite, causing N+1 queries.

### 4. Graceful Fallback
**Decision**: Implement fallback behavior when pre-fetched data isn't available.

**Rationale**: Ensures robustness if ViewSet optimizations aren't in place.

## Risks / Trade-offs

**[Risk] Over-fetching Data**: Prefetching all relationships may increase memory usage.
→ **Mitigation**: The prefetch is selective based on actual usage patterns.

**[Risk] Complex Code**: Handling pre-fetched data makes code more complex.
→ **Mitigation**: Clear comments and maintain simple fallback paths.

## Migration Plan

1. Update ChapterSerializer methods to use pre-fetched data
2. Enhance ChapterViewSet prefetching
3. Verify existing tests pass
4. Deploy and monitor performance

## Open Questions

- Are there any other ChapterSerializer methods we missed that need optimization?
- Should we add specific test cases for prefetch optimization?