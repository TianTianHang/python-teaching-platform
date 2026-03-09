## 1. Implement ChapterSummarySerializer

- [x] 1.1 Add ChapterSummarySerializer class to `backend/courses/serializers.py`
  - Should extend `serializers.ModelSerializer`
  - Should include fields: `id`, `title`, `order`
  - Place after `ChapterGlobalSerializer` (around line 163)

## 2. Update EnrollmentSerializer

- [x] 2.1 Modify `EnrollmentSerializer.get_next_chapter()` method
  - Import `ChapterSummarySerializer` at top of file (if not already imported)
  - Replace `ChapterSerializer(next_chapter).data` with `ChapterSummarySerializer(next_chapter).data`
  - File: `backend/courses/serializers.py`

## 3. Run Tests and Verify

- [x] 3.1 Run serializer tests to verify changes
  - Command: `cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_serializers -v 2`
  - Expected: All tests pass with updated next_chapter structure

- [x] 3.2 Run cache-related tests to ensure no regressions
  - Command: `cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_cache -v 2`

## 4. Verify Performance Improvement (Optional)

- [x] 4.1 Check cache latency in logs after deployment
  - Look for `cache_hit` entries in `logs/cache.log`
  - Expected: Cache read times drop from ~1800ms to ~50ms