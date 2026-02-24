"""
Cache metrics collection for Prometheus monitoring.

This module provides Prometheus metrics for cache operations:
- Cache requests (total, by endpoint)
- Cache hits/misses (total, by endpoint)
- Cache hit rate (calculated)
- Cache penetration attempts
- Cache warming statistics
"""

import logging
import time
from typing import Dict, Any, Optional, List
from prometheus_client import Counter, Histogram, Gauge, Registry, CollectorRegistry
from prometheus_client.metrics import MetricWrapperBase
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

# ============ Prometheus Metrics ============

# Create a custom registry for cache metrics
_cache_metrics_registry = CollectorRegistry()

# Cache request counters
cache_requests_total = Counter(
    'cache_requests_total',
    'Total cache requests',
    ['endpoint', 'status'],  # status: hit, miss, null_value
    registry=_cache_metrics_registry
)

# Cache penetration detection
cache_penetration_attempts_total = Counter(
    'cache_penetration_attempts_total',
    'Total cache penetration attempts (requests for non-existent resources)',
    ['endpoint'],
    registry=_cache_metrics_registry
)

# Cache operation duration
cache_operation_duration_seconds = Histogram(
    'cache_operation_duration_seconds',
    'Cache operation duration in seconds',
    ['operation', 'endpoint'],  # operation: get, set, delete
    registry=_cache_metrics_registry,
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Cache warming metrics
cache_warming_tasks_total = Counter(
    'cache_warming_tasks_total',
    'Total cache warming tasks executed',
    ['warming_type', 'status'],  # warming_type: startup, on_demand, scheduled
    registry=_cache_metrics_registry
)

cache_warming_items_total = Counter(
    'cache_warming_items_total',
    'Total items warmed',
    ['warming_type'],
    registry=_cache_metrics_registry
)

cache_warming_duration_seconds = Histogram(
    'cache_warming_duration_seconds',
    'Cache warming task duration in seconds',
    ['warming_type'],
    registry=_cache_metrics_registry,
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)
)

# Current cache hit rate gauge
cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Current cache hit rate (0-1)',
    ['endpoint'],
    registry=_cache_metrics_registry
)

# Penetration detection gauge
cache_penetration_rate = Gauge(
    'cache_penetration_rate',
    'Cache penetration rate (ratio of null_value to total requests)',
    ['endpoint'],
    registry=_cache_metrics_registry
)


# ============ Metrics Recording Functions ============

def record_cache_hit(endpoint: str, duration: Optional[float] = None):
    """Record a cache hit

    Args:
        endpoint: The endpoint/view name
        duration: Operation duration in seconds (optional)
    """
    cache_requests_total.labels(endpoint=endpoint, status='hit').inc()
    if duration is not None:
        cache_operation_duration_seconds.labels(operation='get', endpoint=endpoint).observe(duration)
    _update_hit_rate_gauge(endpoint)


def record_cache_miss(endpoint: str, duration: Optional[float] = None):
    """Record a cache miss

    Args:
        endpoint: The endpoint/view name
        duration: Operation duration in seconds (optional)
    """
    cache_requests_total.labels(endpoint=endpoint, status='miss').inc()
    if duration is not None:
        cache_operation_duration_seconds.labels(operation='get', endpoint=endpoint).observe(duration)
    _update_hit_rate_gauge(endpoint)


def record_cache_null_value(endpoint: str, duration: Optional[float] = None):
    """Record a null value (cached non-existent resource)

    Args:
        endpoint: The endpoint/view name
        duration: Operation duration in seconds (optional)
    """
    cache_requests_total.labels(endpoint=endpoint, status='null_value').inc()
    if duration is not None:
        cache_operation_duration_seconds.labels(operation='get', endpoint=endpoint).observe(duration)
    _update_hit_rate_gauge(endpoint)
    _update_penetration_rate_gauge(endpoint)


def record_penetration_attempt(endpoint: str, resource_id: str):
    """Record a potential cache penetration attempt

    Args:
        endpoint: The endpoint/view name
        resource_id: The requested resource ID
    """
    cache_penetration_attempts_total.labels(endpoint=endpoint).inc()
    logger.warning(f"Potential cache penetration attempt: {endpoint} - {resource_id}")
    _update_penetration_rate_gauge(endpoint)


