"""
Tests for Django signal handlers in the courses app.

This module tests that cache invalidation signals work correctly
when models are created, updated, or deleted.
"""
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from .factories import (
    CourseFactory,
    ChapterFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
)
from .conftest import CoursesTestCase
from common.utils.cache import get_cache_key


class ChapterProgressSignalTestCase(CoursesTestCase):
    """
    Test cases for ChapterProgress signal handler cache invalidation.
    """

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.user = UserFactory()
        self.course = CourseFactory()
        self.chapter = ChapterFactory(course=self.course, order=0)
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _get_cache_keys_for_page(self, page=1):
        """Generate cache keys for a specific page.

        Note: ChapterViewSet is nested under courses, so its cache key
        now includes parent_pks (course_pk) to ensure proper cache isolation
        between different courses.

        Note: All cache keys include user_id to prevent shared caching between users.
        """
        from urllib.parse import urlencode
        from collections import OrderedDict

        # Generate the query param string as get_cache_key does
        query_params = {'page': str(page)}
        sorted_params = OrderedDict(sorted(query_params.items()))
        param_str = urlencode(sorted_params, doseq=True)

        # ChapterViewSet is nested under courses, so include course_pk as parent_pks
        parent_pks = {'course_pk': str(self.course.id)}
        # All cache keys must include user_id to match the actual view behavior
        extra_params = {'user_id': str(self.user.id)}
        chapter_base = get_cache_key(
            prefix='api',
            view_name='ChapterViewSet',
            parent_pks=parent_pks,
            extra_params=extra_params
        )
        chapter_progress_base = get_cache_key(
            prefix='api',
            view_name='ChapterProgressViewSet',
            extra_params=extra_params
        )
        enrollment_base = get_cache_key(
            prefix='api',
            view_name='EnrollmentViewSet',
            extra_params=extra_params
        )

        return (
            f'{chapter_base}:{param_str}',
            f'{chapter_progress_base}:{param_str}',
            f'{enrollment_base}:{param_str}',
        )

    def test_chapter_progress_signal_invalidates_cache_on_create(self):
        """
        Test that creating a ChapterProgress invalidates related caches.
        """
        # First, populate caches by making API requests with explicit page=1
        # 1. Chapter list endpoint
        response1 = self.client.get(f'/api/v1/courses/{self.course.id}/chapters/?page=1')
        self.assertEqual(response1.status_code, 200)
        # 2. ChapterProgress list endpoint (not nested under courses)
        response2 = self.client.get('/api/v1/chapter-progress/?page=1')
        self.assertEqual(response2.status_code, 200)
        # 3. Enrollment list endpoint
        response3 = self.client.get('/api/v1/enrollments/?page=1')
        self.assertEqual(response3.status_code, 200)

        # Generate expected cache keys
        chapter_key, chapter_progress_key, enrollment_key = self._get_cache_keys_for_page()

        # Verify caches exist before creating ChapterProgress
        self.assertIsNotNone(cache.get(chapter_key))
        self.assertIsNotNone(cache.get(chapter_progress_key))
        self.assertIsNotNone(cache.get(enrollment_key))

        # Create a ChapterProgress (should trigger cache invalidation)
        ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter
        )

        # Verify all related caches are invalidated
        self.assertIsNone(cache.get(chapter_key))
        self.assertIsNone(cache.get(chapter_progress_key))
        self.assertIsNone(cache.get(enrollment_key))

    def test_chapter_progress_signal_invalidates_cache_on_update(self):
        """
        Test that updating a ChapterProgress invalidates related caches.
        """
        # Create a ChapterProgress
        chapter_progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter,
            completed=False
        )

        # Populate caches by making API requests with explicit page=1
        response1 = self.client.get(f'/api/v1/courses/{self.course.id}/chapters/?page=1')
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.get('/api/v1/chapter-progress/?page=1')
        self.assertEqual(response2.status_code, 200)
        response3 = self.client.get('/api/v1/enrollments/?page=1')
        self.assertEqual(response3.status_code, 200)

        # Generate expected cache keys
        chapter_key, chapter_progress_key, enrollment_key = self._get_cache_keys_for_page()

        # Verify caches exist
        self.assertIsNotNone(cache.get(chapter_key))
        self.assertIsNotNone(cache.get(chapter_progress_key))
        self.assertIsNotNone(cache.get(enrollment_key))

        # Update the ChapterProgress (mark as completed)
        chapter_progress.completed = True
        from django.utils import timezone
        chapter_progress.completed_at = timezone.now()
        chapter_progress.save()

        # Verify all related caches are invalidated
        self.assertIsNone(cache.get(chapter_key))
        self.assertIsNone(cache.get(chapter_progress_key))
        self.assertIsNone(cache.get(enrollment_key))

    def test_chapter_progress_signal_invalidates_cache_on_delete(self):
        """
        Test that deleting a ChapterProgress invalidates related caches.
        """
        # Create a ChapterProgress
        chapter_progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter
        )

        # Populate caches by making API requests
        response1 = self.client.get(f'/api/v1/courses/{self.course.id}/chapters/?page=1')
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.get('/api/v1/chapter-progress/?page=1')
        self.assertEqual(response2.status_code, 200)
        response3 = self.client.get('/api/v1/enrollments/?page=1')
        self.assertEqual(response3.status_code, 200)

        # Generate expected cache keys
        chapter_key, chapter_progress_key, enrollment_key = self._get_cache_keys_for_page()

        # Verify caches exist
        self.assertIsNotNone(cache.get(chapter_key))
        self.assertIsNotNone(cache.get(chapter_progress_key))
        self.assertIsNotNone(cache.get(enrollment_key))

        # Delete the ChapterProgress
        chapter_progress.delete()

        # Verify all related caches are invalidated
        self.assertIsNone(cache.get(chapter_key))
        self.assertIsNone(cache.get(chapter_progress_key))
        self.assertIsNone(cache.get(enrollment_key))

    def test_mark_as_completed_invalidates_cache(self):
        """
        Test that calling the mark_as_completed API invalidates cache
        and returns the updated completed status.
        """
        # First, populate caches by making API requests
        chapter_list_response = self.client.get(f'/api/v1/courses/{self.course.id}/chapters/?page=1')
        self.assertEqual(chapter_list_response.status_code, 200)

        chapter_progress_list_response = self.client.get('/api/v1/chapter-progress/?page=1')
        self.assertEqual(chapter_progress_list_response.status_code, 200)

        enrollment_list_response = self.client.get('/api/v1/enrollments/?page=1')
        self.assertEqual(enrollment_list_response.status_code, 200)

        # Generate expected cache keys
        chapter_key, chapter_progress_key, enrollment_key = self._get_cache_keys_for_page()

        # Verify caches exist before calling mark_as_completed
        self.assertIsNotNone(cache.get(chapter_key))
        self.assertIsNotNone(cache.get(chapter_progress_key))
        self.assertIsNotNone(cache.get(enrollment_key))

        # Call the mark_as_completed API
        response = self.client.post(
            f'/api/v1/courses/{self.course.id}/chapters/{self.chapter.id}/mark_as_completed/',
            {'completed': True}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['completed'])

        # Verify all related caches are invalidated
        self.assertIsNone(cache.get(chapter_key))
        self.assertIsNone(cache.get(chapter_progress_key))
        self.assertIsNone(cache.get(enrollment_key))

        # Verify that subsequent API call returns completed status
        chapter_detail_response = self.client.get(
            f'/api/v1/courses/{self.course.id}/chapters/{self.chapter.id}/'
        )
        self.assertEqual(chapter_detail_response.status_code, 200)
        self.assertIsNotNone(chapter_detail_response.data)

        # Verify ChapterProgress was created/updated
        chapter_progress = ChapterProgressFactory._meta.model.objects.get(
            enrollment=self.enrollment,
            chapter=self.chapter
        )
        self.assertTrue(chapter_progress.completed)

    def test_chapter_progress_cache_invalidation_consistency_with_problem_progress(self):
        """
        Test that ChapterProgress signal follows the same pattern as ProblemProgress
        and ensures cache keys are constructed correctly.
        """
        from courses.signals import invalidate_chapter_progress_cache, invalidate_problem_progress_cache
        from courses.views import ChapterViewSet, ChapterProgressViewSet, EnrollmentViewSet, ProblemViewSet
        import inspect

        # Verify that ChapterProgress signal handler exists and has the same signature
        self.assertIsNotNone(invalidate_chapter_progress_cache)

        # Check that both signal handlers use the same decorator pattern
        chapter_progress_sig = inspect.signature(invalidate_chapter_progress_cache)
        problem_progress_sig = inspect.signature(invalidate_problem_progress_cache)

        # Both should have the same parameters: sender, instance, **kwargs
        chapter_params = list(chapter_progress_sig.parameters.keys())

        self.assertEqual(set(chapter_params), {'sender', 'instance', 'kwargs'})

        # Verify cache key construction is consistent
        chapter_cache_key = get_cache_key(
            prefix=ChapterViewSet.cache_prefix,
            view_name=ChapterViewSet.__name__
        )
        chapter_progress_cache_key = get_cache_key(
            prefix=ChapterProgressViewSet.cache_prefix,
            view_name=ChapterProgressViewSet.__name__
        )
        enrollment_cache_key = get_cache_key(
            prefix=EnrollmentViewSet.cache_prefix,
            view_name=EnrollmentViewSet.__name__
        )

        # All cache keys should start with the same prefix
        self.assertTrue(chapter_cache_key.startswith('api:'))
        self.assertTrue(chapter_progress_cache_key.startswith('api:'))
        self.assertTrue(enrollment_cache_key.startswith('api:'))

        # Verify ViewSet names are correctly included
        self.assertIn('ChapterViewSet', chapter_cache_key)
        self.assertIn('ChapterProgressViewSet', chapter_progress_cache_key)
        self.assertIn('EnrollmentViewSet', enrollment_cache_key)

        # Verify the pattern matches ProblemProgress cache key construction
        problem_cache_key = get_cache_key(
            prefix=ProblemViewSet.cache_prefix,
            view_name=ProblemViewSet.__name__
        )
        self.assertTrue(problem_cache_key.startswith('api:'))
        self.assertIn('ProblemViewSet', problem_cache_key)
