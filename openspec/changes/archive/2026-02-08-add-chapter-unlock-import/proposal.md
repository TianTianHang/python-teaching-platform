# Proposal: Add Chapter Unlock Condition Import

## Summary
Add support for importing chapter unlock conditions from markdown files with YAML frontmatter. This enables instructors to define prerequisite chapters and time-based unlock conditions in their course repository, which are then automatically imported into the `ChapterUnlockCondition` model.

## Problem Statement
The `ChapterUnlockCondition` model was recently added ([add-chapter-prerequisites](../archive/2026-01-28-add-chapter-prerequisites/proposal.md)), allowing chapters to have unlock conditions. However, the course import service ([course_import_services](../../../backend/courses/course_import_services/)) currently only supports `ProblemUnlockCondition` import, not `ChapterUnlockCondition` import.

Instructors must manually configure chapter unlock conditions in the admin panel after importing courses, which is:
1. **Error-prone**: Manual configuration may not match the intended curriculum structure
2. **Time-consuming**: Each chapter's unlock conditions must be configured separately
3. **Not reproducible**: Re-importing a course doesn't restore unlock conditions

## Proposed Solution
Extend the course import service to support `ChapterUnlockCondition` import from markdown frontmatter, following the same pattern as `ProblemUnlockCondition` import.

### Markdown Frontmatter Design

Chapter files (`chapters/chapter-*.md`) will support an optional `unlock_conditions` field:

```yaml
---
title: Advanced Loops
order: 2
unlock_conditions:
  type: prerequisite  # 'prerequisite' | 'date' | 'all' | 'none'
  prerequisites:     # Optional: list of chapter orders
    - 1              # Chapter 1 must be completed first
  unlock_date:       # Optional: ISO 8601 datetime
    "2025-03-01T00:00:00Z"
---

# Advanced Loops
Chapter content here...
```

### Key Design Decisions

1. **Reference chapters by order**: Prerequisites are specified as chapter order numbers (integers), not titles. This matches the existing `chapter` field in problem frontmatter.

2. **Two-phase import**: Similar to problem unlock conditions, chapter unlock conditions will be imported in a separate phase after all chapters exist, ensuring prerequisite chapters can be found.

3. **Validation before import**: The markdown parser will validate the `unlock_conditions` structure before the importer processes it.

4. **Update mode support**: When `update_mode=True`, existing unlock conditions are updated; when `False`, they're skipped.

## Affected Components

### Backend
- **[markdown_parser.py](../../../backend/courses/course_import_services/markdown_parser.py)**:
  - Add `validate_chapter_unlock_conditions()` method
  - Add `validate_chapter_prerequisites()` helper method

- **[course_importer.py](../../../backend/courses/course_import_services/course_importer.py)**:
  - Modify `_import_chapter()` to handle basic info only (skip unlock_conditions)
  - Add `_import_chapter_unlock_conditions()` method for Phase 2
  - Add `_link_prerequisite_chapters()` helper method
  - Update `_import_course()` to call Phase 2 for chapters

### Course Repository Format
- Chapter markdown files gain optional `unlock_conditions` field

## Alternatives Considered

### Alternative 1: Reference chapters by title
Use chapter titles instead of order numbers in prerequisites.
- **Rejected**: Titles may change or contain special characters; order numbers are more stable and consistent with problem's `chapter` field.

### Alternative 2: Separate unlock condition file
Store unlock conditions in a separate `unlock.yml` file.
- **Rejected**: Keeps related information separate; frontmatter is cleaner and follows existing pattern.

### Alternative 3: Frontend-only import
Handle unlock conditions in frontend after import.
- **Rejected**: Not secure; backend should enforce data integrity.

## Dependencies
- Existing `ChapterUnlockCondition` model (already implemented)
- Existing `MarkdownFrontmatterParser` class (already implemented)
- Existing `CourseImporter` class (to be extended)

## Success Criteria
1. Instructors can specify `unlock_conditions` in chapter markdown files
2. Import service validates unlock conditions before creating database records
3. Prerequisite chapters are correctly linked via `prerequisite_chapters` M2M field
4. Unlock dates are parsed and stored correctly
5. Update mode properly updates existing unlock conditions
6. Invalid prerequisites (non-existent chapters) are logged as warnings, not errors

## Related Specs
- [chapter-prerequisites](../../../specs/chapter-prerequisites/spec.md) - Chapter unlock condition model
- [course-import](../../../specs/course-import/spec.md) - Course import service specification

## Implementation Approach
Per user requirement, implementation will follow this order:
1. **Design markdown field specification** - Define the YAML structure and validation rules
2. **Implement markdown parser** - Add validation methods to `MarkdownFrontmatterParser`
3. **Modify import script** - Extend `CourseImporter` with unlock condition import logic
