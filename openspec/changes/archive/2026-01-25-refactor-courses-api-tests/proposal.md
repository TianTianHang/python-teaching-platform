# Add Comprehensive API Endpoint Tests for Courses App

## Summary

Add comprehensive test coverage for all ViewSets and API endpoints in the `backend/courses` app. This proposal focuses exclusively on API testing, covering authentication, permissions, HTTP methods, custom actions, and nested routing, building upon the infrastructure proposal.

## Motivation

### Current State

The courses app has 12 ViewSets with extensive API functionality including nested routing, custom actions, and complex permission systems, but currently has minimal API testing. Comprehensive API testing is essential for:

1. **API Contract**: Ensuring all endpoints work correctly
2. **Security**: Verifying authentication and permission enforcement
3. **Validation**: Testing input validation and error responses
4. **Integration**: Testing API interactions with models and services
5. **Documentation**: Providing executable API documentation

### Benefits

1. **Full Coverage**: 300+ test cases covering all ViewSets and endpoints
2. **Security Testing**: Ensure authentication and permissions work correctly
3. **Error Handling**: Test all error scenarios and response formats
4. **API Documentation**: Provide executable tests that serve as documentation
5. **Regression Prevention**: Catch API-related issues early

## Proposed Changes

### 1. Create API Test File

Create `test_views.py` with comprehensive tests for all 12 ViewSets organized by category:

**Core ViewSets** (60 tests)
- `CourseViewSet`: list/search/create, enroll action (atomic transaction), staff-only creation
- `ChapterViewSet`: list by course, mark_completed action (atomic), missing course handling
- `ProblemViewSet`: list by chapter/type, get_next_problem, mark_solved, check_fillblank_answer

**Execution ViewSets** (40 tests)
- `SubmissionViewSet`: create submission (algorithm execution), get results, free code vs problem
- `CodeDraftViewSet`: latest draft retrieval, save with submission association

**Progress ViewSets** (30 tests)
- `EnrollmentViewSet`: CRUD, duplicate prevention
- `ChapterProgressViewSet`: read-only access, user filtering
- `ProblemProgressViewSet`: status filtering, own progress only

**Discussion ViewSets** (50 tests)
- `DiscussionThreadViewSet`: nested routing (/courses/{id}/threads/, /chapters/{id}/threads/, /problems/{id}/threads/)
- `DiscussionReplyViewSet`: nested routing (/threads/{id}/replies/), mention handling

**Exam ViewSets** (40 tests)
- `ExamViewSet`: start exam (create submission), submit answers, get results, time limit calculation
- `ExamSubmissionViewSet`: read-only access, own submissions only

### 2. Authentication & Authorization Tests (50 tests)

Test all permission scenarios:
- Unauthenticated access returns 401
- Unauthorized access returns 403
- Staff-only endpoints enforcement
- Author-only modifications (discussions)

### 3. HTTP Method Testing (40 tests)

Test all HTTP methods for each ViewSet:
- GET: List, Retrieve with filtering, pagination, ordering
- POST: Create with validation, permission checks
- PATCH: Update with partial data
- DELETE: Delete with cascade behavior

### 4. Custom Action Testing (40 tests)

Test all custom actions:
- enroll, mark_completed, mark_solved
- get_next_problem, check_fillblank_answer
- start_exam, submit_exam, get_results

### 5. Nested Routing Testing (30 tests)

Test complex nested URL structures:
- URL parameter validation
- Nested relationship integrity
- Parent resource existence checks
- Hierarchical data access

## Scope

### In Scope

- All 12 ViewSets and their endpoints
- HTTP methods (GET, POST, PATCH, DELETE)
- Custom actions for each ViewSet
- Authentication and permission systems
- Filtering, searching, and ordering
- Nested routing scenarios
- Error responses (400, 401, 403, 404, 405)
- Success responses (200, 201, 204)

### Out of Scope

- Model testing (handled by separate proposal)
- Service layer testing (handled by separate proposal)
- Signal handler testing (handled by separate proposal)
- Admin interface testing (handled by separate proposal)
- Serializer testing (handled by separate proposal)
- Frontend integration testing

## Success Criteria

1. All ViewSets have test coverage
2. Total test count ≥ 300
3. All HTTP methods are tested
4. All permissions are enforced
5. All custom actions work correctly
6. All nested routing scenarios pass
7. Error responses are correct
8. Run `manage.py test courses.tests.test_views` with no failures

## Dependencies

- `refactor-courses-infrastructure` - Required for factories and base test case
- `factory-boy` package (already installed)

## Test Case Categories

### Authentication Tests (50 tests)
- Unauthenticated user attempts
- Valid authentication
- Token-based authentication
- Session-based authentication

### Permission Tests (60 tests)
- Public access vs authenticated
- Resource ownership verification
- Staff-only endpoints
- Role-based permissions

### CRUD Operations (100 tests)
- List views with filtering
- Retrieve views with permissions
- Create operations with validation
- Update operations with partial data
- Delete operations with cascade

### Custom Actions (80 tests)
- Parameter validation
- Action-specific permissions
- Business logic verification
- Response format validation

### Nested Routing (40 tests)
- Multi-level URL parameters
- Parent-child relationship access
- Resource existence checks
- Error handling for invalid paths

### Error Handling (30 tests)
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing auth)
- 403: Forbidden (permission denied)
- 404: Not Found (missing resource)
- 405: Method Not Allowed

## Performance Considerations

- Use `APIClient` for realistic HTTP testing
- Mock external dependencies in test setup
- Use `override_settings` for test configuration
- Database transaction isolation per test

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Complex nested routing hard to test | Test each nesting level independently, then integration |
- API performance issues during testing | Use test database with proper indexes and minimal data |
- Permission system too complex to test | Break down permission tests into manageable scenarios |

## Related Specifications

- Extends `backend-testing` specification
- Depends on `refactor-courses-infrastructure`
- Depends on `add-courses-model-tests` for model creation
- Future proposal: `add-courses-integration-tests` for cross-endpoint testing
