# Tasks: Add Comprehensive API Endpoint Tests for Courses App

This document outlines the step-by-step implementation tasks for adding comprehensive API test coverage to the `courses` app.

## Phase 1: Core ViewSets

### Task 1.1: Test CourseViewSet

**Description**: Create comprehensive tests for CourseViewSet endpoints.

**Steps**:
1. Create test class `CourseViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - Anonymous access returns public courses
   - Authenticated access returns all courses
   - Search by title functionality
   - Filtering capabilities
3. Test `retrieve` action:
   - Get course by ID
   - 404 for non-existent course
4. Test `create` action:
   - Staff-only access enforcement
   - Valid course creation
   - Invalid data validation
5. Test `update` action:
   - Staff-only access
   - Partial update with PATCH
6. Test `destroy` action:
   - Staff-only access
   - Cascade deletion verification
7. Test `enroll` custom action:
   - Atomic enrollment creation
   - Duplicate prevention
   - 201 on success

**Validation**:
- All HTTP methods work correctly
- Permissions are enforced
- Run `manage.py test courses.tests.test_views.CourseViewSetTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 1.2: Test ChapterViewSet

**Description**: Create comprehensive tests for ChapterViewSet endpoints.

**Steps**:
1. Create test class `ChapterViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List chapters by course
   - Course parameter validation
   - Ordering by chapter order
3. Test `retrieve` action:
   - Get chapter by ID
   - 404 for non-existent chapter
4. Test `mark_completed` custom action:
   - Atomic progress update
   - Creates/updates ChapterProgress
   - Sets status to completed
   - Sets completed_at timestamp
5. Test authentication requirements
6. Test permission checks (enrolled users only)

**Validation**:
- mark_completed action is atomic
- Progress is updated correctly
- Run `manage.py test courses.tests.test_views.ChapterViewSetTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 1.3: Test ProblemViewSet

**Description**: Create comprehensive tests for ProblemViewSet endpoints.

**Steps**:
1. Create test class `ProblemViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List problems by chapter
   - Filter by problem type
   - Filter by difficulty
3. Test `retrieve` action:
   - Get problem by ID
   - Include type-specific fields
4. Test `get_next_problem` custom action:
   - Unlock logic progression
   - Difficulty consideration
   - Prerequisite checking
5. Test `mark_solved` custom action:
   - Updates ProblemProgress
   - Records best submission
   - Sets solved_at timestamp
6. Test `check_fillblank_answer` custom action:
   - Answer validation
   - Score calculation
   - Partial credit handling

**Validation**:
- All custom actions work correctly
- Unlock logic is enforced
- Run `manage.py test courses.tests.test_views.ProblemViewSetTestCase`

**Estimated Effort**: Extra Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 2: Execution ViewSets

### Task 2.1: Test SubmissionViewSet

**Description**: Create comprehensive tests for SubmissionViewSet endpoints.

**Steps**:
1. Create test class `SubmissionViewSetTestCase` in `test_views.py`
2. Test `create` action:
   - Algorithm problem submission
   - Free code submission (null problem)
   - Code execution via service
   - Status initialization
3. Test `retrieve` action:
   - Get submission by ID
   - Own submissions only
4. Test `list` action:
   - List user's own submissions
   - Filter by problem
   - Filter by status
5. Test code execution flow:
   - Pending → Judging → Accepted
   - Error status handling
6. Test permission checks (own submissions only)

**Validation**:
- Code execution is triggered
- Status transitions work
- Run `manage.py test courses.tests.test_views.SubmissionViewSetTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 2.2: Test CodeDraftViewSet

**Description**: Create comprehensive tests for CodeDraftViewSet endpoints.

**Steps**:
1. Create test class `CodeDraftViewSetTestCase` in `test_views.py`
2. Test `create` action:
   - Save new draft
   - Associate with submission (optional)
   - save_type validation
3. Test `retrieve` action:
   - Get latest draft for user+problem
   - 404 if no draft exists
4. Test `update` action:
   - Update existing draft
   - Create if doesn't exist
5. Test list action:
   - List user's drafts
   - Filter by problem
6. Test permission checks (own drafts only)

**Validation**:
- Draft save/load works correctly
- Latest draft retrieval functions
- Run `manage.py test courses.tests.test_views.CodeDraftViewSetTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 3: Progress ViewSets

### Task 3.1: Test EnrollmentViewSet

**Description**: Create comprehensive tests for EnrollmentViewSet endpoints.

**Steps**:
1. Create test class `EnrollmentViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List user's enrollments
   - Filter by course
