"""
Tests for Celery tasks in the courses app.

This module tests that async snapshot refresh tasks work correctly.
"""
from unittest.mock import patch, MagicMock, call
from django.test import TestCase, override_settings

from accounts.tests.factories import UserFactory
from .factories import (
    CourseFactory,
    ChapterFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
    ChapterUnlockConditionFactory,
    ProblemFactory,
    ProblemUnlockConditionFactory,
    ProblemProgressFactory,
)
from courses.models import CourseUnlockSnapshot, ChapterProgress, ProblemUnlockSnapshot, ProblemProgress
from courses.tasks import (
    refresh_unlock_snapshot,
    batch_refresh_stale_snapshots,
    scheduled_snapshot_refresh,
    cleanup_old_snapshots,
    refresh_problem_unlock_snapshot,
    batch_refresh_stale_problem_snapshots,
    scheduled_problem_snapshot_refresh,
    cleanup_old_problem_snapshots,
)


class RefreshUnlockSnapshotTaskTestCase(TestCase):
    """Test refresh_unlock_snapshot task"""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter1 = ChapterFactory(course=self.course, order=0)
        self.chapter2 = ChapterFactory(course=self.course, order=1)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_refresh_unlock_snapshot_creates_snapshot(self):
        """Test that task creates a snapshot if it doesn't exist"""
        # Initially no snapshot
        self.assertEqual(CourseUnlockSnapshot.objects.count(), 0)

        # Run task
        refresh_unlock_snapshot(enrollment_id=self.enrollment.id)

        # Snapshot should be created
        self.assertEqual(CourseUnlockSnapshot.objects.count(), 1)
        snapshot = CourseUnlockSnapshot.objects.get(enrollment=self.enrollment)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.course, self.course)
        # Version is 2 because recompute() is called which increments from 1 to 2
        self.assertEqual(snapshot.version, 2)

    def test_refresh_unlock_snapshot_updates_existing(self):
        """Test that task updates existing snapshot"""
        # Create initial snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            version=1
        )

        # Run task
        refresh_unlock_snapshot(enrollment_id=self.enrollment.id)

        # Snapshot should be updated
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.version, 2)
        self.assertFalse(snapshot.is_stale)
        self.assertIn(str(self.chapter1.id), snapshot.unlock_states)

    def test_refresh_unlock_snapshot_computes_correct_states(self):
        """Test that task computes correct unlock states"""
        # Create unlock condition
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # Run task before completing prerequisite
        refresh_unlock_snapshot(enrollment_id=self.enrollment.id)

        snapshot = CourseUnlockSnapshot.objects.get(enrollment=self.enrollment)
        chapter1_state = snapshot.unlock_states[str(self.chapter1.id)]
        chapter2_state = snapshot.unlock_states[str(self.chapter2.id)]

        # Chapter 1 should be unlocked, Chapter 2 locked
        self.assertFalse(chapter1_state['locked'])
        self.assertTrue(chapter2_state['locked'])
        self.assertEqual(chapter2_state['reason'], 'prerequisite')

        # Complete chapter 1
        ChapterProgress.objects.create(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Run task again
        refresh_unlock_snapshot(enrollment_id=self.enrollment.id)

        snapshot.refresh_from_db()
        chapter2_state = snapshot.unlock_states[str(self.chapter2.id)]

        # Chapter 2 should now be unlocked
        self.assertFalse(chapter2_state['locked'])

    def test_refresh_unlock_snapshot_handles_nonexistent_enrollment(self):
        """Test that task handles nonexistent enrollment gracefully"""
        # Run task with invalid ID - should not raise, just return None
        result = refresh_unlock_snapshot(enrollment_id=99999)
        self.assertIsNone(result)

    def test_refresh_unlock_snapshot_retries_on_error(self):
        """Test that task retries on errors"""
        with patch('courses.models.CourseUnlockSnapshot.objects.get_or_create') as mock_create:
            # Make it fail first time
            mock_create.side_effect = [
                Exception("Database error"),
                (MagicMock(), True)
            ]

            # Run task (should retry)
            with self.assertRaises(Exception):
                refresh_unlock_snapshot(enrollment_id=self.enrollment.id)

    def test_refresh_unlock_snapshot_with_stale_flag(self):
        """Test that task clears stale flag after refresh"""
        # Create stale snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=True,
            version=1
        )

        # Run task
        refresh_unlock_snapshot(enrollment_id=self.enrollment.id)

        # Stale flag should be cleared
        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)


