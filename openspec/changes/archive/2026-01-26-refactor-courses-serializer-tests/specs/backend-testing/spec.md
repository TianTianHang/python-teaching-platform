# backend-testing Specification Delta: Courses Serializer Tests

## ADDED Requirements

### Requirement: courses App Serializers Must Have Comprehensive Test Coverage

All 15+ serializers in the `courses` app MUST have comprehensive test coverage with at least 150 test cases covering all serialization and validation functionality.

#### Scenario: Core Serializers Coverage

**GIVEN** CourseModelSerializer, ChapterSerializer, and ProblemSerializer
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **CourseModelSerializer**:
  - Authentication status handling
  - Recent threads inclusion
  - Field ordering customization
  - Read-only fields (title, description)
  - Course instructor relationship
  - Related object serialization
- **ChapterSerializer**:
  - User authentication handling
  - Progress status calculation
  - Course title inclusion
  - Read-only progress fields
  - Chapter content handling
- **ProblemSerializer**:
  - Type-based conditional fields
  - Unlock status logic
  - Progress inclusion
  - Related fields serialization
  - Difficulty display

#### Scenario: Problem Type Serializers Coverage

**GIVEN** AlgorithmProblemSerializer, ChoiceProblemSerializer, and FillBlankProblemSerializer
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **AlgorithmProblemSerializer**:
  - Sample case handling
  - Empty test case sets
  - Code template validation
  - Solution name verification
  - Time/memory limits inclusion
  - Read-only fields enforcement
- **ChoiceProblemSerializer**:
  - Cross-field validation (answer in options)
  - Single/multiple choice format validation
  - Option format validation (A, B, C...)
  - Maximum/minimum option count
  - Required fields validation
  - Correct answer format
- **FillBlankProblemSerializer**:
  - Multiple JSON format support
  - Blank count calculation
  - Case sensitivity handling
  - Answer format validation
  - Score distribution validation
  - Blank type validation

#### Scenario: Progress Serializers Coverage

**GIVEN** EnrollmentSerializer, ChapterProgressSerializer, and ProblemProgressSerializer
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **EnrollmentSerializer**:
  - Progress calculation with zero chapters
  - Chapter status aggregation
  - Read-only fields verification
  - Enrollment date handling
  - Course completion percentage
- **ChapterProgressSerializer**:
  - Status validation (not_started, in_progress, completed)
  - Completed timestamp handling
  - Read-only fields
  - Progress percentage calculation
  - Status transitions
- **ProblemProgressSerializer**:
  - Status transitions
  - Best submission logic
  - Attempt counting
  - Solved timestamp handling
  - Performance metrics inclusion
  - Best submission identification

#### Scenario: Discussion Serializers Coverage

**GIVEN** BriefDiscussionThreadSerializer, DiscussionThreadSerializer, and DiscussionReplySerializer
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **BriefDiscussionThreadSerializer**:
  - Thread summary fields
  - Author information
  - Recent replies count
  - Activity timestamp
  - Pinned/resolved status
- **DiscussionThreadSerializer**:
  - Full thread serialization
  - Nested replies inclusion
  - Reply count
  - Pinned/resolved status
  - Mention handling in content
  - Thread activity updates
- **DiscussionReplySerializer**:
  - Reply content
  - Author information
  - Timestamps
  - Mention processing (@username)
  - Thread activity updates
  - Reply relationships

#### Scenario: Exam Serializers Coverage

**GIVEN** All exam-related serializers (ExamListSerializer, ExamDetailSerializer, etc.)
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **ExamListSerializer**:
  - Time calculation logic
  - Status display
  - Course information
  - Enrollment requirements
  - Time remaining calculation
  - Upcoming/exam status
- **ExamDetailSerializer**:
  - Question shuffling
  - Missing problems handling
  - Total score calculation
  - Passing score display
  - Question details with type-specific fields
  - Timer information
- **ExamCreateSerializer**:
  - Time range validation (start_time < end_time)
  - Question score total validation
  - Question type validation
  - Status transition validation
  - Duplicate prevention
