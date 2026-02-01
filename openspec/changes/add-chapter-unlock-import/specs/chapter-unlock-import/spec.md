# Chapter Unlock Import Specification

## Purpose
Extends the course-import capability to support importing chapter unlock conditions from markdown files with YAML frontmatter.

## ADDED Requirements

### Requirement: Chapter Unlock Condition Markdown Format
Chapter markdown files SHALL support an optional `unlock_conditions` field in YAML frontmatter to define unlock conditions.

#### Scenario: Chapter with prerequisite unlock condition
- **GIVEN** a chapter file `chapters/chapter-2.md` contains valid frontmatter
- **AND** the frontmatter specifies `unlock_conditions.type: 'prerequisite'`
- **AND** `unlock_conditions.prerequisites: [1]`
- **WHEN** the markdown parser reads the file
- **THEN** the unlock conditions are parsed into a dictionary
- **AND** `type` is `'prerequisite'`
- **AND** `prerequisites` is `[1]`

#### Scenario: Chapter with date-based unlock condition
- **GIVEN** a chapter file contains `unlock_conditions.type: 'date'`
- **AND** `unlock_conditions.unlock_date: '2025-03-01T00:00:00Z'`
- **WHEN** the markdown parser reads the file
- **THEN** the unlock conditions are parsed correctly
- **AND** `unlock_date` is parseable as a valid datetime

#### Scenario: Chapter with combined unlock conditions
- **GIVEN** a chapter file contains `unlock_conditions.type: 'all'`
- **AND** specifies both `prerequisites: [1, 2]` and `unlock_date`
- **WHEN** the markdown parser reads the file
- **THEN** all unlock condition fields are parsed
- **AND** the structure is valid for import

#### Scenario: Chapter without unlock conditions
- **GIVEN** a chapter file contains only `title` and `order` fields
- **WHEN** the markdown parser reads the file
- **THEN** the chapter is parsed normally
- **AND** no unlock conditions are present
- **AND** the chapter will be imported as unlocked (default)

---

### Requirement: Chapter Unlock Condition Validation
The markdown parser SHALL validate chapter unlock conditions before the importer processes them.

#### Scenario: Validate valid prerequisite unlock condition
- **GIVEN** a chapter frontmatter has `unlock_conditions.type: 'prerequisite'`
- **AND** `unlock_conditions.prerequisites: [1, 2]`
- **WHEN** `MarkdownFrontmatterParser.validate_chapter_unlock_conditions()` is called
- **THEN** validation passes
- **AND** no `ValueError` is raised

#### Scenario: Reject invalid unlock condition type
- **GIVEN** a chapter frontmatter has `unlock_conditions.type: 'invalid_type'`
- **WHEN** validation runs
- **THEN** a `ValueError` is raised
- **AND** the error message indicates the invalid type
- **AND** valid types are listed in the error

#### Scenario: Require prerequisites field for prerequisite type
- **GIVEN** a chapter frontmatter has `unlock_conditions.type: 'prerequisite'`
- **AND** the `prerequisites` field is missing
- **WHEN** validation runs
- **THEN** a `ValueError` is raised
- **AND** the error message indicates `prerequisites` is required for this type

#### Scenario: Require unlock_date field for date type
- **GIVEN** a chapter frontmatter has `unlock_conditions.type: 'date'`
- **AND** the `unlock_date` field is missing
- **WHEN** validation runs
- **THEN** a `ValueError` is raised
- **AND** the error message indicates `unlock_date` is required for this type

#### Scenario: Validate prerequisites is a list of integers
- **GIVEN** a chapter frontmatter has `unlock_conditions.prerequisites: ['invalid']`
- **WHEN** validation runs
- **THEN** a `ValueError` is raised
- **AND** the error message indicates prerequisites must be a list of integers

#### Scenario: Validate unlock_date is a valid ISO 8601 datetime
- **GIVEN** a chapter frontmatter has `unlock_conditions.unlock_date: 'not-a-date'`
- **WHEN** validation runs
- **THEN** a `ValueError` is raised
- **AND** the error message indicates the datetime format is invalid

