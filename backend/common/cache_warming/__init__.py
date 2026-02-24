"""
Cache warming module for pre-loading frequently accessed data.

Implements three warming strategies:
- Startup warming: Warm core data on application startup
- On-demand warming: Refresh expired data asynchronously
- Scheduled warming: Periodic refresh of hot data
"""

from .tasks import (
    warm_startup_cache,
    warm_on_demand_cache,
    warm_scheduled_cache,
)

__all__ = [
    'warm_startup_cache',
    'warm_on_demand_cache',
    'warm_scheduled_cache',
]
