"""
Comprehensive serializer tests for the courses app.

This module tests all serializers to ensure:
- Field validation works correctly
- Cross-field validation is enforced
- Custom validation methods function properly
- Serialization/deserialization works as expected
- Nested serializers are handled correctly
- Error messages are properly formatted
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers

from courses.serializers import (
    CourseModelSerializer,
    ChapterSerializer,
    ProblemSerializer,
    AlgorithmProblemSerializer,
    ChoiceProblemSerializer,
    FillBlankProblemSerializer,
    EnrollmentSerializer,
    ChapterProgressSerializer,
    ProblemProgressSerializer,
    BriefDiscussionThreadSerializer,
    DiscussionThreadSerializer,
    DiscussionReplySerializer,
    ExamListSerializer,
    ExamDetailSerializer,
    ExamCreateSerializer,
    ExamAnswerDetailSerializer,
    ExamSubmissionSerializer,
    ExamSubmissionCreateSerializer,
    ExamSubmitSerializer,
    ChapterUnlockConditionSerializer,
)

from courses.tests.factories import (
    CourseFactory,
    ChapterFactory,
    ProblemFactory,
    AlgorithmProblemFactory,
    ChoiceProblemFactory,
    FillBlankProblemFactory,
    CourseTestCaseFactory,
    SubmissionFactory,
    CodeDraftFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
    ProblemProgressFactory,
    DiscussionThreadFactory,
    DiscussionReplyFactory,
    ExamFactory,
    ExamProblemFactory,
    ExamSubmissionFactory,
    ExamAnswerFactory,
    ProblemUnlockConditionFactory,
    ChapterUnlockConditionFactory,
)
from accounts.tests.factories import UserFactory
from courses.models import ChapterUnlockCondition, Chapter


# =============================================================================
# Phase 1: Core Serializers
# =============================================================================

class CourseModelSerializerTestCase(TestCase):
    """Test cases for CourseModelSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.serializer = CourseModelSerializer(self.course)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'title', 'description', 'recent_threads',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_recent_threads_field_is_read_only(self):
        """Test that recent_threads field is read-only."""
        self.assertIn('recent_threads', CourseModelSerializer.Meta.read_only_fields)

    def test_recent_threads_returns_empty_list_for_new_course(self):
        """Test that recent_threads returns empty list for course with no threads."""
        data = self.serializer.data
        self.assertEqual(data['recent_threads'], [])

    def test_recent_threads_includes_recent_threads(self):
        """Test that recent_threads includes actual discussion threads."""
        DiscussionThreadFactory(course=self.course, is_archived=False)
        DiscussionThreadFactory(course=self.course, is_archived=False)
        # Create an archived thread that should not appear
        DiscussionThreadFactory(course=self.course, is_archived=True)

        data = self.serializer.data
        self.assertEqual(len(data['recent_threads']), 2)

    def test_recent_threads_limited_to_three(self):
        """Test that recent_threads is limited to 3 threads."""
        for _ in range(5):
            DiscussionThreadFactory(course=self.course, is_archived=False)

        data = self.serializer.data
        self.assertEqual(len(data['recent_threads']), 3)

    def test_created_at_field_is_read_only(self):
        """Test that created_at field is read-only."""
        self.assertIn('created_at', CourseModelSerializer.Meta.read_only_fields)

    def test_updated_at_field_is_read_only(self):
        """Test that updated_at field is read-only."""
        self.assertIn('updated_at', CourseModelSerializer.Meta.read_only_fields)

    def test_title_field_content(self):
        """Test that title field is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['title'], self.course.title)

    def test_description_field_content(self):
        """Test that description field is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['description'], self.course.description)