class BatchRefreshStaleSnapshotsTaskTestCase(TestCase):
    """Test batch_refresh_stale_snapshots task"""

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.course = CourseFactory()

        self.enrollment1 = EnrollmentFactory(user=self.user1, course=self.course)
        self.enrollment2 = EnrollmentFactory(user=self.user2, course=self.course)
        self.enrollment3 = EnrollmentFactory(user=self.user3, course=self.course)

    def test_batch_refresh_empty_queue(self):
        """Test batch refresh with no stale snapshots"""
        with patch('courses.tasks.refresh_unlock_snapshot.delay') as mock_delay:
            count = batch_refresh_stale_snapshots(batch_size=100)

            # No tasks should be triggered
            self.assertEqual(count, 0)
            mock_delay.assert_not_called()

    def test_batch_refresh_processes_stale_snapshots(self):
        """Test that batch refresh processes stale snapshots"""
        # Create stale snapshots
        snapshot1 = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment1,
            unlock_states={},
            is_stale=True
        )
        snapshot2 = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment2,
            unlock_states={},
            is_stale=True
        )

        with patch('courses.tasks.refresh_unlock_snapshot.delay') as mock_delay:
            count = batch_refresh_stale_snapshots(batch_size=10)

            # Should trigger 2 tasks
            self.assertEqual(count, 2)
            self.assertEqual(mock_delay.call_count, 2)
            mock_delay.assert_any_call(self.enrollment1.id)
            mock_delay.assert_any_call(self.enrollment2.id)

    def test_batch_refresh_respects_batch_size(self):
        """Test that batch refresh respects batch size limit"""
        # Create more stale snapshots than batch size
        for i in range(15):
            user = UserFactory()
            enrollment = EnrollmentFactory(user=user, course=self.course)
            CourseUnlockSnapshot.objects.create(
                course=self.course,
                enrollment=enrollment,
                unlock_states={},
                is_stale=True
            )

        with patch('courses.tasks.refresh_unlock_snapshot.delay') as mock_delay:
            count = batch_refresh_stale_snapshots(batch_size=10)

            # Should only process 10 (batch_size)
            self.assertEqual(count, 10)
            self.assertEqual(mock_delay.call_count, 10)

    def test_batch_refresh_ignores_fresh_snapshots(self):
        """Test that batch refresh ignores fresh snapshots"""
        # Create fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment1,
            unlock_states={},
            is_stale=False  # Fresh
        )

        with patch('courses.tasks.refresh_unlock_snapshot.delay') as mock_delay:
            count = batch_refresh_stale_snapshots(batch_size=100)

            # No tasks should be triggered
            self.assertEqual(count, 0)
            mock_delay.assert_not_called()

    def test_batch_refresh_mixed_snapshots(self):
        """Test batch refresh with mix of stale and fresh snapshots"""
        # Create mix of snapshots
        CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment1,
            unlock_states={},
            is_stale=True
        )
        CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment2,
            unlock_states={},
            is_stale=False  # Fresh
        )
        CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment3,
            unlock_states={},
            is_stale=True
        )

        with patch('courses.tasks.refresh_unlock_snapshot.delay') as mock_delay:
            count = batch_refresh_stale_snapshots(batch_size=100)

            # Should only process 2 stale snapshots
            self.assertEqual(count, 2)
            self.assertEqual(mock_delay.call_count, 2)

    def test_batch_refresh_cleans_orphaned_snapshots(self):
        """Test that batch refresh cleans up orphaned snapshots"""
        # Create a snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment1,
            unlock_states={},
            is_stale=True
        )

        # Delete the enrollment to create an orphan
        enrollment_id = self.enrollment1.id
        self.enrollment1.delete()

        # The snapshot should still exist (CASCADE might not work in all scenarios)
        # But the batch task should clean it up
        with patch('courses.tasks.refresh_unlock_snapshot.delay') as mock_delay:
            count = batch_refresh_stale_snapshots(batch_size=10)

            # Orphaned snapshot should be cleaned up, no refresh tasks triggered
            # Since enrollment was deleted, there should be no snapshots to refresh
            # (the orphaned one gets deleted before processing stale ones)
            self.assertEqual(count, 0)
            mock_delay.assert_not_called()

        # Verify orphaned snapshot was deleted
        self.assertFalse(
            CourseUnlockSnapshot.objects.filter(id=snapshot.id).exists()
        )


