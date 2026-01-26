# Refactor Courses App Test Infrastructure

## Summary

Establish the foundational test infrastructure for the `backend/courses` app by creating a modular test structure using factory_boy. This focuses on migrating existing tests and establishing the pattern for future comprehensive testing.

## Motivation

### Current Problems

1. **Single Large File**: All tests are in `courses/tests.py` (724+ lines), making it difficult to navigate and maintain
2. **Manual Test Data Creation**: Each test class manually creates model instances in `setUp()` methods, resulting in code duplication
3. **No Test Data Isolation**: Tests share similar but duplicated setup code
4. **Scalability Issues**: Adding new tests requires modifying the large monolithic file
5. **Inconsistency**: The `accounts` app already uses a better pattern with factory_boy and modular organization

### Benefits of This Migration

1. **Modularity**: Tests split by functional feature (models, views, progress tracking, import, etc.)
2. **Reusability**: Factory_boy provides reusable test data definitions
3. **Maintainability**: Smaller, focused files are easier to understand and modify
4. **Consistency**: Aligns with the established `accounts` app test pattern
5. **Test Foundation**: Provides infrastructure for future comprehensive testing

## Proposed Changes

### 1. Create Modular Test Structure

Create a `courses/tests/` directory with the following files:

- `conftest.py` - Base test case and utilities
- `factories.py` - Factory Boy definitions for all courses models
- `test_models.py` - Model behavior tests (for migration)
- `test_progress_tracking.py` - Progress tracking feature tests (migrated)
- `test_import.py` - Course import functionality tests (migrated)
- `test_cache.py` - Cache-related tests (existing, moved into new structure)

### 2. Implement Factory Boy for All Models

Create factories for 19 courses models:
- Core: `Course`, `Chapter`, `Problem`
- Problem Types: `AlgorithmProblem`, `ChoiceProblem`, `FillBlankProblem`
- Progress: `Enrollment`, `ChapterProgress`, `ProblemProgress`
- Submissions: `Submission`, `CodeDraft`, `TestCase`
- Discussions: `DiscussionThread`, `DiscussionReply`
- Exams: `Exam`, `ExamProblem`, `ExamSubmission`, `ExamAnswer`
- Other: `ProblemUnlockCondition`

### 3. Create Base Test Case Class

Create `CoursesTestCase` in `conftest.py` with:
- Common client setup
- Helper methods for creating authenticated clients
- Helper methods for creating test course structures
- Integration with `AccountsTestCase` for user-related utilities

### 4. Migrate Existing Tests

Migrate all existing tests from `tests.py` to the new modular structure:
- `ProgressTrackingTestCase` → `test_progress_tracking.py`
- `FillBlankImportTestCase` → `test_import.py`
- `FillBlankImportIntegrationTestCase` → `test_import.py`

## Scope

### In Scope

- Creating `courses/tests/` directory structure
- Creating `factories.py` with factory_boy definitions for all 19 models
- Creating `conftest.py` with base test case and utilities
- Migrating existing tests from `tests.py` to new structure
- Ensuring all existing tests continue to pass

### Out of Scope

- Writing new comprehensive tests (proposals 2-6 will handle this)
- Modifying test logic or behavior
- Changes to production code
- Frontend test changes

## Success Criteria

1. All existing tests pass after migration
2. Tests are organized into separate files by functional feature
3. Factory_boy is used for all test data creation
4. Base test case class provides common utilities
5. Code follows the same pattern as `accounts` app tests
6. Test coverage remains the same as original

## Dependencies

- `factory-boy` package (already installed)
- `faker` package (already installed)

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing tests during migration | Migrate incrementally, run tests after each file migration |
| Missing factory setup for complex models | Use `@staticmethod` or `@classmethod` for custom generation logic |
| Test execution time increase | Use `django_get_or_create` for commonly referenced entities (e.g., Course) |
| Import path updates required | Use relative imports within the tests package |

## Related Specifications

This change establishes the foundation for the following future specifications:
- `add-courses-model-tests` - Comprehensive model testing (200+ tests)
- `add-courses-api-tests` - API endpoint testing (300+ tests)
- `add-courses-service-tests` - Business logic testing (150+ tests)
- `add-courses-admin-tests` - Admin interface testing (80+ tests)
- `add-courses-serializer-tests` - Serializer testing (150+ tests)