#### Scenario: Validate all type requires both fields
- **GIVEN** a chapter frontmatter has `unlock_conditions.type: 'all'`
- **AND** only `prerequisites` is provided (missing `unlock_date`)
- **WHEN** validation runs
- **THEN** a `ValueError` is raised
- **AND** the error message indicates both fields are required for type 'all'

---

### Requirement: Chapter Unlock Condition Import
The course importer SHALL support importing chapter unlock conditions from validated frontmatter.

#### Scenario: Import chapter with single prerequisite
- **GIVEN** a chapter file specifies `unlock_conditions.type: 'prerequisite'`
- **AND** `unlock_conditions.prerequisites: [1]`
- **AND** a chapter with `order=1` exists in the course
- **WHEN** the importer processes the chapter (Phase 2)
- **THEN** a `ChapterUnlockCondition` record is created
- **AND** `unlock_condition_type` is `'prerequisite'`
- **AND** the chapter with `order=1` is linked via `prerequisite_chapters`

#### Scenario: Import chapter with multiple prerequisites
- **GIVEN** a chapter file specifies `prerequisites: [1, 2, 3]`
- **AND** all three chapters exist in the course
- **WHEN** the importer processes the chapter
- **THEN** all three chapters are linked via `prerequisite_chapters`
- **AND** the chapter unlocks only after ALL three are completed

#### Scenario: Import chapter with date-based unlock
- **GIVEN** a chapter file specifies `unlock_conditions.type: 'date'`
- **AND** `unlock_date: '2025-03-01T00:00:00Z'`
- **WHEN** the importer processes the chapter
- **THEN** a `ChapterUnlockCondition` record is created
- **AND** `unlock_date` is set to the parsed datetime value
- **AND** `prerequisite_chapters` is empty

#### Scenario: Import chapter with combined conditions
- **GIVEN** a chapter file specifies `unlock_conditions.type: 'all'`
- **AND** includes both `prerequisites` and `unlock_date`
- **WHEN** the importer processes the chapter
- **THEN** a `ChapterUnlockCondition` record is created
- **AND** both `prerequisite_chapters` and `unlock_date` are populated
- **AND** `unlock_condition_type` is `'all'`

#### Scenario: Skip unlock condition import when type is 'none'
- **GIVEN** a chapter file specifies `unlock_conditions.type: 'none'`
- **WHEN** the importer processes the chapter
- **THEN** no `ChapterUnlockCondition` record is created
- **AND** the chapter remains unlocked

#### Scenario: Skip unlock condition import when field is absent
- **GIVEN** a chapter file does not have an `unlock_conditions` field
- **WHEN** the importer processes the chapter
- **THEN** no `ChapterUnlockCondition` record is created
- **AND** the chapter remains unlocked

---

### Requirement: Two-Phase Chapter Import
The importer SHALL use a two-phase approach for chapter import to ensure prerequisite chapters can be found.

#### Scenario: Phase 1 imports basic chapter info
- **GIVEN** the importer is processing chapters
- **WHEN** Phase 1 runs
- **THEN** all chapter basic info is imported (title, order, content)
- **AND** unlock conditions are skipped in Phase 1
- **AND** all chapters exist in the database before Phase 2

#### Scenario: Phase 2 imports unlock conditions
- **GIVEN** Phase 1 has completed and all chapters exist
- **WHEN** Phase 2 runs
- **THEN** each chapter's unlock conditions are processed
- **AND** prerequisite chapters can be found by order number
- **AND** `ChapterUnlockCondition` records are created

#### Scenario: Prerequisite chapter found during Phase 2
- **GIVEN** Chapter A (order=2) has `prerequisites: [1]`
- **AND** Chapter B (order=1) was created in Phase 1
- **WHEN** Phase 2 processes Chapter A's unlock conditions
- **THEN** Chapter B is found by `order=1`
- **AND** Chapter B is linked to Chapter A's unlock condition

---

### Requirement: Prerequisite Chapter Resolution
The importer SHALL resolve prerequisite chapters by order number and handle missing references gracefully.

