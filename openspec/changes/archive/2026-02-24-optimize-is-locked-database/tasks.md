## 1. Backend Infrastructure Preparation

- [x] 1.1 Add database indexes for ChapterUnlockCondition.prerequisite_chapters (if not exists)
- [x] 1.2 Ensure ChapterProgress.chapter_id and enrollment_id have proper indexes
- [x] 1.3 Create a backup of existing courses/views.py before modifications
- [x] 1.4 Review existing test cases for chapter list performance

## 2. Modify ChapterViewSet.get_queryset()

- [x] 2.1 Update get_queryset() to detect student users
- [x] 2.2 Create _annotate_is_locked() method with database annotations
- [x] 2.3 Implement prerequisite check using Exists subquery
- [x] 2.4 Implement date check using Exists subquery
- [x] 2.5 Combine conditions using Case statement for is_locked_db
- [x] 2.6 Update query structure to only add annotations for student users
- [x] 2.7 Remove _filter_locked_chapters() method (replaced with _annotate_is_locked)

## 3. Modify ChapterSerializer

- [x] 3.1 Update get_is_locked() to check for is_locked_db attribute first
- [x] 3.2 Implement fallback to ChapterUnlockService.is_unlocked() when no annotation
- [x] 3.3 Add debug logging for fallback cases
- [x] 3.4 Ensure prerequisite_progress field behavior remains unchanged

## 4. Update Performance Tests

- [x] 4.1 Modify test_chapter_list_with_prefetch_verify to verify new query count
- [x] 4.2 Update performance test to accept < 5 total queries instead of current limits
- [x] 4.3 Add test case for database annotation fallback scenario
- [x] 4.4 Run existing tests to ensure no regression

## 5. Debug and Optimization

- [ ] 5.1 Enable DEBUG SQL output to verify generated queries
- [ ] 5.2 Test with courses having multiple unlock condition types
- [ ] 5.3 Verify edge cases (no unlock conditions, mixed conditions)
- [ ] 5.4 Optimize SQL query if performance is still suboptimal
- [ ] 5.5 Add database EXPLAIN ANALYZE for performance analysis

## 6. Integration Testing

- [x] 6.1 Test chapter list API with student user having locked chapters
- [x] 6.2 Test chapter list API with instructor user (should show all)
- [ ] 6.3 Test chapter list API with unauthenticated user
- [ ] 6.4 Verify prerequisite_progress still works correctly
- [ ] 6.5 Verify unlock_status action still works independently

## 7. Documentation and Cleanup

- [ ] 7.1 Update code comments explaining new database annotation approach
- [ ] 7.2 Remove any DEBUG code that's no longer needed
- [ ] 7.3 Update performance monitoring documentation
- [ ] 7.4 Run full test suite to ensure no breaking changes

## 8. Performance Validation

- [ ] 8.1 Benchmark chapter list response time with 10/50/100 chapters
- [ ] 8.2 Verify query count remains <= 3 for all scenarios
- [ ] 8.3 Test cache invalidation still works correctly
- [ ] 8.4 Compare performance before and after optimization