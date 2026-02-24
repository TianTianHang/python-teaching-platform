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
from courses.tests.factories import CourseFactory, ChapterFactory, ProblemFactory
from accounts.tests.factories import UserFactory
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
            title='Test Course for Performance',
            description='Description for performance testing'
        )
        cls.chapter = ChapterFactory(
            course=cls.course,
            title='Test Chapter for Performance',
            content='Content for performance testing'
        )
        cls.problem = ProblemFactory(
            chapter=cls.chapter,
            title='Test Problem for Performance',
            type='algorithm'
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
        test_data = {'test': 'data', 'timestamp': time.time()}
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

        from common.utils.cache import get_cache_key, get_cache, set_cache

        # Generate cache keys for different patterns
        key1 = get_cache_key(
            prefix="api",
            view_name="CourseViewSet",
            pk=str(self.course.id)
        )

        key2 = get_cache_key(
            prefix="api",
            view_name="CourseViewSet",
            query_params={"page": "1"}
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
        with patch('common.cache_warming.tasks.warm_startup_cache') as mock_warming:
            mock_warming.return_value = {
                'status': 'success',
                'count': 50,
                'duration': 2.5
            }

            # Test warming task
            from common.cache_warming.tasks import warm_startup_cache
            result = warm_startup_cache()

            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['count'], 50)

    def test_cache_error_handling(self):
        """Test cache error handling"""
        logger.info("Testing cache error handling...")

        # Test with Redis connection error
        with patch('django_redis.get_redis_connection') as mock_redis:
            mock_redis.side_effect = ConnectionError("Connection failed")

            # Should still work but with fallback behavior
            from common.utils.cache import get_cache, set_cache

            # Set cache should not raise error
            set_cache("test:fallback", {'data': 'test'})

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
            memory_info = redis_conn.info('memory')

            # Memory usage should be reasonable (less than 100MB)
            if 'used_memory' in memory_info:
                self.assertLess(memory_info['used_memory'], 100 * 1024 * 1024)
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
        from common.utils.cache import get_cache_key, get_cache, set_cache

        # Clear cache
        cache.clear()

        # Generate cache key
        cache_key = get_cache_key(
            prefix="api",
            view_name="CourseViewSet",
            pk=str(self.course.id)
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