# Proposal: Add Chapter Prerequisites (Unlock Conditions)

## Summary
Add unlock condition functionality to chapters, allowing instructors to specify prerequisite chapters that must be completed before a chapter becomes accessible to students. This enables sequential learning paths and ensures students have mastered foundational content before advancing.

## Problem Statement
Currently, all chapters in a course are accessible to enrolled students from the start. This doesn't support:
1. **Sequential learning paths** where foundational concepts must be mastered before advanced topics
2. **Content gating** for curriculum design flexibility
3. **Progressive disclosure** of course material based on demonstrated completion

The problem unlock system already exists for `Problem` models (`ProblemUnlockCondition`), but chapters lack this capability.

## Proposed Solution
Introduce a `ChapterUnlockCondition` model similar to the existing `ProblemUnlockCondition` pattern, with:
- **Prerequisite chapters**: Multiple chapters that must be completed before unlock
- **Optional unlock date**: Time-based gating
- **Backend enforcement**: API checks unlock status before returning chapter content
- **Frontend indication**: Visual feedback showing locked chapters and prerequisites

## Key Design Decisions

### 1. Model Structure
Mirror the existing `ProblemUnlockCondition` pattern for consistency:
```python
class ChapterUnlockCondition(models.Model):
    chapter = OneToOneField(Chapter)
    prerequisite_chapters = ManyToManyField(Chapter, related_name='dependent_chapters')
    unlock_date = DateTimeField(null=True, blank=True)
    unlock_condition_type = CharField(...)  # for future extensibility
```

### 2. Unlock Logic
A chapter is **unlocked** when:
- No unlock condition exists (default: unlocked), OR
- All prerequisite chapters have `ChapterProgress.completed=True` for the user's enrollment, AND
- Current time is past `unlock_date` (if specified)

### 3. API Impact
- `ChapterViewSet` should filter out locked chapters from list/retrieve for students
- Instructors/admins always see all chapters regardless of lock status
- New action `check_unlock_status` to query lock status without returning content

### 4. Frontend Impact
- Chapter list displays lock icon and prerequisite info for locked chapters
- Locked chapters are not clickable/navigable
- Show progress towards meeting prerequisites (e.g., "2/3 prerequisites completed")

## Affected Components

### Backend
- **Models**: Add `ChapterUnlockCondition` to `courses/models.py`
- **Serializers**: Add `ChapterUnlockConditionSerializer`, update `ChapterSerializer`
- **Views**: Update `ChapterViewSet` with unlock logic filtering
- **Services**: Add `ChapterUnlockService` for unlock status checks
- **Admin**: Add inline admin for `ChapterUnlockCondition`
- **Migrations**: Create migration for new model

### Frontend
- **Types**: Add unlock condition types to TypeScript interfaces
- **Components**: Add locked chapter UI, prerequisite progress indicator
- **Loaders**: Filter locked chapters in course chapter list
- **Admin**: Add unlock condition form in chapter admin UI

## Alternatives Considered

### Alternative 1: Use `order` field only
Use chapter order as implicit prerequisite (must complete chapter N before N+1).
- **Rejected**: Too rigid, doesn't support branching or multiple prerequisites

### Alternative 2: Frontend-only enforcement
Store prerequisites as JSON in chapter content, enforce only in UI.
- **Rejected**: Not secure, students could bypass via API calls

### Alternative 3: Extend Chapter model directly
Add `prerequisite_chapters` field directly to Chapter model.
- **Rejected**: Bloats Chapter model, separate condition model follows existing pattern

## Dependencies
- Existing `ChapterProgress.completed` field (tracks chapter completion)
- Existing `ProblemUnlockCondition` pattern (provides reference implementation)
- Enrollment system (provides user-course context)

## Success Criteria
1. Instructors can set prerequisite chapters via admin interface
2. Students cannot access locked chapter content via API
3. Frontend clearly shows locked chapters and prerequisite status
4. Unlock status updates immediately after completing prerequisites
5. Backwards compatible: existing chapters without conditions remain unlocked

## Related Specs
- [progress-cache](../../../specs/progress-cache/spec.md) - Chapter completion tracking
- [course-import](../../../specs/course-import/spec.md) - May need import/export support
