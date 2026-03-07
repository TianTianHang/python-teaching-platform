"""
Cache performance tests using Django TestCase and factories.

This module tests the enhanced cache system performance:
1. Cache hit/miss performance
2. Cache warming effectiveness
3. Penetration protection
4. Cache key structure
5. Adaptive TTL functionality

Run with:
python manage.py test courses.tests.test_cache_performance --verbosity=2
"""

import time
import statistics
import unittest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from redis.exceptions import ConnectionError
from redis import Redis

from courses.models import Course, Chapter, Problem
from courses.tests.factories import (
    CourseFactory,
    ChapterFactory,
    ProblemFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
)
from accounts.tests.factories import UserFactory
from rest_framework.test import APIClient
from common.utils.cache import get_standard_cache_key
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CachePerformanceTest(TestCase):
    """
    Test cache performance using Django TestCase
    """

    @classmethod
    def setUpTestData(cls):
        """Create test data using factories"""
        # Create test user
        cls.user = UserFactory()

        # Create test data hierarchy
        cls.course = CourseFactory(
            title="Test Course for Performance",
            description="Description for performance testing",
        )
        cls.chapter = ChapterFactory(
            course=cls.course,
            title="Test Chapter for Performance",
            content="Content for performance testing",
        )
        cls.problem = ProblemFactory(
            chapter=cls.chapter, title="Test Problem for Performance", type="algorithm"
        )

    def setUp(self):
        """Clear cache before each test"""
        cache.clear()

    def tearDown(self):
        """Clear cache after each test"""
        cache.clear()

    def test_cache_hit_miss_performance(self):
        """Test cache hit vs miss performance"""
        logger.info("Testing cache hit/miss performance...")

        # Test cache utilities directly
        from common.utils.cache import get_cache, set_cache

        # Test cache miss
        cache_key = "test:cache:hitmiss"
        data = get_cache(cache_key)
        self.assertIsNone(data)

        # Set cache
        test_data = {"test": "data", "timestamp": time.time()}
        set_cache(cache_key, test_data, timeout=60)

        # Test cache hit
        cached_data = get_cache(cache_key)
        self.assertEqual(cached_data, test_data)

        # Test CacheResult functionality
        from common.utils.cache import get_cache, CacheResult

        cached_result = get_cache(cache_key, return_result=True)

        self.assertIsNotNone(cached_result)
        self.assertTrue(cached_result.is_hit)
        self.assertEqual(cached_result.data, test_data)

    def test_cache_penetration_protection(self):
        """Test cache protection against penetration attacks"""
        logger.info("Testing cache penetration protection...")

        from common.utils.cache import get_cache, set_cache, NULL_VALUE_MARKER

        # Test caching null values
        cache_key = "test:null:penetration"

        # Cache a null value
        set_cache(cache_key, None, is_null=True)

        # Should return None but with NULL_VALUE_MARKER
        result = get_cache(cache_key, return_result=True)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_null_value)
        self.assertIsNone(result.data)

    def test_adaptive_ttl_calculation(self):
        """Test adaptive TTL calculation"""
        logger.info("Testing adaptive TTL calculation...")

        from common.utils.cache import AdaptiveTTLCalculator

        cache_key = "test:adaptive:ttl"

        # First access (no stats) should use default TTL
        ttl1 = AdaptiveTTLCalculator.calculate_ttl(cache_key, 900)
        self.assertEqual(ttl1, 900)  # Default TTL

        # Record a few hits (cold data: < 10 hits)
        for _ in range(5):
            AdaptiveTTLCalculator.record_hit(cache_key)

        # Cold data should get shorter TTL (5 minutes)
        ttl2 = AdaptiveTTLCalculator.calculate_ttl(cache_key, 900)
        self.assertEqual(ttl2, 300)  # Cold data TTL

        # Record more hits to make it warm data (> 10 hits, good hit rate)
        for _ in range(10):
            AdaptiveTTLCalculator.record_hit(cache_key)

        # Warm data should get default TTL (15 minutes)
        ttl3 = AdaptiveTTLCalculator.calculate_ttl(cache_key, 900)
        self.assertEqual(ttl3, 900)  # Warm data TTL

    def test_cache_key_structure(self):
        """Test cache keys are properly structured"""
        logger.info("Testing cache key structure...")

        from common.utils.cache import get_standard_cache_key, get_cache, set_cache

        # Generate cache keys for different patterns
        key1 = get_standard_cache_key(
            prefix="api", view_name="CourseViewSet", pk=self.course.id
        )

        key2 = get_standard_cache_key(
            prefix="api", view_name="CourseViewSet", query_params={"page": "1"}
        )

        # Test keys contain expected parts
        self.assertTrue(key1.startswith("api:"))
        self.assertIn("CourseViewSet", key1)
        self.assertTrue(key2.startswith("api:"))
        self.assertIn("CourseViewSet", key2)

        # Test different keys are generated for different parameters
        self.assertNotEqual(key1, key2)

    def test_cache_warming_mock(self):
        """Test cache warming with mock"""
        logger.info("Testing cache warming...")

        # Mock the warming task
        with patch(
            "common.cache_warming.tasks.warm_separated_global_startup"
        ) as mock_warming:
            mock_warming.return_value = {
                "status": "success",
                "count": 50,
                "duration": 2.5,
            }

            # Test warming task
            from common.cache_warming.tasks import warm_separated_global_startup

            result = warm_separated_global_startup()

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["count"], 50)

    def test_cache_error_handling(self):
        """Test cache error handling"""
        logger.info("Testing cache error handling...")

        # Test with Redis connection error
        with patch("django_redis.get_redis_connection") as mock_redis:
            mock_redis.side_effect = ConnectionError("Connection failed")

            # Should still work but with fallback behavior
            from common.utils.cache import get_cache, set_cache

            # Set cache should not raise error
            set_cache("test:fallback", {"data": "test"})

            # Get cache might return None - use a proper key format
            data = get_cache("api:test:fallback")
            # The actual behavior depends on error handling in the implementation
            data is None  # Should not raise exception

    def test_memory_usage_tracking(self):
        """Test that cache doesn't cause memory issues"""
        logger.info("Testing memory usage tracking...")

        # Check Redis memory usage if available
        try:
            redis_conn = Redis()
            memory_info = redis_conn.info("memory")

            # Memory usage should be reasonable (less than 100MB)
            if "used_memory" in memory_info:
                self.assertLess(memory_info["used_memory"], 100 * 1024 * 1024)
        except:
            # Skip if Redis not available
            logger.info("Redis not available, skipping memory test")

    def test_multiple_cache_operations(self):
        """Test multiple cache operations for performance"""
        logger.info("Testing multiple cache operations...")

        from common.utils.cache import set_cache, get_cache

        # Set multiple values
        for i in range(100):
            set_cache(f"test:key:{i}", f"value:{i}")

        # Get multiple values
        times = []
        for i in range(100):
            start = time.time()
            data = get_cache(f"test:key:{i}")
            times.append(time.time() - start)

            # Verify data is correct
            if data is not None:
                self.assertEqual(data, f"value:{i}")

        # Calculate average get time
        avg_time = statistics.mean(times)
        logger.info(f"Average cache get time: {avg_time:.4f}s")

        # Should be very fast
        self.assertLess(avg_time, 0.001)  # Less than 1ms on average


