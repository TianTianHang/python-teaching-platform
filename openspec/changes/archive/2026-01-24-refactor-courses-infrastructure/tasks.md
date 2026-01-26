# Tasks: Refactor Courses App Test Infrastructure

This document outlines the step-by-step implementation tasks for establishing the foundational test infrastructure for the `courses` app.

## Phase 1: Directory Structure

### Task 1.1: Create Tests Directory Structure

**Description**: Create the `courses/tests/` directory and initialize as a Python package.

**Steps**:
1. Create directory `backend/courses/tests/`
2. Create `backend/courses/tests/__init__.py` (empty file)
3. Verify the directory structure is correct

**Validation**: `ls -la backend/courses/tests/` shows `__init__.py`

**Estimated Effort**: Small

---

### Task 1.2: Create Factories Module

**Description**: Create `factories.py` with factory_boy definitions for all courses models.

**Steps**:
1. Create `backend/courses/tests/factories.py`
2. Import required modules (factory, Faker, timezone, ContentType)
3. Create factories for each model in dependency order:
   - Core: `CourseFactory`, `ChapterFactory`, `ProblemFactory`
   - Problem Types: `AlgorithmProblemFactory`, `ChoiceProblemFactory`, `FillBlankProblemFactory`
   - Progress: `EnrollmentFactory`, `ChapterProgressFactory`, `ProblemProgressFactory`
   - Submissions: `SubmissionFactory`, `CodeDraftFactory`, `TestCaseFactory`
   - Discussions: `DiscussionThreadFactory`, `DiscussionReplyFactory`
   - Exams: `ExamFactory`, `ExamProblemFactory`, `ExamSubmissionFactory`, `ExamAnswerFactory`
   - Other: `ProblemUnlockConditionFactory`

**Validation**:
- All factories can be imported without errors
- `CourseFactory()` creates a valid Course instance
- `ChapterFactory()` creates a valid Chapter with related Course
- Run `manage.py shell` and test basic factory creation

**Estimated Effort**: Medium

**Dependencies**: Task 1.1

---

### Task 1.3: Create Base Test Case (conftest.py)

**Description**: Create `conftest.py` with `CoursesTestCase` base class and utility methods.

**Steps**:
1. Create `backend/courses/tests/conftest.py`
2. Import `AccountsTestCase` from `accounts.tests.conftest`
3. Create `CoursesTestCase` class inheriting from `TestCase`
4. Implement helper methods:
   - `create_course_structure(chapter_count, problem_count)`
   - `create_enrolled_user(course, user)`
   - `create_discussion_thread(course, author)`
5. Add APIClient setup in `setUp()`

**Validation**:
- `CoursesTestCase` can be imported
- Helper methods work correctly in test context
- Inherits/utilizes accounts test utilities properly

**Estimated Effort**: Medium

**Dependencies**: Task 1.1

---

## Phase 2: Test Migration

### Task 2.1: Migrate Progress Tracking Tests

**Description**: Create `test_progress_tracking.py` and migrate `ProgressTrackingTestCase` tests.

**Steps**:
1. Create `backend/courses/tests/test_progress_tracking.py`
2. Copy `ProgressTrackingTestCase` from existing `tests.py`
3. Update `setUp()` to use factories instead of manual creation
4. Replace direct model instantiation with factories:
   - `User.objects.create_user()` → `UserFactory()`
   - `Course.objects.create()` → `CourseFactory()`
   - `Chapter.objects.create()` → `ChapterFactory()`
   - etc.
5. Update test class to inherit from `CoursesTestCase`
6. Remove redundant setup code

**Validation**:
- Run `manage.py test courses.tests.test_progress_tracking`
- All progress tracking tests pass
- Test coverage matches original

**Estimated Effort**: Large

**Dependencies**: Task 1.2, Task 1.3

---

### Task 2.2: Migrate Import Tests

**Description**: Create `test_import.py` and migrate fill-blank import tests.

**Steps**:
1. Create `backend/courses/tests/test_import.py`
2. Copy `FillBlankImportTestCase` and `FillBlankImportIntegrationTestCase`
3. Update `setUp()` to use factories
4. Update to inherit from `CoursesTestCase`
5. Ensure import logic tests remain unchanged

**Validation**:
- Run `manage.py test courses.tests.test_import`
- All import tests pass
- Import validation still works correctly

