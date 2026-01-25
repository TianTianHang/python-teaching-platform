# backend-testing Specification

## Purpose
TBD - created by archiving change add-accounts-tests. Update Purpose after archive.
## Requirements
### Requirement: accounts App Must Have Comprehensive Test Coverage

The `accounts` app MUST have comprehensive test coverage for all models, serializers, permissions, and views. Tests MUST use factory_boy for test data management and MUST be organized by functional feature.

#### Scenario: Factory Boy Setup

**GIVEN** the project has factory-boy installed
**WHEN** a developer writes tests for the accounts app
**THEN** factories MUST exist for:
- `UserFactory` - creates test User instances with optional admin/st_number/avatar traits
- `MembershipTypeFactory` - creates test MembershipType instances
- `SubscriptionFactory` - creates test Subscription instances with auto-calculated end_date

#### Scenario: User Model Tests

**GIVEN** a User instance created via UserFactory
**WHEN** accessing the user's string representation
**THEN** it MUST return the format `{st_number}-{username}`
**AND** st_number MUST be unique across users
**AND** avatar field MUST accept text data (base64 or URL)

#### Scenario: MembershipType Model Tests

**GIVEN** a MembershipType instance
**WHEN** accessing string representation
**THEN** it MUST return the membership name
**AND** is_active MUST default to True

#### Scenario: Subscription Model Tests

**GIVEN** a Subscription instance
**WHEN** created without an end_date
**THEN** end_date MUST be auto-calculated as start_date + membership_type.duration_days
**AND** string representation MUST return `{user.username} - {membership_type.name}`

#### Scenario: RegisterUserSerializer Validation

**GIVEN** a registration request with valid data
**WHEN** the serializer is validated and saved
**THEN** a User MUST be created with a hashed password
**AND** duplicate st_number MUST raise a ValidationError with message "该学号已被注册"
**AND** password validation MUST be enforced via Django's password validators

#### Scenario: Login Serializer Accepts Username or Student Number

**GIVEN** a user with username "testuser" and st_number "2024000001"
**WHEN** logging in with username="testuser" or username="2024000001"
**THEN** both attempts MUST succeed with correct password
**AND** the response token MUST contain custom claims for username and st_number
**AND** an inactive user MUST NOT be able to login

#### Scenario: Logout Serializer Validation

**GIVEN** a valid refresh token
**WHEN** the logout serializer is validated
**THEN** the refresh token MUST be accepted
**AND** a missing refresh token MUST be rejected

#### Scenario: UserSerializer Subscription Fields

**GIVEN** a user with an active subscription
**WHEN** the user is serialized
**THEN** has_active_subscription MUST return True
**AND** current_subscription MUST contain the subscription details
**AND** id and st_number MUST be read-only fields

#### Scenario: Change Password Serializer

**GIVEN** an authenticated user
**WHEN** changing password with correct old_password
**THEN** the new password MUST be hashed and saved
**AND** the old password MUST no longer work for authentication
**AND** incorrect old_password MUST raise ValidationError

#### Scenario: IsSubscriptionActive Permission

**GIVEN** a permission check for IsSubscriptionActive
**WHEN** the user is unauthenticated
**THEN** permission MUST be denied
**WHEN** the user has no subscription
**THEN** permission MUST be denied
**WHEN** the user has an expired subscription
**THEN** permission MUST be denied
**WHEN** the user has an active subscription (end_date > now)
**THEN** permission MUST be granted

#### Scenario: Login View Success and Failure

**GIVEN** a registered user
**WHEN** posting to /auth/auth/login with correct credentials
**THEN** response status MUST be 200
**AND** response MUST contain access and refresh tokens
**AND** response MUST contain user_id, username, st_number
**WHEN** posting with incorrect credentials
**THEN** response status MUST be 401
**AND** IP address MUST be logged

#### Scenario: Register View Success and Validation

**GIVEN** a registration request with unique username and st_number
**WHEN** posting to /auth/auth/register
**THEN** a new user MUST be created
**AND** response status MUST be 201
**AND** response MUST contain access and refresh tokens
**AND** transaction MUST be rolled back on validation error
**WHEN** st_number already exists
**THEN** response status MUST be 400
**AND** error message MUST indicate duplicate st_number

#### Scenario: Logout View Token Blacklisting

**GIVEN** an authenticated user with a valid refresh token
**WHEN** posting to /auth/auth/logout with the refresh token
**THEN** the refresh token MUST be blacklisted
**AND** response status MUST be 200
**AND** invalid/expired tokens MUST return 400

