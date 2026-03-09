"""
Unit tests for cache metrics module.

Tests the new separate counters implementation for accurate cache performance tracking:
- Total operations counter (all operations)
- Slow operations counter (only >100ms operations)
- Accurate rate calculations using total_operations as denominator
"""

import unittest
from unittest.mock import patch, MagicMock, call
from django.test import override_settings

from common.metrics.cache_metrics import (
    record_cache_hit,
    record_cache_miss,
    record_cache_null_value,
)
from common.utils.logging import CachePerformanceLogger


class TestCacheMetricsTotalOperations(unittest.TestCase):
    """Test that cache metrics properly track total operations separately from slow operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.endpoint = "TestViewSet"

    @patch('common.metrics.cache_metrics._cache_performance_logger')
    @patch('common.metrics.cache_metrics.cache_requests_total')
    @patch('common.metrics.cache_metrics._update_hit_rate_gauge')
    def test_record_cache_hit_fast_operation_always_records(
        self, mock_gauge, mock_prometheus, mock_logger
    ):
        """Test that fast cache hits (<100ms) are always recorded"""
        duration = 0.005  # 5ms - fast operation

        record_cache_hit(self.endpoint, duration=duration)

        # Verify Prometheus metrics are recorded
        mock_prometheus.labels.return_value.inc.assert_called_once()

        # Verify performance logger is called even for fast operations
        mock_logger.record_cache_operation.assert_called_once()
        call_args = mock_logger.record_cache_operation.call_args

        # Verify is_slow parameter is False for fast operations
        self.assertEqual(call_args[1]['endpoint'], self.endpoint)
        self.assertEqual(call_args[1]['operation_type'], 'hit')
        self.assertEqual(call_args[1]['duration_ms'], 5.0)
        self.assertFalse(call_args[1]['is_slow'])

    @patch('common.metrics.cache_metrics._cache_performance_logger')
    @patch('common.metrics.cache_metrics.cache_requests_total')
    @patch('common.metrics.cache_metrics._update_hit_rate_gauge')
    def test_record_cache_hit_slow_operation_marks_slow(
        self, mock_gauge, mock_prometheus, mock_logger
    ):
        """Test that slow cache hits (>100ms) are marked as slow"""
        duration = 0.15  # 150ms - slow operation

        record_cache_hit(self.endpoint, duration=duration)

        # Verify performance logger is called
        mock_logger.record_cache_operation.assert_called_once()
        call_args = mock_logger.record_cache_operation.call_args

        # Verify is_slow parameter is True for slow operations
        self.assertTrue(call_args[1]['is_slow'])

    @patch('common.metrics.cache_metrics._cache_performance_logger')
    @patch('common.metrics.cache_metrics.cache_requests_total')
    @patch('common.metrics.cache_metrics._update_hit_rate_gauge')
    def test_record_cache_miss_fast_operation_always_records(
        self, mock_gauge, mock_prometheus, mock_logger
    ):
        """Test that fast cache misses (<100ms) are always recorded"""
        duration = 0.008  # 8ms - fast operation

        record_cache_miss(self.endpoint, duration=duration)

        # Verify performance logger is called even for fast operations
        mock_logger.record_cache_operation.assert_called_once()
        call_args = mock_logger.record_cache_operation.call_args

        # Verify is_slow parameter is False for fast operations
        self.assertFalse(call_args[1]['is_slow'])

    @patch('common.metrics.cache_metrics._cache_performance_logger')
    @patch('common.metrics.cache_metrics.cache_requests_total')
    @patch('common.metrics.cache_metrics._update_hit_rate_gauge')
    @patch('common.metrics.cache_metrics._update_penetration_rate_gauge')
    def test_record_cache_null_value_fast_operation_always_records(
        self, mock_pen_gauge, mock_gauge, mock_prometheus, mock_logger
    ):
        """Test that fast null value operations (<100ms) are always recorded"""
        duration = 0.003  # 3ms - fast operation

        record_cache_null_value(self.endpoint, duration=duration)

        # Verify performance logger is called even for fast operations
        mock_logger.record_cache_operation.assert_called_once()
        call_args = mock_logger.record_cache_operation.call_args

        # Verify is_slow parameter is False for fast operations
        self.assertFalse(call_args[1]['is_slow'])

    @patch('common.metrics.cache_metrics._cache_performance_logger')
    @patch('common.metrics.cache_metrics.cache_requests_total')
    @patch('common.metrics.cache_metrics._update_hit_rate_gauge')
    def test_record_cache_hit_without_duration(self, mock_gauge, mock_prometheus, mock_logger):
        """Test that cache hits without duration are still recorded"""
        record_cache_hit(self.endpoint)

        # Verify performance logger is called
        mock_logger.record_cache_operation.assert_called_once()
        call_args = mock_logger.record_cache_operation.call_args

        # Verify is_slow parameter is False when duration is None
        self.assertFalse(call_args[1]['is_slow'])
        self.assertIsNone(call_args[1]['duration_ms'])

    @patch('common.metrics.cache_metrics._cache_performance_logger')
    def test_record_cache_operations_handle_errors_gracefully(self, mock_logger):
        """Test that recording errors don't raise exceptions"""
        # Make the logger raise an exception
        mock_logger.record_cache_operation.side_effect = Exception("Redis error")

        # Should not raise exception
        try:
            record_cache_hit(self.endpoint, duration=0.005)
        except Exception:
            self.fail("record_cache_hit should handle exceptions gracefully")


