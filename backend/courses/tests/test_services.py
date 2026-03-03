from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from courses.models import (
    Course,
    Enrollment,
    Chapter,
    ChapterProgress,
    CourseUnlockSnapshot,
    ProblemUnlockSnapshot,
    Problem,
    ProblemProgress,
)
from courses.services import (
    UnlockSnapshotService,
    ChapterUnlockService,
    ProblemUnlockSnapshotService,
)
from accounts.tests.factories import UserFactory
from .factories import (
    CourseFactory,
    EnrollmentFactory,
    ChapterFactory,
    ChapterUnlockConditionFactory,
    ChapterProgressFactory,
    ProblemFactory,
    ProblemUnlockConditionFactory,
    ProblemProgressFactory,
)


class UnlockSnapshotServiceTestCase(TestCase):
    """Test UnlockSnapshotService"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(course=self.course, user=self.user)
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)

    @patch("courses.tasks.refresh_unlock_snapshot.delay")
    def test_get_or_create_snapshot_new(self, mock_delay):
        """Test creating a new snapshot"""
        result = UnlockSnapshotService.get_or_create_snapshot(self.enrollment)

        self.assertEqual(result.enrollment, self.enrollment)
        self.assertEqual(result.course, self.course)
        self.assertTrue(mock_delay.called)
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch("courses.tasks.refresh_unlock_snapshot.delay")
    def test_get_or_create_snapshot_existing(self, mock_delay):
        """Test getting existing snapshot"""
        # Create existing snapshot
        existing_snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={"1": {"locked": False, "reason": None}},
            version=1,
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
            course=self.course, enrollment=self.enrollment, is_stale=False
        )

        UnlockSnapshotService.mark_stale(self.enrollment)

        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_mark_stale_nonexistent_snapshot(self):
        """Test marking non-existent snapshot as stale (should not raise error)"""
        # This should not raise an exception
        UnlockSnapshotService.mark_stale(self.enrollment)

    @patch("courses.tasks.refresh_unlock_snapshot.delay")
    def test_get_unlock_status_hybrid_fresh_snapshot(self, mock_delay):
        """Test hybrid query with fresh snapshot"""
        # Create fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                "1": {"locked": False, "reason": None},
                "2": {"locked": True, "reason": "prerequisite"},
            },
            is_stale=False,
            version=2,
        )

        result = UnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Should use snapshot data
        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_version"], 2)
        self.assertEqual(result["unlock_states"], snapshot.unlock_states)
        # Should not trigger async refresh
        self.assertFalse(mock_delay.called)

    @patch("courses.tasks.refresh_unlock_snapshot.delay")
    def test_get_unlock_status_hybrid_stale_snapshot(self, mock_delay):
        """Test hybrid query with stale snapshot"""
        # Create stale snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                "1": {"locked": False, "reason": None},
                "2": {"locked": True, "reason": "prerequisite"},
            },
            is_stale=True,
            version=2,
        )

        result = UnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Should return stale data but mark as stale
        self.assertEqual(result["source"], "snapshot_stale")
        self.assertEqual(result["snapshot_version"], 2)
        self.assertEqual(result["unlock_states"], snapshot.unlock_states)
        # Should trigger async refresh
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch("courses.tasks.refresh_unlock_snapshot.delay")
    def test_get_unlock_status_hybrid_no_snapshot(self, mock_delay):
        """Test hybrid query when no snapshot exists"""
        result = UnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Should fall back to realtime computation
        self.assertEqual(result["source"], "realtime")
        # Should trigger async snapshot creation
        mock_delay.assert_called_once_with(self.enrollment.id)

    def test_compute_realtime_no_unlock_conditions(self):
        """Test realtime computation without unlock conditions"""
        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Should return unlocked state for all chapters
        self.assertEqual(result["source"], "realtime")
        self.assertEqual(len(result["unlock_states"]), 2)
        self.assertFalse(result["unlock_states"][str(self.chapter1.id)]["locked"])
        self.assertFalse(result["unlock_states"][str(self.chapter2.id)]["locked"])

    def test_compute_realtime_with_prerequisite_condition(self):
        """Test realtime computation with prerequisite condition"""
        # Set up prerequisite
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="prerequisite"
        )
        condition.prerequisite_chapters.set([self.chapter1])

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Chapter1 should be unlocked, chapter2 should be locked
        self.assertFalse(result["unlock_states"][str(self.chapter1.id)]["locked"])
        self.assertTrue(result["unlock_states"][str(self.chapter2.id)]["locked"])
        self.assertEqual(
            result["unlock_states"][str(self.chapter2.id)]["reason"], "prerequisite"
        )

    def test_compute_realtime_completed_prerequisite(self):
        """Test realtime computation with completed prerequisite"""
        # Set up prerequisite
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="prerequisite"
        )
        condition.prerequisite_chapters.set([self.chapter1])

        # Complete chapter1
        ChapterProgress.objects.create(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Both chapters should be unlocked now
        self.assertFalse(result["unlock_states"][str(self.chapter2.id)]["locked"])
        self.assertIsNone(result["unlock_states"][str(self.chapter2.id)]["reason"])

    def test_compute_realtime_with_date_condition(self):
        """Test realtime computation with date condition"""
        future_date = timezone.now() + timedelta(hours=1)
        ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="date", unlock_date=future_date
        )

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Chapter2 should be locked due to date
        self.assertTrue(result["unlock_states"][str(self.chapter2.id)]["locked"])
        self.assertEqual(
            result["unlock_states"][str(self.chapter2.id)]["reason"], "date"
        )

    def test_compute_realtime_both_conditions(self):
        """Test realtime computation with both prerequisite and date conditions"""
        future_date = timezone.now() + timedelta(hours=1)

        # Create unlock condition with both types
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="all", unlock_date=future_date
        )
        condition.prerequisite_chapters.set([self.chapter1])

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Chapter2 should be locked for both reasons
        self.assertTrue(result["unlock_states"][str(self.chapter2.id)]["locked"])
        self.assertEqual(
            result["unlock_states"][str(self.chapter2.id)]["reason"], "both"
        )

    @patch("courses.services.ChapterUnlockService.is_unlocked")
    def test_compute_realtime_service_integration(self, mock_is_unlocked):
        """Test that _compute_realtime correctly uses ChapterUnlockService"""
        # Mock the service method
        mock_is_unlocked.return_value = True  # Chapter is unlocked

        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        # Verify service was called for each chapter
        self.assertEqual(mock_is_unlocked.call_count, 2)
        # Should show chapters as unlocked
        self.assertFalse(result["unlock_states"][str(self.chapter1.id)]["locked"])
        self.assertFalse(result["unlock_states"][str(self.chapter2.id)]["locked"])


class UnlockSnapshotServiceIntegrationTestCase(TestCase):
    """Integration tests for UnlockSnapshotService"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(course=self.course, user=self.user)
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)

        # Set up prerequisite
        self.unlock_condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="prerequisite"
        )
        self.unlock_condition.prerequisite_chapters.set([self.chapter1])

    @patch("courses.tasks.refresh_unlock_snapshot.delay")
    def test_complete_chapter_triggers_refresh(self, mock_delay):
        """Test that completing a chapter triggers snapshot refresh"""
        # Create initial snapshot and populate it
        snapshot = UnlockSnapshotService.get_or_create_snapshot(self.enrollment)
        snapshot.recompute()  # Populate with actual data

        # Initially, chapter2 should be locked
        result = UnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )
        self.assertTrue(result["unlock_states"][str(self.chapter2.id)]["locked"])

        # Complete chapter1
        ChapterProgress.objects.create(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Trigger signal
        from courses.signals import mark_snapshot_stale_on_progress_update

        chapter_progress = ChapterProgress.objects.get(
            enrollment=self.enrollment, chapter=self.chapter1
        )
        mark_snapshot_stale_on_progress_update(
            ChapterProgress, chapter_progress, created=True
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
            is_stale=True,
        )
        # Recompute to populate with actual data
        snapshot.recompute()

        # Get snapshot result (should use fresh snapshot now)
        snapshot_result = UnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Get realtime result
        realtime_result = UnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )

        # Results should match
        self.assertEqual(
            snapshot_result["unlock_states"], realtime_result["unlock_states"]
        )

        # Complete prerequisite chapter
        ChapterProgress.objects.create(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Now they should differ
        new_snapshot_result = UnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )
        new_realtime_result = UnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )

        # Realtime should now show chapter2 unlocked
        self.assertFalse(
            new_realtime_result["unlock_states"][str(self.chapter2.id)]["locked"]
        )
        # Snapshot might still be locked (stale)


