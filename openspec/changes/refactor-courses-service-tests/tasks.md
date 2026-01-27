# Tasks: Add Comprehensive Service Tests for Courses App

This document outlines the step-by-step implementation tasks for adding comprehensive service and signal test coverage to the `courses` app.

## Phase 1: CodeExecutorService

### Task 1.1: Test run_all_test_cases Method

**Description**: Create comprehensive tests for the `run_all_test_cases` method in CodeExecutorService.

**Steps**:
1. Create test class `CodeExecutorServiceTestCase` in `test_services.py`
2. Test successful execution:
   - All test cases pass
   - Return correct results
   - Status mapping (Judge0 → DRF)
3. Test backend connection failures:
   - Connection refused
   - DNS failure
   - Network timeout
4. Test test case execution failures:
   - Individual test failure
   - Multiple test failures
5. Test resource limit exceeded:
   - Time limit exceeded
   - Memory limit exceeded
6. Test code compilation errors:
   - Syntax errors
   - Import errors
   - Type errors
7. Test code wrapping with template:
   - Code is properly wrapped
   - Template variables are substituted
8. Test result aggregation:
   - Scores are calculated
   - Status is determined
9. Test concurrent execution:
   - Multiple submissions at once
10. Test partial failure scenarios:
    - Some test cases pass, some fail

**Validation**:
- All scenarios are tested with proper mocking
- Results are correctly parsed and saved
- Run `manage.py test courses.tests.test_services.CodeExecutorServiceTestCase`

**Estimated Effort**: Extra Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 1.2: Test run_freely Method

**Description**: Create comprehensive tests for the `run_freely` method in CodeExecutorService.

**Steps**:
1. Test successful free code execution:
   - Code is executed
   - Result is returned
   - No test cases used
2. Test timeout handling:
   - Code exceeds time limit
   - Returns timeout status
3. Test memory limit handling:
   - Code exceeds memory limit
   - Returns memory limit status
4. Test execution errors:
   - Runtime errors
   - Exceptions thrown
5. Test safety limits enforcement:
   - Input/output size limits
   - System call restrictions

**Validation**:
- Free execution works without test cases
- Limits are enforced
- Run `manage.py test courses.tests.test_services.run_freely`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 2: External Integration Testing

### Task 2.1: Test Judge0 Integration

**Description**: Create comprehensive tests for external Judge0 API integration.

**Steps**:
1. Test successful Judge0 responses:
   - Mock Judge0 success response
   - Parse response correctly
   - Map to DRF format
2. Test error responses:
   - 400 Bad Request
   - 404 Not Found
   - 429 Too Many Requests
   - 500 Server Error
3. Test network error handling:
   - Connection refused
   - DNS failure
   - Certificate issues (SSL/TLS)
4. Test rate limiting scenarios:
   - Rate limit exceeded
   - Retry logic
5. Test invalid response format:
   - Missing fields
   - Wrong data types
   - Invalid JSON
6. Test backend service unavailability:
   - Service down
   - No response
   - Slow response
7. Test authentication with backend:
   - Valid API key
   - Invalid API key

**Validation**:
- All external scenarios are covered
- Error handling is robust
- Run `manage.py test courses.tests.test_services.ExternalIntegrationTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 3: Database Update Testing

### Task 3.1: Test Database Transaction Handling

**Description**: Create comprehensive tests for database operations in service layer.

**Steps**:
1. Test submission record creation:
   - Create Submission record
   - Set initial status
   - Associate with user and problem
2. Test status persistence:
   - Status updates are saved
   - Timestamps are updated
3. Test transaction atomicity:
   - All operations succeed or none do
   - Partial failures don't leave inconsistent state
4. Test concurrent update handling:
   - Multiple submissions at once
   - No race conditions
5. Test data consistency:
   - Foreign keys are valid
   - Related objects exist
6. Test rollback on failure:
   - Database error causes rollback
   - No partial data saved
7. Test cascade deletion behavior:
   - When problem is deleted
   - When user is deleted

**Validation**:
- Database operations are atomic
- Data is consistent
- Run `manage.py test courses.tests.test_services.DatabaseUpdateTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 4: Discussion Signal Testing

### Task 4.1: Test DiscussionReply post_save Signal

**Description**: Create comprehensive tests for DiscussionReply post_save signal handler.

**Steps**:
1. Create test class `DiscussionSignalTestCase` in `test_signals.py`
2. Test thread reply count update:
   - Increment reply_count on new reply
   - No increment for edits
3. Test activity timestamp update:
   - Update last_activity_at
   - Update timestamp format
4. Test concurrent update handling:
   - Multiple replies at once
   - Reply count accurate
5. Test thread existence check:
   - Signal thread exists before update
   - Graceful handling if deleted
6. Test signal handler error recovery:
   - Signal fails gracefully
   - No partial updates
7. Test multiple replies in quick succession:
   - Handles rapid fire replies
   - No race conditions

**Validation**:
- Signal works correctly
- Thread activity is updated
- Run `manage.py test courses.tests.test_signals.DiscussionSignalTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 5: Progress Signal Testing

### Task 5.1: Test ProblemProgress post_save Signal

**Description**: Create comprehensive tests for ProblemProgress post_save signal handler.

**Steps**:
1. Test cache invalidation triggering:
   - Signal fires on save
   - Cache is invalidated
2. Test cache key generation:
   - Correct key pattern
   - User and problem in key
3. Test pattern matching for cache keys:
   - All related keys invalidated
   - No unrelated keys affected
4. Test multiple signals handling:
   - Multiple saves in one transaction
   - Only one invalidation
5. Test signal handler performance:
   - Many updates at once
   - No performance degradation

**Validation**:
- Cache is invalidated properly
- Key generation is correct
- Run `manage.py test courses.tests.test_signals.ProgressSignalTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 6: Exam Signal Testing

