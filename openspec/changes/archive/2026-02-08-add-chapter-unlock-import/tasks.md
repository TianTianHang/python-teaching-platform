# Tasks: Chapter Unlock Condition Import

## Implementation Order
Per user requirement, tasks are ordered as:
1. Design markdown field specification (completed in design.md)
2. Implement markdown parser
3. Modify import script

## Tasks

### 1. Add Chapter Unlock Condition Validation to Markdown Parser
**File**: `backend/courses/course_import_services/markdown_parser.py`

- [x] Add `validate_chapter_unlock_conditions()` class method to `MarkdownFrontmatterParser`
  - Validate `unlock_conditions` is a dictionary if present
  - Validate `type` is one of: 'prerequisite', 'date', 'all', 'none'
  - Validate required fields based on `type`:
    - 'prerequisite' requires `prerequisites`
    - 'date' requires `unlock_date`
    - 'all' requires both `prerequisites` and `unlock_date`
    - 'none' requires no additional fields
  - Raise `ValueError` with descriptive message if validation fails

- [x] Add `validate_chapter_prerequisites()` helper method
  - Validate `prerequisites` is a list
  - Validate each item is an integer
  - Validate each integer is non-negative
  - Raise `ValueError` if validation fails

- [x] Add `validate_chapter_unlock_date()` helper method
  - Validate input is a string
  - Validate string is parseable as ISO 8601 datetime using `dateutil.parser.isoparse()`
  - Raise `ValueError` if validation fails

**Validation**: Write unit tests in `backend/courses/tests/test_markdown_parser.py` for each validation scenario ✅

---

### 2. Add Chapter Unlock Condition Import to Course Importer
**File**: `backend/courses/course_import_services/course_importer.py`

- [x] Update `stats` dictionary initialization to include:
  - `chapter_unlock_conditions_created: 0`
  - `chapter_unlock_conditions_updated: 0`

- [x] Modify `_import_chapter()` method to skip unlock_conditions in Phase 1
  - Read frontmatter but ignore `unlock_conditions` field
  - Only import basic chapter info (title, order, content)
  - Add comment indicating Phase 1 behavior

- [x] Add `_import_chapter_unlock_conditions()` method
  - Accept `course: Course` and `chapter_file: Path` parameters
  - Parse frontmatter from chapter file
  - Skip if no `unlock_conditions` field
  - Validate unlock conditions using `MarkdownFrontmatterParser.validate_chapter_unlock_conditions()`
  - Find chapter by title (match within course)
  - Call helper to create/update unlock condition

- [x] Add `_link_prerequisite_chapters()` helper method
  - Accept `unlock_cond: ChapterUnlockCondition`, `prerequisite_orders: List[int]`, `course: Course`, `current_chapter: Chapter` parameters
  - Clear existing `prerequisite_chapters` relationships
  - For each order in `prerequisite_orders`:
    - Skip if order matches `current_chapter.order` (self-reference)
    - Try to find chapter by `course` and `order`
    - Log warning if chapter not found, continue with next
    - Add found chapter to `prerequisite_chapters` if valid
  - Log total prerequisites linked

- [x] Add internal helper `_create_or_update_chapter_unlock_condition()`
  - Accept `chapter: Chapter`, `unlock_conditions: Dict`, `course: Course` parameters
  - Extract `type` and `unlock_date` from frontmatter
  - Parse `unlock_date` using `dateutil.parser.parse()` if present
  - Use `ChapterUnlockCondition.objects.get_or_create()` with `chapter` key
  - Update fields if `update_mode=True` and record exists
  - Increment appropriate stats counter
  - Log creation/update

- [x] Modify `_import_course()` to add Phase 2 for chapters
  - After `_import_chapters()` completes
  - Iterate through chapter files again
  - Call `_import_chapter_unlock_conditions()` for each
  - Handle exceptions with try/except, log errors

**Validation**: Write integration tests in `backend/courses/tests/test_course_importer.py`:
- Test importing chapter with single prerequisite ✅
- Test importing chapter with multiple prerequisites ✅
- Test importing chapter with date-based unlock ✅
- Test importing chapter with combined conditions ✅
- Test missing prerequisite chapter handling ✅
- Test self-reference prevention ✅
- Test update mode behavior ✅

---

### 3. Update Imports
**File**: `backend/courses/course_import_services/course_importer.py`

- [x] Add `ChapterUnlockCondition` to imports from `courses.models`

---

### 4. Documentation
- [ ] Add example chapter markdown file with unlock conditions to course repository template
- [ ] Update course import documentation if it exists (Documentation task - can be completed separately)

## Dependencies
- Task 1 must complete before Task 2 (parser validation needed for importer)
- Task 2 and Task 3 can be done together
- Task 4 (documentation) can be done in parallel with implementation

## Validation Checklist
- [x] All validation scenarios from spec.md are covered by parser
- [x] All import scenarios from spec.md are covered by importer
- [x] Unit tests pass for parser validation (30/30 tests passed)
- [x] Integration tests pass for importer (26/26 tests passed)
- [x] Existing tests still pass (no regressions)
- [ ] Manual import test with sample course repository succeeds