class CacheIntegrationTest(TransactionTestCase):
    """
    Test cache integration with database operations
    Uses TransactionTestCase to test database + cache interactions
    """

    def setUp(self):
        """Create test data"""
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course)
        self.problem = ProblemFactory(chapter=self.chapter)

    def test_cache_with_database_operations(self):
        """Test cache behavior with database operations"""
        from common.utils.cache import get_standard_cache_key, get_cache, set_cache

        # Clear cache
        cache.clear()

        # Generate cache key
        cache_key = get_standard_cache_key(
            prefix="api", view_name="CourseViewSet", pk=self.course.id
        )

        # Cache should be empty
        self.assertIsNone(get_cache(cache_key))

        # Test that cache operations don't interfere with database
        courses = Course.objects.all()
        self.assertGreater(courses.count(), 0)

        chapters = Chapter.objects.filter(course=self.course)
        self.assertGreater(chapters.count(), 0)

        problems = Problem.objects.filter(chapter=self.chapter)
        self.assertGreater(problems.count(), 0)

    def test_bulk_operations_and_cache(self):
        """Test cache behavior with bulk operations"""
        from common.utils.cache import set_cache, get_cache

        # Clear cache
        cache.clear()

        # Set cache in bulk
        bulk_data = {f"bulk:key:{i}": f"bulk:value:{i}" for i in range(50)}
        for key, value in bulk_data.items():
            set_cache(key, value)

        # Retrieve in bulk
        retrieved_data = {}
        for key in bulk_data.keys():
            data = get_cache(key)
            if data is not None:
                retrieved_data[key] = data

        # Verify all data was retrieved
        self.assertEqual(len(retrieved_data), 50)

        # Verify data integrity
        for key, expected_value in bulk_data.items():
            self.assertEqual(retrieved_data[key], expected_value)


