"""
Unit tests for cache utilities.

Tests the new cache utilities with separate counters implementation:
- record_cache_total_operation function
- get_cache function with total operation tracking
- CacheResult functionality
- AdaptiveTTLCalculator
"""

import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase

from common.utils.cache import (
    record_cache_total_operation,
    get_cache,
    set_cache,
    CacheResult,
    AdaptiveTTLCalculator,
    NULL_VALUE_MARKER,
    EMPTY_VALUE_MARKER,
)


class TestRecordCacheTotalOperation(unittest.TestCase):
    """Test record_cache_total_operation function"""

    def setUp(self):
        """Set up test fixtures"""
        self.endpoint = "TestViewSet"

    @patch('django_redis.get_redis_connection')
    def test_record_total_operation_increments_counter(self, mock_get_redis):
        """Test that record_cache_total_operation increments the counter"""
        mock_redis = MagicMock()
        mock_redis.hincrby.return_value = 1
        mock_redis.expire.return_value = True
        mock_get_redis.return_value = mock_redis

        record_cache_total_operation(self.endpoint)

        # Verify Redis commands
        mock_redis.hincrby.assert_called_once()
        mock_redis.expire.assert_called_once()

        # Verify correct arguments
        hincrby_args = mock_redis.hincrby.call_args[0]
        self.assertEqual(hincrby_args[1], 'total_operations')
        self.assertEqual(hincrby_args[2], 1)

    @patch('django_redis.get_redis_connection')
    def test_record_total_operation_with_duration(self, mock_get_redis):
        """Test that record_cache_total_operation works with duration parameter"""
        mock_redis = MagicMock()
        mock_redis.hincrby.return_value = 1
        mock_redis.expire.return_value = True
        mock_get_redis.return_value = mock_redis

        record_cache_total_operation(self.endpoint, duration=0.005)

        # Should not raise any exceptions
        self.assertTrue(True)

    @patch('django_redis.get_redis_connection')
    def test_record_total_operation_sets_ttl(self, mock_get_redis):
        """Test that record_cache_total_operation sets TTL"""
        mock_redis = MagicMock()
        mock_redis.hincrby.return_value = 1
        mock_redis.expire.return_value = True
        mock_get_redis.return_value = mock_redis

        record_cache_total_operation(self.endpoint)

        # Verify TTL is set
        mock_redis.expire.assert_called_once()
        expire_args = mock_redis.expire.call_args[0]
        self.assertEqual(expire_args[1], 300)  # Default TTL

    @patch('django_redis.get_redis_connection')
    def test_record_total_operation_handles_errors(self, mock_get_redis):
        """Test that record_cache_total_operation handles Redis errors gracefully"""
        mock_get_redis.side_effect = Exception("Redis connection error")

        # Should not raise exception
        try:
            record_cache_total_operation(self.endpoint)
        except Exception:
            self.fail("record_cache_total_operation should handle Redis errors gracefully")

    @patch('django_redis.get_redis_connection')
    @patch('common.utils.cache.settings')
    def test_record_total_operation_uses_custom_prefix_and_ttl(self, mock_settings, mock_get_redis):
        """Test that custom prefix and TTL are used"""
        mock_redis = MagicMock()
        mock_redis.hincrby.return_value = 1
        mock_redis.expire.return_value = True
        mock_get_redis.return_value = mock_redis

        mock_settings.CACHE_STATS_KEY_PREFIX = 'custom:prefix'
        mock_settings.CACHE_STATS_TTL = 600

        record_cache_total_operation(self.endpoint)

        # Verify custom prefix and TTL are used
        key_arg = mock_redis.hincrby.call_args[0][0]
        self.assertTrue(key_arg.startswith('custom:prefix:'))
        expire_args = mock_redis.expire.call_args[0]
        self.assertEqual(expire_args[1], 600)