class TestCachePerformanceLoggerCalculations(unittest.TestCase):
    """Test that CachePerformanceLogger uses total_operations correctly in calculations"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = CachePerformanceLogger()

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_uses_total_operations_as_denominator(self, mock_get_redis):
        """Test that hit_rate calculation uses total_operations as denominator"""
        endpoint = "TestViewSet"

        # Mock Redis to return stats with total_operations field
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 80,
            b'misses': 15,
            b'null_values': 5,
            b'total_duration_ms': 500.0,
            b'slow_operations': 2,
            b'total_operations': 100,  # Total operations
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats(endpoint)

        # Verify total_operations is used
        self.assertEqual(stats['total_operations'], 100)
        self.assertEqual(stats['total_requests'], 100)

        # Verify calculations use total_operations
        self.assertEqual(stats['hit_rate'], 0.8)  # 80/100
        self.assertEqual(stats['slow_operation_rate'], 0.02)  # 2/100

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_backward_compatibility(self, mock_get_redis):
        """Test backward compatibility when total_operations is missing"""
        endpoint = "TestViewSet"

        # Mock Redis to return stats WITHOUT total_operations field
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 80,
            b'misses': 15,
            b'null_values': 5,
            b'total_duration_ms': 500.0,
            b'slow_operations': 2,
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats(endpoint)

        # Verify fallback to old calculation
        self.assertEqual(stats['total_operations'], 0)
        self.assertEqual(stats['total_requests'], 100)  # 80+15+5
        self.assertEqual(stats['hit_rate'], 0.8)  # 80/100

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_exposes_total_operations_field(self, mock_get_redis):
        """Test that total_operations field is exposed in stats"""
        endpoint = "TestViewSet"

        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 50,
            b'misses': 30,
            b'null_values': 10,
            b'total_duration_ms': 300.0,
            b'slow_operations': 5,
            b'total_operations': 90,
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats(endpoint)

        # Verify total_operations is in the returned dict
        self.assertIn('total_operations', stats)
        self.assertEqual(stats['total_operations'], 90)

    @patch('django_redis.get_redis_connection')
    def test_get_global_stats_uses_total_operations_as_denominator(self, mock_get_redis):
        """Test that global stats use total_operations as denominator"""
        # Mock Redis scan_iter to return endpoint keys
        mock_redis = MagicMock()
        mock_redis.scan_iter.return_value = [
            b'cache:perf:stats:TestViewSet1',
            b'cache:perf:stats:TestViewSet2',
        ]

        # Mock hgetall to return stats with total_operations
        def mock_hgetall(key):
            if b'TestViewSet1' in key:
                return {
                    b'hits': 80,
                    b'misses': 15,
                    b'null_values': 5,
                    b'total_duration_ms': 500.0,
                    b'slow_operations': 2,
                    b'total_operations': 100,
                }
            else:
                return {
                    b'hits': 60,
                    b'misses': 25,
                    b'null_values': 10,
                    b'total_duration_ms': 400.0,
                    b'slow_operations': 3,
                    b'total_operations': 95,
                }

        mock_redis.hgetall.side_effect = mock_hgetall
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_global_stats()

        # Verify totals are calculated correctly
        self.assertEqual(stats['total_operations'], 195)  # 100 + 95
        self.assertEqual(stats['total_requests'], 195)  # Uses total_operations
        self.assertEqual(stats['total_hits'], 140)  # 80 + 60

        # Verify calculations use total_operations
        self.assertAlmostEqual(stats['hit_rate'], 140 / 195, places=2)
        self.assertAlmostEqual(stats['slow_operation_rate'], 5 / 195, places=2)

    @patch('django_redis.get_redis_connection')
    def test_get_global_stats_backward_compatibility(self, mock_get_redis):
        """Test global stats backward compatibility when total_operations is missing"""
        mock_redis = MagicMock()
        mock_redis.scan_iter.return_value = [b'cache:perf:stats:TestViewSet']

        # Return stats WITHOUT total_operations
        mock_redis.hgetall.return_value = {
            b'hits': 80,
            b'misses': 15,
            b'null_values': 5,
            b'total_duration_ms': 500.0,
            b'slow_operations': 2,
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_global_stats()

        # Verify fallback to old calculation
        self.assertEqual(stats['total_operations'], 0)
        self.assertEqual(stats['total_requests'], 100)  # 80+15+5

    @patch('django_redis.get_redis_connection')
    def test_slow_operation_rate_calculation_accuracy(self, mock_get_redis):
        """Test that slow_operation_rate is calculated correctly"""
        endpoint = "TestViewSet"

        # Scenario: 1000 fast ops, 10 slow ops
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 600,
            b'misses': 300,
            b'null_values': 100,
            b'total_duration_ms': 1500.0,
            b'slow_operations': 10,
            b'total_operations': 1000,
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats(endpoint)

        # Verify slow operation rate is ~1% (10/1000), not 100%
        self.assertAlmostEqual(stats['slow_operation_rate'], 0.01, places=2)

    @patch('django_redis.get_redis_connection')
    def test_avg_duration_uses_total_operations(self, mock_get_redis):
        """Test that avg_duration calculation uses total_operations"""
        endpoint = "TestViewSet"

        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 100,
            b'misses': 50,
            b'null_values': 0,
            b'total_duration_ms': 150.0,  # Only slow ops duration recorded
            b'slow_operations': 5,
            b'total_operations': 150,
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats(endpoint)

        # Avg duration = 150ms / 150 total operations = 1ms
        # (Not 150ms / 5 slow ops = 30ms)
        self.assertAlmostEqual(stats['avg_duration_ms'], 1.0, places=1)


class TestCacheMetricsIntegration(unittest.TestCase):
    """Integration tests for cache metrics with separate counters"""

    @patch('common.utils.cache.record_cache_total_operation')
    @patch('common.utils.cache.get_redis_connection')
    @patch('common.utils.cache.cache')
    def test_total_operation_counter_independent_of_slow_operations(self, mock_django_cache, mock_redis, mock_record_total):
        """Test that total_operations counter is independent of slow operation recording"""
        from common.utils.cache import get_cache

        # Mock Django cache to return None (cache miss)
        mock_django_cache.get.return_value = None

        # Mock Redis for record_cache_total_operation
        mock_redis.return_value.hincrby.return_value = 1
        mock_redis.return_value.expire.return_value = True

        cache_key = "test:ChapterViewSet:123"

        # Call get_cache which should record total operation
        result = get_cache(cache_key)

        # Verify record_cache_total_operation was called
        mock_record_total.assert_called_once()

        # Verify it was called with the correct endpoint
        call_args = mock_record_total.call_args
        self.assertEqual(call_args[0][0], 'ChapterViewSet')


if __name__ == '__main__':
    unittest.main()
