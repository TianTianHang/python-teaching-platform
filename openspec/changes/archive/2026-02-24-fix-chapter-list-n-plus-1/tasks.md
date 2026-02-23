## 1. ChapterSerializer.get_status() Optimization

- [x] 1.1 Modify get_status() to use pre-fetched user_progress data
- [x] 1.2 Implement fallback to direct query for non-prefetched scenarios
- [x] 1.3 Verify status field works for all user types

## 2. ChapterSerializer Permission Methods Optimization

- [x] 2.1 Update get_is_locked() to use pre-fetched enrollment data
- [x] 2.2 Optimize get_prerequisite_progress() using progress records
- [x] 2.3 Ensure all permission checks maintain existing behavior

## 3. ChapterUnlockConditionSerializer Optimization

- [x] 3.1 Update get_prerequisite_chapters() to avoid N+1 course queries
- [x] 3.2 Optimize get_prerequisite_titles() using pre-fetched data
- [x] 3.3 Ensure unlock condition data access is efficient

## 4. ChapterViewSet Prefetch Enhancement

- [x] 4.1 Add prefetch_related for unlock_condition__prerequisite_chapters__course
- [x] 4.2 Verify all prefetch optimizations work together
- [x] 4.3 Test with different chapter query filters

## 5. Testing and Verification

- [x] 5.1 Run existing tests to ensure no regressions
- [x] 5.2 Create performance test to verify N+1 elimination
- [x] 5.3 Test with both authenticated and unauthenticated users
- [x] 5.4 Verify API responses remain unchanged