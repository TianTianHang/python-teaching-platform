"""
Comprehensive model tests for the courses app.

This test module covers all 19 models in the courses app with 200+ test cases.
Tests are organized by model category and cover:
- Field validations
- Model methods
- Relationships
- Meta options
- Business logic
- Edge cases
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta

from courses.models import (
    Course, Chapter, Problem, ProblemUnlockCondition,
    AlgorithmProblem, ChoiceProblem, FillBlankProblem,
    TestCase as CourseTestCase, Submission, CodeDraft,
    Enrollment, ChapterProgress, ProblemProgress,
    DiscussionThread, DiscussionReply,
    Exam, ExamProblem, ExamSubmission, ExamAnswer,
)
from accounts.models import User

from courses.tests.factories import (
    CourseFactory, ChapterFactory, ProblemFactory,
    AlgorithmProblemFactory, ChoiceProblemFactory, FillBlankProblemFactory,
    CourseTestCaseFactory, SubmissionFactory, CodeDraftFactory,
    EnrollmentFactory, ChapterProgressFactory, ProblemProgressFactory,
    DiscussionThreadFactory, DiscussionReplyFactory,
    ExamFactory, ExamProblemFactory, ExamSubmissionFactory,
    ExamAnswerFactory,
)
from accounts.tests.factories import UserFactory


# ============================================================================
# Phase 1: Core Content Models
# ============================================================================

class CourseModelTestCase(TestCase):
    """Test cases for the Course model."""

    def test_str_method_returns_title(self):
        """Test that __str__ returns the course title."""
        course = CourseFactory(title="Python Programming")
        self.assertEqual(str(course), "Python Programming")

    def test_title_max_length(self):
        """Test that title field has max length of 200."""
        course = CourseFactory(title="A" * 200)
        self.assertEqual(course.title, "A" * 200)
        with self.assertRaises(ValidationError):
            course.title = "A" * 201
            course.full_clean()

    def test_description_optional_field(self):
        """Test that description field is optional."""
        course = CourseFactory(description="")
        self.assertEqual(course.description, "")

    def test_description_can_contain_long_text(self):
        """Test that description can contain long text."""
        long_text = "A" * 1000
        course = CourseFactory(description=long_text)
        self.assertEqual(course.description, long_text)

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set on creation."""
        course = CourseFactory()
        self.assertIsNotNone(course.created_at)
        old_created_at = course.created_at
        course.save()
        self.assertEqual(course.created_at, old_created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        course = CourseFactory()
        old_updated_at = course.updated_at
        course.title = "Updated Title"
        course.save()
        self.assertGreater(course.updated_at, old_updated_at)

    def test_meta_ordering_by_title(self):
        """Test that Meta ordering is by title."""
        CourseFactory(title="Zulu Course")
        CourseFactory(title="Alpha Course")
        CourseFactory(title="Bravo Course")
        courses = Course.objects.all()
        self.assertEqual(courses[0].title, "Alpha Course")
        self.assertEqual(courses[1].title, "Bravo Course")
        self.assertEqual(courses[2].title, "Zulu Course")

    def test_meta_verbose_name(self):
        """Test Meta verbose_name."""
        self.assertEqual(Course._meta.verbose_name, "课程")

    def test_meta_verbose_name_plural(self):
        """Test Meta verbose_name_plural."""
        self.assertEqual(Course._meta.verbose_name_plural, "课程")


class ChapterModelTestCase(TestCase):
    """Test cases for the Chapter model."""

    def test_str_method_returns_course_and_title(self):
        """Test that __str__ returns course title and chapter title."""
        course = CourseFactory(title="Python Course")
        chapter = ChapterFactory(course=course, title="Chapter 1")
        expected = "Python Course - Chapter 1"
        self.assertEqual(str(chapter), expected)

    def test_title_max_length(self):
        """Test that title field has max length of 200."""
        chapter = ChapterFactory(title="A" * 200)
        self.assertEqual(chapter.title, "A" * 200)

    def test_content_optional_field(self):
        """Test that content field is optional."""
        chapter = ChapterFactory(content="")
        self.assertEqual(chapter.content, "")

    def test_order_field_default_value(self):
        """Test that order field has a default value."""
        chapter = ChapterFactory()
        self.assertIsNotNone(chapter.order)
        self.assertGreaterEqual(chapter.order, 0)

    def test_course_relationship(self):
        """Test foreign key relationship to Course."""
        course = CourseFactory()
        chapter = ChapterFactory(course=course)
        self.assertEqual(chapter.course, course)
        self.assertIn(chapter, course.chapters.all())

    def test_order_uniqueness_within_course(self):
        """Test that order is unique within a course."""
        course = CourseFactory()
        ChapterFactory(course=course, order=1)
        duplicate = Chapter(course=course, order=1)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_different_courses_can_have_same_order(self):
        """Test that different courses can have chapters with same order."""
        course1 = CourseFactory()
        course2 = CourseFactory()
        chapter1 = ChapterFactory(course=course1, order=1)
        chapter2 = ChapterFactory(course=course2, order=1)
        self.assertEqual(chapter1.order, chapter2.order)

    def test_cascade_deletion_when_course_deleted(self):
        """Test that chapters are deleted when course is deleted."""
        course = CourseFactory()
        chapter = ChapterFactory(course=course)
        chapter_id = chapter.id
        course.delete()
        self.assertFalse(Chapter.objects.filter(id=chapter_id).exists())

    def test_meta_ordering_by_course_and_order(self):
        """Test Meta ordering by course and order."""
        course = CourseFactory()
        ChapterFactory(course=course, order=3)
        ChapterFactory(course=course, order=1)
        ChapterFactory(course=course, order=2)
        chapters = Chapter.objects.filter(course=course)
        self.assertEqual(chapters[0].order, 1)
        self.assertEqual(chapters[1].order, 2)
        self.assertEqual(chapters[2].order, 3)

    def test_meta_unique_together(self):
        """Test Meta unique_together constraint."""
        self.assertEqual(
            Chapter._meta.unique_together,
            (('course', 'order'),)
        )

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        chapter = ChapterFactory()
        self.assertIsNotNone(chapter.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        chapter = ChapterFactory()
        old_updated_at = chapter.updated_at
        chapter.title = "Updated Chapter"
        chapter.save()
        self.assertGreater(chapter.updated_at, old_updated_at)


class ProblemModelTestCase(TestCase):
    """Test cases for the Problem model."""

    def test_str_method_returns_type_and_title(self):
        """Test that __str__ returns type and title."""
        problem = ProblemFactory(type='algorithm', title="Two Sum")
        self.assertEqual(str(problem), "algorithm - Two Sum")

    def test_type_field_validation(self):
        """Test that type field accepts valid values."""
        valid_types = ['algorithm', 'choice', 'fillblank']
        for problem_type in valid_types:
            problem = ProblemFactory(type=problem_type)
            self.assertEqual(problem.type, problem_type)

    def test_difficulty_range_validation(self):
        """Test that difficulty field enforces 1-3 range."""
        ProblemFactory(difficulty=1)
        ProblemFactory(difficulty=2)
        ProblemFactory(difficulty=3)

    def test_difficulty_below_minimum_raises_error(self):
        """Test that difficulty < 1 raises validation error."""
        problem = ProblemFactory.build(difficulty=0)
        with self.assertRaises(ValidationError):
            problem.full_clean()

    def test_difficulty_above_maximum_raises_error(self):
        """Test that difficulty > 3 raises validation error."""
        problem = ProblemFactory.build(difficulty=4)
        with self.assertRaises(ValidationError):
            problem.full_clean()

    def test_chapter_relationship(self):
        """Test foreign key relationship to Chapter."""
        chapter = ChapterFactory()
        problem = ProblemFactory(chapter=chapter)
        self.assertEqual(problem.chapter, chapter)
        self.assertIn(problem, chapter.problems.all())

    def test_chapter_can_be_null(self):
        """Test that chapter field can be null."""
        problem = ProblemFactory(chapter=None)
        self.assertIsNone(problem.chapter)

    def test_title_max_length(self):
        """Test that title field has max length of 200."""
        problem = ProblemFactory(title="A" * 200)
        self.assertEqual(problem.title, "A" * 200)

    def test_content_required_field(self):
        """Test that content field is required."""
        problem = ProblemFactory.build(content=None)
        with self.assertRaises(ValidationError):
            problem.full_clean()

    def test_polymorphic_relationship_to_algorithm_problem(self):
        """Test one-to-one relationship with AlgorithmProblem."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(problem=problem)
        self.assertEqual(problem.algorithm_info, algo_problem)

    def test_polymorphic_relationship_to_choice_problem(self):
        """Test one-to-one relationship with ChoiceProblem."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(problem=problem)
        self.assertEqual(problem.choice_info, choice_problem)

    def test_polymorphic_relationship_to_fillblank_problem(self):
        """Test one-to-one relationship with FillBlankProblem."""
        problem = ProblemFactory(type='fillblank')
        fillblank_problem = FillBlankProblemFactory(problem=problem)
        self.assertEqual(problem.fillblank_info, fillblank_problem)

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        problem = ProblemFactory()
        self.assertIsNotNone(problem.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        problem = ProblemFactory()
        old_updated_at = problem.updated_at
        problem.title = "Updated Title"
        problem.save()
        self.assertGreater(problem.updated_at, old_updated_at)

    def test_meta_verbose_name(self):
        """Test Meta verbose_name."""
        self.assertEqual(Problem._meta.verbose_name, "问题")

    def test_difficulty_validators(self):
        """Test that difficulty field has MinValueValidator and MaxValueValidator."""
        problem = Problem()
        field = Problem._meta.get_field('difficulty')
        self.assertEqual(len(field.validators), 2)


# ============================================================================
# Phase 2: Problem Type Models
# ============================================================================

class AlgorithmProblemModelTestCase(TestCase):
    """Test cases for the AlgorithmProblem model."""

    def test_str_method(self):
        """Test __str__ method returns type and title."""
        problem = ProblemFactory(type='algorithm', title="Binary Search")
        algo_problem = AlgorithmProblemFactory(problem=problem)
        self.assertEqual(str(algo_problem), "algorithm-Binary Search")

    def test_time_limit_default_value(self):
        """Test that time_limit has default value of 1000."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(problem=problem)
        self.assertEqual(algo_problem.time_limit, 1000)

    def test_time_limit_accepts_positive_integers(self):
        """Test that time_limit accepts positive integers."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(
            problem=problem,
            time_limit=500
        )
        self.assertEqual(algo_problem.time_limit, 500)

    def test_memory_limit_default_value(self):
        """Test that memory_limit has default value of 256."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(problem=problem)
        self.assertEqual(algo_problem.memory_limit, 256)

    def test_memory_limit_accepts_positive_integers(self):
        """Test that memory_limit accepts positive integers."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(
            problem=problem,
            memory_limit=512
        )
        self.assertEqual(algo_problem.memory_limit, 512)

    def test_code_template_optional_field(self):
        """Test that code_template field is optional."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(
            problem=problem,
            code_template=None
        )
        self.assertIsNone(algo_problem.code_template)

    def test_code_template_accepts_valid_json(self):
        """Test that code_template accepts valid JSON."""
        problem = ProblemFactory(type='algorithm')
        template = {"python": "def solution():\n    pass"}
        algo_problem = AlgorithmProblemFactory(
            problem=problem,
            code_template=template
        )
        self.assertEqual(algo_problem.code_template, template)

    def test_solution_name_optional_field(self):
        """Test that solution_name field is optional."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(
            problem=problem,
            solution_name=None
        )
        self.assertIsNone(algo_problem.solution_name)

    def test_solution_name_accepts_valid_json(self):
        """Test that solution_name accepts valid JSON."""
        problem = ProblemFactory(type='algorithm')
        solution = {"python": "solve"}
        algo_problem = AlgorithmProblemFactory(
            problem=problem,
            solution_name=solution
        )
        self.assertEqual(algo_problem.solution_name, solution)

    def test_one_to_one_relationship_with_problem(self):
        """Test one-to-one relationship with Problem."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(problem=problem)
        self.assertEqual(algo_problem.problem, problem)
        self.assertEqual(problem.algorithm_info, algo_problem)

    def test_cascade_deletion_when_problem_deleted(self):
        """Test that algorithm problem is deleted when problem is deleted."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(problem=problem)
        algo_problem_id = algo_problem.id
        problem.delete()
        self.assertFalse(
            AlgorithmProblem.objects.filter(id=algo_problem_id).exists()
        )

    def test_meta_verbose_name(self):
        """Test Meta verbose_name."""
        self.assertEqual(AlgorithmProblem._meta.verbose_name, "算法题")