def record_cache_warming_task(
    warming_type: str,
    status: str,
    items_count: int,
    duration: float
):
    """Record a cache warming task execution

    Args:
        warming_type: Type of warming (startup, on_demand, scheduled)
        status: Task status (success, error, skipped)
        items_count: Number of items warmed
        duration: Task duration in seconds
    """
    cache_warming_tasks_total.labels(warming_type=warming_type, status=status).inc()
    if items_count > 0:
        cache_warming_items_total.labels(warming_type=warming_type).inc(items_count)
    cache_warming_duration_seconds.labels(warming_type=warming_type).observe(duration)


# ============ Gauge Update Functions ============

def _update_hit_rate_gauge(endpoint: str):
    """Update the cache hit rate gauge for an endpoint"""
    try:
        hit_rate = _calculate_hit_rate_for_endpoint(endpoint)
        if hit_rate is not None:
            cache_hit_rate.labels(endpoint=endpoint).set(hit_rate)
    except Exception as e:
        logger.warning(f"Failed to update hit rate gauge for {endpoint}: {e}")


def _update_penetration_rate_gauge(endpoint: str):
    """Update the penetration rate gauge for an endpoint"""
    try:
        penetration_rate = _calculate_penetration_rate_for_endpoint(endpoint)
        if penetration_rate is not None:
            cache_penetration_rate.labels(endpoint=endpoint).set(penetration_rate)
    except Exception as e:
        logger.warning(f"Failed to update penetration rate gauge for {endpoint}: {e}")


# ============ Calculation Functions ============

def _calculate_hit_rate_for_endpoint(endpoint: str) -> Optional[float]:
    """Calculate hit rate for a specific endpoint"""
    try:
        # Get hit and null_value counts (both are considered "hits" from performance perspective)
        hit_metric = cache_requests_total.labels(endpoint=endpoint, status='hit')._value
        miss_metric = cache_requests_total.labels(endpoint=endpoint, status='miss')._value
        null_metric = cache_requests_total.labels(endpoint=endpoint, status='null_value')._value

        total = hit_metric + miss_metric + null_metric
        if total == 0:
            return None

        # Hit rate includes both actual hits and cached null values (since they avoid DB queries)
        return (hit_metric + null_metric) / total
    except Exception:
        return None


def _calculate_penetration_rate_for_endpoint(endpoint: str) -> Optional[float]:
    """Calculate penetration rate (null_value / total requests) for an endpoint"""
    try:
        hit_metric = cache_requests_total.labels(endpoint=endpoint, status='hit')._value
        miss_metric = cache_requests_total.labels(endpoint=endpoint, status='miss')._value
        null_metric = cache_requests_total.labels(endpoint=endpoint, status='null_value')._value

        total = hit_metric + miss_metric + null_metric
        if total == 0:
            return None

        return null_metric / total
    except Exception:
        return None


def get_cache_hit_rate(endpoint: Optional[str] = None) -> Dict[str, float]:
    """Get cache hit rates

    Args:
        endpoint: Specific endpoint (optional). If None, returns all endpoints.

    Returns:
        Dict mapping endpoint names to hit rates (0-1)
    """
    if endpoint:
        rate = _calculate_hit_rate_for_endpoint(endpoint)
        return {endpoint: rate} if rate is not None else {}

    # Return all endpoints
    result = {}
    try:
        for metric in cache_requests_total.collect():
            for sample in metric.samples:
                if sample.name == 'cache_requests_total':
                    ep = sample.labels.get('endpoint')
                    if ep and ep not in result:
                        rate = _calculate_hit_rate_for_endpoint(ep)
                        if rate is not None:
                            result[ep] = rate
    except Exception as e:
        logger.warning(f"Failed to get cache hit rates: {e}")

    return result


def get_penetration_rate(endpoint: Optional[str] = None) -> Dict[str, float]:
    """Get cache penetration rates

    Args:
        endpoint: Specific endpoint (optional). If None, returns all endpoints.

    Returns:
        Dict mapping endpoint names to penetration rates (0-1)
    """
    if endpoint:
        rate = _calculate_penetration_rate_for_endpoint(endpoint)
        return {endpoint: rate} if rate is not None else {}

    # Return all endpoints
    result = {}
    try:
        for metric in cache_requests_total.collect():
            for sample in metric.samples:
                if sample.name == 'cache_requests_total':
                    ep = sample.labels.get('endpoint')
                    if ep and ep not in result:
                        rate = _calculate_penetration_rate_for_endpoint(ep)
                        if rate is not None:
                            result[ep] = rate
    except Exception as e:
        logger.warning(f"Failed to get penetration rates: {e}")

    return result


