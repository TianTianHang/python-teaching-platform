"""
Unit tests for cache performance logging.

Tests the CachePerformanceLogger with the new separate counters implementation:
- Total operations tracking
- Slow operations tracking
- Accurate rate calculations
- Backward compatibility
"""

import unittest
from unittest.mock import patch, MagicMock
from django.test import override_settings

from common.utils.logging import CachePerformanceLogger


class TestCachePerformanceLoggerRecordOperation(unittest.TestCase):
    """Test CachePerformanceLogger.record_cache_operation method"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = CachePerformanceLogger()

    @patch('django_redis.get_redis_connection')
    def test_record_hit_increments_hits_counter(self, mock_get_redis):
        """Test that recording a hit increments the hits counter"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='hit',
            duration_ms=5.0,
            is_slow=False
        )

        # Verify Redis pipeline was created
        mock_redis.pipeline.assert_called_once()

        # Get the pipeline and verify hincrby was called for hits
        pipe = mock_redis.pipeline.return_value
        pipe.hincrby.assert_any_call('cache:perf:stats:TestViewSet', 'hits', 1)

    @patch('django_redis.get_redis_connection')
    def test_record_miss_increments_misses_counter(self, mock_get_redis):
        """Test that recording a miss increments the misses counter"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='miss',
            duration_ms=10.0,
            is_slow=False
        )

        pipe = mock_redis.pipeline.return_value
        pipe.hincrby.assert_any_call('cache:perf:stats:TestViewSet', 'misses', 1)

    @patch('django_redis.get_redis_connection')
    def test_record_null_value_increments_null_values_counter(self, mock_get_redis):
        """Test that recording a null_value increments the null_values counter"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='null_value',
            duration_ms=3.0,
            is_slow=False
        )

        pipe = mock_redis.pipeline.return_value
        pipe.hincrby.assert_any_call('cache:perf:stats:TestViewSet', 'null_values', 1)

    @patch('django_redis.get_redis_connection')
    def test_record_slow_operation_increments_slow_operations_counter(self, mock_get_redis):
        """Test that recording a slow operation increments the slow_operations counter"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='hit',
            duration_ms=150.0,
            is_slow=True
        )

        pipe = mock_redis.pipeline.return_value
        pipe.hincrby.assert_any_call('cache:perf:stats:TestViewSet', 'slow_operations', 1)

    @patch('django_redis.get_redis_connection')
    def test_record_fast_operation_does_not_increment_slow_operations(self, mock_get_redis):
        """Test that recording a fast operation does not increment slow_operations counter"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='hit',
            duration_ms=5.0,
            is_slow=False
        )

        pipe = mock_redis.pipeline.return_value

        # Verify slow_operations is NOT incremented
        for call_item in pipe.hincrby.call_args_list:
            args, kwargs = call_item
            if len(args) >= 3:
                field = args[1]
                # slow_operations should not be in the calls
                if field == 'slow_operations':
                    self.fail("slow_operations should not be incremented for fast operations")

    @patch('django_redis.get_redis_connection')
    def test_record_operation_with_duration_increments_total_duration(self, mock_get_redis):
        """Test that recording with duration increments total_duration_ms"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='hit',
            duration_ms=25.5,
            is_slow=False
        )

        pipe = mock_redis.pipeline.return_value
        pipe.hincrbyfloat.assert_called_once_with(
            'cache:perf:stats:TestViewSet',
            'total_duration_ms',
            25.5
        )

    @patch('django_redis.get_redis_connection')
    def test_record_operation_sets_ttl(self, mock_get_redis):
        """Test that recording an operation sets TTL on the stats key"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        self.logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='hit',
            duration_ms=5.0,
            is_slow=False
        )

        pipe = mock_redis.pipeline.return_value
        pipe.expire.assert_called_once_with('cache:perf:stats:TestViewSet', 300)

    @patch('django_redis.get_redis_connection')
    def test_record_operation_handles_redis_errors_gracefully(self, mock_get_redis):
        """Test that Redis errors are handled gracefully"""
        mock_get_redis.side_effect = Exception("Redis connection error")

        # Should not raise exception
        try:
            self.logger.record_cache_operation(
                endpoint='TestViewSet',
                operation_type='hit',
                duration_ms=5.0,
                is_slow=False
            )
        except Exception:
            self.fail("record_cache_operation should handle Redis errors gracefully")