3. Test `retrieve` action:
   - Get enrollment by ID
   - Own enrollments only
4. Test `create` action:
   - Create new enrollment
   - Duplicate prevention
   - enrolled_at auto-set
5. Test `destroy` action:
   - Delete enrollment
   - Cascade behavior
6. Test progress calculation in serialization

**Validation**:
- Duplicate enrollment is prevented
- Progress is calculated correctly
- Run `manage.py test courses.tests.test_views.EnrollmentViewSetTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 3.2: Test ChapterProgressViewSet

**Description**: Create comprehensive tests for ChapterProgressViewSet endpoints.

**Steps**:
1. Create test class `ChapterProgressViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List user's chapter progress
   - Filter by course
   - Filter by status
3. Test `retrieve` action:
   - Get progress by ID
   - Own progress only
4. Test read-only enforcement (no create/update/destroy)
5. Test progress percentage calculation

**Validation**:
- Read-only access is enforced
- Filtering works correctly
- Run `manage.py test courses.tests.test_views.ChapterProgressViewSetTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 3.3: Test ProblemProgressViewSet

**Description**: Create comprehensive tests for ProblemProgressViewSet endpoints.

**Steps**:
1. Create test class `ProblemProgressViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List user's problem progress
   - Filter by chapter
   - Filter by status (not_started/in_progress/completed)
3. Test `retrieve` action:
   - Get progress by ID
   - Own progress only
4. Test read-only enforcement
5. Test attempt counting in serialization
6. Test best submission inclusion

**Validation**:
- Status filtering works
- Attempt count is accurate
- Run `manage.py test courses.tests.test_views.ProblemProgressViewSetTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 4: Discussion ViewSets

### Task 4.1: Test DiscussionThreadViewSet

**Description**: Create comprehensive tests for DiscussionThreadViewSet endpoints with nested routing.

**Steps**:
1. Create test class `DiscussionThreadViewSetTestCase` in `test_views.py`
2. Test nested routing:
   - `/courses/{id}/threads/` - List threads by course
   - `/chapters/{id}/threads/` - List threads by chapter
   - `/problems/{id}/threads/` - List threads by problem
3. Test `create` action:
   - Create thread with title and content
   - Associate with course/chapter/problem
   - Set author from request.user
4. Test `retrieve` action:
   - Get thread by ID
   - Include replies count
5. Test `update` action:
   - Author-only modification
   - Update title/content
   - Pin/unpin, resolve/unresolve
6. Test `destroy` action:
   - Author-only deletion
7. Test mention processing in content

**Validation**:
- Nested routing works for all levels
- Author-only permissions enforced
- Run `manage.py test courses.tests.test_views.DiscussionThreadViewSetTestCase`

**Estimated Effort**: Extra Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 4.2: Test DiscussionReplyViewSet

**Description**: Create comprehensive tests for DiscussionReplyViewSet endpoints with nested routing.

**Steps**:
1. Create test class `DiscussionReplyViewSetTestCase` in `test_views.py`
2. Test nested routing:
   - `/threads/{id}/replies/` - List replies by thread
3. Test `create` action:
   - Create reply with content
   - Associate with thread
   - Set author from request.user
   - Update thread activity
4. Test `retrieve` action:
   - Get reply by ID
5. Test `update` action:
   - Author-only modification
   - Update content
6. Test `destroy` action:
   - Author-only deletion
7. Test mention validation (@username format)
8. Test thread activity updates on create/delete

**Validation**:
- Nested routing works
- Thread activity is updated
- Run `manage.py test courses.tests.test_views.DiscussionReplyViewSetTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 5: Exam ViewSets

### Task 5.1: Test ExamViewSet

**Description**: Create comprehensive tests for ExamViewSet endpoints.

**Steps**:
1. Create test class `ExamViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List available exams
   - Filter by course
   - Time calculation (remaining/upcoming)
3. Test `retrieve` action:
   - Get exam by ID
   - Include question details
   - Shuffle questions if configured
4. Test `start_exam` custom action:
   - Create ExamSubmission
   - Set start time
   - Verify enrollment
   - Check for existing submission
5. Test `submit_exam` custom action:
   - Create ExamAnswer records
   - Calculate score
   - Set status to submitted
6. Test `get_results` custom action:
   - Return score breakdown
   - Show correct answers
   - Display pass/fail status
7. Test time limit enforcement

**Validation**:
- One submission per exam is enforced
- Score calculation is correct
- Run `manage.py test courses.tests.test_views.ExamViewSetTestCase`

**Estimated Effort**: Extra Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 5.2: Test ExamSubmissionViewSet

**Description**: Create comprehensive tests for ExamSubmissionViewSet endpoints.

**Steps**:
1. Create test class `ExamSubmissionViewSetTestCase` in `test_views.py`
2. Test `list` action:
   - List user's exam submissions
   - Filter by exam
   - Filter by status
3. Test `retrieve` action:
   - Get submission by ID
   - Own submissions only
   - Include answers
4. Test read-only enforcement (no create/update/destroy)
5. Test score retrieval
6. Test time tracking display

**Validation**:
- Read-only access is enforced
- Score is calculated correctly
- Run `manage.py test courses.tests.test_views.ExamSubmissionViewSetTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 6: Authentication & Authorization

