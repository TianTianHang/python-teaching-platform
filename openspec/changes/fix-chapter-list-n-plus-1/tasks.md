## 1. ChapterSerializer.get_status() Optimization

- [ ] 1.1 Modify get_status() to use pre-fetched user_progress data
- [ ] 1.2 Implement fallback to direct query for non-prefetched scenarios
- [ ] 1.3 Verify status field works for all user types

## 2. ChapterSerializer Permission Methods Optimization

- [ ] 2.1 Update get_is_locked() to use pre-fetched enrollment data
- [ ] 2.2 Optimize get_prerequisite_progress() using progress records
- [ ] 2.3 Ensure all permission checks maintain existing behavior

## 3. ChapterUnlockConditionSerializer Optimization

- [ ] 3.1 Update get_prerequisite_chapters() to avoid N+1 course queries
- [ ] 3.2 Optimize get_prerequisite_titles() using pre-fetched data
- [ ] 3.3 Ensure unlock condition data access is efficient

## 4. ChapterViewSet Prefetch Enhancement

- [ ] 4.1 Add prefetch_related for unlock_condition__prerequisite_chapters__course
- [ ] 4.2 Verify all prefetch optimizations work together
- [ ] 4.3 Test with different chapter query filters

## 5. Testing and Verification

- [ ] 5.1 Run existing tests to ensure no regressions
- [ ] 5.2 Create performance test to verify N+1 elimination
- [ ] 5.3 Test with both authenticated and unauthenticated users
- [ ] 5.4 Verify API responses remain unchanged