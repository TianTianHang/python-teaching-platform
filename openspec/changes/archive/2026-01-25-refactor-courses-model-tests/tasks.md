# Tasks: Add Comprehensive Model Tests for Courses App

This document outlines the step-by-step implementation tasks for adding comprehensive model test coverage to the `courses` app.

## Phase 1: Core Content Models

### Task 1.1: Test Course Model

**Description**: Create comprehensive tests for the Course model.

**Steps**:
- [x] Create test class `CourseModelTestCase` in `test_models.py`
- [x] Test `__str__` method returns title
- [x] Test field validations:
   - [x] Title max length
   - [x] Description optional field
   - [x] Ordering field default value
- [x] Test instructor relationship (Foreign Key to User)
- [x] Test Meta options (ordering, verbose_name)

**Validation**:
- All Course field validations are tested
- Relationship to User is verified
- Run `manage.py test courses.tests.test_models.CourseModelTestCase`

**Estimated Effort**: Small

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 1.2: Test Chapter Model

**Description**: Create comprehensive tests for the Chapter model.

**Steps**:
- [x] Create test class `ChapterModelTestCase` in `test_models.py`
- [x] Test `__str__` method returns course + chapter title
- [x] Test order uniqueness within course
- [x] Test field validations:
   - [x] Title max length
   - [x] Content optional field
   - [x] Order field required
- [x] Test course relationship (Foreign Key)
- [x] Test cascade deletion (when Course deleted)
- [x] Test Meta options (ordering, unique_together)

**Validation**:
- Order uniqueness constraint is enforced
- Cascade deletion works correctly
- Run `manage.py test courses.tests.test_models.ChapterModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 1.3: Test Problem Model

**Description**: Create comprehensive tests for the Problem model.

**Steps**:
- [x] Create test class `ProblemModelTestCase` in `test_models.py`
- [x] Test `__str__` method returns title
- [x] Test type field validation (algorithm, choice, fillblank)
- [x] Test difficulty range validation (1-3)
- [x] Test chapter relationship (Foreign Key)
- [x] Test polymorphic relationship to problem type models
- [x] Test Meta options (ordering, verbose_name)

**Validation**:
- Type field accepts only valid values
- Difficulty field enforces 1-3 range
- Polymorphic relationship works
- Run `manage.py test courses.tests.test_models.ProblemModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 2: Problem Type Models

### Task 2.1: Test AlgorithmProblem Model

**Description**: Create comprehensive tests for the AlgorithmProblem model.

**Steps**:
- [x] Create test class `AlgorithmProblemModelTestCase` in `test_models.py`
- [x] Test time_limit field (positive integers)
- [x] Test memory_limit field (positive integers)
- [x] Test code_template field (optional)
- [x] Test solution_name field (optional)
- [x] Test test_cases JSON field:
   - [x] Valid JSON format
   - [x] Empty array handling
   - [x] Sample case distinction
- [x] Test one-to-one relationship with Problem

**Validation**:
- Time and memory limits enforce positive values
- test_cases accepts valid JSON
- Run `manage.py test courses.tests.test_models.AlgorithmProblemModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 2.2: Test ChoiceProblem Model

**Description**: Create comprehensive tests for the ChoiceProblem model.

**Steps**:
- [x] Create test class `ChoiceProblemModelTestCase` in `test_models.py`
- [x] Test options JSON field:
   - [x] Valid format: [{"A": "option1"}, {"B": "option2"}]
   - [x] Minimum option count (2)
   - [x] Maximum option count (26 for A-Z)
- [x] Test answer field validation:
   - [x] Answer must be in options
   - [x] Single choice: one letter
   - [x] Multiple choice: comma-separated letters
- [x] Test is_multiple field (boolean)
- [x] Test one-to-one relationship with Problem

**Validation**:
- Options format is validated
- Answer-option matching is enforced
- Run `manage.py test courses.tests.test_models.ChoiceProblemModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 2.3: Test FillBlankProblem Model

**Description**: Create comprehensive tests for the FillBlankProblem model.

**Steps**:
- [x] Create test class `FillBlankProblemModelTestCase` in `test_models.py`
- [x] Test blanks JSON field:
   - [x] Multiple supported formats
   - [x] Blank count calculation
- [x] Test answer field:
   - [x] JSON format validation
   - [x] Array of answers
- [x] Test case_sensitive field (boolean)
- [x] Test score_distribution JSON field:
   - [x] Valid score array
   - [x] Total equals blank count
- [x] Test one-to-one relationship with Problem

