# Design: Fix Cache Metrics with Separate Counters

## Context

### Current State

The cache performance monitoring system currently suffers from a critical sampling bias:

1. **Only slow operations are recorded** (>100ms threshold)
2. **Fast operations are completely ignored** in statistics collection
3. **This creates misleading metrics**:
   - Slow operation rate always shows 100% (because denominator only includes slow operations)
   - Average duration is severely inflated (only slow ops are averaged)
   - Hit rate calculations are based on incomplete data

**Example from actual logs**:
```
ChapterViewSet: 1 hit, 1513ms avg, 100% slow rate
Reality: Likely 100+ fast hits (~5ms) + 1 slow hit (1513ms)
True avg: ~20ms, True slow rate: ~1%
```

### Constraints

1. **Performance overhead must remain minimal** - Current `lightweight-cache-stats` spec explicitly requires normal ops (<100ms) to avoid heavy Redis writes
2. **Must maintain backward compatibility** - Existing monitoring dashboards and alerts depend on log format
3. **Cannot lose historical data** - Need to preserve the ability to analyze slow operations in detail

### Stakeholders

- **DevOps team**: Needs accurate metrics for capacity planning and performance monitoring
- **Backend developers**: Need to identify genuinely slow endpoints vs statistical artifacts
- **Product team**: Relies on cache performance for user experience insights

## Goals / Non-Goals

**Goals:**

1. ✅ **Accurate slow operation rate** - Calculate as `slow_operations / total_operations`
2. ✅ **Accurate average duration** - Include all operations in denominator, not just slow ones
3. ✅ **Minimal performance overhead** - Total counter increment should be lightweight (single HINCRBY)
4. ✅ **Preserve slow operation details** - Keep existing detailed recording for ops >100ms
5. ✅ **Backward compatible logs** - Maintain existing log structure, just add `total_operations` field

**Non-Goals:**