### Task 6.1: Test ExamProblem Signal Handlers

**Description**: Create comprehensive tests for Exam model signal handlers.

**Steps**:
1. Test ExamProblem post_save signal:
   - Total score update calculation
   - Update exam's total_score
   - Recalculate passing score if needed
   - Handle skip_signal flag
2. Test concurrent score updates:
   - Multiple ExamProblem changes
   - Final score accurate
3. Test ExamProblem post_delete signal:
   - Total score recalculation
   - Remove deleted problem score
   - Update passing score
4. Test empty exam handling:
   - No problems left
   - Score should be 0

**Validation**:
- Score calculations are correct
- Signal handlers are robust
- Run `manage.py test courses.tests.test_signals.ExamSignalTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 7: Enrollment Signal Testing

### Task 7.1: Test Enrollment post_save Signal

**Description**: Create comprehensive tests for Enrollment model signal handler.

**Steps**:
1. Test enrollment cache clearing:
   - Signal fires on save
   - Related cache is cleared
2. Test cache invalidation timing:
   - Cache is cleared after database commit
   - No stale data
3. Test multiple signal handling:
   - Many enrollments at once
   - Cache cleared efficiently
4. Test signal performance with many enrollments:
   - Bulk import scenario
   - No timeout issues

**Validation**:
- Cache is invalidated correctly
- Performance is acceptable
- Run `manage.py test courses.tests.test_signals.EnrollmentSignalTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 8: Error Recovery Testing

### Task 8.1: Test Error Recovery Scenarios

**Description**: Create comprehensive tests for error recovery in services and signals.

**Steps**:
1. Test service restart scenarios:
   - Service connection restored
   - Resumes operation normally
2. Test database rollback verification:
   - Rollback is complete
   - No data left behind
3. Test cache recovery mechanisms:
   - Cache corruption recovery
   - Recache on access
4. Test external service recovery:
   - Backend service comes back online
   - Continue normal operation
5. Test transaction rollback on failure:
   - Database errors handled
   - No partial state
6. Test signal handler error handling:
   - Signal failure doesn't crash
   - Graceful degradation
7. Test graceful degradation:
   - Service unavailable
   - Return appropriate response

**Validation**:
- Error recovery works
- System remains stable
- Run `manage.py test courses.tests.test_signals.ErrorRecoveryTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 9: Time-Based Testing

### Task 9.1: Test Time-Dependent Logic

**Description**: Create comprehensive tests for time-dependent business logic.

**Steps**:
1. Test exam time limit calculation:
   - Time remaining
   - Time limit enforcement
   - Past/future handling
2. Test progress timestamp handling:
   - Created_at accuracy
   - Updated_at accuracy
   - Timezone handling
3. Test cache expiration:
   - TTL works correctly
   - Cache expires on time
4. Test scheduled operations:
   - Run at specific time
   - Proper scheduling
5. Test temporal validation:
   - Past dates rejected
   - Future dates accepted
6. Test timezone handling:
   - Different timezones
   - UTC conversion
7. Test daylight saving time scenarios:
   - DST changes
   - Time consistency

**Validation**:
- Time-based logic is correct
- Timezones handled properly
- Run `manage.py test courses.tests.test_services.TimeBasedTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 10: Concurrency Testing

### Task 10.1: Test Concurrency Scenarios

**Description**: Create comprehensive tests for concurrent operations.

**Steps**:
1. Test signal handler race conditions:
   - Multiple signals at once
   - No data corruption
2. Test concurrent API calls:
   - Multiple users at once
   - No conflicts
3. Test database transaction isolation:
   - Read committed level
   - No dirty reads
4. Test cache coherency:
   - Multiple updates
   - Consistent view
5. Test lock contention handling:
   - High concurrency
   - No deadlocks
6. Test deadlock prevention:
   - Circular dependencies
   - Timeout handling
7. Test parallel test execution:
   - Tests don't interfere
   - Independent execution

**Validation**:
- Concurrency is handled correctly
- No race conditions
- Run `manage.py test courses.tests.test_signals.ConcurrencyTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 1.1 | Test run_all_test_cases | Extra Large | infrastructure |
| 1.2 | Test run_freely | Medium | infrastructure |
| 2.1 | Test Judge0 integration | Large | infrastructure |
| 3.1 | Test database transactions | Medium | infrastructure |
| 4.1 | Test Discussion signals | Medium | infrastructure |
| 5.1 | Test Progress signals | Medium | infrastructure |
| 6.1 | Test Exam signals | Large | infrastructure |
| 7.1 | Test Enrollment signals | Medium | infrastructure |
| 8.1 | Test error recovery | Large | infrastructure |
| 9.1 | Test time-based logic | Medium | infrastructure |
| 10.1 | Test concurrency scenarios | Large | infrastructure |

## Parallelization Opportunities

- **Tasks 1.1 and 1.2** (CodeExecutorService methods) can be developed in parallel
- **Tasks 4.1-7.1** (Signal tests for different models) can be developed in parallel
- **Tasks 2.1, 3.1, 8.1-10.1** can be developed in parallel groups
- All tasks depend on `refactor-courses-infrastructure` being complete
