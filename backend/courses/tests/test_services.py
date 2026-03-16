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
    Submission,
    JudgingQueueStats,
    AlgorithmProblem,
    TestCase as CourseTestCase,
)
from courses.services import (
    UnlockSnapshotService,
    ChapterUnlockService,
    ProblemUnlockSnapshotService,
    JudgingCapacityService,
    CodeExecutorService,
    CODE_JUDGING_CONFIG,
)
from courses.judge_backend.Judge0Backend import Judge0Backend
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
    SubmissionFactory,
    CourseTestCaseFactory,
    AlgorithmProblemFactory,
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

    def test_compute_realtime_inlined_logic(self):
        """Test that _compute_realtime correctly computes unlock status inline"""
        result = UnlockSnapshotService._compute_realtime(self.course, self.enrollment)

        self.assertIn("unlock_states", result)
        self.assertEqual(result["source"], "realtime")

        for chapter_id in [self.chapter1.id, self.chapter2.id]:
            self.assertIn(str(chapter_id), result["unlock_states"])
            state = result["unlock_states"][str(chapter_id)]
            self.assertIn("locked", state)
            self.assertIn("reason", state)
            self.assertIn("status", state)
            self.assertIn("prerequisite_progress", state)


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
        from common.services import BusinessCacheService

        chapter_ids = [self.chapter1.id, self.chapter2.id]

        # Set cached data using BusinessCacheService
        cached_data = {
            str(self.chapter1.id): {"status": "completed", "is_locked": False},
            str(self.chapter2.id): {"status": "in_progress", "is_locked": False},
        }

        # Pre-populate cache by calling the function once
        # Then mock BusinessCacheService to return cached data
        with patch.object(
            BusinessCacheService, "cache_result", return_value=cached_data
        ) as mock_cache:
            # Call function
            result = get_chapter_user_status(chapter_ids, self.user.id, self.course.id)

            # Verify cached data is returned
            self.assertEqual(result, cached_data)
            # Verify BusinessCacheService was called
            mock_cache.assert_called_once()

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
        from common.services import BusinessCacheService

        chapter_ids = [self.chapter1.id]

        # Mock BusinessCacheService to verify it's called
        with patch.object(
            BusinessCacheService,
            "cache_result",
            side_effect=lambda cache_key, fetcher, timeout: fetcher(),
        ) as mock_cache:
            # Call function (should query DB and cache result)
            result1 = get_chapter_user_status(chapter_ids, self.user.id, self.course.id)

            # Verify BusinessCacheService was called with correct parameters
            mock_cache.assert_called_once()
            call_args = mock_cache.call_args
            self.assertIn(
                "cache_key",
                call_args.kwargs or call_args[1]
                if len(call_args) > 1
                else call_args[1],
            )
            self.assertIn(
                "fetcher",
                call_args.kwargs or call_args[1]
                if len(call_args) > 1
                else call_args[1],
            )
            self.assertEqual(call_args.kwargs.get("timeout", 300), 300)

            # Verify result is returned
            self.assertIsNotNone(result1)
            self.assertIn(str(self.chapter1.id), result1)


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
        from common.services import BusinessCacheService

        problem_ids = [self.problem1.id, self.problem2.id]

        # Set cached data using mock
        cached_data = {
            str(self.problem1.id): {"status": "solved", "is_unlocked": True},
            str(self.problem2.id): {"status": "failed", "is_unlocked": True},
        }

        with patch.object(
            BusinessCacheService, "cache_result", return_value=cached_data
        ) as mock_cache:
            # Call function
            result = get_problem_user_status(problem_ids, self.user.id, self.chapter.id)

            # Verify cached data is returned
            self.assertEqual(result, cached_data)
            # Verify BusinessCacheService was called
            mock_cache.assert_called_once()

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
        from common.services import BusinessCacheService

        problem_ids = [self.problem1.id]

        # Call function and verify BusinessCacheService is used
        with patch.object(BusinessCacheService, "cache_result") as mock_cache:
            # Set up mock to call the actual fetcher function
            def side_effect(cache_key, fetcher, timeout):
                return fetcher()

            mock_cache.side_effect = side_effect

            # Call function (should query DB and cache result)
            result1 = get_problem_user_status(
                problem_ids, self.user.id, self.chapter.id
            )

            # Verify BusinessCacheService was called
            mock_cache.assert_called_once()

        # Verify result is returned
        self.assertIsNotNone(result1)
        self.assertIn(str(self.problem1.id), result1)
        # Result should contain the problem status
        self.assertIn("status", result1[str(self.problem1.id)])

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
        # Expected queries (with select_related/prefetch_related optimization):
        # 1. INSERT for snapshot creation
        # 2. SELECT for progress batch query
        # 3. SELECT for chapters (with select_related unlock_condition + prefetch_related prerequisite_chapters)
        # 4. UPDATE for snapshot save
        with self.assertNumQueries(4):
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