class TestGetCacheWithTotalOperationTracking(TestCase):
    """Test get_cache function with total operation tracking"""

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    def test_get_cache_always_calls_record_total_operation(self, mock_cache_get, mock_record_total):
        """Test that get_cache always calls record_cache_total_operation"""
        mock_cache_get.return_value = None

        get_cache('test:key')

        # Verify record_cache_total_operation was called
        mock_record_total.assert_called_once()
        endpoint_arg = mock_record_total.call_args[0][0]
        self.assertEqual(endpoint_arg, 'key')

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    def test_get_cache_endpoint_extraction(self, mock_cache_get, mock_record_total):
        """Test that endpoint is correctly extracted from cache key"""
        mock_cache_get.return_value = None

        # Test different key formats
        test_cases = [
            'api:ChapterViewSet:123',
            'api:CourseViewSet:query:page=1',
            'simple',
            'a:b:c:d:e',
        ]

        for key in test_cases:
            mock_cache_get.return_value = None
            mock_record_total.reset_mock()

            get_cache(key)

            # Verify endpoint extraction
            endpoint_arg = mock_record_total.call_args[0][0]
            key_parts = key.split(':')
            expected_endpoint = key_parts[1] if len(key_parts) > 1 else (key_parts[0] if key_parts else "unknown")
            self.assertEqual(endpoint_arg, expected_endpoint)

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    def test_get_cache_calls_record_cache_miss(self, mock_cache_get, mock_record_total):
        """Test that get_cache calls record_cache_miss for cache misses"""
        mock_cache_get.return_value = None
        mock_record_cache_miss = MagicMock()

        with patch('common.utils.cache.record_cache_miss', mock_record_cache_miss):
            get_cache('test:key', return_result=True)

            # Verify record_cache_miss was called
            mock_record_cache_miss.assert_called_once()
            self.assertEqual(mock_record_cache_miss.call_args[0][0], 'key')

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    def test_get_cache_calls_record_cache_hit(self, mock_cache_get, mock_record_total):
        """Test that get_cache calls record_cache_hit for cache hits"""
        test_data = {"test": "data"}
        mock_cache_get.return_value = '{"test": "data"}'

        mock_record_cache_hit = MagicMock()
        with patch('common.utils.cache.record_cache_hit', mock_record_cache_hit):
            get_cache('test:key', return_result=True)

            # Verify record_cache_hit was called
            mock_record_cache_hit.assert_called_once()

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    def test_get_cache_calls_record_cache_null_value(self, mock_cache_get, mock_record_total):
        """Test that get_cache calls record_cache_null_value for null values"""
        null_data = {
            "__marker__": NULL_VALUE_MARKER,
            "cached_at": 1234567890.0,
            "ttl": 300,
        }
        mock_cache_get.return_value = null_data

        mock_record_cache_null_value = MagicMock()
        with patch('common.utils.cache.record_cache_null_value', mock_record_cache_null_value):
            get_cache('test:key', return_result=True)

            # Verify record_cache_null_value was called
            mock_record_cache_null_value.assert_called_once()


class TestCacheResult(TestCase):
    """Test CacheResult functionality"""

    def test_cache_result_hit(self):
        """Test CacheResult.hit factory method"""
        result = CacheResult.hit({"data": "test"})

        self.assertEqual(result.status, "HIT")
        self.assertEqual(result.data, {"data": "test"})
        self.assertTrue(result)  # Truthy for hit
        self.assertTrue(result.is_hit)
        self.assertFalse(result.is_miss)
        self.assertFalse(result.is_null_value)

    def test_cache_result_miss(self):
        """Test CacheResult.miss factory method"""
        result = CacheResult.miss()

        self.assertEqual(result.status, "MISS")
        self.assertIsNone(result.data)
        self.assertFalse(result)  # Falsy for miss
        self.assertFalse(result.is_hit)
        self.assertTrue(result.is_miss)
        self.assertFalse(result.is_null_value)

    def test_cache_result_null_value(self):
        """Test CacheResult.null_value factory method"""
        result = CacheResult.null_value(cached_at=1234567890.0)

        self.assertEqual(result.status, "NULL_VALUE")
        self.assertIsNone(result.data)
        self.assertTrue(result)  # Truthy for null_value
        self.assertFalse(result.is_hit)
        self.assertFalse(result.is_miss)
        self.assertTrue(result.is_null_value)

    def test_cache_result_with_ttl(self):
        """Test CacheResult with TTL"""
        result = CacheResult.hit({"data": "test"}, ttl=900)

        self.assertEqual(result.ttl, 900)