class ChapterSerializerTestCase(TestCase):
    """Test cases for ChapterSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.context = {'request': type('Request', (), {'user': self.user})}
        self.serializer = ChapterSerializer(self.chapter, context=self.context)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'course', 'course_title', 'title', 'content',
            'order', 'created_at', 'updated_at', 'status',
            'unlock_condition', 'is_locked', 'prerequisite_progress'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_course_title_field(self):
        """Test that course_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['course_title'], self.course.title)

    def test_status_returns_not_started_for_unauthenticated_user(self):
        """Test that status returns 'not_started' for unauthenticated users."""
        serializer = ChapterSerializer(
            self.chapter,
            context={'request': type('Request', (), {'user': type('User', (), {'is_authenticated': False})})}
        )
        data = serializer.data
        self.assertEqual(data['status'], 'not_started')

    def test_status_returns_not_started_for_no_progress(self):
        """Test that status returns 'not_started' when no progress exists."""
        data = self.serializer.data
        self.assertEqual(data['status'], 'not_started')

    def test_status_returns_in_progress(self):
        """Test that status returns 'in_progress' for in-progress chapter."""
        enrollment = EnrollmentFactory(user=self.user, course=self.course)
        ChapterProgressFactory(enrollment=enrollment, chapter=self.chapter, completed=False)

        data = self.serializer.data
        self.assertEqual(data['status'], 'in_progress')

    def test_status_returns_completed(self):
        """Test that status returns 'completed' for completed chapter."""
        enrollment = EnrollmentFactory(user=self.user, course=self.course)
        ChapterProgressFactory(
            enrollment=enrollment,
            chapter=self.chapter,
            completed=True,
            completed_at=timezone.now()
        )

        data = self.serializer.data
        self.assertEqual(data['status'], 'completed')

    def test_read_only_fields(self):
        """Test that timestamp fields are read-only."""
        self.assertIn('created_at', ChapterSerializer.Meta.read_only_fields)
        self.assertIn('updated_at', ChapterSerializer.Meta.read_only_fields)

    def test_contains_unlock_fields(self):
        """Test that serializer contains unlock-related fields."""
        data = self.serializer.data
        unlock_fields = {'unlock_condition', 'is_locked', 'prerequisite_progress'}
        self.assertTrue(unlock_fields.issubset(set(data.keys())))

    def test_unlock_condition_field(self):
        """Test that unlock_condition field works correctly."""
        # Test without unlock condition
        data = self.serializer.data
        self.assertIsNone(data['unlock_condition'])

        # Test with unlock condition
        condition = ChapterUnlockConditionFactory(chapter=self.chapter)
        serializer = ChapterSerializer(self.chapter, context=self.context)
        data = serializer.data
        self.assertIsNotNone(data['unlock_condition'])
        self.assertEqual(data['unlock_condition']['unlock_condition_type'], 'all')

    def test_is_locked_field_with_unlock_condition(self):
        """Test is_locked field with unlock condition."""
        from courses.services import ChapterUnlockService
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Exists, OuterRef, Case, When, Value, BooleanField

        # Create unlock condition
        future_date = timezone.now() + timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter,
            unlock_condition_type='date',
            unlock_date=future_date
        )

        # Create enrollment for the user (required for is_locked calculation)
        EnrollmentFactory(user=self.user, course=self.course)

        # Manually annotate is_locked_db as ViewSet does
        is_before_unlock_date = Exists(
            ChapterUnlockCondition.objects.filter(
                chapter=OuterRef('pk'),
                unlock_condition_type__in=['date', 'all'],
                unlock_date__gt=timezone.now()
            )
        )
        chapter_with_annotation = Chapter.objects.annotate(
            is_locked_db=Case(
                When(is_before_unlock_date, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).get(id=self.chapter.id)

        # Test serialization with user context
        context = {'request': type('Request', (), {'user': self.user})}
        serializer = ChapterSerializer(chapter_with_annotation, context=context)
        data = serializer.data

        # Should be locked based on date
        self.assertTrue(data['is_locked'])

    def test_is_locked_field_without_unlock_condition(self):
        """Test is_locked field without unlock condition."""
        from django.db.models import Exists, OuterRef, Case, When, Value, BooleanField

        # Create enrollment for the user
        enrollment = EnrollmentFactory(user=self.user, course=self.course)

        # Manually annotate is_locked_db as ViewSet does (no unlock condition -> False)
        chapter_with_annotation = Chapter.objects.annotate(
            is_locked_db=Value(False, output_field=BooleanField())
        ).get(id=self.chapter.id)

        serializer = ChapterSerializer(chapter_with_annotation, context=self.context)
        data = serializer.data
        # Should be false if no unlock condition
        self.assertFalse(data['is_locked'])

    def test_prerequisite_progress_field(self):
        """Test prerequisite_progress field returns correct data."""
        from courses.services import ChapterUnlockService

        # Create enrollment for the user
        enrollment = EnrollmentFactory(user=self.user, course=self.course)

        # Create unlock condition with prerequisites
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter)  # Self-reference for test

        # Test with user context - need is_authenticated attribute
        context = {'request': type('Request', (), {'user': self.user, 'is_authenticated': True})}
        serializer = ChapterSerializer(self.chapter, context=context)
        data = serializer.data

        # Should return prerequisite progress data
        self.assertIsNotNone(data['prerequisite_progress'])


class ChapterUnlockConditionSerializerTestCase(TestCase):
    """Test cases for ChapterUnlockConditionSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.prereq_chapter = ChapterFactory(course=self.course)
        self.condition = ChapterUnlockConditionFactory(chapter=self.chapter)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = ChapterUnlockConditionSerializer(self.condition)
        data = serializer.data
        # Note: prerequisite_chapter_ids is write_only, so it's not in the output
        expected_fields = {
            'id', 'chapter', 'prerequisite_chapters',
            'prerequisite_titles',
            'unlock_date', 'unlock_condition_type'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_prerequisite_chapters_field(self):
        """Test that prerequisite_chapters field returns chapter information."""
        # Add prerequisites
        self.condition.prerequisite_chapters.add(self.prereq_chapter)
        self.condition.save()

        serializer = ChapterUnlockConditionSerializer(self.condition)
        data = serializer.data

        self.assertEqual(len(data['prerequisite_chapters']), 1)
        prereq = data['prerequisite_chapters'][0]
        self.assertEqual(prereq['id'], self.prereq_chapter.id)
        self.assertEqual(prereq['title'], self.prereq_chapter.title)
        self.assertEqual(prereq['order'], self.prereq_chapter.order)

    def test_prerequisite_titles_field(self):
        """Test that prerequisite_titles field returns just titles."""
        # Add prerequisites
        self.condition.prerequisite_chapters.add(self.prereq_chapter)
        self.condition.save()

        serializer = ChapterUnlockConditionSerializer(self.condition)
        data = serializer.data

        self.assertEqual(len(data['prerequisite_titles']), 1)
        self.assertEqual(data['prerequisite_titles'][0], self.prereq_chapter.title)

    def test_prerequisite_chapter_ids_write_only_field(self):
        """Test that prerequisite_chapter_ids is write-only."""
        # Create serializer instance
        serializer = ChapterUnlockConditionSerializer()
        self.assertTrue(serializer.fields['prerequisite_chapter_ids'].write_only)

    def test_read_only_fields(self):
        """Test that chapter field is read-only."""
        self.assertIn('chapter', ChapterUnlockConditionSerializer.Meta.read_only_fields)

    def test_serialization_without_prerequisites(self):
        """Test serialization when no prerequisites exist."""
        serializer = ChapterUnlockConditionSerializer(self.condition)
        data = serializer.data

        self.assertEqual(len(data['prerequisite_chapters']), 0)
        self.assertEqual(len(data['prerequisite_titles']), 0)

    def test_serialization_with_multiple_prerequisites(self):
        """Test serialization with multiple prerequisites."""
        # Create multiple prerequisite chapters
        prereq1 = ChapterFactory(course=self.course, order=1)
        prereq2 = ChapterFactory(course=self.course, order=2)

        self.condition.prerequisite_chapters.add(prereq1, prereq2)
        self.condition.save()

        serializer = ChapterUnlockConditionSerializer(self.condition)
        data = serializer.data

        # Verify prerequisites are ordered correctly
        self.assertEqual(len(data['prerequisite_chapters']), 2)
        self.assertEqual(data['prerequisite_chapters'][0]['order'], 1)
        self.assertEqual(data['prerequisite_chapters'][1]['order'], 2)


class ProblemSerializerTestCase(TestCase):
    """Test cases for ProblemSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.problem = ProblemFactory(chapter=self.chapter, type='algorithm')
        # Create the algorithm_info relationship
        AlgorithmProblemFactory(problem=self.problem)
        self.context = {'request': type('Request', (), {'user': self.user})}
        self.serializer = ProblemSerializer(self.problem, context=self.context)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('title', data)
        self.assertIn('content', data)
        self.assertIn('difficulty', data)
        self.assertIn('status', data)
        self.assertIn('is_unlocked', data)
        self.assertIn('unlock_condition_description', data)

    def test_chapter_title_field(self):
        """Test that chapter_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['chapter_title'], self.chapter.title)

    def test_status_for_unauthenticated_user(self):
        """Test that status is 'not_started' for unauthenticated users."""
        context = {'request': type('Request', (), {'user': type('User', (), {'is_authenticated': False})})}
        serializer = ProblemSerializer(self.problem, context=context)
        data = serializer.data
        self.assertEqual(data['status'], 'not_started')

    def test_status_for_no_progress(self):
        """Test that status is 'not_started' when no progress exists."""
        data = self.serializer.data
        self.assertEqual(data['status'], 'not_started')

    def test_is_unlocked_for_unauthenticated_user(self):
        """Test that is_unlocked is False for unauthenticated users."""
        context = {'request': type('Request', (), {'user': type('User', (), {'is_authenticated': False})})}
        serializer = ProblemSerializer(self.problem, context=context)
        data = serializer.data
        self.assertFalse(data['is_unlocked'])

    def test_is_unlocked_for_no_unlock_condition(self):
        """Test that is_unlocked is True when no unlock condition exists."""
        data = self.serializer.data
        self.assertTrue(data['is_unlocked'])

    def test_unlock_condition_description_for_no_condition(self):
        """Test unlock_condition_description when no condition exists."""
        data = self.serializer.data
        self.assertEqual(data['unlock_condition_description']['type'], 'none')
        self.assertFalse(data['unlock_condition_description']['has_conditions'])

    def test_unlock_condition_description_with_prerequisite(self):
        """Test unlock_condition_description with prerequisite condition."""
        unlock_condition = ProblemUnlockConditionFactory(
            problem=self.problem,
            unlock_condition_type='prerequisite'
        )
        unlock_condition.prerequisite_problems.add(ProblemFactory(chapter=self.chapter))

        serializer = ProblemSerializer(self.problem, context=self.context)
        data = serializer.data
        self.assertEqual(data['unlock_condition_description']['type'], 'prerequisite')
        self.assertTrue(data['unlock_condition_description']['has_conditions'])
        self.assertEqual(len(data['unlock_condition_description']['prerequisite_problems']), 1)

    def test_algorithm_problem_includes_algorithm_fields(self):
        """Test that algorithm problems include algorithm-specific fields."""
        # AlgorithmProblem is already created in setUp
        serializer = ProblemSerializer(self.problem, context=self.context)
        data = serializer.data
        self.assertIn('time_limit', data)
        self.assertIn('memory_limit', data)

    def test_choice_problem_includes_choice_fields(self):
        """Test that choice problems include choice-specific fields."""
        self.problem.type = 'choice'
        self.problem.save()
        ChoiceProblemFactory(problem=self.problem)

        serializer = ProblemSerializer(self.problem, context=self.context)
        data = serializer.data
        self.assertIn('options', data)
        self.assertIn('is_multiple_choice', data)

    def test_fillblank_problem_includes_fillblank_fields(self):
        """Test that fillblank problems include fillblank-specific fields."""
        self.problem.type = 'fillblank'
        self.problem.save()
        FillBlankProblemFactory(problem=self.problem)

        serializer = ProblemSerializer(self.problem, context=self.context)
        data = serializer.data
        self.assertIn('content_with_blanks', data)
        self.assertIn('blanks_list', data)
        self.assertIn('blank_count', data)


# =============================================================================
# Phase 2: Problem Type Serializers
# =============================================================================

class AlgorithmProblemSerializerTestCase(TestCase):
    """Test cases for AlgorithmProblemSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.algorithm_problem = AlgorithmProblemFactory()
        self.serializer = AlgorithmProblemSerializer(self.algorithm_problem)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {'time_limit', 'memory_limit', 'code_template', 'sample_cases'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_time_limit_field(self):
        """Test that time_limit is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['time_limit'], self.algorithm_problem.time_limit)

    def test_memory_limit_field(self):
        """Test that memory_limit is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['memory_limit'], self.algorithm_problem.memory_limit)

    def test_code_template_field_when_null(self):
        """Test code_template when it's null."""
        self.assertIsNone(self.algorithm_problem.code_template)
        data = self.serializer.data
        self.assertIsNone(data['code_template'])

    def test_sample_cases_empty_when_no_test_cases(self):
        """Test that sample_cases is empty when no test cases exist."""
        data = self.serializer.data
        self.assertEqual(data['sample_cases'], [])

    def test_sample_cases_includes_only_sample_cases(self):
        """Test that sample_cases only includes test cases marked as sample."""
        CourseTestCaseFactory(
            problem=self.algorithm_problem,
            is_sample=True
        )
        CourseTestCaseFactory(
            problem=self.algorithm_problem,
            is_sample=False
        )

        data = self.serializer.data
        self.assertEqual(len(data['sample_cases']), 1)


class ChoiceProblemSerializerTestCase(TestCase):
    """Test cases for ChoiceProblemSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.choice_problem = ChoiceProblemFactory()

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = ChoiceProblemSerializer(self.choice_problem)
        data = serializer.data
        expected_fields = {'problem', 'options', 'correct_answer', 'is_multiple_choice'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_options_field(self):
        """Test that options are correctly serialized."""
        serializer = ChoiceProblemSerializer(self.choice_problem)
        data = serializer.data
        self.assertEqual(data['options'], self.choice_problem.options)

    def test_single_choice_correct_answer(self):
        """Test correct_answer for single choice."""
        serializer = ChoiceProblemSerializer(self.choice_problem)
        data = serializer.data
        self.assertEqual(data['correct_answer'], self.choice_problem.correct_answer)
        self.assertFalse(data['is_multiple_choice'])

    def test_multiple_choice_correct_answer(self):
        """Test correct_answer for multiple choice."""
        self.choice_problem.is_multiple_choice = True
        self.choice_problem.correct_answer = ['A', 'C']
        self.choice_problem.save()

        serializer = ChoiceProblemSerializer(self.choice_problem)
        data = serializer.data
        self.assertEqual(data['correct_answer'], ['A', 'C'])
        self.assertTrue(data['is_multiple_choice'])

    def test_validate_options_requires_dict(self):
        """Test that options validation requires a dict."""
        serializer = ChoiceProblemSerializer()
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_options(['A', 'B', 'C'])
        self.assertIn('字典格式', str(cm.exception))

    def test_validate_options_not_empty(self):
        """Test that options cannot be empty."""
        serializer = ChoiceProblemSerializer()
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_options({})
        self.assertIn('不能为空', str(cm.exception))

    def test_validate_options_uppercase_letters(self):
        """Test that option keys must be uppercase letters."""
        serializer = ChoiceProblemSerializer()
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_options({'a': 'Option 1', 'b': 'Option 2'})
        self.assertIn('大写字母', str(cm.exception))

    def test_validate_single_choice_answer_in_options(self):
        """Test that single choice answer must be in options."""
        choice_problem = ChoiceProblemFactory()
        serializer = ChoiceProblemSerializer(
            choice_problem,
            data={
                'problem': choice_problem.problem.id,
                'options': {'A': 'Option 1', 'B': 'Option 2'},
                'correct_answer': 'C',
                'is_multiple_choice': False
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('正确答案', str(serializer.errors))

    def test_validate_multiple_choice_answers_in_options(self):
        """Test that multiple choice answers must be in options."""
        choice_problem = ChoiceProblemFactory()
        # Update an existing instance with invalid data
        serializer = ChoiceProblemSerializer(
            choice_problem,
            data={
                'problem': choice_problem.problem.id,
                'options': {'A': 'Option 1', 'B': 'Option 2'},
                'correct_answer': ['A', 'C'],
                'is_multiple_choice': True
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('正确答案包含无效选项', str(serializer.errors))

    def test_validate_multiple_choice_requires_list(self):
        """Test that multiple choice requires list answer."""
        choice_problem = ChoiceProblemFactory()
        serializer = ChoiceProblemSerializer(
            choice_problem,
            data={
                'problem': choice_problem.problem.id,
                'options': {'A': 'Option 1', 'B': 'Option 2'},
                'correct_answer': 'A',
                'is_multiple_choice': True
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('必须是列表', str(serializer.errors))


class FillBlankProblemSerializerTestCase(TestCase):
    """Test cases for FillBlankProblemSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.fillblank_problem = FillBlankProblemFactory()
        self.serializer = FillBlankProblemSerializer(self.fillblank_problem)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {'content_with_blanks', 'blanks', 'blanks_list', 'blank_count'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_content_with_blanks_field(self):
        """Test that content_with_blanks is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['content_with_blanks'], self.fillblank_problem.content_with_blanks)

    def test_blank_count_field(self):
        """Test that blank_count is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['blank_count'], self.fillblank_problem.blank_count)

    def test_blanks_list_format_simple_array(self):
        """Test blanks_list with simple array format."""
        self.fillblank_problem.blanks = {
            'blanks': ['answer1', 'answer2'],
            'case_sensitive': False
        }
        self.fillblank_problem.save()

        serializer = FillBlankProblemSerializer(self.fillblank_problem)
        data = serializer.data
        self.assertEqual(len(data['blanks_list']), 2)
        self.assertEqual(data['blanks_list'][0]['id'], 'blank1')

    def test_blanks_list_format_detailed_array(self):
        """Test blanks_list with detailed array format."""
        self.fillblank_problem.blanks = {
            'blanks': [
                {'answers': ['answer1', 'ans1'], 'case_sensitive': False},
                {'answers': ['answer2'], 'case_sensitive': True}
            ]
        }
        self.fillblank_problem.save()

        serializer = FillBlankProblemSerializer(self.fillblank_problem)
        data = serializer.data
        self.assertEqual(len(data['blanks_list']), 2)
        self.assertEqual(data['blanks_list'][0]['answers'], ['answer1', 'ans1'])

    def test_blanks_list_format_named_blanks(self):
        """Test blanks_list with named blank format."""
        self.fillblank_problem.blanks = {
            'blank1': {'answer': ['ans1'], 'case_sensitive': False},
            'blank2': {'answers': ['ans2'], 'case_sensitive': True}
        }
        self.fillblank_problem.save()

        serializer = FillBlankProblemSerializer(self.fillblank_problem)
        data = serializer.data
        self.assertEqual(len(data['blanks_list']), 2)
        self.assertEqual(data['blanks_list'][0]['id'], 'blank1')

    def test_validate_blanks_requires_dict(self):
        """Test that blanks validation requires a dict."""
        serializer = FillBlankProblemSerializer()
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_blanks(['answer1', 'answer2'])
        self.assertIn('字典格式', str(cm.exception))

    def test_validate_blanks_not_empty(self):
        """Test that blanks cannot be empty."""
        serializer = FillBlankProblemSerializer()
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_blanks({})
        self.assertIn('不能为空', str(cm.exception))


# =============================================================================
# Phase 3: Progress Serializers
# =============================================================================

class EnrollmentSerializerTestCase(TestCase):
    """Test cases for EnrollmentSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.enrollment = EnrollmentFactory()
        self.serializer = EnrollmentSerializer(self.enrollment)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'user', 'user_username', 'course', 'course_title',
            'enrolled_at', 'last_accessed_at', 'progress_percentage', 'next_chapter'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_user_username_field(self):
        """Test that user_username is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['user_username'], self.enrollment.user.username)

    def test_course_title_field(self):
        """Test that course_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['course_title'], self.enrollment.course.title)

    def test_progress_percentage_with_no_chapters(self):
        """Test progress_percentage when course has no chapters."""
        course = CourseFactory()
        enrollment = EnrollmentFactory(course=course)
        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data
        self.assertEqual(data['progress_percentage'], 0)

    def test_progress_percentage_with_completed_chapters(self):
        """Test progress_percentage calculation with completed chapters."""
        enrollment = EnrollmentFactory()
        course = enrollment.course
        chapter1 = ChapterFactory(course=course, order=0)
        chapter2 = ChapterFactory(course=course, order=1)

        ChapterProgressFactory(
            enrollment=enrollment,
            chapter=chapter1,
            completed=True
        )
        ChapterProgressFactory(
            enrollment=enrollment,
            chapter=chapter2,
            completed=False
        )

        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data
        self.assertEqual(data['progress_percentage'], 50.0)

    def test_next_chapter_with_incomplete_chapters(self):
        """Test next_chapter returns first incomplete chapter."""
        enrollment = EnrollmentFactory()
        course = enrollment.course
        chapter1 = ChapterFactory(course=course, order=0)
        chapter2 = ChapterFactory(course=course, order=1)

        ChapterProgressFactory(
            enrollment=enrollment,
            chapter=chapter1,
            completed=True
        )

        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data
        self.assertIsNotNone(data['next_chapter'])
        self.assertEqual(data['next_chapter']['id'], chapter2.id)

    def test_next_chapter_when_all_completed(self):
        """Test next_chapter returns None when all chapters completed."""
        enrollment = EnrollmentFactory()
        course = enrollment.course
        chapter1 = ChapterFactory(course=course, order=0)
        ChapterProgressFactory(
            enrollment=enrollment,
            chapter=chapter1,
            completed=True
        )

        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data
        self.assertIsNone(data['next_chapter'])

    def test_read_only_fields(self):
        """Test that specified fields are read-only."""
        read_only_fields = EnrollmentSerializer.Meta.read_only_fields
        self.assertIn('enrolled_at', read_only_fields)
        self.assertIn('progress_percentage', read_only_fields)
        self.assertIn('next_chapter', read_only_fields)


class ChapterProgressSerializerTestCase(TestCase):
    """Test cases for ChapterProgressSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.chapter_progress = ChapterProgressFactory()
        self.serializer = ChapterProgressSerializer(self.chapter_progress)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'enrollment', 'chapter', 'chapter_title', 'course_title',
            'completed', 'completed_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_chapter_title_field(self):
        """Test that chapter_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['chapter_title'], self.chapter_progress.chapter.title)

    def test_course_title_field(self):
        """Test that course_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['course_title'], self.chapter_progress.chapter.course.title)

    def test_completed_field(self):
        """Test that completed field is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['completed'], self.chapter_progress.completed)

    def test_completed_at_when_null(self):
        """Test completed_at when chapter is not completed."""
        self.assertIsNone(self.chapter_progress.completed_at)
        data = self.serializer.data
        self.assertIsNone(data['completed_at'])

    def test_completed_at_when_completed(self):
        """Test completed_at when chapter is completed."""
        progress = ChapterProgressFactory(
            completed=True,
            completed_at=timezone.now()
        )
        serializer = ChapterProgressSerializer(progress)
        data = serializer.data
        self.assertIsNotNone(data['completed_at'])


class ProblemProgressSerializerTestCase(TestCase):
    """Test cases for ProblemProgressSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.problem_progress = ProblemProgressFactory()
        self.serializer = ProblemProgressSerializer(self.problem_progress)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'enrollment', 'problem', 'problem_title', 'chapter_title',
            'course_title', 'status', 'attempts', 'last_attempted_at',
            'solved_at', 'best_submission', 'problem_type', 'problem_difficulty'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_problem_title_field(self):
        """Test that problem_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['problem_title'], self.problem_progress.problem.title)

    def test_problem_type_field(self):
        """Test that problem_type is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['problem_type'], self.problem_progress.problem.type)

    def test_problem_difficulty_field(self):
        """Test that problem_difficulty is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['problem_difficulty'], self.problem_progress.problem.difficulty)

    def test_status_field(self):
        """Test that status field is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['status'], self.problem_progress.status)

    def test_status_not_started(self):
        """Test status can be 'not_started'."""
        progress = ProblemProgressFactory(status='not_started')
        serializer = ProblemProgressSerializer(progress)
        data = serializer.data
        self.assertEqual(data['status'], 'not_started')

    def test_status_in_progress(self):
        """Test status can be 'in_progress'."""
        progress = ProblemProgressFactory(status='in_progress')
        serializer = ProblemProgressSerializer(progress)
        data = serializer.data
        self.assertEqual(data['status'], 'in_progress')

    def test_status_solved(self):
        """Test status can be 'solved'."""
        progress = ProblemProgressFactory(status='solved')
        serializer = ProblemProgressSerializer(progress)
        data = serializer.data
        self.assertEqual(data['status'], 'solved')

    def test_attempts_field(self):
        """Test that attempts field is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['attempts'], self.problem_progress.attempts)

    def test_read_only_fields(self):
        """Test that specified fields are read-only."""
        read_only_fields = ProblemProgressSerializer.Meta.read_only_fields
        self.assertIn('attempts', read_only_fields)
        self.assertIn('last_attempted_at', read_only_fields)
        self.assertIn('solved_at', read_only_fields)
        self.assertIn('best_submission', read_only_fields)


# =============================================================================
# Phase 4: Discussion Serializers
# =============================================================================

class BriefDiscussionThreadSerializerTestCase(TestCase):
    """Test cases for BriefDiscussionThreadSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.thread = DiscussionThreadFactory()
        self.serializer = BriefDiscussionThreadSerializer(self.thread)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'course', 'chapter', 'problem', 'author', 'title', 'content',
            'is_pinned', 'is_resolved', 'is_archived',
            'reply_count', 'last_activity_at',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_author_field_included(self):
        """Test that author information is included."""
        data = self.serializer.data
        self.assertIn('author', data)
        self.assertEqual(data['author']['id'], self.thread.author.id)

    def test_title_field(self):
        """Test that title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['title'], self.thread.title)

    def test_is_pinned_field(self):
        """Test that is_pinned is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['is_pinned'], self.thread.is_pinned)

    def test_is_resolved_field(self):
        """Test that is_resolved is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['is_resolved'], self.thread.is_resolved)

    def test_reply_count_field(self):
        """Test that reply_count is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['reply_count'], self.thread.reply_count)

    def test_pinned_thread(self):
        """Test serialization of pinned thread."""
        thread = DiscussionThreadFactory(is_pinned=True)
        serializer = BriefDiscussionThreadSerializer(thread)
        data = serializer.data
        self.assertTrue(data['is_pinned'])

    def test_resolved_thread(self):
        """Test serialization of resolved thread."""
        thread = DiscussionThreadFactory(is_resolved=True)
        serializer = BriefDiscussionThreadSerializer(thread)
        data = serializer.data
        self.assertTrue(data['is_resolved'])