- **ExamAnswerDetailSerializer**:
  - Correct answer display logic
  - User answer inclusion
  - Score calculation
  - Answer correctness verification
  - Partial credit handling
- **ExamSubmissionSerializer**:
  - Null score handling
  - Submission status
  - Time tracking
  - Auto-submission logic
  - Score breakdown
- **ExamSubmissionCreateSerializer**:
  - Duplicate submission prevention
  - Time window validation
  - Enrollment check
  - Question count validation
  - Status validation
- **ExamSubmitSerializer**:
  - Answer presence validation
  - Answer format validation
  - Question type matching
  - Batch validation
  - Score calculation

#### Scenario: Field Validation Testing

**GIVEN** all serializers
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **Required Fields**:
  - Missing required field validation
  - Partial submission handling
  - Empty value validation
- **Field Constraints**:
  - Length validation
  - Numeric range validation
  - Choice field validation
  - Pattern validation
- **Data Types**:
  - String validation
  - Number validation
  - Boolean validation
  - Date/datetime validation
  - JSON validation

#### Scenario: Cross-Field Validation Testing

**GIVEN** all serializers with cross-field validation
**WHEN** serializer tests are written
**THEN** tests MUST cover:
- **Field Dependencies**:
  - Conditional field requirements
  - Value-based field inclusion
  - Mutual exclusivity
- **Value Comparisons**:
  - Date range validation
  - Numeric comparisons
  - String length relationships
- **Business Rules**:
  - Answer-option matching (ChoiceProblem)
  - Time range validation (Exam)
  - Score distribution (FillBlankProblem)

#### Scenario: Serialization Testing

**GIVEN** all serializers
**WHEN** serialization tests are written
**THEN** tests MUST cover:
- **Basic Serialization**:
  - Object to data transformation
  - Field inclusion/exclusion
  - Null value handling
- **Nested Serialization**:
  - Object relationships
  - Depth control
  - Selective inclusion
  - Circular reference handling
- **Custom Serialization**:
  - to_representation methods
  - Computed properties
  - Data transformation
  - Format customization

#### Scenario: Error Message Testing

**GIVEN** all serializers
**WHEN** error testing is written
**THEN** tests MUST cover:
- **Error Formatting**:
  - Field-specific error messages
  - Non-field error messages
  - Validation code mapping
- **Error Structure**:
  - JSON error format consistency
  - Nested error handling
  - Error localization support
- **Edge Cases**:
  - Multiple validation errors
  - Partial validation failures
  - Constraint violation errors

## Success Metrics

1. All serializers have test coverage
2. Total test count ≥ 150
3. All field validations work correctly
4. All cross-field validations pass
5. All custom validation methods work
6. All nested serializers function properly
7. Error messages are properly formatted
8. Serialization performance is acceptable
9. Run `manage.py test courses.tests.test_serializers` with no failures

### Requirement: Serializer Tests Must Cover All Scenarios

Serializer tests MUST cover all possible scenarios including success cases, validation failures, and edge cases.

#### Scenario: Complete Scenario Coverage

**GIVEN** the serializer test suite
**WHEN** running tests
**THEN** all tests MUST cover:
- **Valid Input Scenarios**:
  - Minimal valid data
  - Maximum valid data
  - Typical production data
  - Boundary condition data
- **Invalid Input Scenarios**:
  - Missing required fields
  - Invalid data types
  - Out-of-range values
  - Constraint violations
  - Business rule violations
- **Edge Cases**:
  - Empty collections
  - Null values
  - Maximum values
  - Special characters
  - Unicode characters

#### Scenario: Performance Testing

**GIVEN** serializer performance concerns
**WHEN** performance tests are written
**THEN** tests MUST cover:
- **Serialization Performance**:
  - Large object serialization time
  - Deep nesting performance
  - Many relationship handling
- **Validation Performance**:
  - Complex validation rules performance
  - Large data validation time
  - Cross-field validation performance