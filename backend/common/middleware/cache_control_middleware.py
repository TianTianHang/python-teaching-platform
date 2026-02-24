"""
Custom middleware to add Cache-Control headers to API responses.

This middleware adds appropriate Cache-Control headers based on the response:
- For cacheable API responses: add stale-while-revalidate and max-age
- For empty/null responses: add short max-age
- For 404 responses: add short max-age to prevent cache penetration
"""

import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class CacheControlMiddleware:
    """
    Middleware to add Cache-Control headers to responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only apply to API responses
        if request.path.startswith('/api/'):
            self._add_cache_headers(request, response)

        return response

    def _add_cache_headers(self, request, response):
        """
        Add appropriate Cache-Control headers based on the response content.
        """
        try:
            # Get the view that handled this request
            view_name = self._get_view_name(request)

            # Check if this is a HEAD request (should be cacheable)
            if request.method == 'HEAD':
                response['Cache-Control'] = 'public, max-age=900, stale-while-revalidate=300'
                return

            # For GET requests, check the response content
            if request.method == 'GET':
                # 404 responses - cache for short time to prevent penetration
                if response.status_code == 404:
                    response['Cache-Control'] = 'public, max-age=300, stale-while-revalidate=60'
                    return

                # Empty responses (empty lists, None values) - short cache
                if self._is_empty_response(response):
                    response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=60'
                    return

                # Successful API responses - longer cache with stale-while-revalidate
                if response.status_code == 200:
                    # Get TTL from the view or use default
                    ttl = self._get_cache_ttl(view_name)

                    response['Cache-Control'] = (
                        f'public, max-age={ttl}, stale-while-revalidate=300'
                    )

        except Exception as e:
            logger.warning(f"Error adding cache headers: {e}")

    def _get_view_name(self, request):
        """
        Extract the view name from the request path.
        """
        # Extract the view class name from the path
        # e.g., /api/v1/courses/123 -> CourseViewSet
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 3:
            # Try to get the view class from resolver
            try:
                resolver_match = request.resolver_match
                if resolver_match and hasattr(resolver_match.func, 'view_class'):
                    view_class = resolver_match.func.view_class
                    return view_class.__name__
            except Exception:
                pass

        # Fallback: extract from path
        if len(path_parts) >= 2:
            return path_parts[1].capitalize() + 'ViewSet'

        return 'Unknown'

    def _is_empty_response(self, response):
        """
        Check if the response contains empty data.
        """
        try:
            if hasattr(response, 'data'):
                data = response.data
                return data in ([], {}, None, '')
            elif hasattr(response, 'content'):
                # For JSON responses, check if content is empty
                if response.get('Content-Type', '').startswith('application/json'):
                    content = response.content.decode('utf-8')
                    return content.strip() in ('[]', '{}', 'null', '')
            return False
        except Exception:
            return False

    def _get_cache_ttl(self, view_name):
        """
        Get cache TTL for a specific view.
        """
        # Default TTL
        default_ttl = 900  # 15 minutes

        # View-specific TTL overrides
        view_ttl_map = {
            'CourseViewSet': 900,      # 15 minutes
            'ChapterViewSet': 900,     # 15 minutes
            'ProblemViewSet': 900,     # 15 minutes
            'EnrollmentViewSet': 300,  # 5 minutes (frequently updated)
            'ChapterProgressViewSet': 60,  # 1 minute (frequently updated)
            'ProblemProgressViewSet': 60,  # 1 minute (frequently updated)
            'ExamViewSet': 900,        # 15 minutes
            'ExamSubmissionViewSet': 300,  # 5 minutes
            'FolderViewSet': 900,      # 15 minutes
            'FileEntryViewSet': 300,   # 5 minutes (might change frequently)
        }

        return view_ttl_map.get(view_name, default_ttl)