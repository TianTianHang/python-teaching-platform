"""
Tests for Django signal handlers in the courses app.

This module tests that cache invalidation signals work correctly
when models are created, updated, or deleted.
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from .factories import (
    CourseFactory,
    ChapterFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
    ProblemFactory,
    ProblemProgressFactory,
)
from .conftest import CoursesTestCase
from common.utils.cache import get_cache_key


class ChapterProgressSignalTestCase(CoursesTestCase):
    """
    Test cases for ChapterProgress signal handler cache invalidation.
    """

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course, order=0)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _get_cache_keys_for_page(self, page=1):
        """Generate cache keys for a specific page.

        使用新的分离缓存架构的 cache key 格式：
        - chapter:global:list:{course_id}
        - chapter:status:{course_id}:{user_id}
        """
        # 新的全局数据缓存 key
        global_cache_key = f"chapter:global:list:{self.course.id}"

        # 新的用户状态缓存 key
        status_cache_key = f"chapter:status:{self.course.id}:{self.user.id}"

        return (
            global_cache_key,
            status_cache_key,
            None,  # enrollment 暂无新缓存 key
        )

    def test_chapter_progress_signal_invalidates_cache_on_create(self):
        """
        Test that creating a ChapterProgress invalidates related caches.

        Note: 章节进度变更只应使用户状态缓存失效，全局缓存应保持有效。
        """
        # First, populate caches by making API requests with explicit page=1
        # 1. Chapter list endpoint
        response1 = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/?page=1&exclude=prerequisite_progress"
        )
        self.assertEqual(response1.status_code, 200)

        # Generate expected cache keys
        global_key, status_key, _ = self._get_cache_keys_for_page()

        # Verify caches exist before creating ChapterProgress
        self.assertIsNotNone(cache.get(global_key), "Global cache should exist")
        self.assertIsNotNone(cache.get(status_key), "Status cache should exist")

        # Create a ChapterProgress (should trigger cache invalidation)
        ChapterProgressFactory(enrollment=self.enrollment, chapter=self.chapter)

        # Verify only status cache is invalidated, global cache should remain
        self.assertIsNotNone(
            cache.get(global_key), "Global cache should NOT be invalidated"
        )
        self.assertIsNone(cache.get(status_key), "Status cache should be invalidated")

    def test_chapter_progress_signal_invalidates_cache_on_update(self):
        """
        Test that updating a ChapterProgress invalidates related caches.

        Note: 章节进度变更只应使用户状态缓存失效，全局缓存应保持有效。
        """
        # Create a ChapterProgress
        chapter_progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter, completed=False
        )

        # Populate caches by making API requests with explicit page=1
        response1 = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/?page=1&exclude=prerequisite_progress"
        )
        self.assertEqual(response1.status_code, 200)

        # Generate expected cache keys
        global_key, status_key, _ = self._get_cache_keys_for_page()

        # Verify caches exist
        self.assertIsNotNone(cache.get(global_key), "Global cache should exist")
        self.assertIsNotNone(cache.get(status_key), "Status cache should exist")

        # Update the ChapterProgress (mark as completed)
        chapter_progress.completed = True
        from django.utils import timezone

        chapter_progress.completed_at = timezone.now()
        chapter_progress.save()

        # Verify only status cache is invalidated, global cache should remain
        self.assertIsNotNone(
            cache.get(global_key), "Global cache should NOT be invalidated"
        )
        self.assertIsNone(cache.get(status_key), "Status cache should be invalidated")

    def test_chapter_progress_signal_invalidates_cache_on_delete(self):
        """
        Test that deleting a ChapterProgress invalidates related caches.

        Note: 章节进度变更只应使用户状态缓存失效，全局缓存应保持有效。
        """
        # Create a ChapterProgress
        chapter_progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter
        )

        # Populate caches by making API requests with explicit page=1
        response1 = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/?page=1&exclude=prerequisite_progress"
        )
        self.assertEqual(response1.status_code, 200)

        # Generate expected cache keys
        global_key, status_key, _ = self._get_cache_keys_for_page()

        # Verify caches exist
        self.assertIsNotNone(cache.get(global_key), "Global cache should exist")
        self.assertIsNotNone(cache.get(status_key), "Status cache should exist")

        # Delete the ChapterProgress
        chapter_progress.delete()

        # Verify only status cache is invalidated, global cache should remain
        self.assertIsNotNone(
            cache.get(global_key), "Global cache should NOT be invalidated"
        )
        self.assertIsNone(cache.get(status_key), "Status cache should be invalidated")

    def test_mark_as_completed_invalidates_cache(self):
        """
        Test that calling the mark_as_completed API invalidates cache

        Note: 章节进度变更只应使用户状态缓存失效，全局缓存应保持有效。
        """
        # Populate caches by making API requests with explicit page=1
        response1 = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/?page=1&exclude=prerequisite_progress"
        )
        self.assertEqual(response1.status_code, 200)

        # Generate expected cache keys
        global_key, status_key, _ = self._get_cache_keys_for_page()

        # Verify caches exist
        self.assertIsNotNone(cache.get(global_key), "Global cache should exist")
        self.assertIsNotNone(cache.get(status_key), "Status cache should exist")

        # Call mark_as_completed API
        response = self.client.post(
            f"/api/v1/courses/{self.course.id}/chapters/{self.chapter.id}/mark_as_completed/",
            {"completed": True},
        )
        self.assertEqual(response.status_code, 200)

        # Verify only status cache is invalidated, global cache should remain
        self.assertIsNotNone(
            cache.get(global_key), "Global cache should NOT be invalidated"
        )
        self.assertIsNone(cache.get(status_key), "Status cache should be invalidated")

        # Verify that subsequent API call returns completed status
        chapter_detail_response = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/{self.chapter.id}/"
        )
        self.assertEqual(chapter_detail_response.status_code, 200)
        self.assertIsNotNone(chapter_detail_response.data)

        # Verify ChapterProgress was created/updated
        chapter_progress = ChapterProgressFactory._meta.model.objects.get(
            enrollment=self.enrollment, chapter=self.chapter
        )
        self.assertTrue(chapter_progress.completed)


class SnapshotStaleSignalTestCase(CoursesTestCase):
    """
    Test cases for snapshot staleness marking signal.
    """

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter1 = ChapterFactory(course=self.course, order=0)
        self.chapter2 = ChapterFactory(course=self.course, order=1)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_completing_chapter_marks_snapshot_stale(self):
        """Test that completing a chapter marks snapshot as stale"""
        from courses.models import CourseUnlockSnapshot

        # Create a fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Complete a chapter
        progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Snapshot should be marked stale
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_incomplete_chapter_does_not_mark_stale(self):
        """Test that incomplete chapter progress doesn't mark snapshot stale"""
        from courses.models import CourseUnlockSnapshot

        # Create a fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Create incomplete progress
        progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=False
        )

        # Snapshot should still be fresh
        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)

    def test_no_snapshot_does_not_crash(self):
        """Test that signal handles missing snapshot gracefully"""
        # No snapshot exists
        from courses.models import CourseUnlockSnapshot

        self.assertEqual(CourseUnlockSnapshot.objects.count(), 0)

        # Complete a chapter - should not crash
        progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Still no snapshot
        self.assertEqual(CourseUnlockSnapshot.objects.count(), 0)

    def test_signal_exception_does_not_crash_main_flow(self):
        """Test that signal exceptions don't affect main flow"""
        from courses.models import CourseUnlockSnapshot
        from unittest.mock import patch

        # Create snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Mock mark_stale to raise exception
        with patch("courses.services.UnlockSnapshotService.mark_stale") as mock_mark:
            mock_mark.side_effect = Exception("Database error")

            # Complete a chapter - should not crash despite signal error
            progress = ChapterProgressFactory(
                enrollment=self.enrollment, chapter=self.chapter1, completed=True
            )

            # Progress should still be created
            self.assertIsNotNone(progress.id)

    def test_multiple_chapter_completions(self):
        """Test multiple chapter completions mark snapshot stale"""
        from courses.models import CourseUnlockSnapshot

        # Create a fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Complete multiple chapters
        progress1 = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

        # Mark as fresh again
        snapshot.is_stale = False
        snapshot.save()

        # Complete another chapter
        progress2 = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter2, completed=True
        )

        # Should be marked stale again
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)