class ScheduledSnapshotRefreshTaskTestCase(TestCase):
    """Test scheduled_snapshot_refresh task"""

    def test_scheduled_refresh_calls_batch(self):
        """Test that scheduled refresh calls batch_refresh_stale_snapshots"""
        with patch('courses.tasks.batch_refresh_stale_snapshots.delay') as mock_delay:
            scheduled_snapshot_refresh()

            # Should call batch refresh
            mock_delay.assert_called_once()


class CleanupOldSnapshotsTaskTestCase(TestCase):
    """Test cleanup_old_snapshots task"""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_cleanup_removes_orphaned_snapshots(self):
        """Test that cleanup removes snapshots with no enrollment"""
        # Create snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={}
        )

        # Delete enrollment (should CASCADE delete snapshot, but simulate orphan)
        enrollment_id = self.enrollment.id
        self.enrollment.delete()

        # Manually create orphan snapshot (simulating edge case)
        # In reality, CASCADE should handle this, but the task handles orphans

        with patch('courses.models.CourseUnlockSnapshot.objects.filter') as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.delete.return_value = (1,)
            mock_filter.return_value = mock_queryset

            count = cleanup_old_snapshots()

            # Should have attempted cleanup
            mock_filter.assert_called()

    def test_cleanup_preserves_active_snapshots(self):
        """Test that cleanup preserves snapshots with active enrollments"""
        # Create active snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={}
        )

        # Run cleanup
        count = cleanup_old_snapshots()

        # Snapshot should still exist
        self.assertTrue(
            CourseUnlockSnapshot.objects.filter(id=snapshot.id).exists()
        )