class ProblemUnlockSnapshotServiceTestCase(TestCase):
    """Test ProblemUnlockSnapshotService"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(course=self.course, user=self.user)
        self.chapter = ChapterFactory(course=self.course, order=1)
        self.problem1 = ProblemFactory(chapter=self.chapter)
        self.problem2 = ProblemFactory(chapter=self.chapter)
        self.problem3 = ProblemFactory(chapter=self.chapter)

    @patch("courses.tasks.refresh_problem_unlock_snapshot.delay")
    def test_get_or_create_snapshot_new(self, mock_delay):
        """Test creating a new problem snapshot"""
        result = ProblemUnlockSnapshotService.get_or_create_snapshot(self.enrollment)

        self.assertEqual(result.enrollment, self.enrollment)
        self.assertEqual(result.course, self.course)
        self.assertTrue(mock_delay.called)
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch("courses.tasks.refresh_problem_unlock_snapshot.delay")
    def test_get_or_create_snapshot_existing(self, mock_delay):
        """Test getting existing problem snapshot"""
        # Create existing snapshot
        existing_snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={"1": {"unlocked": True, "reason": None}},
            version=1,
        )

        # Call get_or_create_snapshot
        result = ProblemUnlockSnapshotService.get_or_create_snapshot(self.enrollment)

        # Should return existing snapshot
        self.assertEqual(result, existing_snapshot)
        # Should not trigger async task since snapshot exists
        self.assertFalse(mock_delay.called)

    def test_mark_stale_existing_snapshot(self):
        """Test marking existing problem snapshot as stale"""
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course, enrollment=self.enrollment, is_stale=False
        )

        ProblemUnlockSnapshotService.mark_stale(self.enrollment)

        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_mark_stale_nonexistent_snapshot(self):
        """Test marking non-existent problem snapshot as stale (should not raise error)"""
        # This should not raise an exception
        ProblemUnlockSnapshotService.mark_stale(self.enrollment)

    @patch("courses.tasks.refresh_problem_unlock_snapshot.delay")
    def test_get_unlock_status_hybrid_fresh_snapshot(self, mock_delay):
        """Test hybrid query with fresh problem snapshot"""
        # Create fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                "1": {"unlocked": True, "reason": None},
                "2": {"unlocked": False, "reason": "prerequisite"},
            },
            is_stale=False,
            version=2,
        )

        result = ProblemUnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Should use snapshot data
        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_version"], 2)
        self.assertEqual(result["unlock_states"], snapshot.unlock_states)
        # Should not trigger async refresh
        self.assertFalse(mock_delay.called)

    @patch("courses.tasks.refresh_problem_unlock_snapshot.delay")
    def test_get_unlock_status_hybrid_stale_snapshot(self, mock_delay):
        """Test hybrid query with stale problem snapshot"""
        # Create stale snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={"1": {"unlocked": True, "reason": None}},
            is_stale=True,
            version=1,
        )

        result = ProblemUnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Should use stale snapshot data
        self.assertEqual(result["source"], "snapshot_stale")
        self.assertEqual(result["snapshot_version"], 1)
        self.assertEqual(result["unlock_states"], snapshot.unlock_states)
        # Should trigger async refresh
        self.assertTrue(mock_delay.called)
        mock_delay.assert_called_once_with(self.enrollment.id)

    @patch("courses.tasks.refresh_problem_unlock_snapshot.delay")
    def test_get_unlock_status_hybrid_no_snapshot(self, mock_delay):
        """Test hybrid query with no problem snapshot"""
        result = ProblemUnlockSnapshotService.get_unlock_status_hybrid(
            self.course, self.enrollment
        )

        # Should use realtime computation
        self.assertEqual(result["source"], "realtime")
        # Should trigger async snapshot creation
        self.assertTrue(mock_delay.called)
        mock_delay.assert_called_once_with(self.enrollment.id)

    def test_compute_realtime_no_conditions(self):
        """Test realtime computation with no unlock conditions"""
        result = ProblemUnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )

        self.assertEqual(result["source"], "realtime")
        # All problems should be unlocked
        for problem_id in result["unlock_states"]:
            self.assertTrue(result["unlock_states"][problem_id]["unlocked"])
            self.assertIsNone(result["unlock_states"][problem_id]["reason"])

    def test_compute_realtime_with_prerequisite_condition(self):
        """Test realtime computation with prerequisite unlock condition"""
        # Create unlock condition: problem2 requires problem1 to be solved
        condition = ProblemUnlockConditionFactory(
            problem=self.problem2, unlock_condition_type="prerequisite"
        )
        condition.prerequisite_problems.add(self.problem1)

        result = ProblemUnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )

        self.assertEqual(result["source"], "realtime")
        # problem1 and problem3 should be unlocked
        self.assertTrue(result["unlock_states"][str(self.problem1.id)]["unlocked"])
        self.assertTrue(result["unlock_states"][str(self.problem3.id)]["unlocked"])
        # problem2 should be locked due to prerequisite
        self.assertFalse(result["unlock_states"][str(self.problem2.id)]["unlocked"])
        self.assertEqual(
            result["unlock_states"][str(self.problem2.id)]["reason"], "prerequisite"
        )

        # Complete problem1
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )

        # Recompute - problem2 should now be unlocked
        result2 = ProblemUnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )
        self.assertTrue(result2["unlock_states"][str(self.problem2.id)]["unlocked"])
        self.assertIsNone(result2["unlock_states"][str(self.problem2.id)]["reason"])

    def test_compute_realtime_with_date_condition(self):
        """Test realtime computation with date-based unlock condition"""
        # Create unlock condition with future date
        future_date = timezone.now() + timedelta(days=1)
        condition = ProblemUnlockConditionFactory(
            problem=self.problem2, unlock_condition_type="date", unlock_date=future_date
        )

        result = ProblemUnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )

        self.assertEqual(result["source"], "realtime")
        # problem2 should be locked due to date
        self.assertFalse(result["unlock_states"][str(self.problem2.id)]["unlocked"])
        self.assertEqual(
            result["unlock_states"][str(self.problem2.id)]["reason"], "date"
        )

    def test_compute_realtime_with_both_conditions(self):
        """Test realtime computation with both prerequisite and date conditions"""
        # Create unlock condition with both
        future_date = timezone.now() + timedelta(days=1)
        condition = ProblemUnlockConditionFactory(
            problem=self.problem2, unlock_condition_type="both", unlock_date=future_date
        )
        condition.prerequisite_problems.add(self.problem1)

        result = ProblemUnlockSnapshotService._compute_realtime(
            self.course, self.enrollment
        )

        self.assertEqual(result["source"], "realtime")
        # problem2 should be locked with 'both' reason
        self.assertFalse(result["unlock_states"][str(self.problem2.id)]["unlocked"])
        self.assertEqual(
            result["unlock_states"][str(self.problem2.id)]["reason"], "both"
        )


class ProblemUnlockSnapshotStatusTestCase(TestCase):
    """Test ProblemUnlockSnapshot status field functionality"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(course=self.course, user=self.user)
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.problem1 = ProblemFactory(chapter=self.chapter1, type="algorithm")
        self.problem2 = ProblemFactory(chapter=self.chapter1, type="algorithm")
        self.problem3 = ProblemFactory(chapter=self.chapter1, type="algorithm")

    def test_recompute_includes_status_field(self):
        """Test that recompute includes status in unlock_states"""
        # Create progress records
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem2, status="in_progress"
        )
        # problem3 has no progress record

        # Create snapshot and recompute
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course, enrollment=self.enrollment
        )
        snapshot.recompute()

        # Verify status field is included
        states = snapshot.unlock_states
        self.assertIn("status", states[str(self.problem1.id)])
        self.assertEqual(states[str(self.problem1.id)]["status"], "solved")
        self.assertEqual(states[str(self.problem2.id)]["status"], "in_progress")
        self.assertEqual(states[str(self.problem3.id)]["status"], "not_started")

    def test_recompute_batch_query_progress(self):
        """Test that recompute uses batch query for progress"""
        # Create progress for all problems
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem2, status="solved"
        )

        # Verify recompute doesn't cause N+1 queries
        # Expected queries:
        # 1. INSERT for snapshot creation
        # 2. SELECT for progress batch query
        # 3. SELECT for problems with prefetched unlock_condition
        # 4. UPDATE for snapshot save
        with self.assertNumQueries(4):
            snapshot = ProblemUnlockSnapshot.objects.create(
                course=self.course, enrollment=self.enrollment
            )
            snapshot.recompute()

    def test_backward_compatibility_without_status(self):
        """Test backward compatibility with old snapshot format without status"""
        # Create snapshot with old format (no status field)
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.problem1.id): {"unlocked": True, "reason": None},
                str(self.problem2.id): {"unlocked": True, "reason": None},
            },
        )

        # Verify old format is still valid
        self.assertTrue(snapshot.unlock_states[str(self.problem1.id)]["unlocked"])
        # status key should not exist
        self.assertNotIn("status", snapshot.unlock_states[str(self.problem1.id)])

    def test_serializer_reads_status_from_snapshot(self):
        """Test that serializer reads status from snapshot when available"""
        from courses.serializers import ProblemSerializer

        # Create progress and snapshot
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )

        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course, enrollment=self.enrollment
        )
        snapshot.recompute()

        # Create serializer with snapshot context
        context = {
            "request": type("Request", (), {"user": self.user})(),
            "unlock_states": snapshot.unlock_states,
        }
        serializer = ProblemSerializer(self.problem1, context=context)

        # Verify status comes from snapshot
        self.assertEqual(serializer.data["status"], "solved")

    def test_serializer_fallback_to_db_when_no_status(self):
        """Test that serializer falls back to DB when snapshot lacks status"""
        from courses.serializers import ProblemSerializer

        # Create progress
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )

        # Create snapshot with old format (no status)
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={str(self.problem1.id): {"unlocked": True, "reason": None}},
        )

        # Create serializer with snapshot context
        context = {
            "request": type("Request", (), {"user": self.user})(),
            "unlock_states": snapshot.unlock_states,
        }
        serializer = ProblemSerializer(self.problem1, context=context)

        # Verify status comes from database (fallback)
        self.assertEqual(serializer.data["status"], "solved")


