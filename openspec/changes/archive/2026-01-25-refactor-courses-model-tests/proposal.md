# Add Comprehensive Model Tests for Courses App

## Summary

Add comprehensive test coverage for all 19 models in the `backend/courses` app. This proposal focuses exclusively on model behavior, field validations, relationships, and business logic methods, building upon the foundation established by the infrastructure proposal.

## Motivation

### Current State

The courses app has 19 models with complex business logic and validation rules, but currently has minimal model testing. Comprehensive model testing is essential for:

1. **Data Integrity**: Ensuring model constraints are properly enforced
2. **Business Logic**: Validating custom methods (e.g., `is_unlocked()` for ProblemUnlockCondition)
3. **Relationships**: Verifying foreign key and many-to-many relationships work correctly
4. **Edge Cases**: Testing boundary conditions and error scenarios
5. **Regression Prevention**: Catching model-related issues early

### Benefits

1. **Comprehensive Coverage**: 200+ test cases covering all models
2. **Data Validation**: Ensure field validations work correctly
3. **Relationship Testing**: Verify complex relationships (e.g., polymorphic Problem subclasses)
4. **Business Logic**: Test custom methods and computed properties
5. **Edge Cases**: Cover null values, empty collections, boundary values

## Proposed Changes

### 1. Create Model Test File

Create `test_models.py` with comprehensive tests for all 19 models organized by category:

**Core Content Models** (30 tests)
- `Course`: title validation, description, ordering, instructor relation
- `Chapter`: order uniqueness within course, cascade deletion, content handling
- `Problem`: type validation, difficulty range (1-3), chapter association

**Problem Type Models** (40 tests)
- `AlgorithmProblem`: time/memory limits, code templates, solution names
- `ChoiceProblem`: option format validation (A,B,C...), answer-option matching
- `FillBlankProblem`: blanks JSON format, case sensitivity, answer validation

**Unlock System** (20 tests)
- `ProblemUnlockCondition`: prerequisite dependencies, date-based unlocking, circular dependency detection

**Execution & Testing** (40 tests)
- `TestCase`: sample vs regular case distinction, input/output handling
- `Submission`: all status transitions (pending, judging, accepted, errors), null problem handling
- `CodeDraft`: save_type validation, user-problem uniqueness

**Learning Progress** (40 tests)
- `Enrollment`: duplicate prevention, cascade behavior
- `ChapterProgress`: status transitions (not_started → in_progress → completed)
- `ProblemProgress`: attempt counting, best submission logic, solved_at handling

**Discussion System** (20 tests)
- `DiscussionThread`: pinning, resolution, archiving, activity updates
- `DiscussionReply`: mention validation (@username), thread activity updates

**Exam System** (10 tests)
- `Exam`, `ExamProblem`, `ExamSubmission`, `ExamAnswer`: comprehensive coverage

### 2. Use Factory Boy for Test Data

Leverage the factories created in the infrastructure proposal for test data generation, with additional custom methods for complex scenarios.

### 3. Test Model Meta Options

Verify all Meta options:
- `ordering` fields
- `indexes` functionality
- `unique_together` constraints
- verbose_name and verbose_name_plural

### 4. Test Model Relationships

Verify:
- Foreign key cascade behavior
- Many-to-many relationships
- Related object access
- Reverse lookups

## Scope

### In Scope

- Comprehensive testing of all 19 courses models
- Field validation testing
- Model method testing
- Relationship testing
- Meta options testing
- Business logic method testing
- Edge case testing

### Out of Scope

- API endpoint testing (handled by separate proposal)
- View/ViewSet testing (handled by separate proposal)
- Service layer testing (handled by separate proposal)
- Signal handler testing (handled by separate proposal)
- Admin interface testing (handled by separate proposal)
- Serializer testing (handled by separate proposal)

## Success Criteria

1. All 19 models have test coverage
2. Total test count ≥ 200
3. All model fields are tested
4. All model methods are tested
5. All relationships are verified
6. All edge cases are covered
7. Run `manage.py test courses.tests.test_models` with no failures

## Dependencies

- `refactor-courses-infrastructure` - Required for factories and base test case
- `factory-boy` package (already installed)

## Test Case Categories

### Field Validation Tests (60 tests)
- Required fields
- Field length constraints
- Numeric field ranges (difficulty 1-3)
- Date field validation
- JSON field validation
- File field validation

### Model Method Tests (40 tests)
- `__str__` method
- Custom business logic methods
- Computed properties
- Static/class methods
- Model managers

### Relationship Tests (60 tests)
- Foreign key creation
- Many-to-many creation
- Related object access
- Reverse lookup methods
- Cascade deletion behavior

### Edge Case Tests (40 tests)
- Null values handling
- Empty collections
- Maximum values
- Minimum values
- Invalid input handling

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Complex business logic hard to test | Create helper methods in base test case for common scenarios |
- Model interactions too complex to test | Test models independently first, then integration scenarios |
- Test flakiness due to data dependencies | Use factory_boy with `django_get_or_create` where appropriate |

## Related Specifications

- Extends `backend-testing` specification
- Depends on `refactor-courses-infrastructure`
- Future proposal: `add-courses-relationship-tests` for complex relationship scenarios
