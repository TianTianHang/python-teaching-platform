# Add Business Logic Tests for Courses App

## Summary

Add comprehensive test coverage for business logic services and signal handlers in the `backend/courses` app. This proposal focuses exclusively on service layer testing, including the CodeExecutorService and all signal handlers, building upon the infrastructure proposal.

## Motivation

### Current State

The courses app has complex business logic in services and signal handlers, including code execution and side-effect management, but currently has minimal testing. Business logic testing is essential for:

1. **Core Functionality**: Ensuring critical services work correctly (e.g., code execution)
2. **Integration**: Testing service-layer integration with models and APIs
3. **Error Handling**: Verifying proper error handling and recovery
4. **Performance**: Testing service performance under different conditions
5. **Reliability**: Ensuring deterministic behavior

### Benefits

1. **Service Coverage**: 150+ test cases covering all services and signals
2. **Code Execution Testing**: Thorough testing of algorithm problem execution
3. **Signal Verification**: Ensuring all side effects work correctly
4. **External Integration**: Proper mocking of external dependencies (Judge0)
5. **Error Recovery**: Testing failure scenarios and recovery paths

## Proposed Changes

### 1. Create Service Test File

Create `test_services.py` with comprehensive tests for business logic:

**CodeExecutorService Tests** (80 tests)
- `run_all_test_cases()`:
  - Successful execution with all test cases passing
  - Backend connection failure handling
  - Test case execution failures
  - Resource limit exceeded (time/memory)
  - Code compilation errors
  - Status mapping (Judge0 → DRF)
  - Code wrapping with template
  - Result aggregation
  - Concurrent execution
  - Partial failures

- `run_freely()`:
  - Successful free code execution
  - Timeout handling
  - Memory limit handling
  - Execution errors
  - Safety limits enforcement

**External Integration Tests** (20 tests)
- Mock Judge0 backend responses
- Handle timeout scenarios
- Handle invalid responses
- Network error handling
- Rate limiting scenarios

**Database Update Tests** (20 tests)
- Submission record creation/updates
- Status persistence
- Transaction atomicity
- Concurrent update handling

### 2. Create Signal Test File

Create `test_signals.py` with comprehensive tests for all signal handlers:

**Discussion Signals** (15 tests)
- `DiscussionReply` post_save:
  - Thread reply count update
  - Activity timestamp update
  - Concurrent update handling
  - Thread existence check

**Progress Signals** (10 tests)
- `ProblemProgress` post_save:
  - Cache invalidation
  - Cache key generation
  - Pattern matching
  - Multiple signals handling

**Exam Signals** (15 tests)
- `ExamProblem` post_save:
  - Total score update
  - Skip signal flag handling
  - Concurrent score updates
  - Passing score recalculation
- `ExamProblem` post_delete:
  - Total score recalculation
  - Score update propagation

**Enrollment Signals** (10 tests)
- `Enrollment` post_save:
  - Enrollment cache clearing
  - Cache invalidation timing
  - Multiple signal handling

### 3. Test Service Layer Integration

Test integration between services and other layers:
- Service → Model interactions
- Service → API interactions
- Service → Signal interactions
- Service → Service interactions

## Scope

### In Scope

- All service methods in `courses/services.py`
- All signal handlers in courses models
- External API integration (Judge0)
- Error handling scenarios
- Performance characteristics
- Side effect management
- Cache invalidation patterns

### Out of Scope

- Model testing (handled by separate proposal)
- API endpoint testing (handled by separate proposal)
- View/ViewSet testing (handled by separate proposal)
- Admin interface testing (handled by separate proposal)
- Serializer testing (handled by separate proposal)
- Frontend integration testing

## Success Criteria

1. All service methods have test coverage
2. All signal handlers have test coverage
3. Total test count ≥ 150
4. External dependencies are properly mocked
5. Error scenarios are covered
6. Concurrent operation handling is tested
7. Side effects are verified
8. Run `manage.py test courses.tests.test_services` with no failures

## Dependencies

- `refactor-courses-infrastructure` - Required for factories and base test case
- `refactor-courses-model-tests` - Required for model creation
- `factory-boy` package (already installed)
- `mock` library (standard library)

## Test Case Categories

### Service Method Tests (80 tests)
- Success scenarios with various inputs
- Failure scenarios with error conditions
- Edge cases (empty inputs, maximum values)
- Integration with other services
- Performance under load

### External API Tests (20 tests)
- Mock backend success responses
- Mock backend failure responses
- Timeout handling
- Network error handling
- Rate limiting
- Invalid response formats

### Signal Handler Tests (50 tests)
- Signal triggering conditions
- Side effect verification
- Concurrent signal handling
- Cache invalidation
- Data consistency
- Error recovery

### Error Recovery Tests (20 tests)
- Service restart scenarios
- Database rollback verification
- Cache recovery
- External service recovery
- Transaction rollback

## Testing Techniques

### Mocking Strategy
- Use `unittest.mock` for external dependencies
- Create realistic mock responses
- Test both success and failure modes
- Verify mock interactions

### Time-Based Testing
- Use `freezegun` for deterministic time-based tests
- Test temporal logic in signals
- Test timeout scenarios
- Test scheduled operations

### Concurrent Testing
- Test signal handler race conditions
- Test concurrent API calls
- Test database transaction isolation
- Test cache coherency

## Performance Considerations

- Use `timeit` for performance measurement
- Test with realistic data sizes
- Test with concurrent operations
- Test resource usage limits

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
- Service complexity makes testing difficult | Break down service methods into smaller testable units |
- External service flakiness | Use comprehensive mocking with deterministic responses |
- Signal handler order dependency | Test each signal independently and in combination |
- Concurrency testing complexity | Use deterministic test data and controlled concurrency |

## Related Specifications

- Extends `backend-testing` specification
- Depends on `refactor-courses-infrastructure`
- Depends on `add-courses-model-tests` for model creation
- Future proposal: `add-courses-load-tests` for performance testing
