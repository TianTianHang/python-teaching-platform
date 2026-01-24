# Tasks: Add Comprehensive Model Tests for Courses App

This document outlines the step-by-step implementation tasks for adding comprehensive model test coverage to the `courses` app.

## Phase 1: Core Content Models

### Task 1.1: Test Course Model

**Description**: Create comprehensive tests for the Course model.

**Steps**:
1. Create test class `CourseModelTestCase` in `test_models.py`
2. Test `__str__` method returns title
3. Test field validations:
   - Title max length
   - Description optional field
   - Ordering field default value
4. Test instructor relationship (Foreign Key to User)
5. Test Meta options (ordering, verbose_name)

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
1. Create test class `ChapterModelTestCase` in `test_models.py`
2. Test `__str__` method returns course + chapter title
3. Test order uniqueness within course
4. Test field validations:
   - Title max length
   - Content optional field
   - Order field required
5. Test course relationship (Foreign Key)
6. Test cascade deletion (when Course deleted)
7. Test Meta options (ordering, unique_together)

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
1. Create test class `ProblemModelTestCase` in `test_models.py`
2. Test `__str__` method returns title
3. Test type field validation (algorithm, choice, fillblank)
4. Test difficulty range validation (1-3)
5. Test chapter relationship (Foreign Key)
6. Test polymorphic relationship to problem type models
7. Test Meta options (ordering, verbose_name)

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
1. Create test class `AlgorithmProblemModelTestCase` in `test_models.py`
2. Test time_limit field (positive integers)
3. Test memory_limit field (positive integers)
4. Test code_template field (optional)
5. Test solution_name field (optional)
6. Test test_cases JSON field:
   - Valid JSON format
   - Empty array handling
   - Sample case distinction
7. Test one-to-one relationship with Problem

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
1. Create test class `ChoiceProblemModelTestCase` in `test_models.py`
2. Test options JSON field:
   - Valid format: [{"A": "option1"}, {"B": "option2"}]
   - Minimum option count (2)
   - Maximum option count (26 for A-Z)
3. Test answer field validation:
   - Answer must be in options
   - Single choice: one letter
   - Multiple choice: comma-separated letters
4. Test is_multiple field (boolean)
5. Test one-to-one relationship with Problem

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
1. Create test class `FillBlankProblemModelTestCase` in `test_models.py`
2. Test blanks JSON field:
   - Multiple supported formats
   - Blank count calculation
3. Test answer field:
   - JSON format validation
   - Array of answers
4. Test case_sensitive field (boolean)
5. Test score_distribution JSON field:
   - Valid score array
   - Total equals blank count
6. Test one-to-one relationship with Problem

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
1. Create test class `ProblemUnlockConditionModelTestCase` in `test_models.py`
2. Test prerequisite relationship (to Problem)
3. Test problem relationship (to unlock)
4. Test unlock_type field (date, progress, custom)
5. Test unlock_date field (optional)
6. Test `is_unlocked()` method:
   - Prerequisite solved condition
   - Date-based condition
   - Custom condition
7. Test circular dependency detection

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
1. Create test class `TestCaseModelTestCase` in `test_models.py`
2. Test is_sample field (boolean)
3. Test input field (required)
4. Test output field (required)
5. Test problem relationship (Foreign Key)
6. Test sample vs regular case distinction
7. Test Meta options (ordering)

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
1. Create test class `SubmissionModelTestCase` in `test_models.py`
2. Test status field transitions:
   - pending → judging
   - judging → accepted
   - judging → wrong_answer
   - judging → time_limit_exceeded
   - judging → memory_limit_exceeded
   - judging → compilation_error
   - judging → runtime_error
3. Test null problem handling (free code)
4. Test code field (required)
5. Test language field (required)
6. Test time_used field (optional)
7. Test memory_used field (optional)
8. Test user relationship (Foreign Key)
9. Test problem relationship (Foreign Key, nullable)

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
1. Create test class `CodeDraftModelTestCase` in `test_models.py`
2. Test save_type field (manual, auto_submit)
3. Test code field (required)
4. Test user relationship (Foreign Key)
5. Test problem relationship (Foreign Key)
6. Test submission relationship (Foreign Key, nullable)
7. Test unique_together constraint (user, problem)

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
1. Create test class `EnrollmentModelTestCase` in `test_models.py`
2. Test user relationship (Foreign Key)
3. Test course relationship (Foreign Key)
4. Test enrolled_at field (auto_now_add)
5. Test unique_together constraint (user, course)
6. Test duplicate prevention

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
1. Create test class `ChapterProgressModelTestCase` in `test_models.py`
2. Test status field transitions:
   - not_started → in_progress
   - in_progress → completed