- ❌ Changing the 100ms slow threshold (that's a separate tuning decision)
- ❌ Modifying Prometheus metrics collection (already working correctly)
- ❌ Changing alert threshold logic (just fix the data fed into alerts)
- ❌ Storing all operation details in Redis (would violate lightweight-stats spec)

## Decisions

### Decision 1: Use Separate Redis Counter for Total Operations

**Choice**: Add new `total_operations` field in Redis hash, separate from detailed tracking

**Rationale**:

| Approach | Pros | Cons |
|----------|------|------|
| **Separate counter** (chosen) | Simple, minimal overhead, clear separation of concerns | One more field in Redis hash |
| Record all ops with details | Complete data | Heavy overhead, violates lightweight-stats spec |
| Sample fast ops (e.g., 10%) | Middle ground | Still statistically biased, complex logic |

**Why this wins**:
- Single HINCRBY operation per cache request (~0.1ms overhead)
- Maintains the lightweight principle (no detailed data for fast ops)
- Clear separation: `total_operations` = lightweight counter, `hits/misses/slow_operations` = detailed tracking

### Decision 2: Always Increment Total Counter in cache.py

**Choice**: Move total counter increment to `cache.py` in `get_cache()` function, before any duration checks

**Rationale**:

```python
# In get_cache():
start_time = time.time()
# ... cache.get(key) happens ...
duration = time.time() - start_time

# BEFORE (only recorded slow ops):
if record_cache_hit and duration > 0.1:
    record_cache_hit(endpoint, duration, cache_key=key)

# AFTER (always record total, details only for slow):
record_cache_operation_total(endpoint)  # New lightweight call
if duration > 0.1:
    record_cache_hit(endpoint, duration, cache_key=key)  # Details only for slow
```

**Benefits**:
- Total counter captures ALL operations, regardless of speed
- Detailed recording still only happens for slow ops
- Clear separation in code: lightweight vs heavyweight operations

### Decision 3: Update Calculation Logic in logging.py

**Choice**: Modify `get_endpoint_stats()` and `get_global_stats()` to use `total_operations` as denominator

**Implementation**:
```python
# BEFORE:
hit_rate = hits / (hits + misses)  # Wrong: misses slow ops
slow_rate = slow_operations / (hits + misses + null_values)  # Wrong: denominator too small
avg_duration = total_duration_ms / (hits + misses + null_values)  # Wrong: only slow ops

# AFTER:
hit_rate = hits / total_operations  # Correct: includes all ops
slow_rate = slow_operations / total_operations  # Correct: proper denominator
avg_duration = total_duration_ms / total_operations  # Correct: all ops in avg
```

**Why this matters**:
- Aligns with the spec requirement: "all rate calculations SHALL use total_operations as denominator"
- Ensures metrics are mathematically sound

### Decision 4: Keep Detailed Recording Only for Slow Ops

**Choice**: Maintain existing behavior where `hits`, `misses`, `null_values` counters only increment for slow operations (>100ms)

**Rationale**:

- These counters are used for **trend analysis** of slow operations, not absolute rates
- The `total_operations` counter provides the accurate denominator for rate calculations
- Maintains lightweight principle: detailed analysis only for problematic ops

**Trade-off**: The `hits/misses` counters will continue to show "slow hits" and "slow misses", which is actually useful for identifying what types of ops are slow.

## Risks / Trade-offs

### Risk 1: Increased Redis Write Frequency

**Risk**: Incrementing `total_operations` on every cache op increases Redis load

**Mitigation**:
- Single HINCRBY operation is extremely lightweight (~0.1ms)
- Use Redis pipeline (already implemented in `record_cache_operation`)
- Monitor Redis CPU usage after deployment (should be negligible)

**Metrics to watch**:
- Redis ops/sec increase (expect +100%, but from very low baseline)
- Average cache operation latency (expect < 0.2ms increase)

### Risk 2: Log Format Changes Breaking Dashboards

**Risk**: Adding `total_operations` field might break log parsers

**Mitigation**:
- Field is **additive** (not changing existing fields)
- Backward compatible: old parsers ignore unknown fields
- Provide migration guide for any custom parsers

**Validation**:
- Test with existing log aggregation pipeline
- Verify Grafana dashboards still render correctly

### Risk 3: Historical Data Incompatibility

**Risk**: Old Redis stats won't have `total_operations` field, causing division errors

**Mitigation**:
```python
# In get_endpoint_stats():
total_operations = int(stats.get(b'total_operations', 0))
if total_operations == 0:
    # Fallback to old behavior for backward compatibility
    total_operations = hits + misses + null_values
```

**Migration path**:
- Code handles missing `total_operations` gracefully
- New data populates the field automatically
- Old data ages out after 5-minute TTL

## Migration Plan

### Phase 1: Code Changes (Development)

1. **Update `cache.py`**
   - Add `record_total_operation()` call in `get_cache()`
   - Remove `duration > 0.1` check from hit/miss recording

2. **Update `cache_metrics.py`**
   - Add `record_total_operation()` function
   - Keep existing `record_cache_hit/miss()` logic unchanged

3. **Update `logging.py`**
   - Modify `record_cache_operation()` to accept and store `total_operations` increment
   - Update calculation logic in `get_endpoint_stats()` and `get_global_stats()`
   - Add backward compatibility fallback for missing `total_operations`

### Phase 2: Testing (Staging)

1. **Unit Tests**
   - Test counter increments
   - Test rate calculations with new denominator
   - Test backward compatibility (missing `total_operations` field)

2. **Integration Tests**
   - Run cache operations and verify Redis data
   - Verify log output includes `total_operations`
   - Check calculation accuracy with synthetic data

3. **Performance Tests**
   - Measure overhead of additional HINCRBY operation
   - Verify cache operation latency impact < 0.2ms
   - Monitor Redis CPU during high load

### Phase 3: Deployment (Production)

**Deployment Strategy**: Blue-green deployment

1. **Deploy to one server** (canary)
   - Monitor Redis metrics for 10 minutes
   - Verify logs include `total_operations`
   - Check for errors in log aggregation

2. **Deploy to remaining servers**
   - Gradual rollout over 30 minutes
   - Continuous monitoring of alert dashboards

3. **Monitor for 24 hours**
   - Watch for any spike in Redis load
   - Verify slow operation rates look reasonable (expect drop from 100% to <10%)
   - Check alert triggers (expect fewer false positives)

### Rollback Strategy

**If issues detected**:

1. **Immediate rollback**: Revert code changes
   - Redis data auto-expires in 5 minutes (TTL)
   - Old code will ignore `total_operations` field and use fallback

2. **Data cleanup** (optional):
   ```python
   redis_conn.hdel(f"cache:perf:stats:{endpoint}", 'total_operations')
   ```

3. **Post-mortem**: Analyze logs to determine root cause

## Open Questions

### Q1: Should we backfill `total_operations` for existing stats?

**Status**: ✅ **RESOLVED** - No, not necessary

**Rationale**:
- Redis stats have 5-minute TTL, old data ages out quickly
- Backfill would require complex migration logic
- New code handles missing field gracefully with fallback
- Not worth the complexity for transient data

### Q2: What about Prometheus metrics? Do they need updating?

**Status**: ✅ **RESOLVED** - No, Prometheus metrics are already correct

**Rationale**:
- Prometheus uses `cache_requests_total` counter which already tracks ALL requests
- The issue is specific to Redis-based performance stats used for logging
- Prometheus metrics were never affected by this bug
- Verified by checking `cache_metrics.py` - Prometheus counters always incremented

### Q3: Should we expose `total_operations` in the performance summary log?

**Status**: ✅ **RESOLVED** - Yes, for transparency

**Rationale**:
- Helps operators understand the denominator used in rate calculations
- Useful for debugging metric accuracy
- Minimal overhead (just one more integer field in JSON)
- Aligns with "Alerts SHALL include actionable context" from spec

**Implementation**:
```python
{
  "endpoints": {
    "ChapterViewSet": {
      "total_requests": 100,  # NEW: total_operations
      "hits": 85,
      "misses": 15,
      "hit_rate": 0.85,
      "slow_operations": 2,
      "slow_operation_rate": 0.02,  # Now accurate!
      "avg_duration_ms": 25.5  # Now accurate!
    }
  }
}
```

## Implementation Notes

### Redis Data Structure

```python
# Key: cache:perf:stats:{endpoint}
# Fields:
{
  "hits": 85,              # Only slow hits (for trend analysis)
  "misses": 15,            # Only slow misses
  "null_values": 0,
  "slow_operations": 2,    # Count of ops > 100ms
  "total_duration_ms": 5100.0,  # Sum of durations for all operations
  "total_operations": 100  # NEW: All operations (fast + slow)
}
```

### Code Flow

```
1. Cache operation completes in cache.py
   ↓
2. Always call record_total_operation(endpoint)  # NEW
   ↓
3. If duration > 100ms, call record_cache_hit/miss(endpoint, duration)  # Existing
   ↓
4. Both calls use Redis pipeline for atomicity
   ↓
5. Periodic summary log reads from Redis
   ↓
6. Calculate rates using total_operations as denominator  # FIXED
   ↓
7. Generate accurate performance summary
```

### Performance Budget

| Operation | Baseline | After | Impact |
|-----------|----------|-------|--------|
| Fast cache hit (<100ms) | ~5ms | ~5.1ms | +2% (acceptable) |
| Slow cache hit (>100ms) | ~150ms | ~150.1ms | +0.07% (negligible) |
| Redis write per op | 0 (for fast) | 1 HINCRBY | +0.1ms overhead |
| Summary log generation | ~50ms | ~50ms | No change |

**Overall assessment**: Performance impact is minimal and well within acceptable bounds.