#### Scenario: Me View Authentication Required

**GIVEN** an authenticated user
**WHEN** getting /auth/auth/me
**THEN** response status MUST be 200
**AND** response MUST contain user profile data
**AND** response MUST include active subscription info if present
**WHEN** unauthenticated
**THEN** response status MUST be 401

#### Scenario: User Update View

**GIVEN** an authenticated user
**WHEN** patching /auth/users/me/update/ with valid data
**THEN** email, username, and avatar MAY be updated
**AND** st_number MUST NOT be updatable (read-only)
**AND** user MAY NOT update other users' profiles
**AND** unauthenticated requests MUST return 401

#### Scenario: User List View Admin Only

**GIVEN** an admin user
**WHEN** getting /auth/users
**THEN** response status MUST be 200
**AND** response MUST contain list of all users
**WHEN** requested by non-admin user
**THEN** response status MUST be 403

#### Scenario: User Delete View Admin Only

**GIVEN** an admin user
**WHEN** deleting /auth/users/{id}/delete/
**THEN** the user MUST be deleted
**AND** response status MUST be 204
**WHEN** requested by non-admin user
**THEN** response status MUST be 403

#### Scenario: Membership Type List View

**GIVEN** multiple membership types (active and inactive)
**WHEN** getting /auth/membership-types/
**THEN** response status MUST be 200
**AND** only active membership types (is_active=True) MUST be returned
**AND** results MUST be ordered by duration_days
**AND** no authentication MUST be required

#### Scenario: Change Password View

**GIVEN** an authenticated user
**WHEN** posting to /auth/users/me/change-password/ with correct old_password
**THEN** password MUST be updated
**AND** response status MUST be 200
**AND** user MUST be able to login with new password
**AND** user MUST NOT be able to login with old password
**WHEN** old_password is incorrect
**THEN** response status MUST be 400
**AND** error MUST indicate "旧密码错误"

### Requirement: Tests Must Be Organized by Functional Feature

Tests for the accounts app MUST be organized into separate files by functional area:

#### Scenario: Test File Organization

**GIVEN** the accounts/tests directory
**WHEN** browsing test files
**THEN** the following files MUST exist:
- `test_models.py` - Model behavior tests
- `test_serializers.py` - Serializer validation tests
- `test_permissions.py` - Permission class tests
- `test_auth_views.py` - Login, Register, Logout, Token endpoints
- `test_user_views.py` - Me, Update, List, Delete endpoints
- `test_membership_views.py` - Membership type endpoints
- `test_password_views.py` - Password change endpoint
**AND** `factories.py` MUST contain all factory definitions

### Requirement: Test Data Must Be Isolated

Each test MUST create its own test data and MUST NOT depend on data from other tests.

#### Scenario: Test Isolation

**GIVEN** multiple tests in the same test class
**WHEN** tests run in any order
**THEN** each test MUST use factory-created data
**AND** tests MUST NOT share database state
**AND** tests MUST pass when run individually or as a suite

### Requirement: Factory Boy Must Be Used for Test Data

All test data creation MUST use factory_boy factories instead of direct model instantiation or manual data creation.

#### Scenario: Factory Usage Pattern

**GIVEN** a test that requires a user
**WHEN** creating test data
**THEN** UserFactory() MUST be used instead of User.objects.create()
**AND** factory traits MAY be used for specific user types (admin, with_st_number, etc.)

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

### Requirement: courses App API Endpoints Must Have Comprehensive Test Coverage

All 12 ViewSets and API endpoints in the `courses` app MUST have comprehensive test coverage with at least 300 test cases covering all API functionality.

#### Scenario: Core ViewSets Coverage

**GIVEN** the CourseViewSet, ChapterViewSet, and ProblemViewSet
**WHEN** API tests are written
**THEN** tests MUST cover:
- **CourseViewSet**: list/search/create, enroll action (atomic transaction), staff-only creation, filtering
- **ChapterViewSet**: list by course, mark_completed action (atomic), missing course handling, progress tracking
- **ProblemViewSet**: list by chapter/type, get_next_problem, mark_solved, check_fillblank_answer, unlock logic

#### Scenario: Execution ViewSets Coverage

**GIVEN** SubmissionViewSet and CodeDraftViewSet
**WHEN** API tests are written
**THEN** tests MUST cover:
- **SubmissionViewSet**: create submission (algorithm execution), get results, free code vs problem submission, status handling
- **CodeDraftViewSet**: latest draft retrieval, save with submission association, draft type validation

