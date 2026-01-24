# backend-testing Specification Delta: Courses Infrastructure

## ADDED Requirements

### Requirement: courses App Test Infrastructure Must Be Refactored

The `courses` app test infrastructure MUST be refactored to follow the same modular, factory_boy-based pattern established in the `accounts` app.

#### Scenario: Modular Test Structure

**GIVEN** the courses app test directory
**WHEN** browsing test files
**THEN** the following files MUST exist:
- `conftest.py` - Base test case and utilities
- `factories.py` - Factory Boy definitions for all courses models
- `test_models.py` - Model behavior tests (for migration)
- `test_progress_tracking.py` - Progress tracking feature tests (migrated)
- `test_import.py` - Course import functionality tests (migrated)
- `test_cache.py` - Cache-related tests (existing, moved)

#### Scenario: Factory Boy Setup for All 19 Models

**GIVEN** the project has factory-boy installed
**WHEN** a developer writes tests for the courses app
**THEN** factories MUST exist for all courses models:
- Core: `Course`, `Chapter`, `Problem`
- Problem Types: `AlgorithmProblem`, `ChoiceProblem`, `FillBlankProblem`
- Progress: `Enrollment`, `ChapterProgress`, `ProblemProgress`
- Submissions: `Submission`, `CodeDraft`, `TestCase`
- Discussions: `DiscussionThread`, `DiscussionReply`
- Exams: `Exam`, `ExamProblem`, `ExamSubmission`, `ExamAnswer`
- Other: `ProblemUnlockCondition`

#### Scenario: CoursesTestCase Base Class

**GIVEN** the courses/tests/conftest.py module
**WHEN** a test class inherits from CoursesTestCase
**THEN** the following helper methods MUST be available:
- `create_course_structure(chapter_count, problem_count)` - creates a complete course with chapters and problems
- `create_enrolled_user(course, user)` - creates a user enrolled in a course
- `create_discussion_thread(course, author)` - creates a discussion thread
**AND** an APIClient instance MUST be available as `self.client`

#### Scenario: Existing Test Migration

**GIVEN** the original courses/tests.py with 724+ lines
**WHEN** tests are migrated to the new structure
**THEN** the following test classes MUST be migrated:
- `ProgressTrackingTestCase` → `test_progress_tracking.py`
- `FillBlankImportTestCase` → `test_import.py`
- `FillBlankImportIntegrationTestCase` → `test_import.py`

#### Scenario: No Regression in Test Suite

**GIVEN** the completed test infrastructure refactoring
**WHEN** the full test suite is run
**THEN** all tests MUST pass
**AND** the number of passing tests MUST be equal to the original count
**AND** all original test scenarios MUST be preserved

### Requirement: courses Test Infrastructure Must Enable Future Testing

The refactored test infrastructure MUST provide a solid foundation for comprehensive testing in the following areas:

#### Scenario: Factory Reusability

**GIVEN** the factory definitions in courses/tests/factories.py
**WHEN** developers write new tests
**THEN** all factories MUST be easily reusable with:
- Simple instantiation: `CourseFactory()`
- Optional traits: `CourseFactory(published=True)`
- Related objects: `ChapterFactory(course=CourseFactory())`
- Custom generation: `ProblemFactory(algorithm=True)`

#### Scenario: Base Test Case Utilities

**GIVEN** the CoursesTestCase base class
**WHEN** developers write new tests
**THEN** the following utilities MUST be available:
- Authenticated client creation
- Test course structure creation
- Common test data setup
- Integration with accounts test utilities

#### Scenario: Scalable Test Organization

**GIVEN** the courses/tests/ directory structure
**WHEN** adding new test files
**THEN** the following naming convention MUST be followed:
- `test_models.py` - Model tests (can be expanded)
- `test_services.py` - Service tests (future)
- `test_views.py` - View tests (future)
- `test_serializers.py` - Serializer tests (future)
- `test_admin.py` - Admin tests (future)
**AND** each file MUST be importable and runnable independently

## Success Metrics

1. All existing tests pass in new structure
2. Factory definitions work for all 19 models
3. Base test case provides comprehensive utilities
4. Test organization follows modular pattern
5. No import errors or broken dependencies
6. Ready for future comprehensive testing (model, API, service, admin, serializer tests)