class TestCachePerformanceLoggerGetStats(unittest.TestCase):
    """Test CachePerformanceLogger get_endpoint_stats and get_global_stats methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = CachePerformanceLogger()

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_returns_zero_stats_when_no_data(self, mock_get_redis):
        """Test that get_endpoint_stats returns zeros when no stats exist"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {}
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats('TestViewSet')

        self.assertEqual(stats['endpoint'], 'TestViewSet')
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)
        self.assertEqual(stats['null_values'], 0)
        self.assertEqual(stats['total_requests'], 0)
        self.assertIn('total_operations', stats)
        self.assertEqual(stats['total_operations'], 0)
        self.assertIsNone(stats['hit_rate'])
        self.assertIsNone(stats['miss_rate'])
        self.assertIsNone(stats['penetration_rate'])
        self.assertIsNone(stats['avg_duration_ms'])
        self.assertEqual(stats['slow_operations'], 0)
        self.assertIsNone(stats['slow_operation_rate'])

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_calculates_hit_rate_correctly(self, mock_get_redis):
        """Test that hit_rate is calculated correctly using total_operations"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 80,
            b'misses': 15,
            b'null_values': 5,
            b'total_duration_ms': 500.0,
            b'slow_operations': 2,
            b'total_operations': 100,
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats('TestViewSet')

        self.assertEqual(stats['hit_rate'], 0.8)  # 80/100

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_calculates_slow_operation_rate_correctly(self, mock_get_redis):
        """Test that slow_operation_rate is calculated correctly"""
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

        stats = self.logger.get_endpoint_stats('TestViewSet')

        # Should be ~1% (10/1000), not 100% (10/10)
        self.assertAlmostEqual(stats['slow_operation_rate'], 0.01, places=2)

    @patch('django_redis.get_redis_connection')
    def test_get_endpoint_stats_backward_compatibility_missing_total_operations(self, mock_get_redis):
        """Test backward compatibility when total_operations field is missing"""
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b'hits': 80,
            b'misses': 15,
            b'null_values': 5,
            b'total_duration_ms': 500.0,
            b'slow_operations': 2,
            # total_operations is missing
        }
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_endpoint_stats('TestViewSet')

        # Should fall back to old calculation (hits+misses+null_values)
        self.assertIn('total_operations', stats)
        self.assertEqual(stats['total_operations'], 0)
        self.assertEqual(stats['total_requests'], 100)  # 80+15+5
        self.assertEqual(stats['hit_rate'], 0.8)  # 80/100

    @patch('django_redis.get_redis_connection')
    def test_get_global_stats_aggregates_correctly(self, mock_get_redis):
        """Test that get_global_stats aggregates across all endpoints"""
        mock_redis = MagicMock()
        mock_redis.scan_iter.return_value = [
            b'cache:perf:stats:Endpoint1',
            b'cache:perf:stats:Endpoint2',
        ]

        def mock_hgetall(key):
            if b'Endpoint1' in key:
                return {
                    b'hits': 100,
                    b'misses': 20,
                    b'null_values': 5,
                    b'total_duration_ms': 300.0,
                    b'slow_operations': 3,
                    b'total_operations': 125,
                }
            else:
                return {
                    b'hits': 80,
                    b'misses': 30,
                    b'null_values': 10,
                    b'total_duration_ms': 400.0,
                    b'slow_operations': 4,
                    b'total_operations': 120,
                }

        mock_redis.hgetall.side_effect = mock_hgetall
        mock_get_redis.return_value = mock_redis

        stats = self.logger.get_global_stats()

        self.assertEqual(stats['total_hits'], 180)  # 100+80
        self.assertEqual(stats['total_misses'], 50)  # 20+30
        self.assertEqual(stats['total_null_values'], 15)  # 5+10
        self.assertEqual(stats['total_operations'], 245)  # 125+120
        self.assertEqual(stats['total_requests'], 245)  # Uses total_operations
        self.assertAlmostEqual(stats['hit_rate'], 180/245, places=2)

    @patch('django_redis.get_redis_connection')
    def test_get_all_endpoint_stats(self, mock_get_redis):
        """Test get_all_endpoint_stats returns stats for all endpoints"""
        mock_redis = MagicMock()
        mock_redis.scan_iter.return_value = [
            b'cache:perf:stats:Endpoint1',
            b'cache:perf:stats:Endpoint2',
        ]

        def mock_hgetall(key):
            if b'Endpoint1' in key:
                return {
                    b'hits': 100,
                    b'misses': 20,
                    b'null_values': 5,
                    b'total_duration_ms': 300.0,
                    b'slow_operations': 3,
                    b'total_operations': 125,
                }
            else:
                return {
                    b'hits': 80,
                    b'misses': 30,
                    b'null_values': 10,
                    b'total_duration_ms': 400.0,
                    b'slow_operations': 4,
                    b'total_operations': 120,
                }

        mock_redis.hgetall.side_effect = mock_hgetall
        mock_get_redis.return_value = mock_redis

        with patch.object(self.logger, 'get_endpoint_stats') as mock_get_stats:
            mock_get_stats.side_effect = lambda ep: {
                'endpoint': ep,
                'total_requests': 125 if 'Endpoint1' in ep else 120,
            }

            all_stats = self.logger.get_all_endpoint_stats()

            self.assertEqual(len(all_stats), 2)
            self.assertIn('Endpoint1', all_stats)
            self.assertIn('Endpoint2', all_stats)


class TestCachePerformanceLoggerConfiguration(unittest.TestCase):
    """Test CachePerformanceLogger configuration and settings"""

    @patch('django_redis.get_redis_connection')
    @override_settings(
        CACHE_STATS_KEY_PREFIX='custom:prefix',
        CACHE_STATS_TTL=600
    )
    def test_custom_configuration(self, mock_get_redis):
        """Test that custom configuration is used"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        logger = CachePerformanceLogger()

        # Record an operation
        logger.record_cache_operation(
            endpoint='TestViewSet',
            operation_type='hit',
            duration_ms=5.0,
            is_slow=False
        )

        pipe = mock_redis.pipeline.return_value

        # Verify custom prefix is used
        key_arg = pipe.hincrby.call_args_list[0][0][0]
        self.assertTrue(key_arg.startswith('custom:prefix:'))

        # Verify custom TTL is used
        pipe.expire.assert_called_with('custom:prefix:TestViewSet', 600)

    @patch('django_redis.get_redis_connection')
    def test_default_configuration(self, mock_get_redis):
        """Test that default configuration is used when settings are not provided"""
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        with patch('django.conf.settings') as mock_settings:
            mock_settings.CACHE_STATS_KEY_PREFIX = 'cache:perf:stats'
            mock_settings.CACHE_STATS_TTL = 300

            logger = CachePerformanceLogger()

            # Record an operation
            logger.record_cache_operation(
                endpoint='TestViewSet',
                operation_type='hit',
                duration_ms=5.0,
                is_slow=False
            )

            pipe = mock_redis.pipeline.return_value

            # Verify default prefix is used
            key_arg = pipe.hincrby.call_args_list[0][0][0]
            self.assertTrue(key_arg.startswith('cache:perf:stats:'))

            # Verify default TTL is used
            pipe.expire.assert_called_with('cache:perf:stats:TestViewSet', 300)


class TestCachePerformanceLoggerResetStats(unittest.TestCase):
    """Test CachePerformanceLogger.reset_stats method"""

    @patch('django_redis.get_redis_connection')
    def test_reset_stats_deletes_all_keys(self, mock_get_redis):
        """Test that reset_stats deletes all cache stats keys"""
        mock_redis = MagicMock()
        mock_scan_iter = MagicMock(return_value=[
            b'cache:perf:stats:Endpoint1',
            b'cache:perf:stats:Endpoint2',
        ])
        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete.return_value = 2
        mock_get_redis.return_value = mock_redis

        logger = CachePerformanceLogger()
        logger.reset_stats()

        # Verify scan_iter was called with correct pattern
        mock_scan_iter.assert_called_with(match='cache:perf:stats:*', count=100)

        # Verify delete was called once with the keys
        mock_redis.delete.assert_called_once()
        call_args = mock_redis.delete.call_args

        # Verify it was called with two keys
        self.assertEqual(len(call_args[0]), 2)
        keys = call_args[0][0]
        self.assertIn(b'cache:perf:stats:Endpoint1', keys)
        self.assertIn(b'cache:perf:stats:Endpoint2', keys)


if __name__ == '__main__':
    unittest.main()