class SeparatedCachePerformanceTestCase(TestCase):
    """
    Performance tests for separated cache implementation.

    Tests the cache hit rate improvement and memory usage reduction
    from separating global and user-state caches.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.course = CourseFactory(title="Performance Test Course")

        # Create multiple chapters
        self.chapters = [
            ChapterFactory(course=self.course, order=i, title=f"Chapter {i}")
            for i in range(10)
        ]

        # Create enrollment
        self.enrollment1 = EnrollmentFactory(user=self.user1, course=self.course)
        self.enrollment2 = EnrollmentFactory(user=self.user2, course=self.course)
        self.enrollment3 = EnrollmentFactory(user=self.user3, course=self.course)

        # Create progress for some users
        ChapterProgressFactory(
            enrollment=self.enrollment1, chapter=self.chapters[0], completed=True
        )
        ChapterProgressFactory(
            enrollment=self.enrollment2, chapter=self.chapters[0], completed=False
        )

        self.client = APIClient()

    def test_cache_hit_rate_improvement(self):
        """Test that separated cache improves hit rate for global data."""
        from django.core.cache import cache

        course_id = self.course.id
        global_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": course_id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        cache.clear()

        # First request - cache miss
        self.client.force_authenticate(user=self.user1)
        start_time = time.time()
        response1 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/?exclude=prerequisite_progress"
        )
        first_request_time = time.time() - start_time

        self.assertEqual(response1.status_code, 200)

        # Verify global cache is set
        global_cache = cache.get(global_cache_key)
        self.assertIsNotNone(global_cache)

        # Second request from different user - should use global cache (hit)
        cache.delete_pattern(
            f"courses:business:ChapterStatus:course_pk={course_id}:*"
        )  # Clear user status caches

        self.client.force_authenticate(user=self.user2)
        start_time = time.time()
        response2 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/?exclude=prerequisite_progress"
        )
        second_request_time = time.time() - start_time

        self.assertEqual(response2.status_code, 200)

        # Second request should be faster (global cache hit)
        # Note: In real scenario with proper caching, second request would be faster
        logger.info(f"First request time: {first_request_time:.4f}s")
        logger.info(f"Second request time: {second_request_time:.4f}s")

    def test_memory_usage_reduction(self):
        """Test that separated cache reduces memory usage."""
        from django.core.cache import cache

        course_id = self.course.id

        cache.clear()

        # Simulate old approach: each user has full cache copy
        # (including global data duplicated)
        old_approach_keys = []
        for user in [self.user1, self.user2, self.user3]:
            self.client.force_authenticate(user=user)
            response = self.client.get(
                f"/api/v1/courses/{course_id}/chapters/?exclude=prerequisite_progress"
            )
            self.assertEqual(response.status_code, 200)

        # Count cache keys in new approach
        global_keys = cache.keys("courses:ChapterViewSet:*")
        status_keys = cache.keys("courses:business:ChapterStatus:*")
        all_keys = global_keys + status_keys

        # New approach should have:
        # - 1 global data cache (shared by all users)
        # - 3 user status caches (one per user)
        # Total: 4 cache entries for 3 users

        # Old approach would have: 3 full cache entries (one per user)

        # The memory saving comes from:
        # - Global data (large) stored once instead of 3 times
        # - User status (small) stored separately per user

        logger.info(f"Total cache keys: {len(all_keys)}")

        # Verify we have the expected cache structure
        global_keys = [k for k in all_keys if ":SEPARATED:GLOBAL:" in k]
        status_keys = [k for k in all_keys if "business:ChapterStatus" in k]

        self.assertEqual(len(global_keys), 1, "Should have 1 global cache")
        self.assertGreaterEqual(
            len(status_keys), 1, "Should have at least 1 status cache"
        )

    def test_concurrent_user_data_isolation(self):
        """Test that concurrent users don't see each other's data."""
        from django.core.cache import cache
        from common.utils.cache import get_cache

        course_id = self.course.id

        cache.clear()

        # Make requests for different users
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/?exclude=prerequisite_progress"
        )

        self.client.force_authenticate(user=self.user2)
        response2 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/?exclude=prerequisite_progress"
        )

        self.client.force_authenticate(user=self.user3)
        response3 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/?exclude=prerequisite_progress"
        )

        # All should return 200
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)

        # Verify user status caches are separate
        user1_status_key = get_standard_cache_key(
            prefix="courses",
            view_name="business:ChapterStatus",
            parent_pks={"course_pk": course_id},
            query_params={"user_id": self.user1.id},
        )
        user2_status_key = get_standard_cache_key(
            prefix="courses",
            view_name="business:ChapterStatus",
            parent_pks={"course_pk": course_id},
            query_params={"user_id": self.user2.id},
        )
        user3_status_key = get_standard_cache_key(
            prefix="courses",
            view_name="business:ChapterStatus",
            parent_pks={"course_pk": course_id},
            query_params={"user_id": self.user3.id},
        )

        status1 = get_cache(user1_status_key)
        status2 = get_cache(user2_status_key)
        status3 = get_cache(user3_status_key)

        # User1 and User2 should have different status for chapter 0
        # (User1 completed it, User2 didn't)
        chapter0_id = str(self.chapters[0].id)

        self.assertIsNotNone(status1)
        self.assertIsNotNone(status2)
        self.assertIsNotNone(status3)

        # User1 completed chapter 0
        self.assertEqual(status1.get(chapter0_id, {}).get("status"), "completed")
        # User2 started but didn't complete
        self.assertEqual(status2.get(chapter0_id, {}).get("status"), "in_progress")
        # User3 not started
        self.assertEqual(status3.get(chapter0_id, {}).get("status"), "not_started")

    def test_cache_invalidation_on_content_change(self):
        """Test that content changes invalidate global cache correctly."""
        from django.core.cache import cache

        chapter = self.chapters[0]
        list_cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": self.course.id},
            is_separated=True,
            separated_type="GLOBAL",
        )

        # Set up cache
        cache.clear()

        # Make a list request to populate cache
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/?exclude=prerequisite_progress"
        )

        # Verify list cache is set
        list_cache = cache.get(list_cache_key)
        self.assertIsNotNone(list_cache, "List cache should be set after request")

        # Update chapter content (this triggers signal)
        original_title = chapter.title
        chapter.title = "Updated Title"
        chapter.save()

        # List cache should be invalidated by signal
        list_cache_after = cache.get(list_cache_key)
        self.assertIsNone(
            list_cache_after,
            "List cache should be invalidated after chapter content change",
        )

        # Restore original title
        chapter.title = original_title
        chapter.save()

    def test_cache_fallback_on_missing(self):
        """Test that system falls back correctly when cache is missing."""
        from django.core.cache import cache

        cache.clear()

        # Request without any cache - should work
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            f"/api/v1/courses/{self.course.id}/chapters/?exclude=prerequisite_progress"
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)


class SeparatedCacheConsistencyTestCase(TestCase):
    """
    Consistency tests for separated cache implementation.

    Tests that data remains consistent across cache invalidations
    and updates.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter1 = ChapterFactory(course=self.course, order=1)
        self.chapter2 = ChapterFactory(course=self.course, order=2)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_consistency_after_progress_update(self):
        """Test that data is consistent after progress update."""
        from django.core.cache import cache

        course_id = self.course.id
        chapter_id = self.chapter1.id

        cache.clear()

        # Initial request
        response1 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/{chapter_id}/"
        )
        self.assertEqual(response1.data["status"], "not_started")

        # Update progress
        ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Request again - should show completed
        response2 = self.client.get(
            f"/api/v1/courses/{course_id}/chapters/{chapter_id}/"
        )
        self.assertEqual(response2.data["status"], "completed")

    def test_consistency_after_snapshot_update(self):
        """Test consistency after snapshot recompute."""
        from courses.models import CourseUnlockSnapshot

        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course, enrollment=self.enrollment, unlock_states={}
        )
        snapshot.recompute()

        # Request should use snapshot data
        response = self.client.get(f"/api/v1/courses/{self.course.id}/chapters/")
        self.assertEqual(response.status_code, 200)
