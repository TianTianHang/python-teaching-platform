"""
Factory Boy definitions for courses app test data.
"""
import factory
from factory import django, fuzzy
from django.utils import timezone
from faker import Faker

from courses.models import (
    Course, Chapter, Problem, ProblemUnlockCondition, ChapterUnlockCondition,
    AlgorithmProblem, ChoiceProblem, FillBlankProblem,
    TestCase as CourseTestCase, Submission, CodeDraft,
    Enrollment, ChapterProgress, ProblemProgress,
    DiscussionThread, DiscussionReply,
    Exam, ExamProblem, ExamSubmission, ExamAnswer,
)
from accounts.models import User

fake = Faker()


# ============================================================================
# Core Models
# ============================================================================

class CourseFactory(django.DjangoModelFactory):
    """Factory for creating Course instances."""

    class Meta:
        model = Course

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=3)


class ChapterFactory(django.DjangoModelFactory):
    """Factory for creating Chapter instances."""

    class Meta:
        model = Chapter

    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('sentence', nb_words=3)
    content = factory.Faker('paragraph', nb_sentences=2)
    order = factory.Sequence(lambda n: n)


class ProblemFactory(django.DjangoModelFactory):
    """Factory for creating Problem instances."""

    class Meta:
        model = Problem

    chapter = factory.SubFactory(ChapterFactory)
    type = fuzzy.FuzzyChoice(['algorithm', 'choice', 'fillblank'])
    title = factory.Faker('sentence', nb_words=5)
    content = factory.Faker('paragraph', nb_sentences=2)
    difficulty = fuzzy.FuzzyInteger(1, 3)

    class Params:
        # Trait for algorithm problems
        algorithm = factory.Trait(
            type='algorithm',
        )
        # Trait for choice problems
        choice = factory.Trait(
            type='choice',
        )
        # Trait for fill-blank problems
        fillblank = factory.Trait(
            type='fillblank',
        )


# ============================================================================
# Problem Type Models
# ============================================================================

class AlgorithmProblemFactory(django.DjangoModelFactory):
    """Factory for creating AlgorithmProblem instances."""

    class Meta:
        model = AlgorithmProblem

    problem = factory.SubFactory(ProblemFactory, type='algorithm')
    time_limit = 1000
    memory_limit = 256
    code_template = None
    solution_name = None


class ChoiceProblemFactory(django.DjangoModelFactory):
    """Factory for creating ChoiceProblem instances."""

    class Meta:
        model = ChoiceProblem

    problem = factory.SubFactory(ProblemFactory, type='choice')
    options = factory.LazyFunction(
        lambda: {
            'A': fake.sentence(),
            'B': fake.sentence(),
            'C': fake.sentence(),
            'D': fake.sentence(),
        }
    )
    correct_answer = 'A'
    is_multiple_choice = False

    class Params:
        # Trait for multiple choice
        multiple = factory.Trait(
            is_multiple_choice=True,
            correct_answer=['A', 'C'],
        )


class FillBlankProblemFactory(django.DjangoModelFactory):
    """Factory for creating FillBlankProblem instances."""

    class Meta:
        model = FillBlankProblem

    problem = factory.SubFactory(ProblemFactory, type='fillblank')
    content_with_blanks = "Complete the [blank1] and [blank2]."
    blanks = factory.LazyFunction(
        lambda: {
            'blanks': [
                {'answers': [fake.word()], 'case_sensitive': False},
                {'answers': [fake.word()], 'case_sensitive': False},
            ]
        }
    )
    blank_count = 2


# ============================================================================
# Progress Models
# ============================================================================

class EnrollmentFactory(django.DjangoModelFactory):
    """Factory for creating Enrollment instances."""

    class Meta:
        model = Enrollment
        django_get_or_create = ('user', 'course')

    user = factory.SubFactory('accounts.tests.factories.UserFactory')
    course = factory.SubFactory(CourseFactory)


class ChapterProgressFactory(django.DjangoModelFactory):
    """Factory for creating ChapterProgress instances."""

    class Meta:
        model = ChapterProgress
        django_get_or_create = ('enrollment', 'chapter')

    enrollment = factory.SubFactory(EnrollmentFactory)
    chapter = factory.SubFactory(ChapterFactory)
    completed = False
    completed_at = None

    class Params:
        # Trait for completed chapters
        completed_chapter = factory.Trait(
            completed=True,
            completed_at=factory.LazyFunction(timezone.now),
        )