# =============================================================================
# Batch User Status Retrieval Functions (Phase 1.5 - Task 1.5)
# =============================================================================


class GetChapterUserStatusTestCase(TestCase):
    """Test cases for get_chapter_user_status function."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)
        self.chapter3 = ChapterFactory(course=self.course, order=3)

    def test_returns_cached_status_when_available(self):
        """Test that cached status is returned when available."""
        from courses.services import get_chapter_user_status
        from django.core.cache import cache

        chapter_ids = [self.chapter1.id, self.chapter2.id]
        cache_key = f"chapter:status:{self.course.id}:{self.user.id}"

        # Set cached data
        cached_data = {
            str(self.chapter1.id): {"status": "completed", "is_locked": False},
            str(self.chapter2.id): {"status": "in_progress", "is_locked": False},
        }
        cache.set(cache_key, cached_data, timeout=300)

        # Call function
        result = get_chapter_user_status(chapter_ids, self.user.id, self.course.id)

        # Verify cached data is returned
        self.assertEqual(result, cached_data)

    def test_returns_default_status_for_non_enrolled_user(self):
        """Test that default status is returned for users not enrolled in course."""
        from courses.services import get_chapter_user_status

        non_enrolled_user = UserFactory()
        chapter_ids = [self.chapter1.id, self.chapter2.id]

        result = get_chapter_user_status(
            chapter_ids, non_enrolled_user.id, self.course.id
        )

        # All chapters should be not_started and locked
        for ch_id in chapter_ids:
            self.assertEqual(result[str(ch_id)]["status"], "not_started")
            self.assertTrue(result[str(ch_id)]["is_locked"])

    def test_combines_snapshot_and_progress_data(self):
        """Test that function combines snapshot unlock states with progress data."""
        from courses.services import get_chapter_user_status
        from courses.models import CourseUnlockSnapshot

        chapter_ids = [self.chapter1.id, self.chapter2.id, self.chapter3.id]

        # Create progress records
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter2, completed=False
        )

        # Create snapshot with unlock states
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.chapter1.id): {
                    "locked": False,
                    "reason": None,
                    "status": "completed",
                },
                str(self.chapter2.id): {
                    "locked": False,
                    "reason": None,
                    "status": "in_progress",
                },
                str(self.chapter3.id): {
                    "locked": True,
                    "reason": "prerequisite",
                    "status": "not_started",
                },
            },
        )

        # Call function
        result = get_chapter_user_status(chapter_ids, self.user.id, self.course.id)

        # Verify results
        self.assertEqual(result[str(self.chapter1.id)]["status"], "completed")
        self.assertFalse(result[str(self.chapter1.id)]["is_locked"])

        self.assertEqual(result[str(self.chapter2.id)]["status"], "in_progress")
        self.assertFalse(result[str(self.chapter2.id)]["is_locked"])

        self.assertEqual(result[str(self.chapter3.id)]["status"], "not_started")
        self.assertTrue(result[str(self.chapter3.id)]["is_locked"])

    def test_caches_result_after_db_query(self):
        """Test that result is cached after database query."""
        from courses.services import get_chapter_user_status
        from django.core.cache import cache

        chapter_ids = [self.chapter1.id]
        cache_key = f"chapter:status:{self.course.id}:{self.user.id}"

        # Clear any existing cache
        cache.delete(cache_key)

        # Call function (should query DB and cache result)
        result1 = get_chapter_user_status(chapter_ids, self.user.id, self.course.id)

        # Verify cached data exists
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, result1)


class GetProblemUserStatusTestCase(TestCase):
    """Test cases for get_problem_user_status function."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course, order=1)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)
        self.problem1 = ProblemFactory(chapter=self.chapter)
        self.problem2 = ProblemFactory(chapter=self.chapter)
        self.problem3 = ProblemFactory(chapter=self.chapter)

    def test_returns_cached_status_when_available(self):
        """Test that cached status is returned when available."""
        from courses.services import get_problem_user_status
        from django.core.cache import cache

        problem_ids = [self.problem1.id, self.problem2.id]
        cache_key = f"problem:status:{self.chapter.id}:{self.user.id}"

        # Set cached data
        cached_data = {
            str(self.problem1.id): {"status": "solved", "is_unlocked": True},
            str(self.problem2.id): {"status": "failed", "is_unlocked": True},
        }
        cache.set(cache_key, cached_data, timeout=300)

        # Call function
        result = get_problem_user_status(problem_ids, self.user.id, self.chapter.id)

        # Verify cached data is returned
        self.assertEqual(result, cached_data)

    def test_returns_default_status_for_non_enrolled_user(self):
        """Test that default status is returned for users not enrolled in course."""
        from courses.services import get_problem_user_status

        non_enrolled_user = UserFactory()
        problem_ids = [self.problem1.id, self.problem2.id]

        result = get_problem_user_status(
            problem_ids, non_enrolled_user.id, self.chapter.id
        )

        # All problems should be not_started and locked
        for p_id in problem_ids:
            self.assertEqual(result[str(p_id)]["status"], "not_started")
            self.assertFalse(result[str(p_id)]["is_unlocked"])

    def test_combines_snapshot_and_progress_data(self):
        """Test that function combines snapshot unlock states with progress data."""
        from courses.services import get_problem_user_status
        from courses.models import ProblemUnlockSnapshot

        problem_ids = [self.problem1.id, self.problem2.id, self.problem3.id]

        # Create progress records
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem2, status="failed"
        )

        # Create snapshot with unlock states
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.problem1.id): {
                    "unlocked": True,
                    "reason": None,
                    "status": "solved",
                },
                str(self.problem2.id): {
                    "unlocked": True,
                    "reason": None,
                    "status": "failed",
                },
                str(self.problem3.id): {
                    "unlocked": False,
                    "reason": "chapter_locked",
                    "status": "not_started",
                },
            },
        )

        # Call function
        result = get_problem_user_status(problem_ids, self.user.id, self.chapter.id)

        # Verify results
        self.assertEqual(result[str(self.problem1.id)]["status"], "solved")
        self.assertTrue(result[str(self.problem1.id)]["is_unlocked"])

        self.assertEqual(result[str(self.problem2.id)]["status"], "failed")
        self.assertTrue(result[str(self.problem2.id)]["is_unlocked"])

        self.assertEqual(result[str(self.problem3.id)]["status"], "not_started")
        self.assertFalse(result[str(self.problem3.id)]["is_unlocked"])

    def test_caches_result_after_db_query(self):
        """Test that result is cached after database query."""
        from courses.services import get_problem_user_status
        from django.core.cache import cache

        problem_ids = [self.problem1.id]
        cache_key = f"problem:status:{self.chapter.id}:{self.user.id}"

        # Clear any existing cache
        cache.delete(cache_key)

        # Call function (should query DB and cache result)
        result1 = get_problem_user_status(problem_ids, self.user.id, self.chapter.id)

        # Verify cached data exists
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, result1)

    def test_returns_default_status_for_orphan_chapter(self):
        """Test that default status is returned when chapter doesn't exist."""
        from courses.services import get_problem_user_status

        non_existent_chapter_id = 99999
        problem_ids = [self.problem1.id]

        result = get_problem_user_status(
            problem_ids, self.user.id, non_existent_chapter_id
        )

        # All problems should be not_started and locked
        for p_id in problem_ids:
            self.assertEqual(result[str(p_id)]["status"], "not_started")
            self.assertFalse(result[str(p_id)]["is_unlocked"])