### Task 6.1: Test Authentication Across All ViewSets

**Description**: Create comprehensive authentication tests for all ViewSets.

**Steps**:
1. Create test class `AuthenticationTestCase` in `test_views.py`
2. Test unauthenticated access (401):
   - All protected endpoints return 401
   - Public endpoints work without auth
3. Test authenticated access (200):
   - Valid JWT token
   - Valid session authentication
4. Test invalid token handling:
   - Expired token returns 401
   - Malformed token returns 401
5. Test token refresh flow (if applicable)

**Validation**:
- Unauthenticated requests are rejected
- Valid authentication works
- Run `manage.py test courses.tests.test_views.AuthenticationTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 6.2: Test Permissions Across All ViewSets

**Description**: Create comprehensive permission tests for all ViewSets.

**Steps**:
1. Create test class `PermissionTestCase` in `test_views.py`
2. Test staff-only endpoints (403):
   - Course create/update/destroy
   - Exam management
3. Test author-only modifications (403):
   - Discussion thread updates
   - Discussion reply updates
4. Test enrollment-based access:
   - Chapter/progress access requires enrollment
5. Test ownership-based access:
   - Own submissions only
   - Own progress only
   - Own drafts only

**Validation**:
- Staff-only access is enforced
- Author-only modifications work
- Run `manage.py test courses.tests.test_views.PermissionTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 7: Error Handling

### Task 7.1: Test Error Responses

**Description**: Create comprehensive error response tests for all endpoints.

**Steps**:
1. Create test class `ErrorResponseTestCase` in `test_views.py`
2. Test 400 Bad Request:
   - Validation errors
   - Invalid data format
   - Missing required fields
3. Test 401 Unauthorized:
   - Missing authentication
   - Invalid token
4. Test 403 Forbidden:
   - Permission denied
   - Resource ownership
5. Test 404 Not Found:
   - Invalid ID
   - Non-existent resource
6. Test 405 Method Not Allowed:
   - Incorrect HTTP method
7. Verify error response format consistency

**Validation**:
- All error codes return correctly
- Error messages are informative
- Run `manage.py test courses.tests.test_views.ErrorResponseTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 1.1 | Test CourseViewSet | Large | infrastructure |
| 1.2 | Test ChapterViewSet | Large | infrastructure |
| 1.3 | Test ProblemViewSet | Extra Large | infrastructure |
| 2.1 | Test SubmissionViewSet | Large | infrastructure |
| 2.2 | Test CodeDraftViewSet | Medium | infrastructure |
| 3.1 | Test EnrollmentViewSet | Medium | infrastructure |
| 3.2 | Test ChapterProgressViewSet | Medium | infrastructure |
| 3.3 | Test ProblemProgressViewSet | Medium | infrastructure |
| 4.1 | Test DiscussionThreadViewSet | Extra Large | infrastructure |
| 4.2 | Test DiscussionReplyViewSet | Large | infrastructure |
| 5.1 | Test ExamViewSet | Extra Large | infrastructure |
| 5.2 | Test ExamSubmissionViewSet | Medium | infrastructure |
| 6.1 | Test Authentication | Medium | infrastructure |
| 6.2 | Test Permissions | Large | infrastructure |
| 7.1 | Test Error Responses | Medium | infrastructure |

## Parallelization Opportunities

- **Tasks 1.1-1.3** (Core ViewSets) can be developed in parallel
- **Tasks 2.1-2.2** (Execution ViewSets) can be developed in parallel
- **Tasks 3.1-3.3** (Progress ViewSets) can be developed in parallel
- **Tasks 4.1-4.2** (Discussion ViewSets) can be developed in parallel
- **Tasks 5.1-5.2** (Exam ViewSets) can be developed in parallel
- **Tasks 6.1-6.2, 7.1** (Auth/Permissions/Errors) can be developed in parallel
- All tasks depend on `refactor-courses-infrastructure` being complete
