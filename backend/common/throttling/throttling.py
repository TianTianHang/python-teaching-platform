"""
Custom DRF throttling classes for API rate limiting
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django_redis import get_redis_connection
from datetime import datetime, timedelta
import logging

# Default cache timeout for throttling (in seconds)
DEFAULT_CACHE_TIMEOUT = 300

logger = logging.getLogger(__name__)


class AnonymousRateThrottle(AnonRateThrottle):
    """
    Rate throttle for anonymous users.

    Uses cache to track request rates. Default is 100 requests per hour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set a higher rate for anonymous users in case of cache penetration attempts
        self.rate = getattr(self, 'rate', '100/hour')

    def get_cache_key(self, request, view):
        """
        Generate unique cache key for anonymous users.
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None  # This throttle only applies to anonymous users

        # Use remote address as identifier
        ident = self.get_ident(request)

        # Add endpoint-specific key to prevent attacker bypassing limits
        view_name = getattr(view, '__class__.__name__', 'unknown')

        # Create a more specific cache key
        return f'anonymous_throttle:{view_name}:{ident}'

    def allow_request(self, request, view):
        """
        Check if the request should be allowed.
        Override to add cache penetration protection.
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Allow authenticated users to bypass anonymous throttle
            return True

        # Check for potential cache penetration attacks
        if self._is_cache_penetration_attempt(request, view):
            logger.warning(f"Potential cache penetration attempt: {self.get_ident(request)}")
            return False

        return super().allow_request(request, view)

    def _is_cache_penetration_attempt(self, request, view):
        """
        Detect potential cache penetration attempts.

        Returns True if request appears to be probing for non-existent resources.
        """
        try:
            # Get the current rate limit
            throttle_rate = getattr(self, 'rate', '100/hour')

            # Extract rate from string (e.g., '100/hour' -> 100 requests, timedelta(3600))
            if '/' in throttle_rate:
                num_requests, period = throttle_rate.split('/')
                num_requests = int(num_requests)

                if period == 'hour':
                    duration = timedelta(hours=1)
                elif period == 'minute':
                    duration = timedelta(minutes=1)
                elif period == 'second':
                    duration = timedelta(seconds=1)
                else:
                    return False

                # Create time window
                now = datetime.now()
                start_time = now - duration
                cache_key = f'penetration_check:{self.get_ident(request)}:{getattr(view, "__class__.__name__", "unknown")}'

                # Get current request count in this window
                current_count = cache.get(cache_key, 0)

                # Increment counter
                cache.set(cache_key, current_count + 1, duration.total_seconds())

                # If we're getting close to the limit, flag as potential attack
                return current_count > num_requests * 0.8

        except Exception as e:
            logger.warning(f"Error checking cache penetration: {e}")

        return False