3. Test completed_at field (optional)
4. Test user relationship (Foreign Key)
5. Test chapter relationship (Foreign Key)
6. Test unique_together constraint (user, chapter)

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
1. Create test class `ProblemProgressModelTestCase` in `test_models.py`
2. Test status field transitions:
   - not_started → in_progress
   - in_progress → completed
3. Test attempt_count field (default 0)
4. Test best_submission relationship (Foreign Key, nullable)
5. Test solved_at field (optional)
6. Test performance_metrics JSON field
7. Test user relationship (Foreign Key)
8. Test problem relationship (Foreign Key)
9. Test unique_together constraint (user, problem)

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
1. Create test class `DiscussionThreadModelTestCase` in `test_models.py`
2. Test title field (required)
3. Test content field (required)
4. Test is_pinned field (boolean)
5. Test is_resolved field (boolean)
6. Test is_archived field (boolean)
7. Test last_activity_at field (auto-update)
8. Test user relationship (Foreign Key)
9. Test course relationship (Foreign Key, nullable)
10. Test chapter relationship (Foreign Key, nullable)
11. Test problem relationship (Foreign Key, nullable)

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
1. Create test class `DiscussionReplyModelTestCase` in `test_models.py`
2. Test content field (required)
3. Test mention validation (@username format)
4. Test created_at field (auto_now_add)
5. Test user relationship (Foreign Key)
6. Test thread relationship (Foreign Key)
7. Test author-only modification logic

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
1. Create test class `ExamModelTestCase` in `test_models.py`
2. Test start_time < end_time validation
3. Test status field transitions
4. Test passing_score field
5. Test shuffle_questions field

6. Create test class `ExamProblemModelTestCase`
7. Test score validation (must be > 0)
8. Test order field
9. Test unique_together (exam, problem)

10. Create test class `ExamSubmissionModelTestCase`
11. Test time limit calculation
12. Test status transitions
13. Test one-submission enforcement

14. Create test class `ExamAnswerModelTestCase`
15. Test answer type validation
16. Test score calculation (percentage-based)
17. Test correct answer display logic

**Validation**:
- Time validation is enforced
- Score calculations are correct
- Run `manage.py test courses.tests.test_models.ExamModelTestCase`

**Estimated Effort**: Large

**Dependencies**: `refactor-courses-infrastructure`

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 1.1 | Test Course model | Small | infrastructure |
| 1.2 | Test Chapter model | Medium | infrastructure |
| 1.3 | Test Problem model | Medium | infrastructure |
| 2.1 | Test AlgorithmProblem model | Medium | infrastructure |
| 2.2 | Test ChoiceProblem model | Medium | infrastructure |
| 2.3 | Test FillBlankProblem model | Medium | infrastructure |
| 3.1 | Test ProblemUnlockCondition model | Large | infrastructure |
| 4.1 | Test TestCase model | Small | infrastructure |
| 4.2 | Test Submission model | Large | infrastructure |
| 4.3 | Test CodeDraft model | Medium | infrastructure |
| 5.1 | Test Enrollment model | Medium | infrastructure |
| 5.2 | Test ChapterProgress model | Medium | infrastructure |
| 5.3 | Test ProblemProgress model | Large | infrastructure |
| 6.1 | Test DiscussionThread model | Medium | infrastructure |
| 6.2 | Test DiscussionReply model | Medium | infrastructure |
| 7.1 | Test Exam models | Large | infrastructure |

## Parallelization Opportunities

- **Tasks 1.1-1.3** (Core Models) can be developed in parallel
- **Tasks 2.1-2.3** (Problem Types) can be developed in parallel
- **Tasks 4.1-4.3**, **5.1-5.3**, **6.1-6.2** can each be developed in parallel groups
- All tasks depend on `refactor-courses-infrastructure` being complete
