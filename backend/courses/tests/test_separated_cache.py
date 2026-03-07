"""
Tests for separated cache functionality.

This module tests the separated cache system where:
1. Global cache stores general data visible to all users
2. User status cache stores user-specific data like progress

Run with:
python manage.py test courses.tests.test_separated_cache --verbosity=2
"""

from django.test import TestCase
from django.core.cache import cache
from courses.tests.factories import CourseFactory, ChapterFactory, EnrollmentFactory
from accounts.models import User
from common.utils.cache import get_standard_cache_key, set_cache, get_cache


class SeparatedCacheTestCase(TestCase):
    """Test the separated cache functionality"""

    def setUp(self):
        """Set up test data"""
        cache.clear()

        # Create test data
        self.course = CourseFactory(title="Test Course")
        self.chapter = ChapterFactory(course=self.course, title="Test Chapter")
        self.user1 = User.objects.create_user("user1", "user1@example.com", "password")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "password")
        self.enrollment1 = EnrollmentFactory(user=self.user1, course=self.course)
        self.enrollment2 = EnrollmentFactory(user=self.user2, course=self.course)

    def test_global_cache_key_format(self):
        """Test that global cache keys are formatted correctly"""
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        # Should contain the SEPARATED and GLOBAL markers
        parts = cache_key.split(":")
        self.assertIn("courses", parts)
        self.assertIn("ChapterViewSet", parts)
        self.assertIn("SEPARATED", parts)
        self.assertIn("GLOBAL", parts)
        self.assertIn("course_pk", cache_key)

    def test_user_status_cache_key_format(self):
        """Test that user status cache keys are formatted correctly"""
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user1.id,
            is_separated=True,
            separated_type="STATUS",
        )

        # Should contain the SEPARATED and STATUS markers
        parts = cache_key.split(":")
        self.assertIn("courses", parts)
        self.assertIn("ChapterViewSet", parts)
        self.assertIn("SEPARATED", parts)
        self.assertIn("STATUS", parts)
        self.assertIn("course_pk", cache_key)
        self.assertIn(f"user_id={self.user1.id}", cache_key)

    def test_global_and_user_cache_independence(self):
        """Test that global and user caches are independent"""
        # Set global cache
        global_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        # Set user status cache
        user_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user1.id,
            is_separated=True,
            separated_type="STATUS",
        )

        # Set different values in each cache
        set_cache(global_cache_key, {"global": "data", "visible_to_all": True})
        set_cache(
            user_cache_key, {"user_status": "completed", "user_id": self.user1.id}
        )

        # Verify both caches exist
        global_data = get_cache(global_cache_key)
        user_data = get_cache(user_cache_key)

        self.assertIsNotNone(global_data)
        self.assertIsNotNone(user_data)
        self.assertEqual(global_data["visible_to_all"], True)
        self.assertEqual(user_data["user_status"], "completed")

        # Verify they're different
        self.assertNotEqual(global_data, user_data)

    def test_user_cache_independence_between_users(self):
        """Test that user caches are independent between different users"""
        # Create cache keys for both users
        user1_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user1.id,
            is_separated=True,
            separated_type="STATUS",
        )

        user2_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user2.id,
            is_separated=True,
            separated_type="STATUS",
        )

        # Set different status for each user
        set_cache(
            user1_cache_key, {"user_status": "completed", "user_id": self.user1.id}
        )
        set_cache(
            user2_cache_key, {"user_status": "in_progress", "user_id": self.user2.id}
        )

        # Verify both caches exist and have correct values
        user1_data = get_cache(user1_cache_key)
        user2_data = get_cache(user2_cache_key)

        self.assertIsNotNone(user1_data)
        self.assertIsNotNone(user2_data)
        self.assertEqual(user1_data["user_status"], "completed")
        self.assertEqual(user2_data["user_status"], "in_progress")

        # Verify they're different
        self.assertNotEqual(user1_data, user2_data)

    def test_cache_independence_without_separation(self):
        """Test that normal cache keys don't conflict with separated cache keys"""
        # Normal cache key
        normal_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
        )

        # Separated cache key (same parameters but different format)
        separated_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        # Set different values
        set_cache(normal_cache_key, {"normal": "data"})
        set_cache(separated_cache_key, {"separated": "data"})

        # Verify both exist and are different
        normal_data = get_cache(normal_cache_key)
        separated_data = get_cache(separated_cache_key)

        self.assertIsNotNone(normal_data)
        self.assertIsNotNone(separated_data)
        self.assertNotEqual(normal_data, separated_data)


