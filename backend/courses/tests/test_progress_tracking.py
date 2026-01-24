"""
Progress tracking tests for the courses app.

Tests for enrollment, chapter progress, and problem progress functionality.
"""
from django.contrib.auth import get_user_model

from courses.models import (
    Course, Chapter, Problem, AlgorithmProblem,
    ChoiceProblem, Enrollment, ChapterProgress, ProblemProgress
)
from courses.tests.conftest import CoursesTestCase
from courses.tests.factories import (
    CourseFactory,
    ChapterFactory,
    ProblemFactory,
    AlgorithmProblemFactory,
    ChoiceProblemFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
    ProblemProgressFactory,
)
from accounts.tests.factories import UserFactory

User = get_user_model()


class ProgressTrackingTestCase(CoursesTestCase):
    """Test case for progress tracking functionality."""

    def setUp(self):
        """Set up test data using factories."""
        super().setUp()

        # Create test user
        self.user = UserFactory()

        # Create test course
        self.course = CourseFactory(
            title='Test Course',
            description='A test course for progress tracking'
        )

        # Create test chapter
        self.chapter = ChapterFactory(
            course=self.course,
            title='Test Chapter',
            content='A test chapter',
            order=1
        )

        # Create test algorithm problem
        self.problem = ProblemFactory(
            chapter=self.chapter,
            type='algorithm',
            title='Test Problem',
            content='A test algorithm problem',
            difficulty=2
        )
        self.algorithm_problem = AlgorithmProblemFactory(
            problem=self.problem,
            time_limit=1000,
            memory_limit=256
        )

        # Create test choice problem
        self.choice_problem = ProblemFactory(
            chapter=self.chapter,
            type='choice',
            title='Test Choice Problem',
            content='A test choice problem',
            difficulty=1
        )
        self.choice_problem_detail = ChoiceProblemFactory(
            problem=self.choice_problem,
            options={'A': 'Option A', 'B': 'Option B', 'C': 'Option C'},
            correct_answer='A'
        )

    def test_enrollment_creation(self):
        """测试课程参与记录创建"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )

        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.course, self.course)
        self.assertIsNotNone(enrollment.enrolled_at)
        self.assertIsNotNone(enrollment.last_accessed_at)

        # 测试唯一约束
        with self.assertRaises(Exception):
            Enrollment.objects.create(
                user=self.user,
                course=self.course
            )

    def test_chapter_progress(self):
        """测试章节进度记录"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )

        chapter_progress = ChapterProgress.objects.create(
            enrollment=enrollment,
            chapter=self.chapter,
            completed=True
        )

        self.assertTrue(chapter_progress.completed)
        # self.assertIsNotNone(chapter_progress.completed_at)
        self.assertEqual(str(chapter_progress), f"{self.user.username} - {self.chapter.title} - 已完成")

    def test_problem_progress(self):
        """测试问题进度记录"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )

        problem_progress = ProblemProgress.objects.create(
            enrollment=enrollment,
            problem=self.problem,
            status='solved'
        )

        self.assertEqual(problem_progress.status, 'solved')
        self.assertEqual(problem_progress.attempts, 0)
        self.assertIsNone(problem_progress.solved_at)

        # 更新尝试次数
        problem_progress.attempts = 1
        problem_progress.save()