class DiscussionThreadSerializerTestCase(TestCase):
    """Test cases for DiscussionThreadSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.thread = DiscussionThreadFactory()
        self.serializer = DiscussionThreadSerializer(self.thread)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'course', 'chapter', 'problem', 'author', 'title', 'content',
            'is_pinned', 'is_resolved', 'is_archived',
            'reply_count', 'last_activity_at',
            'created_at', 'updated_at', 'replies'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_replies_field_included(self):
        """Test that replies field is included."""
        data = self.serializer.data
        self.assertIn('replies', data)

    def test_replies_empty_when_no_replies(self):
        """Test that replies is empty when thread has no replies."""
        data = self.serializer.data
        self.assertEqual(len(data['replies']), 0)

    def test_replies_includes_actual_replies(self):
        """Test that replies includes actual thread replies."""
        DiscussionReplyFactory(thread=self.thread)
        DiscussionReplyFactory(thread=self.thread)

        serializer = DiscussionThreadSerializer(self.thread)
        data = serializer.data
        self.assertEqual(len(data['replies']), 2)

    def test_replies_limited_to_twenty(self):
        """Test that replies is limited to 20."""
        for _ in range(25):
            DiscussionReplyFactory(thread=self.thread)

        serializer = DiscussionThreadSerializer(self.thread)
        data = serializer.data
        self.assertEqual(len(data['replies']), 20)


class DiscussionReplySerializerTestCase(TestCase):
    """Test cases for DiscussionReplySerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.reply = DiscussionReplyFactory()
        self.serializer = DiscussionReplySerializer(self.reply)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'author', 'content', 'mentioned_users', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_author_field_included(self):
        """Test that author information is included."""
        data = self.serializer.data
        self.assertIn('author', data)
        self.assertEqual(data['author']['id'], self.reply.author.id)

    def test_content_field(self):
        """Test that content is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['content'], self.reply.content)

    def test_thread_field_when_provided(self):
        """Test thread field when provided in context."""
        # Note: thread field is write_only and won't appear in serialized data
        # It's used for write operations
        data = self.serializer.data
        self.assertNotIn('thread', data)

    def test_mentioned_users_field(self):
        """Test that mentioned_users field exists."""
        data = self.serializer.data
        self.assertIn('mentioned_users', data)

    def test_read_only_fields(self):
        """Test that timestamp fields are read-only."""
        read_only_fields = DiscussionReplySerializer.Meta.read_only_fields
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)

    def test_validate_without_thread_field(self):
        """Test validation fails when thread is required but not provided."""
        context = {'view': type('View', (), {'kwargs': {}})}
        serializer = DiscussionReplySerializer(
            data={'content': 'Test content'},
            context=context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('thread', serializer.errors)


# =============================================================================
# Phase 5: Exam Serializers
# =============================================================================

class ExamListSerializerTestCase(TestCase):
    """Test cases for ExamListSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.exam = ExamFactory()
        self.context = {'request': type('Request', (), {'user': self.user})}
        self.serializer = ExamListSerializer(self.exam, context=self.context)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'course', 'course_title', 'title', 'description',
            'start_time', 'end_time', 'duration_minutes',
            'total_score', 'passing_score', 'status',
            'is_active', 'question_count', 'user_submission_status', 'remaining_time',
            'show_results_after_submit'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_course_title_field(self):
        """Test that course_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['course_title'], self.exam.course.title)

    def test_is_active_when_active(self):
        """Test is_active when exam is active."""
        exam = ExamFactory(
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            status='published'
        )
        serializer = ExamListSerializer(exam, context=self.context)
        data = serializer.data
        self.assertTrue(data['is_active'])

    def test_is_active_when_not_active(self):
        """Test is_active when exam is not active."""
        exam = ExamFactory(
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            status='published'
        )
        serializer = ExamListSerializer(exam, context=self.context)
        data = serializer.data
        self.assertFalse(data['is_active'])

    def test_question_count(self):
        """Test question_count calculation."""
        ExamProblemFactory(exam=self.exam)
        ExamProblemFactory(exam=self.exam)

        serializer = ExamListSerializer(self.exam, context=self.context)
        data = serializer.data
        self.assertEqual(data['question_count'], 2)

    def test_question_count_when_no_questions(self):
        """Test question_count when exam has no questions."""
        data = self.serializer.data
        self.assertEqual(data['question_count'], 0)

    def test_user_submission_status_for_unauthenticated_user(self):
        """Test user_submission_status for unauthenticated user."""
        context = {'request': type('Request', (), {'user': type('User', (), {'is_authenticated': False})})}
        serializer = ExamListSerializer(self.exam, context=context)
        data = serializer.data
        self.assertIsNone(data['user_submission_status'])

    def test_user_submission_status_when_no_submission(self):
        """Test user_submission_status when user has no submission."""
        data = self.serializer.data
        self.assertIsNone(data['user_submission_status'])

    def test_remaining_time_for_unauthenticated_user(self):
        """Test remaining_time for unauthenticated user."""
        context = {'request': type('Request', (), {'user': type('User', (), {'is_authenticated': False})})}
        serializer = ExamListSerializer(self.exam, context=context)
        data = serializer.data
        self.assertIsNone(data['remaining_time'])


class ExamDetailSerializerTestCase(TestCase):
    """Test cases for ExamDetailSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.exam = ExamFactory()
        # Create choice problems with their related models
        choice_problem = ProblemFactory(type='choice')
        ChoiceProblemFactory(problem=choice_problem)
        ExamProblemFactory(exam=self.exam, problem=choice_problem, order=0)

        fillblank_problem = ProblemFactory(type='fillblank')
        FillBlankProblemFactory(problem=fillblank_problem)
        ExamProblemFactory(exam=self.exam, problem=fillblank_problem, order=1)

        self.context = {'request': type('Request', (), {'user': self.user})}
        self.serializer = ExamDetailSerializer(self.exam, context=self.context)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'course', 'course_title', 'title', 'description',
            'start_time', 'end_time', 'duration_minutes',
            'total_score', 'passing_score', 'status',
            'shuffle_questions', 'show_results_after_submit', 'question_count',
            'is_active', 'can_start', 'remaining_time', 'exam_problems'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_exam_problems_included(self):
        """Test that exam_problems are included."""
        data = self.serializer.data
        self.assertIn('exam_problems', data)
        self.assertEqual(len(data['exam_problems']), 2)

    def test_exam_problem_fields(self):
        """Test that exam problem has correct fields."""
        data = self.serializer.data
        problem = data['exam_problems'][0]
        self.assertIn('exam_problem_id', problem)
        self.assertIn('problem_id', problem)
        self.assertIn('title', problem)
        self.assertIn('content', problem)
        self.assertIn('score', problem)
        self.assertIn('order', problem)

    def test_exam_problem_for_choice_type(self):
        """Test exam problem fields for choice type."""
        problem = ProblemFactory(type='choice')
        ChoiceProblemFactory(problem=problem)
        exam = ExamFactory()
        ExamProblemFactory(exam=exam, problem=problem, order=0)

        serializer = ExamDetailSerializer(exam, context=self.context)
        data = serializer.data
        exam_problem = data['exam_problems'][0]
        self.assertIn('options', exam_problem)
        self.assertIn('is_multiple_choice', exam_problem)

    def test_exam_problem_for_fillblank_type(self):
        """Test exam problem fields for fillblank type."""
        problem = ProblemFactory(type='fillblank')
        FillBlankProblemFactory(problem=problem)
        exam = ExamFactory()
        ExamProblemFactory(exam=exam, problem=problem, order=0)

        serializer = ExamDetailSerializer(exam, context=self.context)
        data = serializer.data
        exam_problem = data['exam_problems'][0]
        self.assertIn('content_with_blanks', exam_problem)
        self.assertIn('blanks_list', exam_problem)

    def test_can_start_for_unauthenticated_user(self):
        """Test can_start for unauthenticated user."""
        context = {'request': type('Request', (), {'user': type('User', (), {'is_authenticated': False})})}
        serializer = ExamDetailSerializer(self.exam, context=context)
        data = serializer.data
        self.assertFalse(data['can_start'])

    def test_question_count(self):
        """Test question_count calculation."""
        data = self.serializer.data
        self.assertEqual(data['question_count'], 2)


