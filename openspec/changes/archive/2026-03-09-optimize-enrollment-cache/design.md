## Context

The `EnrollmentViewSet` API is slow due to cache deserialization overhead. Current implementation serializes full `Chapter` objects with all nested data (unlock conditions, prerequisite chapters, content, etc.) for the `next_chapter` field, resulting in ~50KB per enrollment cache entry. This causes 1.8+ second cache read times even on cache hits.

Frontend usage analysis shows only `id` and `title` from `next_chapter` are used (see `frontend/web-student/app/routes/_layout.home.tsx:261-271`).

## Goals / Non-Goals

**Goals:**
- Reduce enrollment cache entry size from ~50KB to ~500 bytes
- Improve cache read latency from 1.8s to ~50ms (36x improvement)
- Maintain full backward compatibility with frontend

**Non-Goals:**
- No changes to API contract (already compatible)
- No changes to caching infrastructure
- No database migrations required

## Decisions

**1. Use lightweight ChapterSummarySerializer instead of full ChapterSerializer**

```python
class ChapterSummarySerializer(serializers.ModelSerializer):
    """Simplified chapter serializer for list/nested scenarios"""
    class Meta:
        model = Chapter
        fields = ["id", "title", "order"]
```

Alternative considered: Return raw dictionary in `get_next_chapter()` method. This would work but Serializer is more maintainable and consistent with codebase patterns.

**2. Update EnrollmentSerializer to use ChapterSummarySerializer**

Replace `ChapterSerializer(next_chapter).data` with `ChapterSummarySerializer(next_chapter).data` in the `get_next_chapter()` method.

## Risks / Trade-offs

**[Risk]** Test failures if tests assert on full chapter object structure  
→ **Mitigation**: Update test assertions to match simplified structure (only id, title, order fields)

**[Risk]** If frontend code changes to use more next_chapter fields, would need to expand serializer  
→ **Mitigation**: This is unlikely based on current frontend analysis; can expand later if needed

## Migration Plan

1. Add `ChapterSummarySerializer` to `courses/serializers.py`
2. Modify `EnrollmentSerializer.get_next_chapter()` to use the new serializer
3. Update tests in `courses/tests/test_serializers.py` 
4. Deploy and monitor cache latency metrics

Rollback: Revert to `ChapterSerializer` in the get_next_chapter method.