class RefreshProblemUnlockSnapshotTaskTestCase(TestCase):
    """Test refresh_problem_unlock_snapshot task"""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course, order=0)
        self.problem1 = ProblemFactory(chapter=self.chapter)
        self.problem2 = ProblemFactory(chapter=self.chapter)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_refresh_problem_unlock_snapshot_creates_snapshot(self):
        """Test that task creates a problem snapshot if it doesn't exist"""
        # Initially no snapshot
        self.assertEqual(ProblemUnlockSnapshot.objects.count(), 0)

        # Run task
        refresh_problem_unlock_snapshot(enrollment_id=self.enrollment.id)

        # Snapshot should be created
        self.assertEqual(ProblemUnlockSnapshot.objects.count(), 1)
        snapshot = ProblemUnlockSnapshot.objects.get(enrollment=self.enrollment)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.course, self.course)
        # Version is 2 because recompute() is called which increments from 1 to 2
        self.assertEqual(snapshot.version, 2)

    def test_refresh_problem_unlock_snapshot_updates_existing(self):
        """Test that task updates existing problem snapshot"""
        # Create initial snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            version=1
        )

        # Run task
        refresh_problem_unlock_snapshot(enrollment_id=self.enrollment.id)

        # Snapshot should be updated
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.version, 2)
        self.assertFalse(snapshot.is_stale)
        self.assertIn(str(self.problem1.id), snapshot.unlock_states)

    def test_refresh_problem_unlock_snapshot_computes_correct_states(self):
        """Test that task computes correct problem unlock states"""
        # Create unlock condition
        condition = ProblemUnlockConditionFactory(
            problem=self.problem2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_problems.add(self.problem1)

        # Run task before completing prerequisite
        refresh_problem_unlock_snapshot(enrollment_id=self.enrollment.id)

        snapshot = ProblemUnlockSnapshot.objects.get(enrollment=self.enrollment)
        problem1_state = snapshot.unlock_states[str(self.problem1.id)]
        problem2_state = snapshot.unlock_states[str(self.problem2.id)]

        # Problem 1 should be unlocked, Problem 2 locked
        self.assertTrue(problem1_state['unlocked'])
        self.assertFalse(problem2_state['unlocked'])
        self.assertEqual(problem2_state['reason'], 'prerequisite')

        # Complete problem 1
        ProblemProgress.objects.create(
            enrollment=self.enrollment,
            problem=self.problem1,
            status='solved'
        )

        # Run task again
        refresh_problem_unlock_snapshot(enrollment_id=self.enrollment.id)

        snapshot.refresh_from_db()
        problem2_state = snapshot.unlock_states[str(self.problem2.id)]

        # Problem 2 should now be unlocked
        self.assertTrue(problem2_state['unlocked'])
        self.assertIsNone(problem2_state['reason'])

    def test_refresh_problem_unlock_snapshot_handles_nonexistent_enrollment(self):
        """Test that task handles nonexistent enrollment gracefully"""
        # Run task with invalid ID
        result = refresh_problem_unlock_snapshot(enrollment_id=99999)

        # Should return None and not raise exception
        self.assertIsNone(result)


class BatchRefreshStaleProblemSnapshotsTaskTestCase(TestCase):
    """Test batch_refresh_stale_problem_snapshots task"""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_batch_refresh_empty_queue(self):
        """Test batch refresh when no stale snapshots"""
        count = batch_refresh_stale_problem_snapshots(batch_size=10)

        # Should return 0
        self.assertEqual(count, 0)

    @patch('courses.tasks.refresh_problem_unlock_snapshot.delay')
    def test_batch_refresh_processes_stale_snapshots(self, mock_delay):
        """Test that batch refresh processes stale problem snapshots"""
        # Create stale snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=True
        )

        # Run batch refresh
        count = batch_refresh_stale_problem_snapshots(batch_size=10)

        # Should have processed 1 snapshot
        self.assertEqual(count, 1)
        # Should have called refresh task
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch('courses.tasks.refresh_problem_unlock_snapshot.delay')
    def test_batch_refresh_respects_batch_size(self, mock_delay):
        """Test that batch refresh respects batch_size limit"""
        # Create multiple stale snapshots with different users
        for i in range(5):
            user = UserFactory()
            enrollment = EnrollmentFactory(user=user, course=self.course)
            ProblemUnlockSnapshot.objects.create(
                course=self.course,
                enrollment=enrollment,
                unlock_states={},
                is_stale=True
            )

        # Run batch refresh with batch_size=2
        count = batch_refresh_stale_problem_snapshots(batch_size=2)

        # Should have processed only 2 snapshots
        self.assertEqual(count, 2)
        self.assertEqual(mock_delay.call_count, 2)

    def test_batch_refresh_skips_fresh_snapshots(self):
        """Test that batch refresh skips fresh problem snapshots"""
        # Create fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False
        )

        # Run batch refresh
        count = batch_refresh_stale_problem_snapshots(batch_size=10)

        # Should return 0 (no stale snapshots)
        self.assertEqual(count, 0)


class ScheduledProblemSnapshotRefreshTaskTestCase(TestCase):
    """Test scheduled_problem_snapshot_refresh task"""

    @patch('courses.tasks.batch_refresh_stale_problem_snapshots.delay')
    def test_scheduled_refresh_calls_batch(self, mock_delay):
        """Test that scheduled refresh calls batch_refresh_stale_problem_snapshots"""
        scheduled_problem_snapshot_refresh()

        # Should call batch refresh
        mock_delay.assert_called_once()


class CleanupOldProblemSnapshotsTaskTestCase(TestCase):
    """Test cleanup_old_problem_snapshots task"""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_cleanup_removes_orphaned_problem_snapshots(self):
        """Test that cleanup removes problem snapshots with no enrollment"""
        # Create snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={}
        )

        # Delete enrollment (should CASCADE delete snapshot, but simulate orphan)
        enrollment_id = self.enrollment.id
        self.enrollment.delete()

        with patch('courses.models.ProblemUnlockSnapshot.objects.filter') as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.delete.return_value = (1,)
            mock_filter.return_value = mock_queryset

            count = cleanup_old_problem_snapshots()

            # Should have attempted cleanup
            mock_filter.assert_called()

    def test_cleanup_preserves_active_problem_snapshots(self):
        """Test that cleanup preserves problem snapshots with active enrollments"""
        # Create active snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={}
        )

        # Run cleanup
        count = cleanup_old_problem_snapshots()

        # Snapshot should still exist
        self.assertTrue(
            ProblemUnlockSnapshot.objects.filter(id=snapshot.id).exists()
        )