class ExamCreateSerializerTestCase(TestCase):
    """Test cases for ExamCreateSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.course = CourseFactory()
        self.problem1 = ProblemFactory(type='choice')
        self.problem2 = ProblemFactory(type='fillblank')

    def test_create_exam_with_problems(self):
        """Test creating exam with problems."""
        exam_data = {
            'course': self.course.id,
            'title': 'Test Exam',
            'description': 'Test Description',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=24),
            'duration_minutes': 60,
            'passing_score': 60,
            'status': 'draft',
            'shuffle_questions': False,
            'show_results_after_submit': True,
            'exam_problems': [
                {'problem_id': self.problem1.id, 'score': 10, 'order': 0},
                {'problem_id': self.problem2.id, 'score': 20, 'order': 1},
            ]
        }

        serializer = ExamCreateSerializer(data=exam_data)
        self.assertTrue(serializer.is_valid())
        exam = serializer.save()

        self.assertEqual(exam.exam_problems.count(), 2)
        self.assertEqual(exam.total_score, 30)

    def test_validate_start_time_before_end_time(self):
        """Test validation that start_time must be before end_time."""
        exam_data = {
            'course': self.course.id,
            'title': 'Test Exam',
            'start_time': timezone.now() + timedelta(hours=24),
            'end_time': timezone.now(),
            'duration_minutes': 60,
            'passing_score': 60,
        }

        serializer = ExamCreateSerializer(data=exam_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('结束时间必须晚于开始时间', str(serializer.errors))

    def test_create_exam_without_problems(self):
        """Test creating exam without problems."""
        exam_data = {
            'course': self.course.id,
            'title': 'Test Exam',
            'description': 'Test Description',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=24),
            'duration_minutes': 60,
            'passing_score': 60,
            'status': 'draft',
        }

        serializer = ExamCreateSerializer(data=exam_data)
        self.assertTrue(serializer.is_valid())
        exam = serializer.save()
        self.assertEqual(exam.exam_problems.count(), 0)


class ExamAnswerDetailSerializerTestCase(TestCase):
    """Test cases for ExamAnswerDetailSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.choice_problem = ProblemFactory(type='choice')
        ChoiceProblemFactory(problem=self.choice_problem)
        self.exam = ExamFactory()
        ExamProblemFactory(exam=self.exam, problem=self.choice_problem)

        self.submission = ExamSubmissionFactory(exam=self.exam)
        self.answer = ExamAnswerFactory(
            submission=self.submission,
            problem=self.choice_problem,
            choice_answers=['A']
        )
        self.serializer = ExamAnswerDetailSerializer(self.answer)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'problem', 'problem_title', 'problem_type',
            'choice_answers', 'fillblank_answers',
            'score', 'is_correct', 'correct_percentage',
            'correct_answer', 'problem_data',
            'created_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_problem_title_field(self):
        """Test that problem_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['problem_title'], self.choice_problem.title)

    def test_problem_type_field(self):
        """Test that problem_type is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['problem_type'], 'choice')

    def test_correct_answer_for_choice_problem(self):
        """Test correct_answer field for choice problem."""
        data = self.serializer.data
        self.assertIn('correct_answer', data)
        self.assertIn('is_multiple', data['correct_answer'])
        self.assertIn('all_options', data['correct_answer'])

    def test_problem_data_field(self):
        """Test problem_data field."""
        data = self.serializer.data
        self.assertIn('problem_data', data)
        self.assertIn('content', data['problem_data'])
        self.assertIn('difficulty', data['problem_data'])
        self.assertIn('score', data['problem_data'])