#### Scenario: Resolve existing prerequisite chapter
- **GIVEN** a chapter specifies `prerequisites: [1]`
- **AND** a chapter with `order=1` exists in the same course
- **WHEN** the importer resolves the prerequisite
- **THEN** the chapter is found by `course` and `order`
- **AND** it is added to `prerequisite_chapters`

#### Scenario: Log warning for non-existent prerequisite
- **GIVEN** a chapter specifies `prerequisites: [99]`
- **AND** no chapter with `order=99` exists in the course
- **WHEN** the importer attempts to resolve the prerequisite
- **THEN** a warning is logged indicating chapter order 99 was not found
- **AND** that prerequisite is skipped
- **AND** the unlock condition is still created with other valid prerequisites

#### Scenario: Prevent self-reference
- **GIVEN** a chapter with `order=2` specifies `prerequisites: [2]`
- **WHEN** the importer attempts to resolve the prerequisite
- **THEN** the self-reference is detected
- **AND** a warning is logged
- **AND** the self-reference is skipped
- **AND** the unlock condition is created without the self-reference

#### Scenario: Handle multiple prerequisites with some invalid
- **GIVEN** a chapter specifies `prerequisites: [1, 99, 2]`
- **AND** only chapters 1 and 2 exist
- **WHEN** the importer resolves the prerequisites
- **THEN** chapters 1 and 2 are linked
- **AND** a warning is logged for chapter 99
- **AND** the unlock condition is created with the valid prerequisites

---

### Requirement: Chapter Unlock Condition Update
The importer SHALL support updating existing chapter unlock conditions when `update_mode=True`.

#### Scenario: Update existing unlock condition
- **GIVEN** a chapter already has a `ChapterUnlockCondition`
- **AND** the markdown file has modified `prerequisites` or `unlock_date`
- **WHEN** the importer runs with `update_mode=True`
- **THEN** the existing `ChapterUnlockCondition` is updated
- **AND** `prerequisite_chapters` are replaced with the new list
- **AND** `unlock_date` is updated to the new value
- **AND** `unlock_condition_type` is updated

#### Scenario: Add unlock condition to existing chapter
- **GIVEN** a chapter exists without unlock conditions
- **AND** the markdown file is updated to include `unlock_conditions`
- **WHEN** the importer runs with `update_mode=True`
- **THEN** a new `ChapterUnlockCondition` is created for the chapter

#### Scenario: Remove unlock condition when field is removed
- **GIVEN** a chapter has a `ChapterUnlockCondition`
- **AND** the markdown file is updated to remove the `unlock_conditions` field
- **WHEN** the importer runs with `update_mode=True`
- **THEN** the existing `ChapterUnlockCondition` is deleted
- **AND** the chapter becomes unlocked

#### Scenario: Skip update when update_mode=False
- **GIVEN** a chapter has existing unlock conditions
- **AND** the markdown file has different unlock conditions
- **WHEN** the importer runs with `update_mode=False`
- **THEN** the existing unlock conditions are not modified
- **AND** the import statistics show the chapter as skipped

---

### Requirement: Import Statistics and Error Reporting
The importer SHALL track unlock condition imports and report errors appropriately.

#### Scenario: Track chapter unlock conditions created
- **GIVEN** the importer creates 5 chapter unlock conditions
- **WHEN** the import completes
- **THEN** the stats dictionary includes `chapter_unlock_conditions_created: 5`

#### Scenario: Track chapter unlock conditions updated
- **GIVEN** the importer updates 3 existing chapter unlock conditions
- **WHEN** the import completes
- **THEN** the stats dictionary includes `chapter_unlock_conditions_updated: 3`

#### Scenario: Log non-critical warnings for missing prerequisites
- **GIVEN** a chapter specifies a non-existent prerequisite
- **WHEN** the importer processes that chapter
- **THEN** a warning is logged
- **AND** the import continues
- **AND** the error is NOT added to the errors list (non-critical)

#### Scenario: Log error for invalid unlock conditions
- **GIVEN** a chapter has invalid `unlock_conditions` (validation fails)
- **WHEN** the importer processes that chapter
- **THEN** an error is logged
- **AND** the error is added to the errors list
- **AND** the unlock condition is not created
