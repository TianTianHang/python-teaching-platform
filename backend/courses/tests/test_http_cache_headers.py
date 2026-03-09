"""
Test HTTP caching behavior for user-isolated caches.

This test verifies that views using user-isolated caching (like EnrollmentViewSet)
do NOT use HTTP caching, to prevent stale data and security issues.
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from courses.models import Course, Enrollment

User = get_user_model()


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
    """Test HTTP cache headers for user-isolated caches"""

    def setUp(self):
        """Create test data"""
        self.client = APIClient()
        # Use a unique username to avoid conflicts with existing test data
        import uuid

        self.user = User.objects.create_user(
            username=f"testuser_{uuid.uuid4().hex[:8]}", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create a course
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
        )

    def test_user_isolated_cache_has_no_cache_headers(self):
        """
        Test that user-isolated caches (EnrollmentViewSet) do NOT use HTTP caching.

        This is critical because:
        1. Each user has different data
        2. Browser caching would prevent Redis cache invalidation from working
        3. Security risk: user might see another user's cached data
        """
        # First request - should get empty list
        response = self.client.get("/api/v1/enrollments/")

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)

        # Check Cache-Control header
        cache_control = response.get("Cache-Control", "")
        print(f"EnrollmentViewSet Cache-Control: {cache_control}")

        # Should NOT allow public caching
        self.assertNotIn("public", cache_control.lower())

        # Should include no-store or no-cache
        self.assertIn("no-store", cache_control.lower())
        self.assertIn("no-cache", cache_control.lower())

        # Should include must-revalidate
        self.assertIn("must-revalidate", cache_control.lower())

        # Check for Pragma: no-cache (HTTP/1.0 fallback)
        pragma = response.get("Pragma", "")
        self.assertEqual(pragma, "no-cache")

    def test_non_user_isolated_cache_has_http_caching(self):
        """
        Test that non-user-isolated caches (CourseViewSet) DO use HTTP caching.
        """
        # Request courses list (not user-isolated)
        response = self.client.get("/api/v1/courses/")

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)

        # Check Cache-Control header
        cache_control = response.get("Cache-Control", "")
        print(f"CourseViewSet Cache-Control: {cache_control}")

        # Should allow public caching
        self.assertIn("public", cache_control.lower())

        # Should include max-age
        self.assertIn("max-age=", cache_control.lower())

        # Should include stale-while-revalidate
        self.assertIn("stale-while-revalidate", cache_control.lower())

    def test_enrollment_after_create_invalidates_cache(self):
        """
        End-to-end test: Verify that enrolling in a course updates the enrollment list.

        This test verifies the complete fix:
        1. Create an enrollment via POST /api/v1/courses/{id}/enroll/
        2. GET /api/v1/enrollments/ should return the new enrollment
        3. This works because:
           - Redis cache is invalidated (signals.py)
           - HTTP caching is disabled (CacheControlMiddleware)
        """
        # Step 1: Get initial enrollment count
        response = self.client.get("/api/v1/enrollments/")
        self.assertEqual(response.status_code, 200)
        initial_count = len(response.data["results"])

        # Step 2: Enroll in the course
        response = self.client.post(f"/api/v1/courses/{self.course.id}/enroll/")
        self.assertEqual(response.status_code, 201)

        # Step 3: Check enrollments again
        # Since HTTP caching is disabled, this should fetch fresh data from Redis/DB
        response = self.client.get("/api/v1/enrollments/")
        self.assertEqual(response.status_code, 200)

        # Should have 1 more enrollment now
        final_count = len(response.data["results"])
        self.assertEqual(final_count, initial_count + 1)

        # Should have 1 enrollment now
        final_count = len(response.data["results"])
        self.assertEqual(final_count, 1)

        # Verify it's the correct enrollment
        enrollment_data = response.data["results"][0]
        self.assertEqual(enrollment_data["course"], self.course.id)
        self.assertEqual(enrollment_data["user"], self.user.id)

    def test_http_caching_headers_for_different_status_codes(self):
        """Test HTTP caching headers for different response types"""
        # Test filter by valid course that has no enrollments - should return 200 with empty list
        response = self.client.get(f"/api/v1/enrollments/?course={self.course.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

        # Check that empty responses still disable HTTP caching for user-isolated views
        cache_control = response.get("Cache-Control", "")
        self.assertIn("no-store", cache_control.lower())
