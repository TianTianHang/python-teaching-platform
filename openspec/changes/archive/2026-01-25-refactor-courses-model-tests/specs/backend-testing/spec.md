# backend-testing Specification Delta: Courses Model Tests

## ADDED Requirements

### Requirement: courses App Models Must Have Comprehensive Test Coverage

The 19 models in the `courses` app MUST have comprehensive test coverage with at least 200 test cases covering all model functionality.

#### Scenario: Core Content Models Coverage

**GIVEN** the courses app with Course, Chapter, and Problem models
**WHEN** model tests are written
**THEN** tests MUST cover:
- **Course**: title validation, description, ordering, instructor relation
- **Chapter**: order uniqueness within course, cascade deletion, content handling
- **Problem**: type validation, difficulty range (1-3), chapter association

#### Scenario: Problem Type Models Coverage

**GIVEN** the courses app with AlgorithmProblem, ChoiceProblem, and FillBlankProblem models
**WHEN** model tests are written
**THEN** tests MUST cover:
- **AlgorithmProblem**: time/memory limits, code templates, solution names, test_cases JSON
- **ChoiceProblem**: option format validation (A,B,C...), answer-option matching, single/multiple choice
- **FillBlankProblem**: blanks JSON format, case sensitivity, answer validation, multiple format support

#### Scenario: Unlock System Coverage

**GIVEN** the ProblemUnlockCondition model
**WHEN** model tests are written
**THEN** tests MUST cover:
- Prerequisite dependencies validation
- Date-based unlocking logic
- Circular dependency detection
- User progress validation
- `is_unlocked()` method business logic

#### Scenario: Execution & Testing Models Coverage

**GIVEN** TestCase, Submission, and CodeDraft models
**WHEN** model tests are written
**THEN** tests MUST cover:
- **TestCase**: sample vs regular case distinction, input/output handling
- **Submission**: all status transitions (pending, judging, accepted, errors), null problem handling, resource limits
- **CodeDraft**: save_type validation, user-problem uniqueness, submission association

#### Scenario: Learning Progress Models Coverage

**GIVEN** Enrollment, ChapterProgress, and ProblemProgress models
**WHEN** model tests are written
**THEN** tests MUST cover:
- **Enrollment**: duplicate prevention, cascade behavior, atomic operations
- **ChapterProgress**: status transitions (not_started → in_progress → completed), timestamp handling
- **ProblemProgress**: attempt counting, best submission logic, solved_at handling, performance metrics

#### Scenario: Discussion System Models Coverage

**GIVEN** DiscussionThread and DiscussionReply models
**WHEN** model tests are written
**THEN** tests MUST cover:
- **DiscussionThread**: pinning, resolution, archiving, activity updates, mention handling
- **DiscussionReply**: mention validation (@username), thread activity updates, author-based permissions

#### Scenario: Exam System Models Coverage

**GIVEN** Exam, ExamProblem, ExamSubmission, and ExamAnswer models
**WHEN** model tests are written
**THEN** tests MUST cover:
- **Exam**: time validation (start_time < end_time), status transitions, passing score, question shuffling
- **ExamProblem**: duplicate prevention, score validation, order validation, problem type validation
- **ExamSubmission**: time limit calculation, status transitions, score calculation, one-submission enforcement
- **ExamAnswer**: answer type validation, scoring calculation (percentage-based), correct answer display logic

#### Scenario: Model Meta Options Testing

**GIVEN** all courses models
**WHEN** model tests are written
**THEN** tests MUST verify:
- `ordering` fields functionality
- `indexes` performance and uniqueness
- `unique_together` constraints
- `verbose_name` and `verbose_name_plural` display

#### Scenario: Model Relationships Testing

**GIVEN** all courses models
**WHEN** model tests are written
**THEN** tests MUST verify:
- Foreign key cascade behavior
- Many-to-many relationships
- Related object access methods
- Reverse lookup functionality
- Polymorphic relationships (Problem subclasses)

#### Scenario: Field Validation Testing

**GIVEN** all courses models
**WHEN** model tests are written
**THEN** tests MUST cover:
- Required field validation
- Field length constraints
- Numeric field ranges (e.g., difficulty 1-3)
- Date field validation
- JSON field format validation
- File field validation
- Choice field validation

#### Scenario: Edge Case Testing

**GIVEN** all courses models
**WHEN** model tests are written
**THEN** tests MUST cover:
- Null value handling
- Empty collections
- Maximum/minimum values
- Invalid input scenarios
- Boundary conditions

## Success Metrics

1. All 19 models have test coverage
2. Total test count ≥ 200
3. All model fields are tested
4. All model methods are tested
5. All relationships are verified
6. All business logic methods are tested
7. All edge cases are covered
8. Run `manage.py test courses.tests.test_models` with no failures

### Requirement: Model Tests Must Use Factory Boy

All model tests MUST use the factory_boy factories defined in the infrastructure proposal.

#### Scenario: Factory Usage in Tests

**GIVEN** the model test suite
**WHEN** running tests
**THEN** all tests MUST use:
- `CourseFactory()` for course creation
- `ChapterFactory(course=CourseFactory())` for related objects
- `ProblemFactory(chapter=ChapterFactory(), algorithm=True)` for typed problems
- `EnrollmentFactory(user=UserFactory(), course=CourseFactory())` for progress
- All factory traits for variations (published, archived, etc.)

#### Scenario: Test Data Isolation

**GIVEN** the model test suite
**WHEN** running multiple tests
**THEN** each test MUST create its own test data
**AND** tests MUST NOT share database state
**AND** `django_get_or_create` MUST be used appropriately for performance