class CustomUserRateThrottle(UserRateThrottle):
    """
    Rate throttle for authenticated users.

    Uses user ID for tracking. Default is 1000 requests per hour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set a higher rate for authenticated users
        self.rate = getattr(self, 'rate', '1000/hour')

    def get_cache_key(self, request, view):
        """
        Generate unique cache key for authenticated users.
        """
        if not request.user.is_authenticated:
            return None

        user_id = request.user.id
        view_name = getattr(view, '__class__.__name__', 'unknown')

        # Create cache key with user ID and view
        return f'user_throttle:{view_name}:{user_id}'


class BurstRateThrottle(AnonymousRateThrottle):
    """
    Burst rate throttle for protecting against sudden spikes.

    Allows short bursts of requests but limits average rate.
    """
    THROTTLE_RATES = {
        'burst_anon': '20/minute',    # 20 requests per minute for burst
        'burst_user': '100/minute',   # 100 requests per minute for authenticated users
    }

    def get_cache_key(self, request, view):
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f'burst_throttle:user:{request.user.id}'
        ident = self.get_ident(request)
        return f'burst_throttle:anon:{ident}'


class SlowRequestThrottle(AnonRateThrottle):
    """
    Throttle that limits the rate of slow requests.

    Helps prevent resource exhaustion attacks where clients send very slow requests.
    """
    THROTTLE_RATES = {
        'slow': '10/minute',  # Only 10 slow requests per minute
    }

    def allow_request(self, request, view):
        """
        Add custom header check for slow requests.
        """
        # Look for header indicating slow client
        if request.META.get('HTTP_X_SLOW_REQUEST', '').lower() == 'true':
            # This is a slow request, apply stricter limits
            return super(AnonymousRateThrottle, self).allow_request(request, view)

        return True


class APIKeyThrottle(AnonymousRateThrottle):
    """
    Throttle for API key based authentication.

    For APIs that use API keys instead of authentication.
    """
    THROTTLE_RATES = {
        'api_key': '500/hour',
    }

    def get_cache_key(self, request, view):
        """
        Get API key from request.
        """
        # Try to get API key from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
            return f'api_key_throttle:{api_key}'

        # Try to get API key from query parameters
        api_key = request.GET.get('api_key')
        if api_key:
            return f'api_key_throttle:{api_key}'

        # No API key, use remote address
        ident = self.get_ident(request)
        return f'api_key_throttle:anon:{ident}'


# Custom exception response
class ThrottleExceptionResponse(Response):
    """
    Custom throttle response with helpful error message.
    """

    def __init__(self, detail=None):
        detail = detail or {
            'error': 'Rate limit exceeded',
            'detail': 'You have made too many requests. Please try again later.',
            'retry_after': getattr(self, 'wait', 60)
        }
        super().__init__(detail, status=status.HTTP_429_TOO_MANY_REQUESTS)


# View-level throttling decorators
def throttle_view(rate):
    """
    Decorator to throttle a specific view with a custom rate.

    Args:
        rate (str): Rate limit string (e.g., '10/minute', '100/hour')
    """
    from rest_framework.throttling import SimpleRateThrottle

    class ViewThrottle(SimpleRateThrottle):
        rate = rate
        scope = 'view_throttle'

        def get_cache_key(self, request, view):
            if hasattr(request, 'user') and request.user.is_authenticated:
                return f'view_throttle:user:{request.user.id}'
            ident = self.get_ident(request)
            return f'view_throttle:anon:{ident}'

    def decorator(view_func):
        def wrapper(*args, **kwargs):
            request = args[0]
            throttle = ViewThrottle()
            if not throttle.allow_request(request, view_func):
                return ThrottleExceptionResponse()
            return view_func(*args, **kwargs)
        return wrapper

    return decorator


# Helper function to check if request is being throttled
def is_throttled(request):
    """
    Check if a request is currently being throttled.

    Returns:
        tuple: (bool, str) - (is_throttled, reason)
    """
    try:
        # Check anonymous throttle
        anon_throttle = AnonymousRateThrottle()
        if anon_throttle.get_cache_key(request) and not anon_throttle.allow_request(request, None):
            return True, "Anonymous rate limit exceeded"

        # Check user throttle
        user_throttle = UserRateThrottle()
        if user_throttle.get_cache_key(request) and not user_throttle.allow_request(request, None):
            return True, "User rate limit exceeded"

        return False, None

    except Exception as e:
        logger.warning(f"Error checking throttling: {e}")
        return False, None


# Get current rate limit status
def get_rate_limit_status(request):
    """
    Get the current rate limit status for a request.

    Returns:
        dict: {
            'is_throttled': bool,
            'type': str,
            'remaining': int,
            'reset': timestamp
        }
    """
    result = {
        'is_throttled': False,
        'type': None,
        'remaining': 0,
        'reset': None
    }

    try:
        # Check anonymous throttle
        anon_throttle = AnonymousRateThrottle()
        if anon_throttle.get_cache_key(request):
            anon_cache_key = anon_throttle.get_cache_key(request)
            current_count = cache.get(anon_cache_key, 0)
            result.update({
                'is_throttled': current_count > 0,
                'type': 'anonymous',
                'remaining': max(0, 100 - current_count)  # Assuming 100/hour
            })

        # Check user throttle
        user_throttle = UserRateThrottle()
        if user_throttle.get_cache_key(request):
            user_cache_key = user_throttle.get_cache_key(request)
            current_count = cache.get(user_cache_key, 0)
            result.update({
                'is_throttled': current_count > 0,
                'type': 'user',
                'remaining': max(0, 1000 - current_count)  # Assuming 1000/hour
            })

    except Exception as e:
        logger.warning(f"Error getting rate limit status: {e}")

    return result