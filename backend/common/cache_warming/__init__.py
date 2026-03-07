"""
Cache warming module for pre-loading frequently accessed data.

Implements cache warming for SeparatedCacheService GLOBAL layer:
- Startup warming: Warm GLOBAL data on application startup
- On-demand warming: Refresh expired data asynchronously
- Scheduled warming: Periodic refresh of hot (high hit rate >30%) data
"""

from .tasks import (
    warm_separated_global_startup,
    warm_separated_global_on_demand,
    warm_separated_global_scheduled,
    cache_performance_summary,
)

__all__ = [
    "warm_separated_global_startup",
    "warm_separated_global_on_demand",
    "warm_separated_global_scheduled",
    "cache_performance_summary",
]