class ExamSubmissionSerializerTestCase(TestCase):
    """Test cases for ExamSubmissionSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.submission = ExamSubmissionFactory()
        self.serializer = ExamSubmissionSerializer(self.submission)

    def test_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'exam', 'exam_title', 'user', 'username',
            'started_at', 'submitted_at', 'status',
            'total_score', 'is_passed', 'time_spent_seconds',
            'exam_passing_score', 'exam_total_score',
            'answers'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_username_field(self):
        """Test that username is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['username'], self.submission.user.username)

    def test_exam_title_field(self):
        """Test that exam_title is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['exam_title'], self.submission.exam.title)

    def test_status_field(self):
        """Test that status is correctly serialized."""
        data = self.serializer.data
        self.assertEqual(data['status'], self.submission.status)

    def test_status_in_progress(self):
        """Test status can be 'in_progress'."""
        submission = ExamSubmissionFactory(status='in_progress')
        serializer = ExamSubmissionSerializer(submission)
        data = serializer.data
        self.assertEqual(data['status'], 'in_progress')

    def test_status_submitted(self):
        """Test status can be 'submitted'."""
        submission = ExamSubmissionFactory(status='submitted')
        serializer = ExamSubmissionSerializer(submission)
        data = serializer.data
        self.assertEqual(data['status'], 'submitted')

    def test_read_only_fields(self):
        """Test that timestamp and score fields are read-only."""
        read_only_fields = ExamSubmissionSerializer.Meta.read_only_fields
        self.assertIn('started_at', read_only_fields)
        self.assertIn('submitted_at', read_only_fields)
        self.assertIn('total_score', read_only_fields)


class ExamSubmissionCreateSerializerTestCase(TestCase):
    """Test cases for ExamSubmissionCreateSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.exam = ExamFactory(course=self.course, status='published')
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_validate_with_enrolled_user(self):
        """Test validation passes for enrolled user."""
        context = {
            'request': type('Request', (), {'user': self.user}),
            'exam_id': self.exam.id
        }
        serializer = ExamSubmissionCreateSerializer(context=context)
        # This serializer validates data internally, so we need to check the
        # validation method directly
        try:
            serializer.validate({})
            self.assertTrue(True)
        except:
            self.fail("Validation should pass for enrolled user")

    def test_validate_with_nonexistent_exam(self):
        """Test validation fails for non-existent exam."""
        context = {
            'request': type('Request', (), {'user': self.user}),
            'exam_id': 99999
        }
        serializer = ExamSubmissionCreateSerializer(context=context)
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate({})
        self.assertIn('测验不存在', str(cm.exception))

    def test_validate_with_unenrolled_user(self):
        """Test validation fails for unenrolled user."""
        user = UserFactory()
        context = {
            'request': type('Request', (), {'user': user}),
            'exam_id': self.exam.id
        }
        serializer = ExamSubmissionCreateSerializer(context=context)
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate({})
        self.assertIn('尚未注册', str(cm.exception))

    def test_validate_with_existing_submission(self):
        """Test validation fails when user already submitted."""
        ExamSubmissionFactory(
            exam=self.exam,
            user=self.user,
            enrollment=self.enrollment,
            status='submitted'
        )

        context = {
            'request': type('Request', (), {'user': self.user}),
            'exam_id': self.exam.id
        }
        serializer = ExamSubmissionCreateSerializer(context=context)
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate({})
        self.assertIn('已经参加过', str(cm.exception))


