# Cache Monitoring and Operations Guide

This document provides comprehensive guidance for monitoring and operating the enhanced cache system.

## Overview

The enhanced cache system includes:
- Penetration protection (NULL_VALUE caching)
- Adaptive TTL based on access patterns
- Cache warming with startup/on-demand/scheduled strategies
- Prometheus metrics for monitoring
- Rate limiting for API protection

## Key Metrics

### Prometheus Endpoints

- **Metrics**: `http://your-domain.com/metrics`
- **Health Check**: `http://your-domain.com/api/health/cache`

### Critical Metrics to Monitor

| Metric | Description | Warning Threshold | Critical Threshold |
|--------|-------------|------------------|-------------------|
| `cache_hit_rate` | Overall cache hit rate | < 80% | < 60% |
| `cache_penetration_rate` | Null value requests ratio | > 10% | > 20% |
| `cache_warming_duration_seconds` | Warming task duration | > 60s | > 120s |
| `cache_requests_total` | Total cache requests by status | - | - |
| `cache_penetration_attempts_total` | Potential penetration attempts | - | - |

### Dashboards

#### 1. Cache Performance Dashboard
- **Hit Rate Trend**: Track 7-day trend
- **Penetration Rate**: Monitor for spikes
- **Response Times**: API vs cache performance
- **Warming Status**: Task completion rate

#### 2. Alerting Dashboard
- **Low Hit Rate Alerts**: When hit rate < 80% for > 15 minutes
- **High Penetration Alerts**: When penetration rate > 10%
- **Warming Failures**: Task failures in last hour
- **Slow Requests**: Requests exceeding 1 second

## Feature Flags

The system supports gradual rollout via feature flags:

```python
# Check features
from common.feature_flags import is_cache_feature_enabled

if is_cache_feature_enabled():
    # Use enhanced cache
    pass
```

### Feature Control Commands

```bash
# Enable enhanced cache (production)
python manage.py shell
>>> from common.feature_flags import enable_cache_feature
>>> enable_cache_feature()

# Set rollout percentage (gradual rollout)
>>> from common.feature_flags import FeatureFlagService
>>> FeatureFlagService.set_percentage(Feature.ENHANCED_CACHE, 50)

# Add user to whitelist
>>> FeatureFlagService.add_to_whitelist(Feature.ENHANCED_CACHE, 12345)
```

## Cache Warming

### Strategies

1. **Startup Warming**
   - Triggers: Application startup
   - Priority: Course details > Course lists > Chapters > Problems
   - Duration: ~3-5 minutes

2. **On-Demand Warming**
   - Triggers: Stale data requests
   - Behavior: Returns stale data, refreshes in background
   - Deduplication: Prevents duplicate refreshes

3. **Scheduled Warming**
   - Triggers: Every hour
   - Criteria: High hit rate (>30%) and >100 requests
   - Duration: ~1-2 minutes

### Monitoring Warming

```bash
# Check warming statistics
redis-cli HGETALL cache_warming_stats

# Monitor active warming tasks
redis-cli KEYS cache_warming_lock:startup:*
```

### Warming Configuration

```python
# settings.py
CACHE_WARMING = {
    'ENABLED': True,
    'STARTUP_COURSE_LIMIT': 100,  # Courses to warm at startup
    'CHAPTERS_PER_COURSE': 5,     # Chapters per course
    'PROBLEM_LIMIT': 100,         # Popular problems to warm
    'SCHEDULED_INTERVAL': 3600,  # 1 hour
}
```

## Rate Limiting

### Configuration

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'common.throttling.AnonRateThrottle',
        'common.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Anonymous users
        'user': '1000/hour',     # Authenticated users
    },
}
```

### Checking Throttling Status

```python
# Check if request is being throttled
from common.throttling import is_throttled, get_rate_limit_status

throttled, reason = is_throttled(request)
status = get_rate_limit_status(request)
```

## Troubleshooting

### Common Issues

#### 1. Low Hit Rate
**Symptoms**: `cache_hit_rate` < 80%
**Actions**:
- Check for new API endpoints not using cache
- Verify cache keys are properly generated
- Look for frequent data changes

#### 2. Cache Penetration Attack
**Symptoms**: `cache_penetration_rate` > 10%
**Actions**:
- Enable penetration protection feature flag
- Check for bots scraping non-existent resources
- Monitor for suspicious patterns in logs

#### 3. Slow Cache Warming
**Symptoms**: Warming tasks taking > 60 seconds
**Actions**:
- Increase timeout for warming tasks
- Check database performance
- Reduce concurrent warming tasks

#### 4. Memory Usage High
**Symptoms**: Redis memory usage > 80%
**Actions**:
- Reduce default TTL values
- Enable adaptive TTL
- Clear old warming statistics

### Manual Cache Operations

```bash
# Clear all cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Clear specific cache patterns
>>> from common.utils.cache import delete_cache_pattern
>>> delete_cache_pattern("api:*")

# Check cache size
>>> from django_redis import get_redis_connection
>>> r = get_redis_connection("default")
>>> r.dbsize()
```

### Rolling Back Changes

```bash
# Disable all new features
python manage.py shell
>>> from common.feature_flags import disable_cache_feature
>>> disable_cache_feature()
>>> from common.feature_flags import FeatureFlagService
>>> FeatureFlagService.disable_feature(Feature.CACHE_WARMING)
>>> FeatureFlagService.disable_feature(Feature.RATE_LIMITING)
```

## Performance Tuning

### Redis Configuration

```redis
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60
```

### Django Settings Tuning

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'django'
    }
}
```

### Monitoring Queries

```sql
-- Check cache hit rate by endpoint
SELECT
    view_name,
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY view_name) as percentage
FROM cache_stats
GROUP BY view_name, status
ORDER BY view_name, count DESC;
```

## Deployment Checklist

### Pre-Deployment
- [ ] Backup current Redis data
- [ ] Verify feature flags are set to GRADUAL (0%)
- [ ] Monitor baseline performance for 24 hours

### Deployment
- [ ] Deploy new code to staging
- [ ] Run tests: `uv run python manage.py test`
- [ ] Check metrics: `http://staging.com/metrics`

### Post-Deployment
- [ ] Monitor error rates for 1 hour
- [ ] Check cache warming startup tasks
- [ ] Verify cache headers are present

### Gradual Rollout
- [ ] Set feature flag to 10% for 24 hours
- [ ] Monitor for any issues
- [ ] Gradually increase: 25% → 50% → 75% → 100%

## Contact Information

- **Cache Team**: cache-team@example.com
- **DevOps**: devops@example.com
- **Emergency**: on-call@example.com

## Incident Response

### Severity 1 (Critical)
- Cache system down for > 5 minutes
- Feature flag immediately disabled
- Page cache enabled as fallback

### Severity 2 (Major)
- Hit rate < 60% for > 30 minutes
- Warming failures > 50%
- On-call notification

### Severity 3 (Minor)
- Performance degradation
- Alerting issues
- Schedule fix during maintenance window