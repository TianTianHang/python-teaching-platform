"""
Cache metrics module for Prometheus integration.

Provides metrics collection for:
- Cache hit/miss rates
- Cache penetration detection
- Cache warming statistics
"""

from .cache_metrics import (
    get_cache_metrics_registry,
    record_cache_hit,
    record_cache_miss,
    record_cache_null_value,
    record_penetration_attempt,
    get_cache_hit_rate,
    get_all_cache_stats,
)

__all__ = [
    'get_cache_metrics_registry',
    'record_cache_hit',
    'record_cache_miss',
    'record_cache_null_value',
    'record_penetration_attempt',
    'get_cache_hit_rate',
    'get_all_cache_stats',
]