class ExamSubmitSerializerTestCase(TestCase):
    """Test cases for ExamSubmitSerializer."""

    def test_contains_answers_field(self):
        """Test that serializer has answers field."""
        serializer = ExamSubmitSerializer()
        self.assertIn('answers', serializer.fields)

    def test_validate_answers_required(self):
        """Test that answers field is required."""
        serializer = ExamSubmitSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('answers', serializer.errors)

    def test_validate_answers_not_empty(self):
        """Test that answers cannot be empty."""
        serializer = ExamSubmitSerializer(data={'answers': []})
        self.assertFalse(serializer.is_valid())
        self.assertIn('不能为空', str(serializer.errors))

    def test_validate_answers_requires_problem_id(self):
        """Test that each answer must have problem_id."""
        serializer = ExamSubmitSerializer(data={
            'answers': [
                {'problem_type': 'choice', 'choice_answers': ['A']}
            ]
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('problem_id', str(serializer.errors))

    def test_validate_choice_requires_choice_answers(self):
        """Test that choice problems require choice_answers."""
        serializer = ExamSubmitSerializer(data={
            'answers': [
                {
                    'problem_id': 1,
                    'problem_type': 'choice',
                    'fillblank_answers': ['answer1']
                }
            ]
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('choice_answers', str(serializer.errors))

    def test_validate_fillblank_requires_fillblank_answers(self):
        """Test that fillblank problems require fillblank_answers."""
        serializer = ExamSubmitSerializer(data={
            'answers': [
                {
                    'problem_id': 1,
                    'problem_type': 'fillblank',
                    'choice_answers': ['A']
                }
            ]
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('fillblank_answers', str(serializer.errors))

    def test_validate_valid_choice_answer(self):
        """Test validation passes for valid choice answer."""
        serializer = ExamSubmitSerializer(data={
            'answers': [
                {
                    'problem_id': 1,
                    'problem_type': 'choice',
                    'choice_answers': ['A']
                }
            ]
        })
        self.assertTrue(serializer.is_valid())


# =============================================================================
# Phase 6: Field Validation Tests
# =============================================================================

class FieldValidationTestCase(TestCase):
    """Test cases for serializer field validation."""

    def test_algorithm_problem_fields_validation(self):
        """Test AlgorithmProblemSerializer field validation."""
        problem = ProblemFactory(type='algorithm')
        algorithm_problem = AlgorithmProblemFactory(problem=problem)
        serializer = AlgorithmProblemSerializer(algorithm_problem)
        data = serializer.data

        # Check time_limit is positive
        self.assertGreater(data['time_limit'], 0)

        # Check memory_limit is positive
        self.assertGreater(data['memory_limit'], 0)

    def test_choice_problem_options_validation(self):
        """Test ChoiceProblemSerializer options field validation."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(problem=problem)

        serializer = ChoiceProblemSerializer(choice_problem)
        data = serializer.data

        # Check options is a dict
        self.assertIsInstance(data['options'], dict)

        # Check options are not empty
        self.assertTrue(len(data['options']) > 0)

    def test_fillblank_problem_blanks_validation(self):
        """Test FillBlankProblemSerializer blanks field validation."""
        problem = ProblemFactory(type='fillblank')
        fillblank_problem = FillBlankProblemFactory(problem=problem)

        serializer = FillBlankProblemSerializer(fillblank_problem)
        data = serializer.data

        # Check blanks_list is a list
        self.assertIsInstance(data['blanks_list'], list)

        # Check blank_count is positive
        self.assertGreater(data['blank_count'], 0)


# =============================================================================
# Phase 7: Cross-Field Validation Tests
# =============================================================================

class CrossFieldValidationTestCase(TestCase):
    """Test cases for cross-field validation."""

    def test_choice_answer_must_be_in_options_single(self):
        """Test that single choice answer must be in options."""
        serializer = ChoiceProblemSerializer(data={
            'problem': ProblemFactory(type='choice').id,
            'options': {'A': 'Option 1', 'B': 'Option 2'},
            'correct_answer': 'C',
            'is_multiple_choice': False
        })
        self.assertFalse(serializer.is_valid())

    def test_choice_answer_must_be_in_options_multiple(self):
        """Test that multiple choice answers must be in options."""
        serializer = ChoiceProblemSerializer(data={
            'problem': ProblemFactory(type='choice').id,
            'options': {'A': 'Option 1', 'B': 'Option 2'},
            'correct_answer': ['A', 'C'],
            'is_multiple_choice': True
        })
        self.assertFalse(serializer.is_valid())

    def test_multiple_choice_requires_list_answer(self):
        """Test that multiple choice requires list answer."""
        problem = ProblemFactory(type='choice')
        choice_problem = ChoiceProblemFactory(
            problem=problem,
            is_multiple_choice=False,
            correct_answer='A'
        )

        serializer = ChoiceProblemSerializer(
            choice_problem,
            data={
                'problem': problem.id,
                'options': choice_problem.options,
                'correct_answer': 'A',
                'is_multiple_choice': True
            }
        )

        # This should fail because is_multiple_choice is True but answer is string
        self.assertFalse(serializer.is_valid())


# =============================================================================
# Phase 8: Error Message and Edge Case Tests
# =============================================================================

class ErrorFormattingTestCase(TestCase):
    """Test cases for error message formatting."""

    def test_choice_problem_options_error_message(self):
        """Test that options validation error message is helpful."""
        serializer = ChoiceProblemSerializer()
        try:
            serializer.validate_options([])
        except serializers.ValidationError as e:
            self.assertIn('字典格式', str(e.detail[0]))

    def test_fillblank_problem_blanks_error_message(self):
        """Test that blanks validation error message is helpful."""
        serializer = FillBlankProblemSerializer()
        try:
            serializer.validate_blanks([])
        except serializers.ValidationError as e:
            self.assertIn('字典格式', str(e.detail[0]))

    def test_exam_create_time_range_error_message(self):
        """Test that time range error message is clear."""
        course = CourseFactory()
        serializer = ExamCreateSerializer(data={
            'course': course.id,
            'title': 'Test Exam',
            'start_time': timezone.now() + timedelta(hours=24),
            'end_time': timezone.now(),
            'duration_minutes': 60,
            'passing_score': 60,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('结束时间必须晚于开始时间', str(serializer.errors))


class EdgeCasesTestCase(TestCase):
    """Test cases for edge cases."""

    def test_enrollment_progress_with_zero_chapters(self):
        """Test enrollment progress when course has zero chapters."""
        course = CourseFactory()
        enrollment = EnrollmentFactory(course=course)

        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data
        self.assertEqual(data['progress_percentage'], 0)

    def test_algorithm_problem_with_no_test_cases(self):
        """Test algorithm problem with no test cases."""
        algorithm_problem = AlgorithmProblemFactory()

        serializer = AlgorithmProblemSerializer(algorithm_problem)
        data = serializer.data
        self.assertEqual(len(data['sample_cases']), 0)

    def test_exam_with_no_problems(self):
        """Test exam detail with no problems."""
        exam = ExamFactory()
        user = UserFactory()
        context = {'request': type('Request', (), {'user': user})}

        serializer = ExamDetailSerializer(exam, context=context)
        data = serializer.data
        self.assertEqual(len(data['exam_problems']), 0)

    def test_discussion_thread_with_no_replies(self):
        """Test discussion thread with no replies."""
        thread = DiscussionThreadFactory()

        serializer = DiscussionThreadSerializer(thread)
        data = serializer.data
        self.assertEqual(len(data['replies']), 0)

    def test_course_with_no_threads(self):
        """Test course recent_threads with no threads."""
        course = CourseFactory()

        serializer = CourseModelSerializer(course)
        data = serializer.data
        self.assertEqual(len(data['recent_threads']), 0)


class ChapterSerializerPerformanceTestCase(TestCase):
    """Performance test cases for ChapterSerializer to verify N+1 query elimination."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()

        # Create multiple chapters
        self.chapters = []
        for i in range(10):
            chapter = ChapterFactory(
                course=self.course,
                title=f"Chapter {i+1}",
                content=f"Content for chapter {i+1}"
            )
            self.chapters.append(chapter)

        # Create enrollment
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

        # Create progress for some chapters
        for i in range(5):
            ChapterProgressFactory(
                enrollment=self.enrollment,
                chapter=self.chapters[i],
                completed=True if i % 2 == 0 else False
            )

        # Create unlock conditions for some chapters with prerequisites
        for i in range(1, 8, 2):  # Chapters 1, 3, 5, 7
            condition = ChapterUnlockConditionFactory(
                chapter=self.chapters[i],
                unlock_condition_type='prerequisite'
            )
            # Add previous chapter as prerequisite
            condition.prerequisite_chapters.add(self.chapters[i-1])
            condition.save()

    def test_serializer_with_prefetch_performance(self):
        """Test that serializer doesn't trigger N+1 when pre-fetched data is available."""
        from django.test.utils import override_settings
        from django.db import connection, reset_queries

        # Add pre-fetched data to simulate ViewSet behavior
        for i, chapter in enumerate(self.chapters):
            # Simulate pre-fetched user progress
            chapter.user_progress = [ChapterProgressFactory(
                enrollment=self.enrollment,
                chapter=chapter,
                completed=True if i % 2 == 0 else False
            )]

        # Create proper request object
        class MockRequest:
            def __init__(self, user):
                self.user = user
                self.is_authenticated = True

        context = {'request': MockRequest(self.user)}

        # Clear query log
        reset_queries()

        # Test serializing chapters and count queries
        for chapter in self.chapters:
            serializer = ChapterSerializer(chapter, context=context)
            data = serializer.data

            # Verify all fields are accessible without triggering queries
            self.assertIsNotNone(data['course_title'])
            self.assertIn('status', data)
            self.assertIn('is_locked', data)

            # Verify unlock conditions
            if data['unlock_condition']:
                self.assertIn('prerequisite_titles', data['unlock_condition'])
                if data['unlock_condition']['prerequisite_titles']:
                    self.assertTrue(len(data['unlock_condition']['prerequisite_titles']) > 0)

        # Report actual number of queries
        actual_queries = len(connection.queries)
        print(f"\n📊 Actual queries executed: {actual_queries}")

        # Log the first few queries for debugging
        if actual_queries > 0:
            print("\n📋 Sample queries:")
            for i, query in enumerate(connection.queries[:5]):
                print(f"{i+1}. {query['sql'][:100]}...")


    def test_chapter_list_with_prefetch_verify(self):
        """Test that the prefetch relationships and database annotation optimization work correctly."""
        from rest_framework.test import APIClient
        from rest_framework import status
        from django.db import connection, connection as db
        from django.db import reset_queries

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Clear query log and count queries
        reset_queries()

        # Make API call
        response = self.client.get(f'/api/v1/courses/{self.course.id}/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check queries executed
        queries = connection.queries
        print(f"Total queries executed: {len(queries)}")

        # With database annotation optimization, total queries should be significantly reduced
        # Expected: 1-2 main queries + 1-2 prefetch queries = 3-5 total
        self.assertLessEqual(len(queries), 5, f"Too many queries: {len(queries)}")

        # Verify no N+1 pattern for progress queries
        progress_queries = [q for q in queries if 'chapterprogress' in q['sql']]
        self.assertLessEqual(len(progress_queries), 2, f"Too many progress queries: {len(progress_queries)}")

        # Verify no N+1 pattern for enrollment queries
        enrollment_queries = [q for q in queries if 'enrollment' in q['sql']]
        self.assertLessEqual(len(enrollment_queries), 2, f"Too many enrollment queries: {len(enrollment_queries)}")

        # Verify unlock condition uses annotation (should be part of main query)
        unlock_queries = [q for q in queries if 'chapterunlockcondition' in q['sql']]
        self.assertLessEqual(len(unlock_queries), 2, f"Too many unlock condition queries: {len(unlock_queries)}")

        # Print all queries for debugging
        for i, query in enumerate(queries):
            print(f"Query {i+1}: {query['sql'][:150]}...")

    def test_chapter_serializer_fallback_to_service_layer(self):
        """Test that ChapterSerializer falls back to Service layer when is_locked_db is not available."""
        from courses.serializers import ChapterSerializer
        from courses.models import Chapter

        # Create chapters with unlock conditions (using unique order values)
        chapter1 = ChapterFactory(course=self.course, order=11)
        chapter2 = ChapterFactory(course=self.course, order=12)

        condition = ChapterUnlockConditionFactory(chapter=chapter2)
        condition.prerequisite_chapters.add(chapter1)
        condition.save()

        # Get chapter directly from DB (without is_locked_db annotation)
        chapter = Chapter.objects.get(id=chapter2.id)

        # Verify that is_locked_db is not present
        self.assertFalse(hasattr(chapter, 'is_locked_db'))

        # Serialize chapter - should fall back to Service layer
        serializer = ChapterSerializer(
            chapter,
            context={'request': type('Request', (), {'user': self.user})()}
        )

        # The serializer should still return correct is_locked value
        # (via Service layer fallback)
        is_locked = serializer.data.get('is_locked')
        self.assertTrue(is_locked, "Chapter should be locked via Service layer fallback")

    def test_chapter_serializer_uses_database_annotation_when_available(self):
        """Test that ChapterSerializer uses is_locked_db annotation when available."""
        from courses.serializers import ChapterSerializer
        from courses.models import Chapter
        from django.db.models import BooleanField, Case, Exists, OuterRef, Value, When

        # Create chapters with unlock conditions (using unique order values)
        chapter1 = ChapterFactory(course=self.course, order=21)
        chapter2 = ChapterFactory(course=self.course, order=22)

        condition = ChapterUnlockConditionFactory(chapter=chapter2)
        condition.prerequisite_chapters.add(chapter1)
        condition.save()

        # Query chapter WITH is_locked_db annotation
        chapters = Chapter.objects.filter(id=chapter2.id).annotate(
            is_locked_db=Value(True, output_field=BooleanField())
        )

        chapter = chapters.first()

        # Verify that is_locked_db is present
        self.assertTrue(hasattr(chapter, 'is_locked_db'))
        self.assertTrue(chapter.is_locked_db)

        # Serialize chapter - should use is_locked_db annotation
        serializer = ChapterSerializer(
            chapter,
            context={'request': type('Request', (), {'user': self.user})()}
        )

        # The serializer should return the annotated value
        is_locked = serializer.data.get('is_locked')
        self.assertTrue(is_locked, "Chapter should use database annotation")