#### Scenario: Progress ViewSets Coverage

**GIVEN** EnrollmentViewSet, ChapterProgressViewSet, and ProblemProgressViewSet
**WHEN** API tests are written
**THEN** tests MUST cover:
- **EnrollmentViewSet**: CRUD operations, duplicate prevention, enrollment status
- **ChapterProgressViewSet**: read-only access, user filtering, status filtering
- **ProblemProgressViewSet**: status filtering (not_started/in_progress/completed), own progress only, attempt counting

#### Scenario: Discussion ViewSets Coverage

**GIVEN** DiscussionThreadViewSet and DiscussionReplyViewSet
**WHEN** API tests are written
**THEN** tests MUST cover:
- **DiscussionThreadViewSet**: nested routing (/courses/{id}/threads/, /chapters/{id}/threads/, /problems/{id}/threads/), creation, listing, updating, deleting
- **DiscussionReplyViewSet**: nested routing (/threads/{id}/replies/), mention handling, thread activity updates, author-only modifications

#### Scenario: Exam ViewSets Coverage

**GIVEN** ExamViewSet and ExamSubmissionViewSet
**WHEN** API tests are written
**THEN** tests MUST cover:
- **ExamViewSet**: start exam (create submission), submit answers, get results, time limit calculation, status handling
- **ExamSubmissionViewSet**: read-only access, own submissions only, score retrieval, status filtering

#### Scenario: Authentication & Authorization Coverage

**GIVEN** all courses API endpoints
**WHEN** API tests are written
**THEN** tests MUST cover:
- Unauthenticated access returns 401
- Unauthorized access returns 403
- Staff-only endpoints enforcement (e.g., course creation)
- Author-only modifications (e.g., discussion replies)
- JWT token validation
- Session authentication

#### Scenario: HTTP Method Testing

**GIVEN** all courses API endpoints
**WHEN** API tests are written
**THEN** tests MUST cover all HTTP methods:
- **GET**: List views with filtering, search, pagination; Retrieve views with permissions
- **POST**: Create operations with validation, permission checks, data transformation
- **PATCH**: Update operations with partial data, field validation, permission checks
- **DELETE**: Delete operations with cascade behavior, permission checks

#### Scenario: Custom Action Testing

**GIVEN** all custom actions in courses ViewSets
**WHEN** API tests are written
**THEN** tests MUST cover:
- **enroll**: Atomic enrollment creation, duplicate prevention
- **mark_completed**: Chapter completion tracking, progress updates
- **mark_solved**: Problem solving status, best submission tracking
- **get_next_problem**: Unlock logic progression, difficulty consideration
- **check_fillblank_answer**: Answer validation scoring
- **start_exam**: Exam initiation, time tracking
- **submit_exam**: Answer submission, validation
- **get_results**: Score calculation, passing determination

#### Scenario: Nested Routing Testing

**GIVEN** the complex nested URL structure
**WHEN** API tests are written
**THEN** tests MUST cover:
- URL parameter validation (numeric, UUID)
- Parent resource existence checks
- Nested relationship access (course → chapter → problem)
- Hierarchical permission enforcement
- Cross-level data access (exam → course → user)
- Error handling for invalid nested paths

#### Scenario: Filtering, Searching, and Ordering

**GIVEN** all list view endpoints
**WHEN** API tests are written
**THEN** tests MUST cover:
- **Filtering**: by status, type, date ranges, completion status
- **Searching**: by title, description, content
- **Ordering**: by creation date, update date, custom fields (order, difficulty)
- **Pagination**: page size, page number, count parameter
- **Field selection**: sparse fieldsets, include/exclude

#### Scenario: Error Response Testing

**GIVEN** all API endpoints
**WHEN** API tests are written
**THEN** tests MUST cover all error scenarios:
- **400 Bad Request**: Validation errors, invalid data format
- **401 Unauthorized**: Missing authentication token
- **403 Forbidden**: Permission denied, resource ownership
- **404 Not Found**: Missing resource, invalid ID
- **405 Method Not Allowed**: Incorrect HTTP method
- **422 Unprocessable Entity**: Semantic validation errors

#### Scenario: Success Response Testing

**GIVEN** all API endpoints
**WHEN** API tests are written
**THEN** tests MUST cover success scenarios:
- **200 OK**: Successful GET/requests
- **201 Created**: Successful POST requests
- **204 No Content**: Successful DELETE requests
- **Response format**: Consistent JSON structure
- **Response headers**: Proper Content-Type, ETag, Cache-Control

