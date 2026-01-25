# backend-testing Specification Delta: Courses API Tests

## ADDED Requirements

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

## Success Metrics

1. All 12 ViewSets have test coverage
2. Total test count ≥ 300
3. All HTTP methods are tested
4. All permissions are enforced
5. All custom actions work correctly
6. All nested routing scenarios pass
7. Error responses are correct
8. Success responses are properly formatted
9. Run `manage.py test courses.tests.test_views` with no failures

### Requirement: API Tests Must Use Real HTTP Testing

API tests MUST use real HTTP client testing rather than direct model calls.

#### Scenario: HTTP Client Usage

**GIVEN** the API test suite
**WHEN** running tests
**THEN** all tests MUST use:
- `APIClient()` for realistic HTTP testing
- `client.get()`, `client.post()`, `client.patch()`, `client.delete()` methods
- Proper authentication headers (JWT or session)
- Real HTTP status codes and response bodies
- Request validation (URL paths, headers, body format)

#### Scenario: Content-Type Handling

**GIVEN** the API test suite
**WHEN** testing API interactions
**THEN** tests MUST verify:
- Request Content-Type headers are properly set
- Response Content-Type is application/json
- JSON request/response handling
- File upload handling for media uploads
- Content negotiation