class ProblemProgressFactory(django.DjangoModelFactory):
    """Factory for creating ProblemProgress instances."""

    class Meta:
        model = ProblemProgress
        django_get_or_create = ('enrollment', 'problem')

    enrollment = factory.SubFactory(EnrollmentFactory)
    problem = factory.SubFactory(ProblemFactory)
    status = 'not_started'
    attempts = 0
    last_attempted_at = None
    solved_at = None
    best_submission = None

    class Params:
        # Trait for in-progress problems
        in_progress = factory.Trait(
            status='in_progress',
            attempts=fuzzy.FuzzyInteger(1, 5),
            last_attempted_at=factory.LazyFunction(timezone.now),
        )
        # Trait for solved problems
        solved = factory.Trait(
            status='solved',
            attempts=fuzzy.FuzzyInteger(1, 5),
            last_attempted_at=factory.LazyFunction(timezone.now),
            solved_at=factory.LazyFunction(timezone.now),
        )


# ============================================================================
# Submission Models
# ============================================================================

class SubmissionFactory(django.DjangoModelFactory):
    """Factory for creating Submission instances."""

    class Meta:
        model = Submission

    user = factory.SubFactory('accounts.tests.factories.UserFactory')
    problem = factory.SubFactory(ProblemFactory)
    code = factory.Faker('paragraph')
    language = 'python'
    status = 'pending'
    execution_time = None
    memory_used = None
    output = ''
    error = ''

    class Params:
        # Trait for accepted submissions
        accepted = factory.Trait(
            status='accepted',
            execution_time=fuzzy.FuzzyFloat(10, 1000),
            memory_used=fuzzy.FuzzyFloat(1000, 10000),
        )
        # Trait for failed submissions
        wrong_answer = factory.Trait(
            status='wrong_answer',
        )


class CodeDraftFactory(django.DjangoModelFactory):
    """Factory for creating CodeDraft instances."""

    class Meta:
        model = CodeDraft

    user = factory.SubFactory('accounts.tests.factories.UserFactory')
    problem = factory.SubFactory(ProblemFactory, type='algorithm')
    code = factory.Faker('paragraph')
    language = 'python'
    save_type = 'auto_save'
    submission = None

    class Params:
        # Trait for manual save
        manual = factory.Trait(
            save_type='manual_save',
        )
        # Trait for submission drafts
        submission_draft = factory.Trait(
            save_type='submission',
            submission=factory.SubFactory(SubmissionFactory),
        )


class CourseTestCaseFactory(django.DjangoModelFactory):
    """Factory for creating TestCase instances."""

    class Meta:
        model = CourseTestCase

    problem = factory.SubFactory(AlgorithmProblemFactory)
    input_data = factory.Faker('paragraph')
    expected_output = factory.Faker('paragraph')
    is_sample = False

    class Params:
        # Trait for sample test cases
        sample = factory.Trait(
            is_sample=True,
        )


# ============================================================================
# Discussion Models
# ============================================================================

class DiscussionThreadFactory(django.DjangoModelFactory):
    """Factory for creating DiscussionThread instances."""

    class Meta:
        model = DiscussionThread

    course = factory.SubFactory(CourseFactory)
    chapter = None
    problem = None
    author = factory.SubFactory('accounts.tests.factories.UserFactory')
    title = factory.Faker('sentence', nb_words=6)
    content = factory.Faker('paragraph', nb_sentences=3)
    is_pinned = False
    is_resolved = False
    is_archived = False
    reply_count = 0

    class Params:
        # Trait for pinned threads
        pinned = factory.Trait(
            is_pinned=True,
        )
        # Trait for resolved threads
        resolved = factory.Trait(
            is_resolved=True,
        )


class DiscussionReplyFactory(django.DjangoModelFactory):
    """Factory for creating DiscussionReply instances."""

    class Meta:
        model = DiscussionReply

    thread = factory.SubFactory(DiscussionThreadFactory)
    author = factory.SubFactory('accounts.tests.factories.UserFactory')
    content = factory.Faker('paragraph', nb_sentences=2)


# ============================================================================
# Exam Models
# ============================================================================