**Estimated Effort**: Medium

**Dependencies**: Task 1.2, Task 1.3

---

### Task 2.3: Move Cache Tests

**Description**: Move existing `test_cache.py` into the new tests directory.

**Steps**:
1. Verify `backend/courses/test_cache.py` exists
2. Move file to `backend/courses/tests/test_cache.py`
3. Update if needed to use new base test case
4. Ensure imports are correct

**Validation**:
- Run `manage.py test courses.tests.test_cache`
- All cache tests pass

**Estimated Effort**: Small

**Dependencies**: Task 1.1

---

## Phase 3: Verification and Cleanup

### Task 3.1: Run Full Test Suite

**Description**: Run the complete courses test suite to ensure all tests pass.

**Steps**:
1. Run `manage.py test courses.tests`
2. Verify all tests pass
3. Check for any import errors or missing dependencies
4. Verify test count matches or exceeds original

**Validation**:
- All tests pass
- No errors or warnings
- Test coverage is maintained

**Estimated Effort**: Small

**Dependencies**: Task 2.1, Task 2.2, Task 2.3

---

### Task 3.2: Remove Old Tests File

**Description**: Remove the old `backend/courses/tests.py` file after successful migration.

**Steps**:
1. Verify all tests pass in new structure
2. Backup old `tests.py` (optional)
3. Delete `backend/courses/tests.py`
4. Run test suite again to confirm

**Validation**:
- Old file is removed
- Tests still run from new location
- No import errors

**Estimated Effort**: Small

**Dependencies**: Task 3.1

---

### Task 3.3: Update Documentation

**Description**: Update any project documentation that references the old test structure.

**Steps**:
1. Search for references to `courses/tests.py` in docs
2. Update references to point to new modular structure
3. Update testing guides if they exist

**Validation**:
- Documentation reflects new structure
- No outdated references remain

**Estimated Effort**: Small

**Dependencies**: Task 3.2

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 1.1 | Create tests directory | Small | None |
| 1.2 | Create factories module | Medium | 1.1 |
| 1.3 | Create base test case | Medium | 1.1 |
| 2.1 | Migrate progress tests | Large | 1.2, 1.3 |
| 2.2 | Migrate import tests | Medium | 1.2, 1.3 |
| 2.3 | Move cache tests | Small | 1.1 |
| 3.1 | Run full test suite | Small | 2.1, 2.2, 2.3 |
| 3.2 | Remove old tests file | Small | 3.1 |
| 3.3 | Update documentation | Small | 3.2 |

## Parallelization Opportunities

- **Tasks 1.2 and 1.3** can be developed in parallel after 1.1 is complete
- **Tasks 2.1, 2.2, 2.3** can be worked on in parallel once foundation (1.2, 1.3) is complete

## Rollback Plan

If issues arise during migration:

1. Keep old `tests.py` until all new tests are verified
2. Use git branches for each phase
3. Can revert to previous state at any phase boundary
4. New tests can be run alongside old tests during transition

---

## Completion Status

All tasks have been completed successfully!

| Task | Status | Completed Date |
|------|--------|----------------|
| 1.1 | ✅ Completed | 2026-01-24 |
| 1.2 | ✅ Completed | 2026-01-24 |
| 1.3 | ✅ Completed | 2026-01-24 |
| 2.1 | ✅ Completed | 2026-01-24 |
| 2.2 | ✅ Completed | 2026-01-24 |
| 2.3 | ✅ Completed | 2026-01-24 |
| 3.1 | ✅ Completed | 2026-01-24 |
| 3.2 | ✅ Completed | 2026-01-24 |
| 3.3 | ✅ Completed | 2026-01-24 |

**Summary**:
- ✅ Created `courses/tests/` directory structure with `__init__.py`
- ✅ Created `factories.py` with factory_boy definitions for all 19 models
- ✅ Created `conftest.py` with `CoursesTestCase` base class
- ✅ Migrated `ProgressTrackingTestCase` to `test_progress_tracking.py`
- ✅ Migrated import tests to `test_import.py`
- ✅ Moved `test_cache.py` to `tests/test_cache.py`
- ✅ All 29 tests pass successfully
- ✅ Removed old `tests.py` file
- ✅ Updated documentation references

The test infrastructure refactoring is complete and ready for use!