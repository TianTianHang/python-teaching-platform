## Context

The ProblemSerializer currently has N+1 query issues when retrieving user progress and unlock conditions. The ProblemViewSet already prefetches user progress data using `Prefetch('progress_records', ...)` but the serializer doesn't utilize this data, instead querying the database again in `get_status()`.

## Goals / Non-Goals

**Goals:**
- Eliminate N+1 queries in ProblemSerializer by using pre-fetched data
- Maintain backward compatibility with existing API responses
- Ensure all functionality works without authentication
- Keep code maintainable and readable

**Non-Goals:**
- Performance testing (will be done separately)
- Frontend changes (only backend optimization)
- Caching improvements (handled by Django CacheMixin)

## Decisions

### 1. Use Pre-fetched Progress Data
**Decision**: Modify `get_status()` to use `user_progress_list` from pre-fetched data instead of querying ProblemProgress directly.

**Rationale**: The ProblemViewSet already prefetches user progress, so we should leverage this existing optimization rather than adding additional prefetches.

### 2. Add select_related for Unlock Condition
**Decision**: Add `select_related('unlock_condition')` to ProblemViewSet queryset.

**Rationale**: Most problems will have unlock conditions, and this avoids a separate query per problem to access the relation.

### 3. Prefetch Prerequisite Problems
**Decision**: Use `Prefetch('unlock_condition__prerequisite_problems')` for better performance when accessing prerequisite data.

**Rationale**: The `get_unlock_condition_description()` method frequently accesses prerequisite problems data, so prefetching this avoids multiple additional queries.

### 4. Graceful Handling for Missing Data
**Decision**: Implement fallback behavior when pre-fetched data isn't available.

**Rationale**: Ensures robustness if ViewSet optimizations aren't in place or if serializer is used independently.

## Risks / Trade-offs

**[Risk] Over-fetching Data**: Prefetching all problem types' details may fetch unused data.
→ **Mitigation**: ViewSet already filters by type, prefetching is conditional on request parameters.

**[Risk] Memory Usage**: Prefetching large relationship trees increases memory usage.
→ **Mitigation**: Use `to_attr` to control access to pre-fetched data, only access when needed.

**[Risk] Breaking Changes**: Changes to serializer methods may affect external consumers.
→ **Mitigation**: Maintain same return values and structure, only optimize internal queries.

## Migration Plan

1. Add select_related and prefetch to ProblemViewSet
2. Update ProblemSerializer.get_status() to use pre-fetched data
3. Update unlock_condition methods to handle pre-fetched data
4. Verify existing tests still pass
5. Deploy with feature flag if needed

## Open Questions

- Should we add database query logging to verify the optimization works?
- Are there any edge cases with unauthenticated users we should test specifically?