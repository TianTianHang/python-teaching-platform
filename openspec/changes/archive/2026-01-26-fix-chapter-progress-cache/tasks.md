## 1. Implementation

- [x] 1.1 Add signal handler for `ChapterProgress` model in `backend/courses/signals.py`
  - Import `ChapterProgress`, `ChapterViewSet`, `ChapterProgressViewSet`, `EnrollmentViewSet`
  - Create `@receiver([post_save, post_delete], sender=ChapterProgress)` function
  - Invalidate `ChapterViewSet` list cache
  - Invalidate `ChapterProgressViewSet` list cache
  - Invalidate `EnrollmentViewSet` list cache (since progress percentage and next chapter depend on ChapterProgress)
- [x] 1.2 Verify the signal handler is registered by checking `apps.py` or `__init__.py`
- [x] 1.3 Test the cache invalidation manually or add test cases

## 2. Testing

- [x] 2.1 Write test case: `test_chapter_progress_signal_invalidates_cache_on_create`
  - Create a chapter progress record
  - Verify that ChapterViewSet cache is invalidated
  - Verify that ChapterProgressViewSet cache is invalidated
  - Verify that EnrollmentViewSet cache is invalidated
- [x] 2.2 Write test case: `test_chapter_progress_signal_invalidates_cache_on_update`
  - Update an existing chapter progress (mark as completed)
  - Verify that all related caches are invalidated
  - Call chapter detail API and verify completed status is returned
- [x] 2.3 Write test case: `test_chapter_progress_signal_invalidates_cache_on_delete`
  - Delete a chapter progress record
  - Verify that all related caches are invalidated
- [x] 2.4 Write test case: `test_mark_as_completed_invalidates_cache`
  - Call the `mark_as_completed` action API
  - Verify that chapter status returns "completed" in subsequent API calls
  - Verify that enrollment progress percentage is updated correctly
  - Verify that next chapter is updated correctly
- [x] 2.5 Write test case: `test_chapter_progress_cache_invalidation_consistency_with_problem_progress`
  - Verify that ChapterProgress signal follows the same pattern as ProblemProgress
  - Ensure cache keys are constructed correctly
- [x] 2.6 Run all tests: `uv run python manage.py test courses.tests.test_signals`
- [x] 2.7 Verify manual testing: Use API client or frontend to test the full flow
