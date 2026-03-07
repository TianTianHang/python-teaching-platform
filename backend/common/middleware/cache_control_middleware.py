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
        if request.path.startswith("/api/"):
            self._add_cache_headers(request, response)

        return response

    def _add_cache_headers(self, request, response):
        """
        Add appropriate Cache-Control headers based on the response content.
        """
        try:
            # Get the view that handled this request
            view_name = self._get_view_name(request)
            view_instance = self._get_view_instance(request)

            # Check if this view uses user-isolated caching
            # If so, disable HTTP caching to prevent stale data and security issues
            if self._is_user_isolated_cache(view_instance, view_name):
                logger.info(f"Disabling HTTP cache for user-isolated view: {view_name}")
                response["Cache-Control"] = (
                    "private, no-store, no-cache, must-revalidate"
                )
                response["Pragma"] = "no-cache"
                response["Expires"] = "0"
                return

            # Check if this is a HEAD request (should be cacheable)
            if request.method == "HEAD":
                response["Cache-Control"] = (
                    "public, max-age=900, stale-while-revalidate=300"
                )
                return

            # For GET requests, check the response content
            if request.method == "GET":
                # 404 responses - cache for short time to prevent penetration
                if response.status_code == 404:
                    response["Cache-Control"] = (
                        "public, max-age=300, stale-while-revalidate=60"
                    )
                    return

                # Empty responses (empty lists, None values) - short cache
                if self._is_empty_response(response):
                    response["Cache-Control"] = (
                        "public, max-age=60, stale-while-revalidate=60"
                    )
                    return

                # Successful API responses - longer cache with stale-while-revalidate
                if response.status_code == 200:
                    # Get TTL from the view or use default
                    ttl = self._get_cache_ttl(view_name)

                    response["Cache-Control"] = (
                        f"public, max-age={ttl}, stale-while-revalidate=300"
                    )

        except Exception as e:
            logger.warning(f"Error adding cache headers: {e}")

    def _get_view_name(self, request):
        """
        Extract the view name from the request path.
        """
        # Extract the view class name from the path
        # e.g., /api/v1/courses/123 -> CourseViewSet
        path_parts = request.path.strip("/").split("/")
        logger.debug(f"Path parts: {path_parts}")

        if len(path_parts) >= 3:
            # Try to get the view class from resolver
            try:
                resolver_match = request.resolver_match
                if resolver_match and hasattr(resolver_match.func, "view_class"):
                    view_class = resolver_match.func.view_class
                    logger.debug(f"Got view class from resolver: {view_class.__name__}")
                    return view_class.__name__
            except Exception as e:
                logger.debug(f"Error getting view from resolver: {e}")

        # Fallback: extract from path
        # Path format: /api/v1/{resource}/...
        # We want the {resource} part to convert to ResourceViewSet
        if len(path_parts) >= 3:
            resource_name = path_parts[2]
            # Remove trailing 's' for plural resources and capitalize
            view_name = resource_name.capitalize().rstrip("s") + "ViewSet"
            logger.debug(f"Extracted view name from path: {view_name}")
            return view_name

        logger.debug(f"Could not determine view name, path_parts: {path_parts}")
        return "Unknown"

    def _get_view_instance(self, request):
        """
        Get the actual view instance from the request.
        Returns None if not available.
        """
        try:
            resolver_match = request.resolver_match
            if resolver_match and hasattr(resolver_match.func, "view_class"):
                # For DRF views, try to get the view instance from the request
                if hasattr(request, "parser_context"):
                    view_instance = request.parser_context.get("view")
                    if view_instance:
                        logger.debug(
                            f"Found view instance: {view_instance.__class__.__name__}"
                        )
                        return view_instance

                # Alternative: try to get from request.drf_router_view if available
                if hasattr(request, "drf_router_view"):
                    return request.drf_router_view
        except Exception as e:
            logger.debug(f"Error getting view instance: {e}")
        return None

    def _is_user_isolated_cache(self, view_instance, view_name):
        """
        Check if the view uses user-isolated caching.

        User-isolated caches should NOT use HTTP caching because:
        1. Each user has different data, so browser caching would show wrong data
        2. Redis cache invalidation won't affect browser cache
        3. Security risk: user might see another user's cached data

        Args:
            view_instance: The DRF view instance
            view_name: The view class name

        Returns:
            bool: True if the view uses user-isolated caching
        """
        # First, check view instance attributes
        if view_instance:
            try:
                # Check if the view uses StandardCacheListMixin with cache_user_isolated=True
                if hasattr(view_instance, "cache_user_isolated"):
                    logger.debug(
                        f"View {view_name} has cache_user_isolated={view_instance.cache_user_isolated}"
                    )
                    return view_instance.cache_user_isolated

                # Check if the view has cache_list_config with user_isolated=True
                if hasattr(view_instance, "cache_list_config"):
                    config = view_instance.cache_list_config
                    if isinstance(config, dict) and config.get("user_isolated"):
                        logger.debug(
                            f"View {view_name} has cache_list_config with user_isolated=True"
                        )
                        return True
            except Exception as e:
                logger.debug(f"Error checking view instance: {e}")

        # Fallback 1: use a whitelist of known user-isolated ViewSet names (singular)
        user_isolated_views = {
            "EnrollmentViewSet",
            "EnrollmentListViewSet",  # Handle plural forms too
            "ChapterProgressViewSet",
            "ProblemProgressViewSet",
            "ExamSubmissionViewSet",
        }

        if view_name in user_isolated_views:
            logger.debug(f"View {view_name} is in user-isolated whitelist")
            return True

        # Fallback 2: check by resource name (from URL path)
        # Extract resource name from view_name
        if view_name.endswith("ViewSet"):
            resource = view_name[:-8].lower()  # Remove "ViewSet" suffix
            logger.debug(f"Extracted resource name: {resource}")

            # Map resource names to user-isolated status
            user_isolated_resources = {
                "enrollment",
                "enrollmentlist",
                "chapterprogress",
                "problemprogress",
                "examsubmission",
            }

            if resource in user_isolated_resources:
                logger.debug(f"Resource '{resource}' is user-isolated")
                return True

        logger.debug(f"View {view_name} is NOT user-isolated")
        return False

    def _is_empty_response(self, response):
        """
        Check if the response contains empty data.
        """
        try:
            if hasattr(response, "data"):
                data = response.data
                return data in ([], {}, None, "")
            elif hasattr(response, "content"):
                # For JSON responses, check if content is empty
                if response.get("Content-Type", "").startswith("application/json"):
                    content = response.content.decode("utf-8")
                    return content.strip() in ("[]", "{}", "null", "")
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
            "CourseViewSet": 900,  # 15 minutes
            "ChapterViewSet": 900,  # 15 minutes
            "ProblemViewSet": 900,  # 15 minutes
            "EnrollmentViewSet": 300,  # 5 minutes (frequently updated)
            "ChapterProgressViewSet": 60,  # 1 minute (frequently updated)
            "ProblemProgressViewSet": 60,  # 1 minute (frequently updated)
            "ExamViewSet": 900,  # 15 minutes
            "ExamSubmissionViewSet": 300,  # 5 minutes
            "FolderViewSet": 900,  # 15 minutes
            "FileEntryViewSet": 300,  # 5 minutes (might change frequently)
        }

        return view_ttl_map.get(view_name, default_ttl)