class ExamFactory(django.DjangoModelFactory):
    """Factory for creating Exam instances."""

    class Meta:
        model = Exam

    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=2)
    start_time = factory.LazyFunction(timezone.now)
    end_time = factory.LazyAttribute(
        lambda o: timezone.now() + timezone.timedelta(hours=24)
    )
    duration_minutes = 60
    total_score = 100
    passing_score = 60
    status = 'draft'
    shuffle_questions = False
    show_results_after_submit = True

    class Params:
        # Trait for published exams
        published = factory.Trait(
            status='published',
        )
        # Trait for archived exams
        archived = factory.Trait(
            status='archived',
        )


class ExamProblemFactory(django.DjangoModelFactory):
    """Factory for creating ExamProblem instances."""

    class Meta:
        model = ExamProblem

    exam = factory.SubFactory(ExamFactory)
    problem = factory.SubFactory(ProblemFactory, type=fuzzy.FuzzyChoice(['choice', 'fillblank']))
    score = 10
    order = 0
    is_required = True


class ExamSubmissionFactory(django.DjangoModelFactory):
    """Factory for creating ExamSubmission instances."""

    class Meta:
        model = ExamSubmission
        django_get_or_create = ('exam', 'user')

    exam = factory.SubFactory(ExamFactory)
    enrollment = factory.SubFactory(EnrollmentFactory)
    user = factory.SubFactory('accounts.tests.factories.UserFactory')
    submitted_at = None
    status = 'in_progress'
    total_score = None
    is_passed = None
    time_spent_seconds = None

    class Params:
        # Trait for submitted exams
        submitted = factory.Trait(
            status='submitted',
            submitted_at=factory.LazyFunction(timezone.now),
        )
        # Trait for graded exams
        graded = factory.Trait(
            status='graded',
            submitted_at=factory.LazyFunction(timezone.now),
            total_score=fuzzy.FuzzyInteger(60, 100),
            is_passed=True,
        )


class ExamAnswerFactory(django.DjangoModelFactory):
    """Factory for creating ExamAnswer instances."""

    class Meta:
        model = ExamAnswer

    submission = factory.SubFactory(ExamSubmissionFactory)
    problem = factory.SubFactory(ProblemFactory)
    choice_answers = None
    fillblank_answers = None
    score = None
    is_correct = None
    correct_percentage = None

    class Params:
        # Trait for choice problem answers
        choice = factory.Trait(
            problem=factory.SubFactory(ProblemFactory, type='choice'),
            choice_answers=['A'],
        )
        # Trait for fill-blank problem answers
        fillblank = factory.Trait(
            problem=factory.SubFactory(ProblemFactory, type='fillblank'),
            fillblank_answers=['answer1', 'answer2'],
        )
        # Trait for graded answers
        graded = factory.Trait(
            score=fuzzy.FuzzyInteger(5, 10),
            is_correct=True,
            correct_percentage=100.0,
        )


# ============================================================================
# Other Models
# ============================================================================

class ProblemUnlockConditionFactory(django.DjangoModelFactory):
    """Factory for creating ProblemUnlockCondition instances."""

    class Meta:
        model = ProblemUnlockCondition

    problem = factory.SubFactory(ProblemFactory)
    unlock_date = None
    unlock_condition_type = 'none'

    class Params:
        # Trait for prerequisite-based unlock
        prerequisite = factory.Trait(
            unlock_condition_type='prerequisite',
        )
        # Trait for date-based unlock
        date_based = factory.Trait(
            unlock_condition_type='date',
            unlock_date=factory.LazyFunction(timezone.now),
        )
        # Trait for both conditions
        both = factory.Trait(
            unlock_condition_type='both',
            unlock_date=factory.LazyFunction(timezone.now),
        )


class ChapterUnlockConditionFactory(django.DjangoModelFactory):
    """Factory for creating ChapterUnlockCondition instances."""

    class Meta:
        model = ChapterUnlockCondition

    chapter = factory.SubFactory(ChapterFactory)
    unlock_date = None
    unlock_condition_type = 'all'

    class Params:
        # Trait for prerequisite-based unlock
        prerequisite_only = factory.Trait(
            unlock_condition_type='prerequisite',
        )
        # Trait for date-based unlock
        date_only = factory.Trait(
            unlock_condition_type='date',
            unlock_date=factory.LazyFunction(timezone.now),
        )
