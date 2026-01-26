# backend-testing Specification Delta: Courses Service Tests

## ADDED Requirements

### Requirement: courses App Business Logic Must Have Comprehensive Test Coverage

All services and signal handlers in the `courses` app MUST have comprehensive test coverage with at least 150 test cases covering all business logic.

#### Scenario: CodeExecutorService Coverage

**GIVEN** the CodeExecutorService in courses/services.py
**WHEN** service tests are written
**THEN** tests MUST cover:
- **run_all_test_cases()**:
  - Successful execution with all test cases passing
  - Backend connection failure handling
  - Test case execution failures
  - Resource limit exceeded (time/memory)
  - Code compilation errors
  - Status mapping (Judge0 → DRF)
  - Code wrapping with template
  - Result aggregation
  - Concurrent execution handling
  - Partial failure scenarios

- **run_freely()**:
  - Successful free code execution
  - Timeout handling
  - Memory limit handling
  - Execution errors
  - Safety limits enforcement

#### Scenario: External Integration Testing

**GIVEN** the CodeExecutorService interaction with Judge0 backend
**WHEN** service tests are written
**THEN** tests MUST cover:
- Mock Judge0 backend responses (success, error, timeout)
- Network error handling (connection refused, DNS failure)
- Rate limiting scenarios
- Invalid response format handling
- Backend service unavailability
- Certificate issues (SSL/TLS errors)
- Authentication with backend

#### Scenario: Database Update Testing

**GIVEN** service interactions with database
**WHEN** service tests are written
**THEN** tests MUST cover:
- Submission record creation/updates
- Status persistence and updates
- Transaction atomicity
- Concurrent update handling
- Data consistency verification
- Rollback on failure
- Foreign key constraints
- Cascade deletion behavior

#### Scenario: Discussion Signal Coverage

**GIVEN** Discussion model signals
**WHEN** signal tests are written
**THEN** tests MUST cover:
- **DiscussionReply post_save**:
  - Thread reply count update
  - Activity timestamp update
  - Concurrent update handling
  - Thread existence check
  - Signal handler error recovery
  - Multiple replies in quick succession

#### Scenario: Progress Signal Coverage

**GIVEN** Progress model signals
**WHEN** signal tests are written
**THEN** tests MUST cover:
- **ProblemProgress post_save**:
  - Cache invalidation triggering
  - Cache key generation correctness
  - Pattern matching for cache keys
  - Multiple signals handling
  - Signal handler performance with many updates

#### Scenario: Exam Signal Coverage

**GIVEN** Exam model signals
**WHEN** signal tests are written
**THEN** tests MUST cover:
- **ExamProblem post_save**:
  - Total score update calculation
  - Skip signal flag handling
  - Concurrent score updates
  - Passing score recalculation
  - Score update propagation
- **ExamProblem post_delete**:
  - Total score recalculation
  - Score update propagation
  - Empty exam handling

#### Scenario: Enrollment Signal Coverage

**GIVEN** Enrollment model signals
**WHEN** signal tests are written
**THEN** tests MUST cover:
- **Enrollment post_save**:
  - Enrollment cache clearing
  - Cache invalidation timing
  - Multiple signal handling
  - Signal performance with many enrollments

#### Scenario: Error Recovery Testing

**GIVEN** service and signal error scenarios
**WHEN** error handling tests are written
**THEN** tests MUST cover:
- Service restart scenarios
- Database rollback verification
- Cache recovery mechanisms
- External service recovery
- Transaction rollback on failure
- Signal handler error handling
- Graceful degradation

#### Scenario: Time-Based Testing

**GIVEN** time-dependent business logic
**WHEN** time-based tests are written
**THEN** tests MUST cover:
- Exam time limit calculation
- Progress timestamp handling
- Cache expiration
- Scheduled operations
- Temporal validation (past/future dates)
- Timezone handling
- Daylight saving time scenarios

#### Scenario: Concurrency Testing

**GIVEN** concurrent operation scenarios
**WHEN** concurrency tests are written
**THEN** tests MUST cover:
- Signal handler race conditions
- Concurrent API calls
- Database transaction isolation
- Cache coherency
- Lock contention handling
- Deadlock prevention
- Parallel test execution

## Success Metrics

1. All service methods have test coverage
2. All signal handlers have test coverage
3. Total test count ≥ 150
4. External dependencies are properly mocked
5. Error scenarios are covered
6. Concurrent operation handling is tested
7. Side effects are verified
8. Time-based logic is tested
9. Run `manage.py test courses.tests.test_services` with no failures

### Requirement: Service Tests Must Use Proper Mocking Strategy

Service tests MUST use comprehensive mocking for external dependencies while maintaining test realism.

#### Scenario: Mocking External Dependencies

**GIVEN** the service test suite
**WHEN** running tests
**THEN** all external dependencies MUST be mocked:
- Judge0 API calls mocked with `unittest.mock`
- Database operations mocked for performance
- Cache operations mocked for isolation
- Network calls mocked with timeout scenarios
- File operations mocked with various scenarios
- Mock responses include success, failure, and edge cases

#### Scenario: Realistic Test Data

**GIVEN** the service test suite
**WHEN** creating test scenarios
**THEN** test data MUST be:
- Realistically sized (not minimal artificial data)
- Representative of actual production data
- Include edge cases and boundary conditions
- Properly formatted (JSON, files, etc.)
- Varied enough to cover all scenarios

#### Scenario: Test Isolation

**GIVEN** the service test suite
**WHEN** running tests
**THEN** each test MUST be:
- Independent of other tests
- Not share database state
- Not share cache state
- Not leave side effects
- Use transaction rollback where applicable
- Reset global state where necessary