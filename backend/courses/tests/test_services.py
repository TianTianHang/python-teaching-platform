from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from courses.models import Course, Enrollment, Chapter, ChapterProgress, CourseUnlockSnapshot
from courses.services import UnlockSnapshotService, ChapterUnlockService
from accounts.tests.factories import UserFactory
from .factories import (
    CourseFactory, EnrollmentFactory, ChapterFactory,
    ChapterUnlockConditionFactory, ChapterProgressFactory
)


class UnlockSnapshotServiceTestCase(TestCase):
    """Test UnlockSnapshotService"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(
            course=self.course,
            user=self.user
        )
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)

    @patch('courses.tasks.refresh_unlock_snapshot.delay')
    def test_get_or_create_snapshot_new(self, mock_delay):
        """Test creating a new snapshot"""
        result = UnlockSnapshotService.get_or_create_snapshot(self.enrollment)

        self.assertEqual(result.enrollment, self.enrollment)
        self.assertEqual(result.course, self.course)
        self.assertTrue(mock_delay.called)
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch('courses.tasks.refresh_unlock_snapshot.delay')
    def test_get_or_create_snapshot_existing(self, mock_delay):
        """Test getting existing snapshot"""
        # Create existing snapshot
        existing_snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={'1': {'locked': False, 'reason': None}},
            version=1
        )

        # Call get_or_create_snapshot
        result = UnlockSnapshotService.get_or_create_snapshot(self.enrollment)

        # Should return existing snapshot
        self.assertEqual(result, existing_snapshot)
        # Should not trigger async task since snapshot exists
        self.assertFalse(mock_delay.called)

    def test_mark_stale_existing_snapshot(self):
        """Test marking existing snapshot as stale"""
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            is_stale=False
        )

        UnlockSnapshotService.mark_stale(self.enrollment)

        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_mark_stale_nonexistent_snapshot(self):
        """Test marking non-existent snapshot as stale (should not raise error)"""
        # This should not raise an exception
        UnlockSnapshotService.mark_stale(self.enrollment)

    @patch('courses.tasks.refresh_unlock_snapshot.delay')
    def test_get_unlock_status_hybrid_fresh_snapshot(self, mock_delay):
        """Test hybrid query with fresh snapshot"""
        # Create fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                '1': {'locked': False, 'reason': None},
                '2': {'locked': True, 'reason': 'prerequisite'}
            },
            is_stale=False,
            version=2
        )

        result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)

        # Should use snapshot data
        self.assertEqual(result['source'], 'snapshot')
        self.assertEqual(result['snapshot_version'], 2)
        self.assertEqual(result['unlock_states'], snapshot.unlock_states)
        # Should not trigger async refresh
        self.assertFalse(mock_delay.called)

    @patch('courses.tasks.refresh_unlock_snapshot.delay')
    def test_get_unlock_status_hybrid_stale_snapshot(self, mock_delay):
        """Test hybrid query with stale snapshot"""
        # Create stale snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                '1': {'locked': False, 'reason': None},
                '2': {'locked': True, 'reason': 'prerequisite'}
            },
            is_stale=True,
            version=2
        )

        result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)

        # Should return stale data but mark as stale
        self.assertEqual(result['source'], 'snapshot_stale')
        self.assertEqual(result['snapshot_version'], 2)
        self.assertEqual(result['unlock_states'], snapshot.unlock_states)
        # Should trigger async refresh
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch('courses.tasks.refresh_unlock_snapshot.delay')
    def test_get_unlock_status_hybrid_no_snapshot(self, mock_delay):
        """Test hybrid query when no snapshot exists"""
        result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)

        # Should fall back to realtime computation
        self.assertEqual(result['source'], 'realtime')
        # Should trigger async snapshot creation
        mock_delay.assert_called_once_with(self.enrollment.id)

    def test_compute_realtime_no_unlock_conditions(self):
        """Test realtime computation without unlock conditions"""
        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Should return unlocked state for all chapters
        self.assertEqual(result['source'], 'realtime')
        self.assertEqual(len(result['unlock_states']), 2)
        self.assertFalse(result['unlock_states'][str(self.chapter1.id)]['locked'])
        self.assertFalse(result['unlock_states'][str(self.chapter2.id)]['locked'])

    def test_compute_realtime_with_prerequisite_condition(self):
        """Test realtime computation with prerequisite condition"""
        # Set up prerequisite
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.set([self.chapter1])

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Chapter1 should be unlocked, chapter2 should be locked
        self.assertFalse(result['unlock_states'][str(self.chapter1.id)]['locked'])
        self.assertTrue(result['unlock_states'][str(self.chapter2.id)]['locked'])
        self.assertEqual(result['unlock_states'][str(self.chapter2.id)]['reason'], 'prerequisite')

    def test_compute_realtime_completed_prerequisite(self):
        """Test realtime computation with completed prerequisite"""
        # Set up prerequisite
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.set([self.chapter1])

        # Complete chapter1
        ChapterProgress.objects.create(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Both chapters should be unlocked now
        self.assertFalse(result['unlock_states'][str(self.chapter2.id)]['locked'])
        self.assertIsNone(result['unlock_states'][str(self.chapter2.id)]['reason'])

    def test_compute_realtime_with_date_condition(self):
        """Test realtime computation with date condition"""
        future_date = timezone.now() + timedelta(hours=1)
        ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='date',
            unlock_date=future_date
        )

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Chapter2 should be locked due to date
        self.assertTrue(result['unlock_states'][str(self.chapter2.id)]['locked'])
        self.assertEqual(result['unlock_states'][str(self.chapter2.id)]['reason'], 'date')

    def test_compute_realtime_both_conditions(self):
        """Test realtime computation with both prerequisite and date conditions"""
        future_date = timezone.now() + timedelta(hours=1)

        # Create unlock condition with both types
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='all',
            unlock_date=future_date
        )
        condition.prerequisite_chapters.set([self.chapter1])

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Chapter2 should be locked for both reasons
        self.assertTrue(result['unlock_states'][str(self.chapter2.id)]['locked'])
        self.assertEqual(result['unlock_states'][str(self.chapter2.id)]['reason'], 'both')

    @patch('courses.services.ChapterUnlockService.is_unlocked')
    def test_compute_realtime_service_integration(self, mock_is_unlocked):
        """Test that _compute_realtime correctly uses ChapterUnlockService"""
        # Mock the service method
        mock_is_unlocked.return_value = True  # Chapter is unlocked

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Verify service was called for each chapter
        self.assertEqual(mock_is_unlocked.call_count, 2)
        # Should show chapters as unlocked
        self.assertFalse(result['unlock_states'][str(self.chapter1.id)]['locked'])
        self.assertFalse(result['unlock_states'][str(self.chapter2.id)]['locked'])


class UnlockSnapshotServiceIntegrationTestCase(TestCase):
    """Integration tests for UnlockSnapshotService"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(
            course=self.course,
            user=self.user
        )
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)

        # Set up prerequisite
        self.unlock_condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        self.unlock_condition.prerequisite_chapters.set([self.chapter1])

    @patch('courses.tasks.refresh_unlock_snapshot.delay')
    def test_complete_chapter_triggers_refresh(self, mock_delay):
        """Test that completing a chapter triggers snapshot refresh"""
        # Create initial snapshot and populate it
        snapshot = UnlockSnapshotService.get_or_create_snapshot(self.enrollment)
        snapshot.recompute()  # Populate with actual data

        # Initially, chapter2 should be locked
        result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)
        self.assertTrue(result['unlock_states'][str(self.chapter2.id)]['locked'])

        # Complete chapter1
        ChapterProgress.objects.create(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Trigger signal
        from courses.signals import mark_snapshot_stale_on_progress_update
        chapter_progress = ChapterProgress.objects.get(
            enrollment=self.enrollment,
            chapter=self.chapter1
        )
        mark_snapshot_stale_on_progress_update(
            ChapterProgress,
            chapter_progress,
            created=True
        )

        # Check that snapshot was marked stale
        snapshot = CourseUnlockSnapshot.objects.get(enrollment=self.enrollment)
        self.assertTrue(snapshot.is_stale)

        # Verify that refresh task was triggered
        mock_delay.assert_called()

    def test_snapshot_realtime_consistency(self):
        """Test that snapshot and realtime computation produce same results"""
        # Create initial snapshot with proper states
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=True
        )
        # Recompute to populate with actual data
        snapshot.recompute()

        # Get snapshot result (should use fresh snapshot now)
        snapshot_result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)

        # Get realtime result
        realtime_result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Results should match
        self.assertEqual(snapshot_result['unlock_states'], realtime_result['unlock_states'])

        # Complete prerequisite chapter
        ChapterProgress.objects.create(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Now they should differ
        new_snapshot_result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)
        new_realtime_result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Realtime should now show chapter2 unlocked
        self.assertFalse(new_realtime_result['unlock_states'][str(self.chapter2.id)]['locked'])
        # Snapshot might still be locked (stale)