class ProblemSnapshotStaleSignalTestCase(CoursesTestCase):
    """
    Test cases for problem snapshot staleness marking signal.
    """

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.problem1 = ProblemFactory(chapter=self.chapter)
        self.problem2 = ProblemFactory(chapter=self.chapter)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_solving_problem_marks_snapshot_stale(self):
        """Test that solving a problem marks snapshot as stale"""
        from courses.models import ProblemUnlockSnapshot

        # Create a fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Solve a problem
        progress = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )

        # Snapshot should be marked stale
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_incomplete_problem_does_not_mark_stale(self):
        """Test that incomplete problem progress doesn't mark snapshot stale"""
        from courses.models import ProblemUnlockSnapshot

        # Create a fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Create incomplete progress
        progress = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="in_progress"
        )

        # Snapshot should still be fresh
        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)

    def test_failed_problem_does_not_mark_stale(self):
        """Test that failed problem attempts don't mark snapshot stale"""
        from courses.models import ProblemUnlockSnapshot

        # Create a fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Create failed progress
        progress = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="failed"
        )

        # Snapshot should still be fresh
        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)

    def test_no_problem_snapshot_does_not_crash(self):
        """Test that signal handles missing snapshot gracefully"""
        # No snapshot exists
        from courses.models import ProblemUnlockSnapshot

        self.assertEqual(ProblemUnlockSnapshot.objects.count(), 0)

        # Solve a problem - should not crash
        progress = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )

        # Still no snapshot
        self.assertEqual(ProblemUnlockSnapshot.objects.count(), 0)

    def test_signal_exception_does_not_crash_main_flow(self):
        """Test that signal exceptions don't affect main flow"""
        from courses.models import ProblemUnlockSnapshot
        from unittest.mock import patch

        # Create a fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Mock mark_stale to raise exception
        with patch(
            "courses.services.ProblemUnlockSnapshotService.mark_stale"
        ) as mock_mark:
            mock_mark.side_effect = Exception("Database error")

            # Solve a problem - should not crash despite signal error
            progress = ProblemProgressFactory(
                enrollment=self.enrollment, problem=self.problem1, status="solved"
            )

            # Progress should still be created
            self.assertIsNotNone(progress.id)

    def test_multiple_problem_solutions(self):
        """Test multiple problem solutions mark snapshot stale"""
        from courses.models import ProblemUnlockSnapshot

        # Create a fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Solve first problem
        progress1 = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="solved"
        )

        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

        # Mark as fresh again
        snapshot.is_stale = False
        snapshot.save()

        # Solve another problem
        progress2 = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem2, status="solved"
        )

        # Should be marked stale again
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_status_change_to_solved_marks_stale(self):
        """Test that changing status to solved marks snapshot stale"""
        from courses.models import ProblemUnlockSnapshot

        # Create a fresh snapshot
        snapshot = ProblemUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False,
        )

        # Create in_progress progress
        progress = ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem1, status="in_progress"
        )

        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)

        # Update to solved
        progress.status = "solved"
        progress.save()

        # Snapshot should now be marked stale
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)


