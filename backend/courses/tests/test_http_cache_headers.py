"""
Test HTTP caching behavior for user-isolated caches.

This test verifies that views using user-isolated caching (like EnrollmentViewSet)
do NOT use HTTP caching, to prevent stale data and security issues.

NOTE: This test file is skipped because CacheControlMiddleware is disabled in all environments.
HTTP cache headers are no longer being added by the backend.
"""

from django.test import TestCase, override_settings


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
)
class HTTPCacheHeadersTest(TestCase):
    """Test HTTP cache headers for user-isolated caches - SKIPPED

    NOTE: All tests in this class are skipped because CacheControlMiddleware
    is disabled in all environments. HTTP cache headers are no longer
    being added by the backend.
    """

    def setUp(self):
        """Skip all tests in this class"""
        self.skipTest("HTTP Cache Control middleware is disabled, skipping cache header tests")