class CourseUnlockSnapshotStatusTestCase(TestCase):
    """Test CourseUnlockSnapshot status field functionality"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory()
        self.user = UserFactory()
        self.enrollment = EnrollmentFactory(course=self.course, user=self.user)
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)
        self.chapter3 = ChapterFactory(course=self.course, order=3)

    def test_recompute_includes_status_field(self):
        """Test that recompute includes status in unlock_states"""
        # Create progress records
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter2, completed=False
        )
        # chapter3 has no progress record

        # Create snapshot and recompute
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course, enrollment=self.enrollment
        )
        snapshot.recompute()

        # Verify status field is included
        states = snapshot.unlock_states
        self.assertIn("status", states[str(self.chapter1.id)])
        self.assertEqual(states[str(self.chapter1.id)]["status"], "completed")
        self.assertEqual(states[str(self.chapter2.id)]["status"], "in_progress")
        self.assertEqual(states[str(self.chapter3.id)]["status"], "not_started")

    def test_recompute_batch_query_progress(self):
        """Test that recompute uses batch query for progress"""
        # Create progress for all chapters
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter2, completed=True
        )

        # Verify recompute doesn't cause N+1 queries
        # Expected queries (with prefetch_related optimization):
        # 1. INSERT for snapshot creation
        # 2. SELECT for progress batch query
        # 3. SELECT for chapters (with prefetch for unlock conditions)
        # 4. SELECT for unlock conditions (batched via prefetch_related)
        # 5. UPDATE for snapshot save
        with self.assertNumQueries(5):
            snapshot = CourseUnlockSnapshot.objects.create(
                course=self.course, enrollment=self.enrollment
            )
            snapshot.recompute()

    def test_backward_compatibility_without_status(self):
        """Test backward compatibility with old snapshot format without status"""
        # Create snapshot with old format (no status field)
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.chapter1.id): {"locked": False, "reason": None},
                str(self.chapter2.id): {"locked": True, "reason": "prerequisite"},
            },
        )

        # Verify old format is still valid
        self.assertFalse(snapshot.unlock_states[str(self.chapter1.id)]["locked"])
        # status key should not exist
        self.assertNotIn("status", snapshot.unlock_states[str(self.chapter1.id)])

    def test_serializer_reads_status_from_snapshot(self):
        """Test that serializer reads status from snapshot when available"""
        from courses.serializers import ChapterSerializer

        # Create progress and snapshot
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course, enrollment=self.enrollment
        )
        snapshot.recompute()

        # Create serializer with snapshot context
        context = {
            "request": type("Request", (), {"user": self.user})(),
            "unlock_states": snapshot.unlock_states,
        }
        serializer = ChapterSerializer(self.chapter1, context=context)

        # Verify status comes from snapshot
        self.assertEqual(serializer.data["status"], "completed")

    def test_serializer_fallback_to_db_when_no_status(self):
        """Test that serializer falls back to DB when snapshot lacks status"""
        from courses.serializers import ChapterSerializer

        # Create progress
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Create snapshot with old format (no status)
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={str(self.chapter1.id): {"locked": False, "reason": None}},
        )

        # Create serializer with snapshot context
        context = {
            "request": type("Request", (), {"user": self.user})(),
            "unlock_states": snapshot.unlock_states,
        }
        serializer = ChapterSerializer(self.chapter1, context=context)

        # Verify status comes from database (fallback)
        self.assertEqual(serializer.data["status"], "completed")
