# Implementation Tasks: Fix Cache Metrics with Separate Counters

## 1. Backend Dependencies Setup

- [x] 1.1 Add missing type hints for new total_operations parameter in cache_metrics.py
- [x] 1.2 Import record_cache_hit/miss functions in cache_utils.py (check for existing imports)

## 2. Update cache.py - Add Total Counter

- [x] 2.1 Create new record_cache_total_operation() function in cache_utils.py
  - Accepts endpoint and optional duration (for debugging)
  - Uses Redis HINCRBY to increment total_operations for the endpoint
  - Maintains same 300s TTL as existing stats
  - Includes error handling to prevent Redis failures from affecting cache operations

- [x] 2.2 Modify get_cache() to call record_cache_total_operation()
  - Call immediately after cache.get() with extracted endpoint name
  - Before any duration checks or hit/miss recording
  - Ensure it's called even for cache misses and null values

- [x] 2.3 Update all record_cache_hit/miss/null_value calls in get_cache()
  - Remove the `duration > 0.1` condition from all calls
  - Always pass the actual duration (slow ops will have detailed recording)
  - Verify all three types of operations (hit, miss, null_value) are updated

## 3. Update cache_metrics.py - Modify Recording Logic

- [x] 3.1 Update record_cache_hit() function
  - Remove the duration > 0.1 condition check
  - Always call _cache_performance_logger.record_cache_operation()
  - Pass is_slow parameter based on duration > 0.1

- [x] 3.2 Update record_cache_miss() function
  - Remove the duration > 0.1 condition check
  - Always call _cache_performance_logger.record_cache_operation()
  - Pass is_slow parameter based on duration > 0.1

- [x] 3.3 Update record_cache_null_value() function
  - Modify to remove condition check (already always called)
  - Pass is_slow parameter based on duration > 0.1

## 4. Update logging.py - Add Total Counter Support

- [x] 4.1 Modify record_cache_operation() method
  - Add new parameter: increment_total (default True)
  - When increment_total is True, increment total_operations field
  - Maintain backward compatibility with existing behavior

- [x] 4.2 Update get_endpoint_stats() method
  - Add total_operations to returned stats dictionary
  - Use total_operations as denominator for hit_rate and slow_operation_rate calculations
  - Add backward compatibility fallback when total_operations is missing
  - Calculate average duration using total_operations (not just hits+misses)

- [x] 4.3 Update get_global_stats() method
  - Aggregate total_operations across all endpoints
  - Use total_operations as denominator for global calculations
  - Ensure slow_operation_rate = total_slow_operations / total_operations

- [x] 4.4 Create tests for calculation accuracy
  - Test with fast operations only (should show 0% slow rate)
  - Test with mixed operations (should calculate accurate percentages)
  - Test with missing total_operations field (should fall back gracefully)

## 5. Add Unit Tests

- [x] 5.1 Create test_cache_metrics.py
  - Test record_cache_hit/miss always increments total_operations
  - Test is_slow parameter is correctly passed for fast/slow operations
  - Test rate calculations use correct denominator

- [x] 5.2 Create test_cache_logging.py
  - Test record_cache_operation with and without total counter
  - Test get_endpoint_stats with missing total_operations field
  - Test calculation accuracy with various data scenarios

- [x] 5.3 Create test_cache_utils.py
  - Test get_cache() always calls record_cache_total_operation
  - Test record_cache_hit/miss calls work with removed duration condition
  - Test all cache operation types (hit, miss, null_value) update counters

## 6. Integration Testing

- [x] 6.1 Setup test environment with mock Redis
- [x] 6.2 Test full cache workflow with mixed fast/slow operations
- [x] 6.3 Verify periodic summary log uses correct calculations
- [x] 6.4 Test backward compatibility with existing data structures

## 7. Performance Testing

- [x] 7.1 Measure cache operation latency with overhead
  - Baseline: average cache operation time
  - After: should increase by < 0.2ms per operation
- [x] 7.2 Verify Redis load increase is minimal
  - Monitor Redis ops/sec during high cache traffic
  - Should see +100% writes but CPU impact should be negligible
- [x] 7.3 Test with synthetic data to verify accuracy
  - Generate 1000 fast ops, 10 slow ops
  - Verify slow rate = 10 / 1010 = 0.99% (not 100%)

## 8. Update Configuration Documentation

- [ ] 8.1 Update CACHE_PERFORMANCE_ALERT_THRESHOLDS documentation
  - Explain that slow_operation_rate is now calculated correctly
  - Update example configurations for the new accurate metrics
- [ ] 8.2 Add migration guide for existing dashboards
  - Document the new total_operations field in logs
  - Explain how to adjust queries for accurate percentages

## 9. Deployment Preparation

- [ ] 9.1 Create monitoring dashboard queries for accurate metrics
- [ ] 9.2 Test rollback procedure on staging environment
- [ ] 9.3 Prepare deployment checklist with validation steps
- [ ] 9.4 Setup alert thresholds based on accurate metrics

## 10. Production Deployment and Validation

- [ ] 10.1 Deploy to one server as canary
- [ ] 10.2 Monitor Redis metrics for 10 minutes
- [ ] 10.3 Verify performance logs include total_operations field
- [ ] 10.4 Check that slow_operation rates are < 10% (not 100%)
- [ ] 10.5 Deploy to remaining servers gradually
- [ ] 10.6 Validate that dashboards show correct metrics
- [ ] 10.7 Verify alert triggers work correctly with new data
