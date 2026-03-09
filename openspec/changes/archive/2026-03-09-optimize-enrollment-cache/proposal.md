## Why

Enrollment cache operations are taking 1.8+ seconds even on cache hits, causing slow API responses. Analysis reveals the root cause: `EnrollmentSerializer.get_next_chapter()` serializes full `Chapter` objects (~50KB each with nested `unlock_condition`, `prerequisite_chapters`, `content`, etc.) when the frontend only needs `id` and `title`. This causes massive JSON serialization/deserialization overhead.

## What Changes

- **Create `ChapterSummarySerializer`**: New lightweight serializer with only `id`, `title`, `order` fields
- **Update `EnrollmentSerializer.get_next_chapter()`**: Use `ChapterSummarySerializer` instead of full `ChapterSerializer`
- **Update tests**: Adjust test assertions to expect simplified chapter data structure
- **No API contract changes**: Frontend already only uses `id` and `title` from `next_chapter`, so this is fully backward compatible

## Capabilities

### New Capabilities
None - this is a performance optimization with no new functionality.

### Modified Capabilities
None - the API contract remains unchanged. Frontend behavior is unaffected.

## Impact

- **Backend**: `courses/serializers.py` (add `ChapterSummarySerializer`, modify `EnrollmentSerializer`)
- **Tests**: `courses/tests/test_serializers.py` (update `next_chapter` assertions)
- **Performance**: Expected 36x improvement (1.8s → ~50ms per cache read)
- **Cache size**: ~100x reduction in enrollment cache entry size (50KB → ~500 bytes)
- **No breaking changes**: Frontend already only uses `id` and `title`, so no frontend code changes needed