class JudgingCapacityServiceTestCase(TestCase):
    """Test cases for JudgingCapacityService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = JudgingCapacityService()
        self.user = UserFactory()
        self.problem = ProblemFactory(type="algorithm")
        self.service.invalidate_cache()

    def test_init_service(self):
        """Test that service initializes with correct config"""
        self.assertIsInstance(self.service.config, dict)
        self.assertEqual(self.service.config["max_queue_size"], 18)
        self.assertEqual(self.service.config["soft_timeout_sec"], 270)
        self.assertEqual(self.service.config["hard_timeout_sec"], 300)

    def test_get_cache_key(self):
        """Test that cache key is generated correctly"""
        key = self.service.get_cache_key()
        self.assertEqual(key, "judging_capacity:current")

    def test_get_current_capacity_empty_system(self):
        """Test capacity calculation with empty system"""
        capacity = self.service.get_current_capacity()

        self.assertEqual(capacity["pending_count"], 0)
        self.assertEqual(capacity["running_count"], 0)
        self.assertEqual(capacity["total_capacity"], 18)
        self.assertEqual(capacity["available_slots"], 18)
        self.assertEqual(capacity["status"], "available")

    def test_get_current_capacity_with_pending_tasks(self):
        """Test capacity calculation with pending tasks"""
        # Create submissions and queue stats
        for i in range(5):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(submission=submission, status="pending")

        capacity = self.service.get_current_capacity(use_cache=False)

        self.assertEqual(capacity["pending_count"], 5)
        self.assertEqual(capacity["running_count"], 0)
        self.assertEqual(capacity["available_slots"], 13)
        self.assertEqual(capacity["status"], "available")

    def test_get_current_capacity_over_warning_threshold(self):
        """Test capacity calculation over warning threshold"""
        # Create submissions and queue stats
        for i in range(12):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(submission=submission, status="pending")

        capacity = self.service.get_current_capacity(use_cache=False)

        self.assertEqual(capacity["status"], "busy")

    def test_get_current_capacity_at_max_limit(self):
        """Test capacity calculation at maximum limit"""
        # Create submissions and queue stats
        for i in range(18):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(submission=submission, status="pending")

        capacity = self.service.get_current_capacity(use_cache=False)

        self.assertEqual(capacity["status"], "full")
        self.assertEqual(capacity["available_slots"], 0)

    def test_get_current_capacity_running_tasks(self):
        """Test capacity calculation with running tasks"""
        # Create 5 pending and 3 running tasks
        for i in range(5):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(submission=submission, status="pending")

        for i in range(3):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(
                submission=submission, status="started", started_at=timezone.now()
            )

        capacity = self.service.get_current_capacity(use_cache=False)

        # pending_count includes both "pending" and "started" statuses
        self.assertEqual(capacity["pending_count"], 8)
        self.assertEqual(capacity["running_count"], 3)
        self.assertEqual(capacity["available_slots"], 10)

    @patch("courses.services.cache")
    def test_capacity_caching(self, mock_cache):
        """Test that capacity information is cached"""
        mock_cache.get.return_value = None

        # First call should populate cache
        self.service.get_current_capacity()

        # Verify cache was set
        mock_cache.set.assert_called()
        args, kwargs = mock_cache.set.call_args
        self.assertEqual(args[0], self.service.get_cache_key())
        self.assertEqual(kwargs.get("timeout", args[2] if len(args) > 2 else 30), 30)

        # Second call should use cache
        mock_cache.get.return_value = {
            "pending_count": 5,
            "running_count": 0,
            "total_capacity": 18,
            "available_slots": 13,
            "status": "busy",
        }

        capacity = self.service.get_current_capacity()
        mock_cache.get.assert_called()

    @patch("courses.services.cache")
    def test_cache_invalidation(self, mock_cache):
        """Test cache invalidation"""
        self.service.invalidate_cache()

        mock_cache.delete.assert_called_once_with(self.service.get_cache_key())

    def test_can_accept_submission_available(self):
        """Test accepting submission when system is available"""
        can_accept, reason = self.service.can_accept_submission()

        self.assertTrue(can_accept)
        self.assertEqual(reason, "")

    def test_can_accept_submission_full(self):
        """Test rejecting submission when system is full"""
        # Fill the queue
        for i in range(18):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(submission=submission, status="pending")

        self.service.invalidate_cache()
        can_accept, reason = self.service.can_accept_submission()

        self.assertFalse(can_accept)
        self.assertEqual(reason, "系统繁忙，请稍后再试")

    def test_estimate_wait_time(self):
        """Test wait time estimation"""
        position_1 = self.service.estimate_wait_time(1)
        position_5 = self.service.estimate_wait_time(5)
        position_0 = self.service.estimate_wait_time(0)

        self.assertEqual(position_1, 30)  # 1 * 30 seconds
        self.assertEqual(position_5, 150)  # 5 * 30 seconds
        self.assertEqual(position_0, 0)

    def test_get_queue_position(self):
        """Test getting queue position for a submission"""
        # Create a submission
        submission = SubmissionFactory(user=self.user, problem=self.problem)
        stats = JudgingQueueStats.objects.create(
            submission=submission, status="pending"
        )

        # Create some tasks ahead (created_at is auto_now_add, must use update)
        for i in range(3):
            ahead_submission = SubmissionFactory(user=self.user, problem=self.problem)
            ahead_stats = JudgingQueueStats.objects.create(
                submission=ahead_submission,
                status="pending",
            )
            ahead_stats.created_at = stats.created_at - timezone.timedelta(
                minutes=i + 1
            )
            ahead_stats.save(update_fields=["created_at"])

        position = self.service.get_queue_position(submission)

        self.assertEqual(position, 4)

    def test_get_queue_position_not_in_queue(self):
        """Test getting queue position when not in queue"""
        submission = SubmissionFactory(user=self.user, problem=self.problem)
        position = self.service.get_queue_position(submission)

        self.assertIsNone(position)

    def test_get_system_status_empty(self):
        """Test system status with empty system"""
        status = self.service.get_system_status()

        self.assertIn("capacity", status)
        self.assertIn("recent_performance", status)
        self.assertIn("config", status)

        self.assertEqual(status["capacity"]["pending_count"], 0)
        self.assertEqual(status["capacity"]["status"], "available")

    def test_get_system_status_with_performance_stats(self):
        """Test system status with performance statistics"""
        from datetime import timedelta

        mock_now = timezone.now()

        # Create completed submission with wait and execution times
        submission = SubmissionFactory(user=self.user, problem=self.problem)
        JudgingQueueStats.objects.create(
            submission=submission,
            status="success",
            completed_at=mock_now - timedelta(minutes=30),
            queue_wait_seconds=15,
            execution_seconds=10,
        )

        with patch("django.utils.timezone.now", return_value=mock_now):
            status = self.service.get_system_status()

        self.assertEqual(status["recent_performance"]["total_completed_last_hour"], 1)
        self.assertEqual(status["recent_performance"]["avg_wait_time_seconds"], 15)
        self.assertEqual(status["recent_performance"]["avg_execution_time_seconds"], 10)

    def test_capacity_value_bounds(self):
        """Test that capacity values never go negative"""
        # Create more submissions than capacity
        for i in range(20):
            submission = SubmissionFactory(user=self.user, problem=self.problem)
            JudgingQueueStats.objects.create(submission=submission, status="pending")

        capacity = self.service.get_current_capacity(use_cache=False)

        self.assertEqual(capacity["available_slots"], 0)
        self.assertEqual(capacity["pending_count"], 20)


class CodeJudgingConfigTestCase(TestCase):
    """Test cases for CODE_JUDGING_CONFIG"""

    def test_config_values(self):
        """Test that config values are set correctly"""
        config = CODE_JUDGING_CONFIG

        self.assertEqual(config["max_queue_size"], 18)
        self.assertEqual(config["warning_threshold"], 10)
        self.assertEqual(config["soft_timeout_sec"], 270)
        self.assertEqual(config["hard_timeout_sec"], 300)
        self.assertEqual(config["queue_timeout_sec"], 120)
        self.assertEqual(config["cache_timeout_sec"], 30)
        self.assertEqual(config["avg_judging_time_sec"], 30)
        self.assertEqual(config["max_retries"], 3)


class CodeExecutorServiceTestCase(TestCase):
    """Test cases for CodeExecutorService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = CodeExecutorService()
        self.user = UserFactory()
        self.algorithm_problem = AlgorithmProblemFactory()
        self.problem = self.algorithm_problem.problem
        self.test_case = CourseTestCaseFactory(
            problem=self.algorithm_problem,
            input_data='{"test": "input"}',
            expected_output='{"result": "output"}',
        )
        self.algorithm_problem.test_cases.add(self.test_case)
        self.algorithm_problem.solution_name = {"python": "solve"}
        self.algorithm_problem.save()

    @patch("courses.services.Judge0Backend")
    def test_run_all_test_cases_sync_success(self, mock_backend):
        """Test synchronous code execution with success"""
        # Create service with mocked backend
        mock_instance = mock_backend.return_value
        mock_instance.get_language_id.return_value = 3
        mock_instance.submit_code.return_value = {"token": "test_token"}
        mock_instance.get_result.return_value = {
            "status_id": 3,
            "stdout": '{"result": "success"}',
            "stderr": "",
            "time": 100,
            "memory": 50,
        }

        service = CodeExecutorService(backend=mock_instance)

        # Execute sync mode
        submission = service.run_all_test_cases(
            user=self.user,
            problem=self.problem,
            code='def solve():\n    return {"result": "output"}',
            language="python",
        )

        # Verify submission created and updated
        self.assertEqual(submission.user, self.user)
        self.assertEqual(submission.problem, self.problem)
        self.assertEqual(submission.status, "accepted")
        self.assertIn("Test case", submission.output)
        self.assertIsNotNone(submission.execution_time)
        self.assertIsNotNone(submission.memory_used)

    @patch("courses.services.Judge0Backend")
    def test_run_all_test_cases_sync_failure(self, mock_backend):
        """Test synchronous code execution with failure"""
        # Create service with mocked backend
        mock_instance = mock_backend.return_value
        mock_instance.get_language_id.return_value = 3
        mock_instance.submit_code.return_value = {"token": "test_token"}
        mock_instance.get_result.return_value = {
            "status_id": 4,  # Wrong answer
            "stdout": '{"result": "wrong"}',
            "stderr": "",
            "time": 100,
            "memory": 50,
        }

        service = CodeExecutorService(backend=mock_instance)

        # Execute sync mode
        submission = service.run_all_test_cases(
            user=self.user,
            problem=self.problem,
            code='def solve():\n    return {"result": "wrong"}',
            language="python",
        )

        # Verify submission marked as wrong answer
        self.assertEqual(submission.status, "wrong_answer")

    @patch("courses.services.Judge0Backend")
    def test_run_all_test_cases_async_success(self, mock_backend):
        """Test asynchronous code execution with success"""
        # Create submission with queue stats
        submission = SubmissionFactory(user=self.user, problem=self.problem)
        queue_stats = JudgingQueueStats.objects.create(
            submission=submission, status="pending"
        )

        # Create service with mocked backend
        mock_instance = mock_backend.return_value
        mock_instance.get_language_id.return_value = 3
        mock_instance.submit_code.return_value = {"token": "test_token"}
        mock_instance.get_result.return_value = {
            "status_id": 3,
            "stdout": '{"result": "success"}',
            "stderr": "",
            "time": 100,
            "memory": 50,
        }

        service = CodeExecutorService(backend=mock_instance)

        # Execute async mode
        result = service.run_all_test_cases_async(
            submission=submission,
            problem=self.problem,
            code='def solve():\n    return {"result": "output"}',
            language="python",
        )

        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "accepted")
        self.assertIn("execution_seconds", result)
        self.assertIn("queue_wait_seconds", result)

        # Verify queue stats updated
        queue_stats.refresh_from_db()
        self.assertEqual(queue_stats.status, "success")
        self.assertIsNotNone(queue_stats.started_at)
        self.assertIsNotNone(queue_stats.completed_at)
        self.assertEqual(queue_stats.execution_seconds, result["execution_seconds"])
        self.assertIsNotNone(queue_stats.queue_wait_seconds)

        # Verify submission updated
        submission.refresh_from_db()
        self.assertEqual(submission.status, "accepted")
        self.assertIsNotNone(submission.execution_time)

    @patch("courses.services.Judge0Backend")
    def test_run_all_test_cases_async_failure(self, mock_backend):
        """Test asynchronous code execution with failure"""
        # Create submission with queue stats
        submission = SubmissionFactory(user=self.user, problem=self.problem)
        queue_stats = JudgingQueueStats.objects.create(
            submission=submission, status="pending"
        )

        # Create service with mocked backend
        mock_instance = mock_backend.return_value
        mock_instance.get_language_id.return_value = 3
        mock_instance.submit_code.return_value = {"token": "test_token"}
        mock_instance.get_result.return_value = {
            "status_id": 4,  # Wrong answer
            "stdout": '{"result": "wrong"}',
            "stderr": "runtime error",
            "time": 100,
            "memory": 50,
        }

        service = CodeExecutorService(backend=mock_instance)

        # Execute async mode
        result = service.run_all_test_cases_async(
            submission=submission,
            problem=self.problem,
            code='def solve():\n    return {"result": "wrong"}',
            language="python",
        )

        # Verify result - execution succeeded but answer was wrong
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "wrong_answer")
        self.assertIn("execution_seconds", result)

        # Verify queue stats updated - execution succeeded so status is "success"
        queue_stats.refresh_from_db()
        self.assertEqual(queue_stats.status, "success")

        # Verify submission updated with wrong_answer status and stderr in error
        submission.refresh_from_db()
        self.assertEqual(submission.status, "wrong_answer")
        self.assertIn("runtime error", submission.error)  # stderr is in submission.error

    def test_run_all_test_cases_async_no_queue_stats(self):
        """Test async mode without queue stats (should handle gracefully)"""
        # Create submission without queue stats
        submission = SubmissionFactory(user=self.user, problem=self.problem)

        # Execute async mode without mocking backend (will fail)
        result = self.service.run_all_test_cases_async(
            submission=submission,
            problem=self.problem,
            code='def solve():\n    return {"result": "output"}',
            language="python",
        )

        # Should handle gracefully and mark as internal error
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(submission.status, "internal_error")

    @patch("courses.services.Judge0Backend")
    def test_execute_test_cases_internal_error_handling(self, mock_backend):
        """Test internal error handling in test case execution"""
        # Create submission
        submission = SubmissionFactory(user=self.user, problem=self.problem)

        # Create service with mocked backend
        mock_instance = mock_backend.return_value
        mock_instance.get_language_id.side_effect = Exception("Backend error")

        service = CodeExecutorService(backend=mock_instance)

        # Execute internal method
        result = service._execute_test_cases_internal(
            submission=submission,
            problem=self.problem,
            code="def solve():\n    pass",
            language="python",
        )

        # Should handle error gracefully
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "internal_error")
        self.assertIn("Backend error", result["error"])

    @patch("courses.services.Judge0Backend")
    def test_execute_test_cases_no_test_cases(self, mock_backend):
        """Test handling when no test cases are available"""
        # Use existing algorithm problem and clear its test cases
        self.algorithm_problem.test_cases.all().delete()

        # Create submission
        submission = SubmissionFactory(user=self.user, problem=self.problem)

        # Create service with mocked backend (not actually used since no test cases)
        mock_instance = mock_backend.return_value
        service = CodeExecutorService(backend=mock_instance)

        # Execute internal method
        result = service._execute_test_cases_internal(
            submission=submission,
            problem=self.problem,
            code="def solve():\n    pass",
            language="python",
        )

        # Should handle no test cases
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "compilation_error")
        self.assertIn("No test cases available", result["error"])

    def test_backward_compatibility_sync_method(self):
        """Test that sync method remains unchanged for backward compatibility"""
        # Verify the original method signature is preserved
        import inspect

        sync_method = self.service.run_all_test_cases
        sig = inspect.signature(sync_method)

        # Should accept user, problem, code, and optional language
        params = list(sig.parameters.keys())
        self.assertIn("user", params)
        self.assertIn("problem", params)
        self.assertIn("code", params)
        self.assertIn("language", params)

        # Should return Submission instance
        self.assertEqual(sig.return_annotation, Submission)

    def test_async_method_signature(self):
        """Test async method signature"""
        import inspect

        async_method = self.service.run_all_test_cases_async
        sig = inspect.signature(async_method)

        # Should accept submission, problem, code, and optional language
        params = list(sig.parameters.keys())
        self.assertIn("submission", params)
        self.assertIn("problem", params)
        self.assertIn("code", params)
        self.assertIn("language", params)

        # Should return Dict[str, Any]
        self.assertIn("Dict", str(sig.return_annotation))

    def test_code_executor_service_init(self):
        """Test CodeExecutorService initialization"""
        # Test with default backend
        service = CodeExecutorService()
        self.assertIsInstance(service.backend, Judge0Backend)

        # Test with custom backend
        mock_backend = MagicMock()
        service = CodeExecutorService(backend=mock_backend)
        self.assertEqual(service.backend, mock_backend)


