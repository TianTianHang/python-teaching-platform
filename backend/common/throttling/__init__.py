"""
DRF throttling classes for rate limiting
"""

from .throttling import AnonymousRateThrottle, CustomUserRateThrottle

__all__ = [
    'AnonymousRateThrottle',
    'CustomUserRateThrottle',
]

# Export UserRateThrottle as alias for backward compatibility
UserRateThrottle = CustomUserRateThrottle