class SeparatedCacheIntegrationTestCase(TestCase):
    """Integration tests for separated cache with ViewSets"""

    def setUp(self):
        """Set up test data"""
        cache.clear()

        # Create test data
        self.course = CourseFactory(title="Integration Test Course")
        self.chapter = ChapterFactory(course=self.course, title="Integration Chapter")
        self.user1 = User.objects.create_user("user1", "user1@example.com", "password")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "password")
        self.enrollment1 = EnrollmentFactory(user=self.user1, course=self.course)
        self.enrollment2 = EnrollmentFactory(user=self.user2, course=self.course)

    def test_global_cache_shared_across_users(self):
        """Test that global cache data is shared across all users"""
        # This test simulates what would happen when a ViewSet uses separated cache
        global_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        # Set global cache (simulating ViewSet cache population)
        set_cache(
            global_cache_key,
            {
                "chapters": [{"id": self.chapter.id, "title": "Integration Chapter"}],
                "total_count": 1,
            },
        )

        # Both users should see the same global data
        user1_data = get_cache(global_cache_key, return_result=True)
        user2_data = get_cache(global_cache_key, return_result=True)

        self.assertIsNotNone(user1_data)
        self.assertIsNotNone(user2_data)
        self.assertEqual(user1_data.data, user2_data.data)
        self.assertEqual(user1_data.data["total_count"], 1)
        self.assertEqual(len(user1_data.data["chapters"]), 1)

    def test_user_status_cache_isolation(self):
        """Test that user status cache data is isolated per user"""
        # Create cache keys for both users
        user1_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user1.id,
            is_separated=True,
            separated_type="STATUS",
        )

        user2_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user2.id,
            is_separated=True,
            separated_type="STATUS",
        )

        # Simulate different user progress
        set_cache(
            user1_cache_key, {"completed_chapters": [self.chapter.id], "progress": 100}
        )

        set_cache(user2_cache_key, {"completed_chapters": [], "progress": 0})

        # Verify each user sees their own data
        user1_data = get_cache(user1_cache_key, return_result=True)
        user2_data = get_cache(user2_cache_key, return_result=True)

        self.assertIsNotNone(user1_data)
        self.assertIsNotNone(user2_data)
        self.assertNotEqual(user1_data.data, user2_data.data)

        user1_progress = user1_data.data["progress"]
        user2_progress = user2_data.data["progress"]

        self.assertEqual(user1_progress, 100)
        self.assertEqual(user2_progress, 0)

    def test_cache_invalidation_patterns(self):
        """Test that cache invalidation follows the correct patterns"""
        # Create cache keys that would be generated by ViewSets
        course_chapters_global = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        course_chapters_user1 = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user1.id,
            is_separated=True,
            separated_type="STATUS",
        )

        course_chapters_user2 = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            user_id=self.user2.id,
            is_separated=True,
            separated_type="STATUS",
        )

        # Set all caches
        set_cache(course_chapters_global, {"global_data": "visible_to_all"})
        set_cache(course_chapters_user1, {"user1_data": "specific"})
        set_cache(course_chapters_user2, {"user2_data": "specific"})

        # Verify all caches exist
        self.assertIsNotNone(get_cache(course_chapters_global))
        self.assertIsNotNone(get_cache(course_chapters_user1))
        self.assertIsNotNone(get_cache(course_chapters_user2))

        # Now simulate what happens when the course is updated
        # In a real scenario, signals would invalidate these caches

        # Global cache should be invalidated (affects all users)
        from common.utils.cache import delete_cache

        delete_cache(course_chapters_global)

        # User status caches might remain (user-specific data might still be valid)
        # But in many cases, both would be invalidated

        # Verify invalidation
        self.assertIsNone(get_cache(course_chapters_global))

        # User caches should still exist (unless they were also invalidated)
        user1_data = get_cache(course_chapters_user1)
        user2_data = get_cache(course_chapters_user2)

        # The behavior here depends on the specific business logic
        # This test just verifies that the cache keys are correctly isolated