class GenerateJudge0CodeTest(TestCase):
    """Test generate_judge0_code function with Python literal support"""

    def test_json_array_input(self):
        """Test JSON array input - backward compatibility"""
        from courses.services import generate_judge0_code

        user_code = "def solve(a, b):\n    return a + b"
        code = generate_judge0_code(user_code, "solve", "python")

        # Verify the generated code contains parse_input function
        self.assertIn("def parse_input(input_data):", code)
        self.assertIn("import ast", code)

        # Test that the generated code can parse JSON array
        exec_globals = {}
        exec(code, exec_globals)

        # Simulate stdin parsing
        result = exec_globals["parse_input"]("[1, 2]")
        self.assertEqual(result, [1, 2])

    def test_json_object_input(self):
        """Test JSON object input - backward compatibility"""
        from courses.services import generate_judge0_code

        user_code = "def solve(n, s):\n    return n + len(s)"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result = exec_globals["parse_input"]('{"n": 5, "s": "hello"}')
        self.assertEqual(result, {"n": 5, "s": "hello"})

    def test_python_tuple_input(self):
        """Test Python tuple input - new feature"""
        from courses.services import generate_judge0_code

        user_code = "def access_tuple(t, index):\n    return t[index]"
        code = generate_judge0_code(user_code, "access_tuple", "python")

        exec_globals = {}
        exec(code, exec_globals)

        # Test tuple parsing
        result = exec_globals["parse_input"]("[(1,2,3), 2]")
        self.assertEqual(result, [(1, 2, 3), 2])
        self.assertIsInstance(result[0], tuple)

    def test_python_tuple_direct(self):
        """Test direct tuple input like (1, 2, 3)"""
        from courses.services import generate_judge0_code

        user_code = "def solve(a, b, c):\n    return a + b + c"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result = exec_globals["parse_input"]("(1, 2, 3)")
        self.assertEqual(result, (1, 2, 3))

    def test_python_set_input(self):
        """Test Python set input - new feature"""
        from courses.services import generate_judge0_code

        user_code = "def solve(s):\n    return len(s)"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result = exec_globals["parse_input"]("{1, 2, 3}")
        self.assertEqual(result, {1, 2, 3})
        self.assertIsInstance(result, set)

    def test_python_boolean_input(self):
        """Test Python boolean input - new feature"""
        from courses.services import generate_judge0_code

        user_code = "def solve(flag):\n    return not flag"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result_true = exec_globals["parse_input"]("True")
        self.assertEqual(result_true, True)
        self.assertIsInstance(result_true, bool)

        result_false = exec_globals["parse_input"]("False")
        self.assertEqual(result_false, False)

    def test_python_none_input(self):
        """Test Python None input - new feature"""
        from courses.services import generate_judge0_code

        user_code = "def solve(value):\n    return value is None"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result = exec_globals["parse_input"]("None")
        self.assertEqual(result, None)

    def test_mixed_types_input(self):
        """Test mixed types input"""
        from courses.services import generate_judge0_code

        user_code = "def solve(a, b, c, d):\n    return [a, b, c, d]"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result = exec_globals["parse_input"]("[(1,2,3), True, None, 'text']")
        self.assertEqual(result, [(1, 2, 3), True, None, "text"])

    def test_security_reject_code_injection(self):
        """Test that code injection is not executed - treated as string"""
        from courses.services import generate_judge0_code

        user_code = "def solve(x):\n    return x"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        # Malicious code should NOT be executed, just returned as string
        result = exec_globals["parse_input"]("__import__('os').system('ls')")
        # Should be returned as plain string, not executed
        self.assertEqual(result, "__import__('os').system('ls')")
        self.assertIsInstance(result, str)

    def test_security_reject_expression(self):
        """Test that expressions are not executed - treated as string"""
        from courses.services import generate_judge0_code

        user_code = "def solve(x):\n    return x"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        # Expressions like function calls should NOT be executed
        result = exec_globals["parse_input"]("len([1,2,3])")
        # Should be returned as plain string, not executed
        self.assertEqual(result, "len([1,2,3])")
        self.assertIsInstance(result, str)

    def test_fallback_comma_split(self):
        """Test fallback to comma split for non-JSON/non-Python input"""
        from courses.services import generate_judge0_code

        user_code = "def solve(a, b):\n    return a + b"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        # Fallback to split by ', '
        result = exec_globals["parse_input"]("hello, world")
        self.assertEqual(result, ["hello", "world"])

    def test_simple_string_no_comma(self):
        """Test simple string without comma"""
        from courses.services import generate_judge0_code

        user_code = "def solve(s):\n    return s.upper()"
        code = generate_judge0_code(user_code, "solve", "python")

        exec_globals = {}
        exec(code, exec_globals)

        result = exec_globals["parse_input"]("hello")
        self.assertEqual(result, "hello")