class SeparatedCacheSignalHandlersTestCase(TestCase):
    """
    Test cases for separated cache signal handlers.

    Tests the new signal handlers that invalidate separated global and user-state caches.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course, order=1)
        self.problem = ProblemFactory(chapter=self.chapter)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_on_chapter_progress_change_invalidates_user_status_cache(self):
        """Test that chapter progress change invalidates user status cache."""
        from django.core.cache import cache

        user_id = self.user.id
        course_id = self.course.id

        # Set up a user status cache
        cache_key = f"chapter:status:{course_id}:{user_id}"
        cache.set(cache_key, {"1": {"status": "completed"}}, timeout=300)

        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))

        # Create chapter progress (should trigger signal)
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter, completed=True
        )

        # Verify cache was invalidated
        self.assertIsNone(cache.get(cache_key))

    def test_on_chapter_progress_change_does_not_affect_other_users(self):
        """Test that chapter progress change doesn't affect other users' caches."""
        from django.core.cache import cache

        # Create another user
        other_user = UserFactory()

        # Set up caches for both users
        user_cache_key = f"chapter:status:{self.course.id}:{self.user.id}"
        other_cache_key = f"chapter:status:{self.course.id}:{other_user.id}"

        cache.set(user_cache_key, {"1": {"status": "not_started"}}, timeout=300)
        cache.set(other_cache_key, {"1": {"status": "completed"}}, timeout=300)

        # Create chapter progress for self.user (should trigger signal)
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter, completed=True
        )

        # Verify self.user's cache was invalidated
        self.assertIsNone(cache.get(user_cache_key))

        # Verify other_user's cache is still intact
        self.assertIsNotNone(cache.get(other_cache_key))

    def test_on_problem_progress_change_invalidates_user_status_cache(self):
        """Test that problem progress change invalidates user status cache."""
        from django.core.cache import cache

        user_id = self.user.id
        chapter_id = self.chapter.id

        # Set up a user status cache
        cache_key = f"problem:status:{chapter_id}:{user_id}"
        cache.set(cache_key, {"1": {"status": "solved"}}, timeout=300)

        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))

        # Create problem progress (should trigger signal)
        ProblemProgressFactory(
            enrollment=self.enrollment, problem=self.problem, status="solved"
        )

        # Verify cache was invalidated
        self.assertIsNone(cache.get(cache_key))

    def test_on_chapter_content_change_invalidates_global_cache(self):
        """Test that chapter content change invalidates global data cache."""
        from django.core.cache import cache

        chapter_id = self.chapter.id
        course_id = self.course.id

        # Set up global caches
        chapter_cache_key = f"chapter:global:{chapter_id}"
        list_cache_key = f"chapter:global:list:{course_id}"

        cache.set(chapter_cache_key, {"id": chapter_id, "title": "Test"}, timeout=1800)
        cache.set(list_cache_key, [{"id": chapter_id}], timeout=1800)

        # Verify caches exist
        self.assertIsNotNone(cache.get(chapter_cache_key))
        self.assertIsNotNone(cache.get(list_cache_key))

        # Update chapter content (should trigger signal)
        self.chapter.title = "Updated Title"
        self.chapter.save()

        # Verify caches were invalidated
        self.assertIsNone(cache.get(chapter_cache_key))
        self.assertIsNone(cache.get(list_cache_key))

    def test_on_problem_content_change_invalidates_global_cache(self):
        """Test that problem content change invalidates global data cache."""
        from django.core.cache import cache

        problem_id = self.problem.id
        chapter_id = self.chapter.id

        # Set up global caches
        problem_cache_key = f"problem:global:{problem_id}"
        list_cache_key = f"problem:global:list:{chapter_id}"

        cache.set(problem_cache_key, {"id": problem_id, "title": "Test"}, timeout=1800)
        cache.set(list_cache_key, [{"id": problem_id}], timeout=1800)

        # Verify caches exist
        self.assertIsNotNone(cache.get(problem_cache_key))
        self.assertIsNotNone(cache.get(list_cache_key))

        # Update problem content (should trigger signal)
        self.problem.title = "Updated Title"
        self.problem.save()

        # Verify caches were invalidated
        self.assertIsNone(cache.get(problem_cache_key))
        self.assertIsNone(cache.get(list_cache_key))

    def test_on_chapter_content_change_does_not_invalidate_user_status_cache(self):
        """Test that chapter content change doesn't invalidate user status cache."""
        from django.core.cache import cache

        # Set up user status cache
        user_cache_key = f"chapter:status:{self.course.id}:{self.user.id}"
        cache.set(user_cache_key, {"1": {"status": "completed"}}, timeout=300)

        # Update chapter content (should trigger signal)
        self.chapter.title = "Updated Title"
        self.chapter.save()

        # Verify user status cache is still intact
        self.assertIsNotNone(cache.get(user_cache_key))

    def test_on_problem_content_change_orphan_problem(self):
        """Test that problem content change handles orphan problems correctly."""
        from django.core.cache import cache

        # Create orphan problem (no chapter)
        orphan_problem = ProblemFactory(chapter=None)

        # Set up global cache
        problem_cache_key = f"problem:global:{orphan_problem.id}"
        cache.set(
            problem_cache_key, {"id": orphan_problem.id, "title": "Test"}, timeout=1800
        )

        # Verify cache exists
        self.assertIsNotNone(cache.get(problem_cache_key))

        # Update problem content (should trigger signal)
        orphan_problem.title = "Updated Title"
        orphan_problem.save()

        # Verify cache was invalidated
        self.assertIsNone(cache.get(problem_cache_key))