class TestAdaptiveTTLCalculator(TestCase):
    """Test AdaptiveTTLCalculator functionality"""

    def test_get_stats_key_format(self):
        """Test that get_stats_key returns the correct format"""
        key = AdaptiveTTLCalculator.get_stats_key("test_key")
        self.assertEqual(key, "cache_stats:test_key")

    @patch('django_redis.get_redis_connection')
    def test_calculate_ttl_default(self, mock_get_redis):
        """Test calculate_ttl with no existing stats"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {}
        mock_get_redis.return_value = mock_redis

        ttl = AdaptiveTTLCalculator.calculate_ttl("test_key", 900)
        self.assertEqual(ttl, 900)  # Default TTL

    @patch('django_redis.get_redis_connection')
    def test_calculate_ttl_cold_data(self, mock_get_redis):
        """Test TTL for cold data"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 5,
            b'misses': 0,
        }
        mock_get_redis.return_value = mock_redis

        ttl = AdaptiveTTLCalculator.calculate_ttl("test_key", 900)
        self.assertEqual(ttl, 300)  # Cold data TTL

    @patch('django_redis.get_redis_connection')
    def test_calculate_ttl_warm_data(self, mock_get_redis):
        """Test TTL for warm data"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 50,  # > 10 hits
            b'misses': 10,
            b'total_requests': 60,
        }
        mock_redis.hgetall.return_value = {
            b'hits': 50,
            b'misses': 10,
        }
        mock_get_redis.return_value = mock_redis

        ttl = AdaptiveTTLCalculator.calculate_ttl("test_key", 900)
        self.assertEqual(ttl, 900)  # Default TTL for warm data

    @patch('django_redis.get_redis_connection')
    def test_calculate_ttl_hot_data(self, mock_get_redis):
        """Test TTL for hot data"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 200,  # > 100 hits
            b'misses': 50,
        }
        mock_get_redis.return_value = mock_redis

        ttl = AdaptiveTTLCalculator.calculate_ttl("test_key", 900)
        self.assertEqual(ttl, 1800)  # Hot data TTL (30 minutes)

    @patch('django_redis.get_redis_connection')
    def test_calculate_ttl_low_hit_rate(self, mock_get_redis):
        """Test TTL for data with low hit rate"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 10,
            b'misses': 90,  # Low hit rate
            b'total_requests': 100,
        }
        mock_get_redis.return_value = mock_redis

        ttl = AdaptiveTTLCalculator.calculate_ttl("test_key", 900)
        self.assertEqual(ttl, 300)  # Short TTL for low hit rate data


class TestCacheGetWithDifferentDataTypes(TestCase):
    """Test get_cache function with different data types and scenarios"""

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    @patch('common.utils.cache.json.loads')
    def test_get_cache_handles_empty_list(self, mock_json_loads, mock_cache_get, mock_record_total):
        """Test that get_cache handles empty list data"""
        mock_cache_get.return_value = '{"__marker__": "__EMPTY_VALUE__", "data": []}'
        mock_json_loads.return_value = {"__marker__": "__EMPTY_VALUE__", "data": []}

        result = get_cache('test:key', return_result=True)

        self.assertEqual(result.status, "HIT")
        self.assertEqual(result.data, [])

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.cache.get')
    def test_get_cache_handles_exception(self, mock_cache_get, mock_record_total):
        """Test that get_cache handles exceptions gracefully"""
        mock_cache_get.side_effect = Exception("Cache error")

        result = get_cache('test:key', return_result=True)

        self.assertEqual(result.status, "MISS")
        self.assertIsNone(result.data)


class TestCacheWithMetricsRecording(TestCase):
    """Test cache operations with metrics recording integration"""

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.record_cache_hit')
    @patch('common.utils.cache.record_cache_miss')
    @patch('common.utils.cache.record_cache_null_value')
    def test_all_operations_record_total_operation(
        self, mock_record_null, mock_record_miss, mock_record_hit, mock_record_total
    ):
        """Test that all cache operations record total operation"""
        mock_record_cache_miss = MagicMock()

        # Test miss
        mock_record_cache_miss = MagicMock()
        with patch('common.utils.cache.record_cache_miss', mock_record_cache_miss):
            get_cache('test:miss', return_result=True)
            mock_record_cache_miss.assert_called()

        # Test hit with data
        with patch('common.utils.cache.cache.get') as mock_cache_get, \
             patch('common.utils.cache.json.loads') as mock_json_loads, \
             patch('common.utils.cache.record_cache_hit') as mock_record_hit:

            mock_cache_get.return_value = '{"test": "data"}'
            mock_json_loads.return_value = {"test": "data"}

            get_cache('test:hit', return_result=True)
            mock_record_hit.assert_called()

        # Test null value
        with patch('common.utils.cache.cache.get') as mock_cache_get, \
             patch('common.utils.cache.json.loads') as mock_json_loads, \
             patch('common.utils.cache.record_cache_null_value') as mock_record_null:

            null_data = {"__marker__": NULL_VALUE_MARKER, "cached_at": 1234567890.0}
            mock_cache_get.return_value = '{"__marker__": "__NULL_VALUE__", "cached_at": 1234567890.0}'
            mock_json_loads.return_value = null_data

            get_cache('test:null', return_result=True)
            mock_record_null.assert_called()

        # Verify total operation is recorded for each call
        self.assertGreaterEqual(mock_record_total.call_count, 3)


if __name__ == '__main__':
    unittest.main()