**Validation**:
- Multiple JSON formats are supported
- Score distribution matches blank count
- Run `manage.py test courses.tests.test_models.FillBlankProblemModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 3: Unlock System

### Task 3.1: Test ProblemUnlockCondition Model

**Description**: Create comprehensive tests for the ProblemUnlockCondition model.

**Steps**:
- [x] Create test class `ProblemUnlockConditionModelTestCase` in `test_models.py`
- [x] Test prerequisite relationship (to Problem)
- [x] Test problem relationship (to unlock)
- [x] Test unlock_type field (date, progress, custom)
- [x] Test unlock_date field (optional)
- [x] Test `is_unlocked()` method:
   - [x] Prerequisite solved condition
   - [x] Date-based condition
   - [x] Custom condition
- [x] Test circular dependency detection

**Validation**:
- Prerequisite logic works correctly
- Date-based unlocking functions
- Circular dependencies are detected
- Run `manage.py test courses.tests.test_models.ProblemUnlockConditionModelTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 4: Execution & Testing

### Task 4.1: Test TestCase Model

**Description**: Create comprehensive tests for the TestCase model.

**Steps**:
- [x] Create test class `TestCaseModelTestCase` in `test_models.py`
- [x] Test is_sample field (boolean)
- [x] Test input field (required)
- [x] Test output field (required)
- [x] Test problem relationship (Foreign Key)
- [x] Test sample vs regular case distinction
- [x] Test Meta options (ordering)

**Validation**:
- is_sample distinguishes sample cases
- Input/output fields are required
- Run `manage.py test courses.tests.test_models.TestCaseModelTestCase`

**Estimated Effort**: Small

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 4.2: Test Submission Model

**Description**: Create comprehensive tests for the Submission model.

**Steps**:
- [x] Create test class `SubmissionModelTestCase` in `test_models.py`
- [x] Test status field transitions:
   - [x] pending → judging
   - [x] judging → accepted
   - [x] judging → wrong_answer
   - [x] judging → time_limit_exceeded
   - [x] judging → memory_limit_exceeded
   - [x] judging → compilation_error
   - [x] judging → runtime_error
- [x] Test null problem handling (free code)
- [x] Test code field (required)
- [x] Test language field (required)
- [x] Test time_used field (optional)
- [x] Test memory_used field (optional)
- [x] Test user relationship (Foreign Key)
- [x] Test problem relationship (Foreign Key, nullable)

**Validation**:
- All status transitions work
- Null problem is handled correctly
- Run `manage.py test courses.tests.test_models.SubmissionModelTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 4.3: Test CodeDraft Model

**Description**: Create comprehensive tests for the CodeDraft model.

**Steps**:
- [x] Create test class `CodeDraftModelTestCase` in `test_models.py`
- [x] Test save_type field (manual, auto_submit)
- [x] Test code field (required)
- [x] Test user relationship (Foreign Key)
- [x] Test problem relationship (Foreign Key)
- [x] Test submission relationship (Foreign Key, nullable)
- [x] Test unique_together constraint (user, problem)

**Validation**:
- save_type accepts valid values
- User-problem uniqueness is enforced
- Run `manage.py test courses.tests.test_models.CodeDraftModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 5: Learning Progress

### Task 5.1: Test Enrollment Model

**Description**: Create comprehensive tests for the Enrollment model.

**Steps**:
- [x] Create test class `EnrollmentModelTestCase` in `test_models.py`
- [x] Test user relationship (Foreign Key)
- [x] Test course relationship (Foreign Key)
- [x] Test enrolled_at field (auto_now_add)
- [x] Test unique_together constraint (user, course)
- [x] Test duplicate prevention

**Validation**:
- Duplicate enrollment is prevented
- enrolled_at is auto-set
- Run `manage.py test courses.tests.test_models.EnrollmentModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 5.2: Test ChapterProgress Model

**Description**: Create comprehensive tests for the ChapterProgress model.

**Steps**:
- [x] Create test class `ChapterProgressModelTestCase` in `test_models.py`
- [x] Test status field transitions:
   - [x] not_started → in_progress
   - [x] in_progress → completed
- [x] Test completed_at field (optional)
- [x] Test user relationship (Foreign Key)
- [x] Test chapter relationship (Foreign Key)
- [x] Test unique_together constraint (user, chapter)

**Validation**:
- Status transitions are enforced
- completed_at is set when status=completed
- Run `manage.py test courses.tests.test_models.ChapterProgressModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 5.3: Test ProblemProgress Model

**Description**: Create comprehensive tests for the ProblemProgress model.

**Steps**:
- [x] Create test class `ProblemProgressModelTestCase` in `test_models.py`
- [x] Test status field transitions:
   - [x] not_started → in_progress
   - [x] in_progress → completed
- [x] Test attempt_count field (default 0)
- [x] Test best_submission relationship (Foreign Key, nullable)
- [x] Test solved_at field (optional)
- [x] Test performance_metrics JSON field
- [x] Test user relationship (Foreign Key)
- [x] Test problem relationship (Foreign Key)
- [x] Test unique_together constraint (user, problem)

