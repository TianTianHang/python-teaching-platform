# Change: Fix Chapter Progress Cache Invalidation

## Why

When users call the `mark_as_completed` API to mark a chapter as completed, the cache is not being invalidated. This causes the chapter status to still show as "not completed" when retrieved, even though the database has been updated. The root cause is that `ChapterProgress` model lacks Django signal handlers for automatic cache invalidation, unlike `ProblemProgress` which has proper signal handlers.

## What Changes

- Add Django signal handlers (`post_save`, `post_delete`) for `ChapterProgress` model in `backend/courses/signals.py`
- Invalidate related caches when `ChapterProgress` is created, updated, or deleted:
  - Chapter list/detail caches (via `ChapterViewSet`)
  - ChapterProgress list/detail caches (via `ChapterProgressViewSet`)
  - Enrollment detail caches (via `EnrollmentViewSet`) - since `get_progress_percentage()` and `get_next_chapter()` depend on ChapterProgress data
- Follow the existing pattern used by `ProblemProgress` signal handler for consistency

## Impact

- Affected specs: New capability for progress cache management
- Affected code:
  - `backend/courses/signals.py` - Add new signal handler
  - Related tests may need updating to verify cache invalidation behavior
