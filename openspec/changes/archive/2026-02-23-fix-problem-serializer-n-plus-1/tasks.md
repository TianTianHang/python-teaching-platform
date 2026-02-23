## 1. ProblemViewSet Optimization

- [x] 1.1 Add select_related('unlock_condition') to ProblemViewSet queryset
- [x] 1.2 Add prefetch_related for unlock_condition__prerequisite_problems
- [x] 1.3 Update get_queryset() to handle prefetch optimization for different problem types

## 2. ProblemSerializer.get_status() Fix

- [x] 2.1 Modify get_status() to use pre-fetched user_progress_list data
- [x] 2.2 Add fallback to direct query if pre-fetched data isn't available
- [x] 2.3 Verify status field works correctly for authenticated users

## 3. ProblemSerializer Unlock Condition Optimization

- [x] 3.1 Update get_unlock_condition_description() to handle pre-fetched data
- [x] 3.2 Optimize prerequisite problems retrieval from pre-fetched data
- [x] 3.3 Ensure unlock methods work with pre-fetched conditions

## 4. Testing and Verification

- [x] 4.1 Run existing tests to ensure no regressions
- [x] 4.2 Create test case for N+1 query fix verification
- [x] 4.3 Test with both authenticated and unauthenticated users
- [x] 4.4 Verify API responses remain unchanged