**Validation**:
- Status transitions work correctly
- attempt_count increments properly
- best_submission logic works
- Run `manage.py test courses.tests.test_models.ProblemProgressModelTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 6: Discussion System

### Task 6.1: Test DiscussionThread Model

**Description**: Create comprehensive tests for the DiscussionThread model.

**Steps**:
- [x] Create test class `DiscussionThreadModelTestCase` in `test_models.py`
- [x] Test title field (required)
- [x] Test content field (required)
- [x] Test is_pinned field (boolean)
- [x] Test is_resolved field (boolean)
- [x] Test is_archived field (boolean)
- [x] Test last_activity_at field (auto-update)
- [x] Test user relationship (Foreign Key)
- [x] Test course relationship (Foreign Key, nullable)
- [x] Test chapter relationship (Foreign Key, nullable)
- [x] Test problem relationship (Foreign Key, nullable)

**Validation**:
- last_activity_at updates on new replies
- Pinned/resolved/archived flags work
- Run `manage.py test courses.tests.test_models.DiscussionThreadModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

### Task 6.2: Test DiscussionReply Model

**Description**: Create comprehensive tests for the DiscussionReply model.

**Steps**:
- [x] Create test class `DiscussionReplyModelTestCase` in `test_models.py`
- [x] Test content field (required)
- [x] Test mention validation (@username format)
- [x] Test created_at field (auto_now_add)
- [x] Test user relationship (Foreign Key)
- [x] Test thread relationship (Foreign Key)
- [x] Test author-only modification logic

**Validation**:
- Mention format is validated
- Thread activity is updated
- Run `manage.py test courses.tests.test_models.DiscussionReplyModelTestCase`

**Estimated Effort**: Medium

**Dependencies**: `refactor-courses-infrastructure`

---

## Phase 7: Exam System

### Task 7.1: Test Exam Models

**Description**: Create comprehensive tests for Exam, ExamProblem, ExamSubmission, and ExamAnswer models.

**Steps**:
- [x] Create test class `ExamModelTestCase` in `test_models.py`
- [x] Test start_time < end_time validation
- [x] Test status field transitions
- [x] Test passing_score field
- [x] Test shuffle_questions field

- [x] Create test class `ExamProblemModelTestCase`
- [x] Test score validation (must be > 0)
- [x] Test order field
- [x] Test unique_together (exam, problem)

- [x] Create test class `ExamSubmissionModelTestCase`
- [x] Test time limit calculation
- [x] Test status transitions
- [x] Test one-submission enforcement

- [x] Create test class `ExamAnswerModelTestCase`
- [x] Test answer type validation
- [x] Test score calculation (percentage-based)
- [x] Test correct answer display logic

**Validation**:
- Time validation is enforced
- Score calculations are correct
- Run `manage.py test courses.tests.test_models.ExamModelTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Task Summary

| Task | Description | Effort | Dependencies | Status |
|------|-------------|--------|--------------|--------|
| 1.1 | Test Course model | Small | infrastructure | [✓] Completed |
| 1.2 | Test Chapter model | Medium | infrastructure | [✓] Completed |
| 1.3 | Test Problem model | Medium | infrastructure | [✓] Completed |
| 2.1 | Test AlgorithmProblem model | Medium | infrastructure | [✓] Completed |
| 2.2 | Test ChoiceProblem model | Medium | infrastructure | [✓] Completed |
| 2.3 | Test FillBlankProblem model | Medium | infrastructure | [✓] Completed |
| 3.1 | Test ProblemUnlockCondition model | Large | infrastructure | [✓] Completed |
| 4.1 | Test TestCase model | Small | infrastructure | [✓] Completed |
| 4.2 | Test Submission model | Large | infrastructure | [✓] Completed |
| 4.3 | Test CodeDraft model | Medium | infrastructure | [✓] Completed |
| 5.1 | Test Enrollment model | Medium | infrastructure | [✓] Completed |
| 5.2 | Test ChapterProgress model | Medium | infrastructure | [✓] Completed |
| 5.3 | Test ProblemProgress model | Large | infrastructure | [✓] Completed |
| 6.1 | Test DiscussionThread model | Medium | infrastructure | [✓] Completed |
| 6.2 | Test DiscussionReply model | Medium | infrastructure | [✓] Completed |
| 7.1 | Test Exam models | Large | infrastructure | [✓] Completed |

## Final Result

**All 225 tests across 16 test classes have been implemented and are passing.**

✓ **Total test cases**: 225
✓ **Coverage**: 19 models
✓ **Status**: All tests passing

## Parallelization Opportunities

- **Tasks 1.1-1.3** (Core Models) can be developed in parallel
- **Tasks 2.1-2.3** (Problem Types) can be developed in parallel
- **Tasks 4.1-4.3**, **5.1-5.3**, **6.1-6.2** can each be developed in parallel groups
- All tasks depend on `refactor-courses-infrastructure` being complete
