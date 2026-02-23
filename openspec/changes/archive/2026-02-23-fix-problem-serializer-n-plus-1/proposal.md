## Why

The ProblemSerializer in the backend currently suffers from severe N+1 query issues, particularly in the `get_status()` method which executes a database query for each problem to fetch user progress. This causes performance degradation when loading problem lists, especially as the number of problems grows.

## What Changes

- Fix N+1 query in `ProblemSerializer.get_status()` by using pre-fetched `user_progress_list` data from ViewSet
- Optimize `ProblemSerializer.get_unlock_condition_description()` by prefetching prerequisite problems data
- Add appropriate select_related and prefetch_related to QuerySet to prevent additional database hits
- Ensure all problem list APIs are optimized for performance

## Capabilities

### New Capabilities
- `problem-list-optimization`: Optimize problem list API by eliminating N+1 queries in ProblemSerializer

### Modified Capabilities
- `problem-status-retrieval`: Improve performance of user progress retrieval from O(n) queries to O(1)

## Impact

- **Backend**: courses/serializers.py, courses/views.py ProblemViewSet
- **API**: `/api/problems/` list endpoint performance improvement
- **Database**: Reduced query count from ~n+1 to 2-3 queries per problem list request
- **Frontend**: Problem lists will load faster, especially for users with many problems
- **Tests**: Test coverage for prefetch optimization needs to be maintained