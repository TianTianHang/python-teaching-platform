"""
Tests for ChapterUnlockService.

This test module covers the chapter unlock logic including:
- Unlock status checks for different condition types
- Prerequisite chapter validation
- Unlock date validation
- Edge cases and error handling
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from courses.models import Chapter, ChapterUnlockCondition, ChapterProgress
from courses.services import ChapterUnlockService

from courses.tests.factories import (
    CourseFactory, ChapterFactory, ChapterUnlockConditionFactory,
    EnrollmentFactory, ChapterProgressFactory,
)
from accounts.tests.factories import UserFactory


class ChapterUnlockServiceTestCase(TestCase):
    """Test cases for ChapterUnlockService."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

        # Create chapters in order
        self.chapter1 = ChapterFactory(course=self.course, order=1, title="Chapter 1")
        self.chapter2 = ChapterFactory(course=self.course, order=2, title="Chapter 2")
        self.chapter3 = ChapterFactory(course=self.course, order=3, title="Chapter 3")

    def test_chapter_without_condition_is_unlocked(self):
        """Test that a chapter without unlock condition is unlocked."""
        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter1, self.enrollment)
        self.assertTrue(is_unlocked)

    def test_chapter_with_no_condition_attribute_is_unlocked(self):
        """Test that a chapter without unlock_condition attribute is unlocked."""
        # Create a new chapter without any unlock condition
        new_chapter = ChapterFactory(course=self.course, order=4)
        is_unlocked = ChapterUnlockService.is_unlocked(new_chapter, self.enrollment)
        self.assertTrue(is_unlocked)

    def test_locked_when_prerequisites_not_met(self):
        """Test that chapter is locked when prerequisites are not completed."""
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertFalse(is_unlocked)

    def test_unlocked_when_all_prerequisites_met(self):
        """Test that chapter is unlocked when all prerequisites are completed."""
        # Set up unlock condition
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete prerequisites
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertTrue(is_unlocked)

    def test_locked_when_only_some_prerequisites_met(self):
        """Test that chapter is locked when only some prerequisites are completed."""
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete only chapter1
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertFalse(is_unlocked)

    def test_locked_before_unlock_date(self):
        """Test that chapter is locked before unlock date."""
        future_date = timezone.now() + timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='date',
            unlock_date=future_date
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        self.assertFalse(is_unlocked)

    def test_unlocked_after_unlock_date(self):
        """Test that chapter is unlocked after unlock date."""
        past_date = timezone.now() - timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='date',
            unlock_date=past_date
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        self.assertTrue(is_unlocked)

    def test_locked_when_type_all_and_prerequisites_not_met(self):
        """Test 'all' type requires both prerequisites and date."""
        future_date = timezone.now() + timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='all',
            unlock_date=future_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete prerequisites but date is in future
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertFalse(is_unlocked)

    def test_locked_when_type_all_and_date_not_met(self):
        """Test 'all' type requires both prerequisites and date."""
        past_date = timezone.now() - timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='all',
            unlock_date=past_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Date is met but prerequisites not completed
        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertFalse(is_unlocked)

    def test_unlocked_when_type_all_and_both_met(self):
        """Test 'all' type unlocks when both prerequisites and date are met."""
        past_date = timezone.now() - timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='all',
            unlock_date=past_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete prerequisites
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertTrue(is_unlocked)

    def test_prerequisite_type_ignores_date(self):
        """Test 'prerequisite' type ignores unlock date."""
        future_date = timezone.now() + timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite',
            unlock_date=future_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete prerequisites, date is in future but should be ignored
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertTrue(is_unlocked)

    def test_date_type_ignores_prerequisites(self):
        """Test 'date' type ignores prerequisites."""
        past_date = timezone.now() - timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='date',
            unlock_date=past_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Date is met, prerequisites not completed but should be ignored
        is_unlocked = ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        self.assertTrue(is_unlocked)


class ChapterUnlockServiceGetUnlockStatusTestCase(TestCase):
    """Test cases for ChapterUnlockService.get_unlock_status method."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

        self.chapter1 = ChapterFactory(course=self.course, order=1, title="Chapter 1")
        self.chapter2 = ChapterFactory(course=self.course, order=2, title="Chapter 2")
        self.chapter3 = ChapterFactory(course=self.course, order=3, title="Chapter 3")

    def test_unlock_status_without_condition(self):
        """Test get_unlock_status for chapter without condition."""
        status = ChapterUnlockService.get_unlock_status(self.chapter1, self.enrollment)

        self.assertFalse(status['is_locked'])
        self.assertIsNone(status['reason'])
        self.assertIsNone(status['prerequisite_progress'])
        self.assertIsNone(status['unlock_date'])
        self.assertIsNone(status['time_until_unlock'])

    def test_unlock_status_with_prerequisites(self):
        """Test get_unlock_status shows prerequisite progress."""
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete only chapter1
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        status = ChapterUnlockService.get_unlock_status(self.chapter3, self.enrollment)

        self.assertTrue(status['is_locked'])
        self.assertEqual(status['reason'], 'prerequisite')
        self.assertIsNotNone(status['prerequisite_progress'])
        self.assertEqual(status['prerequisite_progress']['total'], 2)
        self.assertEqual(status['prerequisite_progress']['completed'], 1)
        self.assertEqual(len(status['prerequisite_progress']['remaining']), 1)
        self.assertEqual(status['prerequisite_progress']['remaining'][0]['id'], self.chapter2.id)

    def test_unlock_status_with_date(self):
        """Test get_unlock_status shows unlock date info."""
        future_date = timezone.now() + timedelta(days=2, hours=5, minutes=30)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='date',
            unlock_date=future_date
        )

        status = ChapterUnlockService.get_unlock_status(self.chapter2, self.enrollment)

        self.assertTrue(status['is_locked'])
        self.assertEqual(status['reason'], 'date')
        self.assertIsNotNone(status['time_until_unlock'])
        self.assertEqual(status['time_until_unlock']['days'], 2)
        self.assertEqual(status['time_until_unlock']['hours'], 5)
        self.assertEqual(status['time_until_unlock']['minutes'], 30)

    def test_unlock_status_with_both_conditions(self):
        """Test get_unlock_status with both prerequisite and date conditions."""
        future_date = timezone.now() + timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='all',
            unlock_date=future_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        status = ChapterUnlockService.get_unlock_status(self.chapter3, self.enrollment)

        self.assertTrue(status['is_locked'])
        self.assertEqual(status['reason'], 'both')
        self.assertIsNotNone(status['prerequisite_progress'])
        self.assertIsNotNone(status['time_until_unlock'])

    def test_unlock_status_unlocked_when_all_met(self):
        """Test get_unlock_status returns unlocked when all conditions met."""
        past_date = timezone.now() - timedelta(days=1)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='all',
            unlock_date=past_date
        )
        condition.prerequisite_chapters.add(self.chapter1, self.chapter2)

        # Complete prerequisites
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        status = ChapterUnlockService.get_unlock_status(self.chapter3, self.enrollment)

        self.assertFalse(status['is_locked'])
        self.assertIsNone(status['reason'])