def get_all_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics

    Returns:
        Dict containing:
        - total_requests: Total cache requests
        - hit_rate: Overall hit rate
        - endpoint_stats: Per-endpoint statistics
        - penetration_alerts: Endpoints with high penetration rate (>10%)
    """
    result = {
        'total_requests': 0,
        'hit_rate': 0.0,
        'endpoint_stats': {},
        'penetration_alerts': []
    }

    try:
        total_requests = 0
        total_hits = 0
        total_nulls = 0

        # Aggregate per-endpoint stats
        for metric in cache_requests_total.collect():
            for sample in metric.samples:
                if sample.name == 'cache_requests_total':
                    endpoint = sample.labels.get('endpoint')
                    status = sample.labels.get('status')
                    value = sample.value

                    if endpoint not in result['endpoint_stats']:
                        result['endpoint_stats'][endpoint] = {
                            'hit': 0,
                            'miss': 0,
                            'null_value': 0,
                            'total': 0,
                            'hit_rate': 0.0,
                            'penetration_rate': 0.0
                        }

                    result['endpoint_stats'][endpoint][status] = int(value)
                    result['endpoint_stats'][endpoint]['total'] += int(value)
                    total_requests += int(value)

                    if status == 'hit':
                        total_hits += int(value)
                    elif status == 'null_value':
                        total_nulls += int(value)

        # Calculate overall hit rate
        if total_requests > 0:
            result['hit_rate'] = (total_hits + total_nulls) / total_requests

        result['total_requests'] = total_requests

        # Calculate per-endpoint rates
        for endpoint, stats in result['endpoint_stats'].items():
            if stats['total'] > 0:
                stats['hit_rate'] = (stats['hit'] + stats['null_value']) / stats['total']
                stats['penetration_rate'] = stats['null_value'] / stats['total']

                # Alert on high penetration rate (>10%)
                if stats['penetration_rate'] > 0.1 and stats['total'] > 100:
                    result['penetration_alerts'].append({
                        'endpoint': endpoint,
                        'penetration_rate': stats['penetration_rate'],
                        'null_value_count': stats['null_value'],
                        'total_requests': stats['total']
                    })

    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")

    return result


def get_cache_metrics_registry() -> Registry:
    """Get the cache metrics Prometheus registry

    Returns:
        The Prometheus Registry containing all cache metrics
    """
    return _cache_metrics_registry


def reset_metrics():
    """Reset all metrics (useful for testing)"""
    for metric in list(_cache_metrics_registry.collect()):
        for sample in metric.samples:
            if hasattr(sample, 'metric'):
                metric.clear()


# ============ Alert Threshold Functions ============

def check_low_hit_rate_alert(threshold: float = 0.8, min_requests: int = 100) -> List[Dict[str, Any]]:
    """Check for endpoints with low hit rate

    Args:
        threshold: Hit rate threshold (default 0.8 = 80%)
        min_requests: Minimum requests to consider (default 100)

    Returns:
        List of endpoints with hit rate below threshold
    """
    alerts = []
    stats = get_all_cache_stats()

    for endpoint, ep_stats in stats['endpoint_stats'].items():
        if ep_stats['total'] >= min_requests and ep_stats['hit_rate'] < threshold:
            alerts.append({
                'endpoint': endpoint,
                'hit_rate': ep_stats['hit_rate'],
                'total_requests': ep_stats['total'],
                'threshold': threshold
            })

    return alerts


def check_high_penetration_alert(threshold: float = 0.1, min_requests: int = 100) -> List[Dict[str, Any]]:
    """Check for endpoints with high penetration rate

    Args:
        threshold: Penetration rate threshold (default 0.1 = 10%)
        min_requests: Minimum requests to consider (default 100)

    Returns:
        List of endpoints with penetration rate above threshold
    """
    alerts = []
    stats = get_all_cache_stats()

    for alert in stats['penetration_alerts']:
        if alert['penetration_rate'] > threshold and alert['total_requests'] >= min_requests:
            alerts.append(alert)

    return alerts