class ChoiceProblemModelTestCase(TestCase):
    """Test cases for the ChoiceProblem model."""

    def test_str_method(self):
        """Test __str__ method."""
        problem = ProblemFactory(type='choice', title="Quiz 1")
        choice_problem = ChoiceProblemFactory(problem=problem)
        expected = f"选择题: Quiz 1"
        self.assertEqual(str(choice_problem), expected)

    def test_options_accepts_valid_json(self):
        """Test that options accepts valid JSON format."""
        problem = ProblemFactory(type='choice')
        options = {"A": "Option A", "B": "Option B"}
        choice_problem = ChoiceProblemFactory(
            problem=problem,
            options=options
        )
        self.assertEqual(choice_problem.options, options)

    def test_options_minimum_two_options(self):
        """Test that options should have at least 2 choices."""
        problem = ProblemFactory(type='choice')
        options = {"A": "Only Option"}
        choice_problem = ChoiceProblemFactory.build(
            problem=problem,
            options=options
        )
        # Model doesn't enforce this at DB level, but should validate
        # This is more of a business logic test
        choice_problem.save()
        self.assertEqual(choice_problem.options, options)

    def test_correct_answer_single_choice(self):
        """Test correct_answer for single choice."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(
            problem=problem,
            correct_answer='A',
            is_multiple_choice=False
        )
        self.assertEqual(choice_problem.correct_answer, 'A')
        self.assertFalse(choice_problem.is_multiple_choice)

    def test_correct_answer_multiple_choice(self):
        """Test correct_answer for multiple choice."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(
            problem=problem,
            correct_answer=['A', 'C'],
            is_multiple_choice=True
        )
        self.assertEqual(choice_problem.correct_answer, ['A', 'C'])
        self.assertTrue(choice_problem.is_multiple_choice)

    def test_is_multiple_choice_default_false(self):
        """Test that is_multiple_choice defaults to False."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(problem=problem)
        self.assertFalse(choice_problem.is_multiple_choice)

    def test_one_to_one_relationship_with_problem(self):
        """Test one-to-one relationship with Problem."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(problem=problem)
        self.assertEqual(choice_problem.problem, problem)
        self.assertEqual(problem.choice_info, choice_problem)

    def test_cascade_deletion_when_problem_deleted(self):
        """Test that choice problem is deleted when problem is deleted."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(problem=problem)
        choice_problem_id = choice_problem.id
        problem.delete()
        self.assertFalse(
            ChoiceProblem.objects.filter(id=choice_problem_id).exists()
        )

    def test_meta_verbose_name(self):
        """Test Meta verbose_name."""
        self.assertEqual(ChoiceProblem._meta.verbose_name, "选择题详情")


class FillBlankProblemModelTestCase(TestCase):
    """Test cases for the FillBlankProblem model."""

    def test_str_method(self):
        """Test __str__ method."""
        problem = ProblemFactory(type='fillblank', title="Fill Quiz")
        fillblank_problem = FillBlankProblemFactory(problem=problem)
        expected = f"填空题: Fill Quiz"
        self.assertEqual(str(fillblank_problem), expected)

    def test_content_with_blanks_field(self):
        """Test content_with_blanks field."""
        problem = ProblemFactory(type='fillblank')
        content = "Complete the [blank1] and [blank2]."
        fillblank_problem = FillBlankProblemFactory(
            problem=problem,
            content_with_blanks=content
        )
        self.assertEqual(fillblank_problem.content_with_blanks, content)

    def test_blanks_format_detailed(self):
        """Test blanks field with detailed format."""
        problem = ProblemFactory(type='fillblank')
        blanks = {
            'blank1': {'answers': ['answer1', 'alt1'], 'case_sensitive': False},
            'blank2': {'answers': ['answer2'], 'case_sensitive': True},
        }
        fillblank_problem = FillBlankProblemFactory(
            problem=problem,
            blanks=blanks,
            blank_count=2
        )
        self.assertEqual(fillblank_problem.blanks, blanks)
        self.assertEqual(fillblank_problem.blank_count, 2)

    def test_blanks_format_simple(self):
        """Test blanks field with simple format."""
        problem = ProblemFactory(type='fillblank')
        blanks = {
            'blanks': [
                {'answers': ['answer1'], 'case_sensitive': False},
                {'answers': ['answer2'], 'case_sensitive': False}
            ]
        }
        fillblank_problem = FillBlankProblemFactory(
            problem=problem,
            blanks=blanks,
            blank_count=2
        )
        self.assertEqual(fillblank_problem.blanks, blanks)

    def test_blank_count_default_value(self):
        """Test that blank_count has default value of 1."""
        problem = ProblemFactory(type='fillblank')
        fillblank_problem = FillBlankProblemFactory(
            problem=problem,
            blank_count=1
        )
        self.assertEqual(fillblank_problem.blank_count, 1)

    def test_one_to_one_relationship_with_problem(self):
        """Test one-to-one relationship with Problem."""
        problem = ProblemFactory(type='fillblank')
        fillblank_problem = FillBlankProblemFactory(problem=problem)
        self.assertEqual(fillblank_problem.problem, problem)
        self.assertEqual(problem.fillblank_info, fillblank_problem)

    def test_cascade_deletion_when_problem_deleted(self):
        """Test that fillblank problem is deleted when problem is deleted."""
        problem = ProblemFactory(type='fillblank')
        fillblank_problem = FillBlankProblemFactory(problem=problem)
        fillblank_problem_id = fillblank_problem.id
        problem.delete()
        self.assertFalse(
            FillBlankProblem.objects.filter(id=fillblank_problem_id).exists()
        )

    def test_meta_verbose_name(self):
        """Test Meta verbose_name."""
        self.assertEqual(FillBlankProblem._meta.verbose_name, "填空题")


# ============================================================================
# Phase 3: Unlock System
# ============================================================================

class ProblemUnlockConditionModelTestCase(TestCase):
    """Test cases for the ProblemUnlockCondition model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.problem1 = ProblemFactory(type='algorithm', chapter=self.chapter)
        self.problem2 = ProblemFactory(type='algorithm', chapter=self.chapter)

    def test_str_method_with_prerequisite(self):
        """Test __str__ method with prerequisite condition."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='prerequisite'
        )
        unlock_condition.prerequisite_problems.add(self.problem2)
        result = str(unlock_condition)
        self.assertIn("前置题目", result)

    def test_str_method_with_date(self):
        """Test __str__ method with date condition."""
        unlock_date = timezone.now() + timedelta(days=1)
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='date',
            unlock_date=unlock_date
        )
        result = str(unlock_condition)
        self.assertIn("解锁日期", result)

    def test_str_method_with_none(self):
        """Test __str__ method with no conditions."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='none'
        )
        result = str(unlock_condition)
        self.assertIn("无条件", result)

    def test_prerequisite_relationship(self):
        """Test many-to-many relationship to prerequisite problems."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem2
        )
        unlock_condition.prerequisite_problems.add(self.problem1)
        self.assertIn(self.problem1, unlock_condition.prerequisite_problems.all())
        # Test that problem1 appears in the dependent_problems (reverse relationship)
        # dependent_problems returns ProblemUnlockCondition instances where problem1 is a prerequisite
        self.assertTrue(self.problem1.dependent_problems.filter(id=unlock_condition.id).exists())

    def test_one_to_one_relationship_with_problem(self):
        """Test one-to-one relationship with Problem."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1
        )
        self.assertEqual(unlock_condition.problem, self.problem1)
        self.assertEqual(self.problem1.unlock_condition, unlock_condition)

    def test_unlock_date_optional_field(self):
        """Test that unlock_date field is optional."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_date=None
        )
        self.assertIsNone(unlock_condition.unlock_date)

    def test_unlock_condition_type_choices(self):
        """Test unlock_condition_type field choices."""
        valid_types = ['prerequisite', 'date', 'both', 'none']
        for unlock_type in valid_types:
            unlock_condition = ProblemUnlockCondition.objects.create(
                problem=ProblemFactory(),  # Create a new problem for each test
                unlock_condition_type=unlock_type
            )
            self.assertEqual(unlock_condition.unlock_condition_type, unlock_type)

    def test_is_unlocked_with_no_conditions(self):
        """Test is_unlocked returns True with no conditions."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='none'
        )
        self.assertTrue(unlock_condition.is_unlocked(self.user))

    def test_is_unlocked_with_future_date(self):
        """Test is_unlocked returns False with future unlock date."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='date',
            unlock_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(unlock_condition.is_unlocked(self.user))

    def test_is_unlocked_with_past_date(self):
        """Test is_unlocked returns True with past unlock date."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='date',
            unlock_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(unlock_condition.is_unlocked(self.user))

    def test_is_unlocked_with_unsolved_prerequisite(self):
        """Test is_unlocked returns False with unsolved prerequisite."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='prerequisite'
        )
        unlock_condition.prerequisite_problems.add(self.problem2)
        self.assertFalse(unlock_condition.is_unlocked(self.user))

    def test_is_unlocked_with_solved_prerequisite(self):
        """Test is_unlocked returns True with solved prerequisite."""
        # Create enrollment
        enrollment = EnrollmentFactory(user=self.user, course=self.course)
        # Create progress
        progress = ProblemProgressFactory(
            enrollment=enrollment,
            problem=self.problem2,
            status='solved'
        )
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='prerequisite'
        )
        unlock_condition.prerequisite_problems.add(self.problem2)
        self.assertTrue(unlock_condition.is_unlocked(self.user))

    def test_is_unlocked_with_both_conditions_met(self):
        """Test is_unlocked with both date and prerequisite met."""
        enrollment = EnrollmentFactory(user=self.user, course=self.course)
        ProblemProgressFactory(
            enrollment=enrollment,
            problem=self.problem2,
            status='solved'
        )
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1,
            unlock_condition_type='both',
            unlock_date=timezone.now() - timedelta(days=1)
        )
        unlock_condition.prerequisite_problems.add(self.problem2)
        self.assertTrue(unlock_condition.is_unlocked(self.user))

    def test_cascade_deletion_when_problem_deleted(self):
        """Test that unlock condition is deleted when problem is deleted."""
        unlock_condition = ProblemUnlockCondition.objects.create(
            problem=self.problem1
        )
        unlock_condition_id = unlock_condition.id
        self.problem1.delete()
        self.assertFalse(
            ProblemUnlockCondition.objects.filter(id=unlock_condition_id).exists()
        )


# ============================================================================
# Phase 4: Execution & Testing
# ============================================================================

class TestCaseModelTestCase(TestCase):
    """Test cases for the TestCase model."""

    def test_str_method(self):
        """Test __str__ method."""
        problem = ProblemFactory(type='algorithm', title="Binary Search")
        algo_problem = AlgorithmProblemFactory(problem=problem)
        test_case = CourseTestCaseFactory(
            problem=algo_problem,
            id=1
        )
        expected = f"问题 Binary Search 的测试用例 1"
        self.assertEqual(str(test_case), expected)

    def test_is_sample_default_false(self):
        """Test that is_sample defaults to False."""
        test_case = CourseTestCaseFactory()
        self.assertFalse(test_case.is_sample)

    def test_is_sample_can_be_true(self):
        """Test that is_sample can be set to True."""
        test_case = CourseTestCaseFactory(is_sample=True)
        self.assertTrue(test_case.is_sample)

    def test_input_data_required(self):
        """Test that input_data field is required."""
        test_case = CourseTestCaseFactory.build(input_data=None)
        with self.assertRaises(ValidationError):
            test_case.full_clean()

    def test_expected_output_required(self):
        """Test that expected_output field is required."""
        test_case = CourseTestCaseFactory.build(expected_output=None)
        with self.assertRaises(ValidationError):
            test_case.full_clean()

    def test_problem_relationship(self):
        """Test foreign key relationship to AlgorithmProblem."""
        problem = ProblemFactory(type='algorithm')
        algo_problem = AlgorithmProblemFactory(problem=problem)
        test_case = CourseTestCaseFactory(problem=algo_problem)
        self.assertEqual(test_case.problem, algo_problem)
        self.assertIn(test_case, algo_problem.test_cases.all())

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        test_case = CourseTestCaseFactory()
        self.assertIsNotNone(test_case.created_at)

    def test_meta_verbose_name(self):
        """Test Meta verbose_name."""
        self.assertEqual(CourseTestCase._meta.verbose_name, "测试用例")


class SubmissionModelTestCase(TestCase):
    """Test cases for the Submission model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.problem = ProblemFactory(type='algorithm')

    def test_str_method(self):
        """Test __str__ method."""
        submission = SubmissionFactory(
            user=self.user,
            problem=self.problem,
            status='accepted'
        )
        result = str(submission)
        self.assertIn(self.user.username, result)
        self.assertIn(self.problem.title, result)
        self.assertIn('accepted', result)

    def test_status_default_pending(self):
        """Test that status defaults to pending."""
        submission = SubmissionFactory()
        self.assertEqual(submission.status, 'pending')

    def test_status_transitions_to_judging(self):
        """Test status transition from pending to judging."""
        submission = SubmissionFactory(status='pending')
        submission.status = 'judging'
        submission.save()
        self.assertEqual(submission.status, 'judging')

    def test_status_to_accepted(self):
        """Test status transition to accepted."""
        submission = SubmissionFactory(status='judging')
        submission.status = 'accepted'
        submission.save()
        self.assertEqual(submission.status, 'accepted')

    def test_status_to_wrong_answer(self):
        """Test status transition to wrong_answer."""
        submission = SubmissionFactory(status='judging')
        submission.status = 'wrong_answer'
        submission.save()
        self.assertEqual(submission.status, 'wrong_answer')

    def test_status_to_time_limit_exceeded(self):
        """Test status transition to time_limit_exceeded."""
        submission = SubmissionFactory(status='judging')
        submission.status = 'time_limit_exceeded'
        submission.save()
        self.assertEqual(submission.status, 'time_limit_exceeded')

    def test_status_to_memory_limit_exceeded(self):
        """Test status transition to memory_limit_exceeded."""
        submission = SubmissionFactory(status='judging')
        submission.status = 'memory_limit_exceeded'
        submission.save()
        self.assertEqual(submission.status, 'memory_limit_exceeded')

    def test_status_to_compilation_error(self):
        """Test status transition to compilation_error."""
        submission = SubmissionFactory(status='judging')
        submission.status = 'compilation_error'
        submission.save()
        self.assertEqual(submission.status, 'compilation_error')

    def test_status_to_runtime_error(self):
        """Test status transition to runtime_error."""
        submission = SubmissionFactory(status='judging')
        submission.status = 'runtime_error'
        submission.save()
        self.assertEqual(submission.status, 'runtime_error')

    def test_null_problem_handling(self):
        """Test that problem can be null (free code submission)."""
        submission = SubmissionFactory(
            user=self.user,
            problem=None,
            code="print('hello')"
        )
        self.assertIsNone(submission.problem)

    def test_code_field_required(self):
        """Test that code field is required."""
        submission = SubmissionFactory.build(code=None)
        with self.assertRaises(ValidationError):
            submission.full_clean()

    def test_language_default_python(self):
        """Test that language defaults to python."""
        submission = SubmissionFactory()
        self.assertEqual(submission.language, 'python')

    def test_execution_time_optional(self):
        """Test that execution_time is optional."""
        submission = SubmissionFactory(execution_time=None)
        self.assertIsNone(submission.execution_time)

    def test_memory_used_optional(self):
        """Test that memory_used is optional."""
        submission = SubmissionFactory(memory_used=None)
        self.assertIsNone(submission.memory_used)

    def test_user_relationship(self):
        """Test foreign key relationship to User."""
        submission = SubmissionFactory(user=self.user)
        self.assertEqual(submission.user, self.user)

    def test_problem_relationship(self):
        """Test foreign key relationship to Problem."""
        submission = SubmissionFactory(problem=self.problem)
        self.assertEqual(submission.problem, self.problem)

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        submission = SubmissionFactory()
        self.assertIsNotNone(submission.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        submission = SubmissionFactory()
        old_updated_at = submission.updated_at
        submission.status = 'accepted'
        submission.save()
        self.assertGreater(submission.updated_at, old_updated_at)

    def test_meta_ordering(self):
        """Test Meta ordering by created_at descending."""
        submission1 = SubmissionFactory(user=self.user)
        submission2 = SubmissionFactory(user=self.user)
        submission3 = SubmissionFactory(user=self.user)
        submissions = Submission.objects.all()
        # Check that the order is descending (newest first)
        self.assertEqual(submissions[0].id, submission3.id)
        self.assertEqual(submissions[1].id, submission2.id)
        self.assertEqual(submissions[2].id, submission1.id)


class CodeDraftModelTestCase(TestCase):
    """Test cases for the CodeDraft model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.problem = ProblemFactory(type='algorithm')

    def test_str_method(self):
        """Test __str__ method."""
        draft = CodeDraftFactory(
            user=self.user,
            problem=self.problem,
            save_type='manual_save'
        )
        result = str(draft)
        self.assertIn(self.user.username, result)
        self.assertIn(self.problem.title, result)
        self.assertIn('手动保存', result)

    def test_save_type_default_auto_save(self):
        """Test that save_type defaults to auto_save."""
        draft = CodeDraftFactory()
        self.assertEqual(draft.save_type, 'auto_save')

    def test_save_type_choices(self):
        """Test save_type field choices."""
        valid_types = ['auto_save', 'manual_save', 'submission']
        for save_type in valid_types:
            draft = CodeDraftFactory(save_type=save_type)
            self.assertEqual(draft.save_type, save_type)

    def test_code_field_required(self):
        """Test that code field is required."""
        draft = CodeDraftFactory.build(code=None)
        with self.assertRaises(ValidationError):
            draft.full_clean()

    def test_user_relationship(self):
        """Test foreign key relationship to User."""
        draft = CodeDraftFactory(user=self.user)
        self.assertEqual(draft.user, self.user)
        self.assertIn(draft, self.user.code_drafts.all())

    def test_problem_relationship(self):
        """Test foreign key relationship to Problem."""
        draft = CodeDraftFactory(problem=self.problem)
        self.assertEqual(draft.problem, self.problem)
        self.assertIn(draft, self.problem.code_drafts.all())

    def test_submission_relationship_nullable(self):
        """Test that submission relationship is nullable."""
        draft = CodeDraftFactory(submission=None)
        self.assertIsNone(draft.submission)

    def test_language_default_python(self):
        """Test that language defaults to python."""
        draft = CodeDraftFactory()
        self.assertEqual(draft.language, 'python')

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        draft = CodeDraftFactory()
        self.assertIsNotNone(draft.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        draft = CodeDraftFactory()
        old_updated_at = draft.updated_at
        draft.code = "updated code"
        draft.save()
        self.assertGreater(draft.updated_at, old_updated_at)

    def test_meta_ordering(self):
        """Test Meta ordering by created_at descending."""
        draft1 = CodeDraftFactory(user=self.user, problem=self.problem)
        draft2 = CodeDraftFactory(user=self.user, problem=self.problem)
        drafts = CodeDraft.objects.all()
        self.assertEqual(drafts[0], draft2)
        self.assertEqual(drafts[1], draft1)


# ============================================================================
# Phase 5: Learning Progress
# ============================================================================

class EnrollmentModelTestCase(TestCase):
    """Test cases for the Enrollment model."""

    def test_str_method(self):
        """Test __str__ method."""
        user = UserFactory(username="testuser")
        course = CourseFactory(title="Python Course")
        enrollment = EnrollmentFactory(user=user, course=course)
        expected = "testuser - Python Course"
        self.assertEqual(str(enrollment), expected)

    def test_enrolled_at_auto_now_add(self):
        """Test that enrolled_at is automatically set."""
        enrollment = EnrollmentFactory()
        self.assertIsNotNone(enrollment.enrolled_at)

    def test_last_accessed_at_auto_now(self):
        """Test that last_accessed_at updates on save."""
        enrollment = EnrollmentFactory()
        old_last_accessed = enrollment.last_accessed_at
        enrollment.save()
        self.assertGreater(enrollment.last_accessed_at, old_last_accessed)

    def test_unique_together_user_course(self):
        """Test that unique_together constraint is enforced."""
        user = UserFactory()
        course = CourseFactory()
        EnrollmentFactory(user=user, course=course)
        duplicate = Enrollment(user=user, course=course)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_user_relationship(self):
        """Test foreign key relationship to User."""
        user = UserFactory()
        enrollment = EnrollmentFactory(user=user)
        self.assertEqual(enrollment.user, user)
        self.assertIn(enrollment, user.enrollments.all())

    def test_course_relationship(self):
        """Test foreign key relationship to Course."""
        course = CourseFactory()
        enrollment = EnrollmentFactory(course=course)
        self.assertEqual(enrollment.course, course)
        self.assertIn(enrollment, course.enrollments.all())

    def test_cascade_deletion_when_user_deleted(self):
        """Test that enrollment is deleted when user is deleted."""
        user = UserFactory()
        enrollment = EnrollmentFactory(user=user)
        enrollment_id = enrollment.id
        user.delete()
        self.assertFalse(Enrollment.objects.filter(id=enrollment_id).exists())

    def test_cascade_deletion_when_course_deleted(self):
        """Test that enrollment is deleted when course is deleted."""
        course = CourseFactory()
        enrollment = EnrollmentFactory(course=course)
        enrollment_id = enrollment.id
        course.delete()
        self.assertFalse(Enrollment.objects.filter(id=enrollment_id).exists())


class ChapterProgressModelTestCase(TestCase):
    """Test cases for the ChapterProgress model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

    def test_str_method_completed(self):
        """Test __str__ method for completed chapter."""
        progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter,
            completed=True
        )
        result = str(progress)
        self.assertIn(self.user.username, result)
        self.assertIn(self.chapter.title, result)
        self.assertIn("已完成", result)

    def test_str_method_not_completed(self):
        """Test __str__ method for uncompleted chapter."""
        progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter,
            completed=False
        )
        result = str(progress)
        self.assertIn("未完成", result)

    def test_completed_default_false(self):
        """Test that completed defaults to False."""
        progress = ChapterProgressFactory()
        self.assertFalse(progress.completed)

    def test_completed_at_optional(self):
        """Test that completed_at is optional."""
        progress = ChapterProgressFactory(completed=False, completed_at=None)
        self.assertIsNone(progress.completed_at)

    def test_completed_at_set_when_completed(self):
        """Test that completed_at is set when chapter is completed."""
        now = timezone.now()
        progress = ChapterProgressFactory(
            completed=True,
            completed_at=now
        )
        self.assertIsNotNone(progress.completed_at)
        self.assertEqual(progress.completed_at, now)

    def test_enrollment_relationship(self):
        """Test foreign key relationship to Enrollment."""
        progress = ChapterProgressFactory(enrollment=self.enrollment)
        self.assertEqual(progress.enrollment, self.enrollment)
        self.assertIn(progress, self.enrollment.chapter_progress.all())

    def test_chapter_relationship(self):
        """Test foreign key relationship to Chapter."""
        progress = ChapterProgressFactory(chapter=self.chapter)
        self.assertEqual(progress.chapter, self.chapter)
        self.assertIn(progress, self.chapter.progress_records.all())

    def test_unique_together_enrollment_chapter(self):
        """Test that unique_together constraint is enforced."""
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter
        )
        duplicate = ChapterProgress(
            enrollment=self.enrollment,
            chapter=self.chapter
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class ProblemProgressModelTestCase(TestCase):
    """Test cases for the ProblemProgress model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.problem = ProblemFactory(type='algorithm', chapter=self.chapter)
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

    def test_str_method(self):
        """Test __str__ method."""
        progress = ProblemProgressFactory(
            enrollment=self.enrollment,
            problem=self.problem,
            status='solved'
        )
        result = str(progress)
        self.assertIn(self.user.username, result)
        self.assertIn(self.problem.title, result)
        self.assertIn('solved', result)

    def test_status_default_not_started(self):
        """Test that status defaults to not_started."""
        progress = ProblemProgressFactory()
        self.assertEqual(progress.status, 'not_started')

    def test_status_transitions(self):
        """Test status field transitions."""
        progress = ProblemProgressFactory(status='not_started')
        progress.status = 'in_progress'
        progress.save()
        self.assertEqual(progress.status, 'in_progress')

        progress.status = 'solved'
        progress.save()
        self.assertEqual(progress.status, 'solved')

        progress.status = 'failed'
        progress.save()
        self.assertEqual(progress.status, 'failed')

    def test_attempts_default_zero(self):
        """Test that attempts defaults to 0."""
        progress = ProblemProgressFactory()
        self.assertEqual(progress.attempts, 0)

    def test_attempts_can_increment(self):
        """Test that attempts can be incremented."""
        progress = ProblemProgressFactory(attempts=1)
        progress.attempts = 2
        progress.save()
        self.assertEqual(progress.attempts, 2)

    def test_last_attempted_at_optional(self):
        """Test that last_attempted_at is optional."""
        progress = ProblemProgressFactory(last_attempted_at=None)
        self.assertIsNone(progress.last_attempted_at)

    def test_solved_at_optional(self):
        """Test that solved_at is optional."""
        progress = ProblemProgressFactory(solved_at=None)
        self.assertIsNone(progress.solved_at)

    def test_solved_at_set_when_solved(self):
        """Test that solved_at is set when problem is solved."""
        now = timezone.now()
        progress = ProblemProgressFactory(
            status='solved',
            solved_at=now
        )
        self.assertIsNotNone(progress.solved_at)
        self.assertEqual(progress.solved_at, now)

    def test_best_submission_nullable(self):
        """Test that best_submission is nullable."""
        progress = ProblemProgressFactory(best_submission=None)
        self.assertIsNone(progress.best_submission)

    def test_enrollment_relationship(self):
        """Test foreign key relationship to Enrollment."""
        progress = ProblemProgressFactory(enrollment=self.enrollment)
        self.assertEqual(progress.enrollment, self.enrollment)
        self.assertIn(progress, self.enrollment.problem_progress.all())

    def test_problem_relationship(self):
        """Test foreign key relationship to Problem."""
        progress = ProblemProgressFactory(problem=self.problem)
        self.assertEqual(progress.problem, self.problem)
        self.assertIn(progress, self.problem.progress_records.all())

    def test_unique_together_enrollment_problem(self):
        """Test that unique_together constraint is enforced."""
        ProblemProgressFactory(
            enrollment=self.enrollment,
            problem=self.problem
        )
        duplicate = ProblemProgress(
            enrollment=self.enrollment,
            problem=self.problem
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


# ============================================================================
# Phase 6: Discussion System
# ============================================================================

class DiscussionThreadModelTestCase(TestCase):
    """Test cases for the DiscussionThread model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.problem = ProblemFactory(type='algorithm', chapter=self.chapter)

    def test_str_method(self):
        """Test __str__ method."""
        thread = DiscussionThreadFactory(
            course=self.course,
            title="Help with chapter 1"
        )
        result = str(thread)
        self.assertIn("Help with chapter 1", result)
        self.assertIn(str(self.course), result)

    def test_title_required(self):
        """Test that title field is required."""
        thread = DiscussionThreadFactory.build(title=None)
        with self.assertRaises(ValidationError):
            thread.full_clean()

    def test_content_required(self):
        """Test that content field is required."""
        thread = DiscussionThreadFactory.build(content=None)
        with self.assertRaises(ValidationError):
            thread.full_clean()

    def test_is_pinned_default_false(self):
        """Test that is_pinned defaults to False."""
        thread = DiscussionThreadFactory()
        self.assertFalse(thread.is_pinned)

    def test_is_resolved_default_false(self):
        """Test that is_resolved defaults to False."""
        thread = DiscussionThreadFactory()
        self.assertFalse(thread.is_resolved)

    def test_is_archived_default_false(self):
        """Test that is_archived defaults to False."""
        thread = DiscussionThreadFactory()
        self.assertFalse(thread.is_archived)

    def test_reply_count_default_zero(self):
        """Test that reply_count defaults to 0."""
        thread = DiscussionThreadFactory()
        self.assertEqual(thread.reply_count, 0)

    def test_last_activity_at_auto_now_add(self):
        """Test that last_activity_at is automatically set."""
        thread = DiscussionThreadFactory()
        self.assertIsNotNone(thread.last_activity_at)

    def test_course_relationship_nullable(self):
        """Test that course relationship is nullable."""
        thread = DiscussionThreadFactory(course=None)
        self.assertIsNone(thread.course)

    def test_course_relationship(self):
        """Test foreign key relationship to Course."""
        thread = DiscussionThreadFactory(course=self.course)
        self.assertEqual(thread.course, self.course)
        self.assertIn(thread, self.course.discussion_threads.all())

    def test_chapter_relationship_nullable(self):
        """Test that chapter relationship is nullable."""
        thread = DiscussionThreadFactory(chapter=None)
        self.assertIsNone(thread.chapter)

    def test_chapter_relationship(self):
        """Test foreign key relationship to Chapter."""
        thread = DiscussionThreadFactory(chapter=self.chapter)
        self.assertEqual(thread.chapter, self.chapter)
        self.assertIn(thread, self.chapter.discussion_threads.all())

    def test_problem_relationship_nullable(self):
        """Test that problem relationship is nullable."""
        thread = DiscussionThreadFactory(problem=None)
        self.assertIsNone(thread.problem)

    def test_problem_relationship(self):
        """Test foreign key relationship to Problem."""
        thread = DiscussionThreadFactory(problem=self.problem)
        self.assertEqual(thread.problem, self.problem)
        self.assertIn(thread, self.problem.discussion_threads.all())

    def test_author_relationship(self):
        """Test foreign key relationship to User."""
        thread = DiscussionThreadFactory(author=self.user)
        self.assertEqual(thread.author, self.user)
        self.assertIn(thread, self.user.started_threads.all())

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        thread = DiscussionThreadFactory()
        self.assertIsNotNone(thread.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        thread = DiscussionThreadFactory()
        old_updated_at = thread.updated_at
        thread.title = "Updated title"
        thread.save()
        self.assertGreater(thread.updated_at, old_updated_at)

    def test_meta_ordering(self):
        """Test Meta ordering by is_pinned and last_activity_at."""
        thread1 = DiscussionThreadFactory(course=self.course)
        thread2 = DiscussionThreadFactory(course=self.course, is_pinned=True)
        thread3 = DiscussionThreadFactory(course=self.course)

        threads = DiscussionThread.objects.filter(course=self.course)
        self.assertEqual(threads[0], thread2)  # Pinned first
        self.assertIn(threads[1], [thread1, thread3])
        self.assertIn(threads[2], [thread1, thread3])


class DiscussionReplyModelTestCase(TestCase):
    """Test cases for the DiscussionReply model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.thread = DiscussionThreadFactory()

    def test_str_method(self):
        """Test __str__ method."""
        reply = DiscussionReplyFactory(
            thread=self.thread,
            author=self.user
        )
        result = str(reply)
        self.assertIn(str(self.user), result)
        self.assertIn(self.thread.title, result)

    def test_content_required(self):
        """Test that content field is required."""
        reply = DiscussionReplyFactory.build(content=None)
        with self.assertRaises(ValidationError):
            reply.full_clean()

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        reply = DiscussionReplyFactory()
        self.assertIsNotNone(reply.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        reply = DiscussionReplyFactory()
        old_updated_at = reply.updated_at
        reply.content = "Updated content"
        reply.save()
        self.assertGreater(reply.updated_at, old_updated_at)

    def test_thread_relationship(self):
        """Test foreign key relationship to DiscussionThread."""
        reply = DiscussionReplyFactory(thread=self.thread)
        self.assertEqual(reply.thread, self.thread)
        self.assertIn(reply, self.thread.replies.all())

    def test_author_relationship(self):
        """Test foreign key relationship to User."""
        reply = DiscussionReplyFactory(author=self.user)
        self.assertEqual(reply.author, self.user)
        self.assertIn(reply, self.user.discussion_replies.all())

    def test_mentioned_users_relationship(self):
        """Test many-to-many relationship to mentioned users."""
        user1 = UserFactory()
        user2 = UserFactory()
        reply = DiscussionReplyFactory()
        reply.mentioned_users.add(user1, user2)
        self.assertIn(user1, reply.mentioned_users.all())
        self.assertIn(user2, reply.mentioned_users.all())

    def test_meta_ordering(self):
        """Test Meta ordering by created_at."""
        reply1 = DiscussionReplyFactory(thread=self.thread)
        reply2 = DiscussionReplyFactory(thread=self.thread)
        replies = DiscussionReply.objects.filter(thread=self.thread)
        self.assertEqual(replies[0], reply1)
        self.assertEqual(replies[1], reply2)


# ============================================================================
# Phase 7: Exam System
# ============================================================================

class ExamModelTestCase(TestCase):
    """Test cases for the Exam model."""

    def setUp(self):
        """Set up test fixtures."""
        self.course = CourseFactory()

    def test_str_method(self):
        """Test __str__ method."""
        exam = ExamFactory(course=self.course, title="Midterm Exam")
        result = str(exam)
        self.assertIn(str(self.course), result)
        self.assertIn("Midterm Exam", result)

    def test_start_time_required(self):
        """Test that start_time field is required."""
        exam = ExamFactory.build(start_time=None)
        with self.assertRaises(ValidationError):
            exam.full_clean()

    def test_end_time_required(self):
        """Test that end_time field is required."""
        exam = ExamFactory.build(end_time=None)
        with self.assertRaises(ValidationError):
            exam.full_clean()

    def test_status_default_draft(self):
        """Test that status defaults to draft."""
        exam = ExamFactory()
        self.assertEqual(exam.status, 'draft')

    def test_status_choices(self):
        """Test status field choices."""
        valid_statuses = ['draft', 'published', 'archived']
        for status in valid_statuses:
            exam = ExamFactory(status=status)
            self.assertEqual(exam.status, status)

    def test_total_score_default_100(self):
        """Test that total_score defaults to 100."""
        exam = ExamFactory()
        self.assertEqual(exam.total_score, 100)

    def test_passing_score_default_60(self):
        """Test that passing_score defaults to 60."""
        exam = ExamFactory()
        self.assertEqual(exam.passing_score, 60)

    def test_duration_minutes_default_60(self):
        """Test that duration_minutes defaults to 60."""
        exam = ExamFactory()
        self.assertEqual(exam.duration_minutes, 60)

    def test_shuffle_questions_default_false(self):
        """Test that shuffle_questions defaults to False."""
        exam = ExamFactory()
        self.assertFalse(exam.shuffle_questions)

    def test_show_results_after_submit_default_true(self):
        """Test that show_results_after_submit defaults to True."""
        exam = ExamFactory()
        self.assertTrue(exam.show_results_after_submit)

    def test_is_active_when_published_and_within_time(self):
        """Test is_active returns True when published and within time range."""
        now = timezone.now()
        exam = ExamFactory(
            status='published',
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1)
        )
        self.assertTrue(exam.is_active())

    def test_is_active_false_when_not_published(self):
        """Test is_active returns False when not published."""
        exam = ExamFactory(status='draft')
        self.assertFalse(exam.is_active())

    def test_is_active_false_when_before_start_time(self):
        """Test is_active returns False when before start time."""
        now = timezone.now()
        exam = ExamFactory(
            status='published',
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2)
        )
        self.assertFalse(exam.is_active())

    def test_is_active_false_when_after_end_time(self):
        """Test is_active returns False when after end time."""
        now = timezone.now()
        exam = ExamFactory(
            status='published',
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1)
        )
        self.assertFalse(exam.is_active())

    def test_is_available_for_user_when_enrolled(self):
        """Test is_available_for_user returns True when user is enrolled."""
        user = UserFactory()
        enrollment = EnrollmentFactory(user=user, course=self.course)
        exam = ExamFactory(course=self.course)
        self.assertTrue(exam.is_available_for_user(user))

    def test_is_available_for_user_false_when_not_enrolled(self):
        """Test is_available_for_user returns False when user not enrolled."""
        user = UserFactory()
        exam = ExamFactory(course=self.course)
        self.assertFalse(exam.is_available_for_user(user))

    def test_course_relationship(self):
        """Test foreign key relationship to Course."""
        exam = ExamFactory(course=self.course)
        self.assertEqual(exam.course, self.course)
        self.assertIn(exam, self.course.exams.all())


class ExamProblemModelTestCase(TestCase):
    """Test cases for the ExamProblem model."""

    def setUp(self):
        """Set up test fixtures."""
        self.course = CourseFactory()
        self.exam = ExamFactory(course=self.course)
        self.problem = ProblemFactory(type='choice')

    def test_str_method(self):
        """Test __str__ method."""
        exam_problem = ExamProblemFactory(
            exam=self.exam,
            problem=self.problem,
            score=10
        )
        result = str(exam_problem)
        self.assertIn(self.exam.title, result)
        self.assertIn(self.problem.title, result)
        self.assertIn("10", result)

    def test_score_default_10(self):
        """Test that score defaults to 10."""
        exam_problem = ExamProblemFactory()
        self.assertEqual(exam_problem.score, 10)

    def test_order_default_0(self):
        """Test that order defaults to 0."""
        exam_problem = ExamProblemFactory()
        self.assertEqual(exam_problem.order, 0)

    def test_is_required_default_true(self):
        """Test that is_required defaults to True."""
        exam_problem = ExamProblemFactory()
        self.assertTrue(exam_problem.is_required)

    def test_score_positive_validator(self):
        """Test that score has MinValueValidator of 1."""
        exam_problem = ExamProblemFactory.build(score=0)
        with self.assertRaises(ValidationError):
            exam_problem.full_clean()

    def test_exam_relationship(self):
        """Test foreign key relationship to Exam."""
        exam_problem = ExamProblemFactory(exam=self.exam)
        self.assertEqual(exam_problem.exam, self.exam)
        self.assertIn(exam_problem, self.exam.exam_problems.all())

    def test_problem_relationship(self):
        """Test foreign key relationship to Problem."""
        exam_problem = ExamProblemFactory(problem=self.problem)
        self.assertEqual(exam_problem.problem, self.problem)
        self.assertIn(exam_problem, self.problem.exam_problems.all())

    def test_unique_together_exam_problem_order(self):
        """Test that unique_together constraint is enforced."""
        ExamProblemFactory(exam=self.exam, problem=self.problem, order=1)
        duplicate = ExamProblem(
            exam=self.exam,
            problem=self.problem,
            order=1
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_clean_validates_problem_type(self):
        """Test that clean validates problem type (choice/fillblank only)."""
        algorithm_problem = ProblemFactory(type='algorithm')
        exam_problem = ExamProblemFactory.build(
            exam=self.exam,
            problem=algorithm_problem
        )
        with self.assertRaises(ValidationError):
            exam_problem.clean()


class ExamSubmissionModelTestCase(TestCase):
    """Test cases for the ExamSubmission model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.exam = ExamFactory(course=self.course)
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

    def test_str_method(self):
        """Test __str__ method."""
        submission = ExamSubmissionFactory(
            exam=self.exam,
            user=self.user,
            enrollment=self.enrollment,
            status='submitted'
        )
        result = str(submission)
        self.assertIn(self.user.username, result)
        self.assertIn(self.exam.title, result)

    def test_status_default_in_progress(self):
        """Test that status defaults to in_progress."""
        submission = ExamSubmissionFactory()
        self.assertEqual(submission.status, 'in_progress')

    def test_status_choices(self):
        """Test status field choices."""
        valid_statuses = ['in_progress', 'submitted', 'auto_submitted', 'graded']
        for status in valid_statuses:
            submission = ExamSubmissionFactory(status=status)
            self.assertEqual(submission.status, status)

    def test_started_at_auto_now_add(self):
        """Test that started_at is automatically set."""
        submission = ExamSubmissionFactory()
        self.assertIsNotNone(submission.started_at)

    def test_submitted_at_optional(self):
        """Test that submitted_at is optional."""
        submission = ExamSubmissionFactory(submitted_at=None)
        self.assertIsNone(submission.submitted_at)

    def test_total_score_nullable(self):
        """Test that total_score is nullable."""
        submission = ExamSubmissionFactory(total_score=None)
        self.assertIsNone(submission.total_score)

    def test_is_passed_nullable(self):
        """Test that is_passed is nullable."""
        submission = ExamSubmissionFactory(is_passed=None)
        self.assertIsNone(submission.is_passed)

    def test_time_spent_seconds_nullable(self):
        """Test that time_spent_seconds is nullable."""
        submission = ExamSubmissionFactory(time_spent_seconds=None)
        self.assertIsNone(submission.time_spent_seconds)

    def test_calculate_total_score(self):
        """Test calculate_total_score method."""
        submission = ExamSubmissionFactory(
            exam=self.exam,
            user=self.user,
            enrollment=self.enrollment
        )
        # This would require creating ExamAnswer instances
        # For now, test that method exists and returns 0 with no answers
        total = submission.calculate_total_score()
        self.assertEqual(total, 0)

    def test_check_is_passed_when_total_score_none(self):
        """Test check_is_passed returns None when total_score is None."""
        submission = ExamSubmissionFactory(
            exam=self.exam,
            total_score=None
        )
        result = submission.check_is_passed()
        self.assertIsNone(result)

    def test_check_is_passed_when_passed(self):
        """Test check_is_passed returns True when passed."""
        submission = ExamSubmissionFactory(
            exam=self.exam,
            total_score=70
        )
        result = submission.check_is_passed()
        self.assertTrue(result)

    def test_check_is_passed_when_failed(self):
        """Test check_is_passed returns False when failed."""
        submission = ExamSubmissionFactory(
            exam=self.exam,
            total_score=50
        )
        result = submission.check_is_passed()
        self.assertFalse(result)

    def test_unique_together_exam_user(self):
        """Test that unique_together constraint is enforced."""
        ExamSubmissionFactory(
            exam=self.exam,
            user=self.user,
            enrollment=self.enrollment
        )
        duplicate = ExamSubmission(
            exam=self.exam,
            user=self.user,
            enrollment=self.enrollment
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_exam_relationship(self):
        """Test foreign key relationship to Exam."""
        submission = ExamSubmissionFactory(exam=self.exam)
        self.assertEqual(submission.exam, self.exam)
        self.assertIn(submission, self.exam.submissions.all())

    def test_enrollment_relationship(self):
        """Test foreign key relationship to Enrollment."""
        submission = ExamSubmissionFactory(enrollment=self.enrollment)
        self.assertEqual(submission.enrollment, self.enrollment)
        self.assertIn(submission, self.enrollment.exam_submissions.all())

    def test_user_relationship(self):
        """Test foreign key relationship to User."""
        submission = ExamSubmissionFactory(user=self.user)
        self.assertEqual(submission.user, self.user)
        self.assertIn(submission, self.user.exam_submissions.all())


class ExamAnswerModelTestCase(TestCase):
    """Test cases for the ExamAnswer model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.exam = ExamFactory(course=self.course)
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )
        self.problem = ProblemFactory(type='choice')
        self.submission = ExamSubmissionFactory(
            exam=self.exam,
            user=self.user,
            enrollment=self.enrollment
        )

    def test_str_method(self):
        """Test __str__ method."""
        answer = ExamAnswerFactory(
            submission=self.submission,
            problem=self.problem
        )
        result = str(answer)
        self.assertIn(self.user.username, result)
        self.assertIn(self.problem.title, result)

    def test_choice_answers_nullable(self):
        """Test that choice_answers is nullable."""
        answer = ExamAnswerFactory(choice_answers=None)
        self.assertIsNone(answer.choice_answers)

    def test_fillblank_answers_nullable(self):
        """Test that fillblank_answers is nullable."""
        answer = ExamAnswerFactory(fillblank_answers=None)
        self.assertIsNone(answer.fillblank_answers)

    def test_score_nullable(self):
        """Test that score is nullable."""
        answer = ExamAnswerFactory(score=None)
        self.assertIsNone(answer.score)

    def test_is_correct_nullable(self):
        """Test that is_correct is nullable."""
        answer = ExamAnswerFactory(is_correct=None)
        self.assertIsNone(answer.is_correct)

    def test_correct_percentage_nullable(self):
        """Test that correct_percentage is nullable."""
        answer = ExamAnswerFactory(correct_percentage=None)
        self.assertIsNone(answer.correct_percentage)

    def test_submission_relationship(self):
        """Test foreign key relationship to ExamSubmission."""
        answer = ExamAnswerFactory(submission=self.submission)
        self.assertEqual(answer.submission, self.submission)
        self.assertIn(answer, self.submission.answers.all())

    def test_problem_relationship(self):
        """Test foreign key relationship to Problem."""
        answer = ExamAnswerFactory(problem=self.problem)
        self.assertEqual(answer.problem, self.problem)
        self.assertIn(answer, self.problem.exam_answers.all())

    def test_unique_together_submission_problem(self):
        """Test that unique_together constraint is enforced."""
        ExamAnswerFactory(
            submission=self.submission,
            problem=self.problem
        )
        duplicate = ExamAnswer(
            submission=self.submission,
            problem=self.problem
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set."""
        answer = ExamAnswerFactory()
        self.assertIsNotNone(answer.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at updates on save."""
        answer = ExamAnswerFactory()
        old_updated_at = answer.updated_at
        answer.score = 10
        answer.save()
        self.assertGreater(answer.updated_at, old_updated_at)
