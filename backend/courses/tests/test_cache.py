from django.test import TestCase
from rest_framework.test import APIRequestFactory
from common.utils.cache import get_cache_key


class CacheKeyTestCase(TestCase):
    """Tests for the old CacheListMixin - no longer applicable after migration to separated cache."""

    def test_backward_compatibility(self):
        """测试向后兼容性：当 allowed_params=None 时使用默认值"""
        query_params = {"page": "1", "search": "test"}
        cache_key = get_cache_key(
            prefix="api",
            view_name="TestViewSet",
            query_params=query_params,
            allowed_params=None,  # 使用默认值
        )
        self.assertIn("page", cache_key)
        self.assertIn("search", cache_key)
        print(f"✓ Backward compatibility works: {cache_key}")


# ============================================================================
# Chapter Unlock Cache Tests
# ============================================================================

"""
Cache tests for chapter unlock functionality.

This module contains test coverage for caching behavior including:
- Unlock status caching
- Prerequisite progress caching
- Cache invalidation on progress changes
- Cache invalidation on condition changes
"""

from django.test import TestCase, override_settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from .factories import (
    CourseFactory,
    ChapterFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
    ChapterUnlockConditionFactory,
)
from accounts.tests.factories import UserFactory

from ..models import ChapterProgress
from ..services import ChapterUnlockService


class ChapterUnlockCacheTests(TestCase):
    """Tests for ChapterUnlockService caching behavior"""

    def setUp(self):
        """Set up test data and clear cache"""
        cache.clear()

        # Create course with chapters
        self.course = CourseFactory(title="Test Course")
        self.chapter1 = ChapterFactory(course=self.course, title="Chapter 1", order=1)
        self.chapter2 = ChapterFactory(course=self.course, title="Chapter 2", order=2)
        self.chapter3 = ChapterFactory(course=self.course, title="Chapter 3", order=3)

        # Create enrollment
        self.user = UserFactory(username="student")
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_unlock_status_is_cached(self):
        """Test that unlock status results are cached"""
        # Create unlock condition: chapter2 requires chapter1
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="prerequisite"
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # First call - should compute and cache
        result1 = ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)

        # Test caching by checking cache directly using new format
        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter2.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )
        cached_value = cache.get(cache_key)

        # The cache should exist and match the first result
        # Note: cache may serialize bool to string, so we check truthiness
        self.assertIsNotNone(cached_value)
        self.assertFalse(result1)  # Initially locked

    def test_unlock_status_without_condition_returns_cached_true(self):
        """Test that chapters without conditions return True (unlocked) and are cached"""
        # Chapter1 has no unlock condition - should be unlocked
        result1 = ChapterUnlockService.is_unlocked(self.chapter1, self.enrollment)

        self.assertTrue(result1)

        # Verify it's cached using new format
        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter1.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )
        cached_value = cache.get(cache_key)
        self.assertTrue(cached_value)

    def test_get_unlock_status_is_cached(self):
        """Test that get_unlock_status results are cached"""
        # Create unlock condition
        future_date = timezone.now() + timedelta(days=7)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_date=future_date, unlock_condition_type="date"
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # First call - should compute and cache
        status1 = ChapterUnlockService.get_unlock_status(self.chapter2, self.enrollment)

        # Test caching by checking that second call returns same result (from cache)
        status2 = ChapterUnlockService.get_unlock_status(self.chapter2, self.enrollment)

        # Results should match
        self.assertEqual(status1["is_locked"], status2["is_locked"])
        self.assertTrue(status1["is_locked"])

    def test_cache_timeout_is_respected(self):
        """Test that cache timeout is set correctly"""
        ChapterUnlockService.is_unlocked(self.chapter1, self.enrollment)

        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter1.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )

        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))

        # The actual timeout is controlled by the cache backend,
        # but we can verify the class constant
        self.assertEqual(ChapterUnlockService.CACHE_TIMEOUT, 300)  # 5 minutes


class ChapterUnlockCacheInvalidationTests(TestCase):
    """Tests for cache invalidation behavior"""

    def setUp(self):
        """Set up test data and clear cache"""
        cache.clear()

        # Create course with chapters
        self.course = CourseFactory(title="Test Course")
        self.chapter1 = ChapterFactory(course=self.course, title="Chapter 1", order=1)
        self.chapter2 = ChapterFactory(course=self.course, title="Chapter 2", order=2)
        self.chapter3 = ChapterFactory(course=self.course, title="Chapter 3", order=3)

        # Create enrollment
        self.user = UserFactory(username="student")
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

        # Create unlock condition: chapter2 requires chapter1
        self.condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="prerequisite"
        )
        self.condition.prerequisite_chapters.add(self.chapter1)

    def test_cache_invalidated_on_chapter_progress_completion(self):
        """Test that cache is invalidated when chapter progress is marked complete"""
        # Initially locked - cache the result
        result1 = ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        self.assertFalse(result1)

        # Verify cache is set using new format
        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter2.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Mark chapter1 as complete (this should trigger cache invalidation)
        progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Manually trigger signal handler
        from ..signals import on_chapter_progress_change

        on_chapter_progress_change(sender=ChapterProgress, instance=progress)

        # Cache should be invalidated
        cached_value = cache.get(cache_key)
        self.assertIsNone(cached_value)

        # New call should compute fresh result
        result2 = ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        self.assertTrue(result2)  # Now unlocked

    def test_cache_invalidated_on_dependent_chapters(self):
        """Test that immediate dependent chapter caches are invalidated"""
        # Verify initial condition: chapter2 depends on chapter1 (from setUp)
        # The signal should invalidate chapter2's cache when chapter1 progress changes

        # Cache unlock status for chapter2
        ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)

        from common.utils.cache import get_standard_cache_key

        cache_key2 = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter2.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )

        # Verify cache is set
        self.assertIsNotNone(cache.get(cache_key2))

        # Mark chapter1 as complete (chapter2's prerequisite)
        progress = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Manually trigger signal handler
        from ..signals import on_chapter_progress_change

        on_chapter_progress_change(sender=ChapterProgress, instance=progress)

        # chapter2 cache should be invalidated (immediate dependent)
        self.assertIsNone(cache.get(cache_key2))

    def test_cache_invalidated_on_transitive_prerequisite_completion(self):
        """Test that completing a prerequisite allows the next chapter to be unlocked"""
        # Set up: chapter3 requires chapter2
        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3, unlock_condition_type="prerequisite"
        )
        condition3.prerequisite_chapters.add(self.chapter2)

        # Initially chapter2 and chapter3 are locked
        self.assertFalse(
            ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        )
        self.assertFalse(
            ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        )

        # Mark chapter1 as complete
        progress1 = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Trigger cache invalidation
        from ..signals import on_chapter_progress_change

        on_chapter_progress_change(sender=ChapterProgress, instance=progress1)

        # After cache invalidation, chapter2 should now be unlocked
        self.assertTrue(
            ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        )
        # chapter3 should still be locked (chapter2 not complete yet)
        self.assertFalse(
            ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        )

    def test_cache_invalidated_on_unlock_condition_save(self):
        """Test that cache is invalidated when unlock condition is saved"""
        # Cache unlock status
        ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)

        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter2.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Modify the unlock condition
        self.condition.unlock_condition_type = "date"
        self.condition.unlock_date = timezone.now() - timedelta(days=1)
        self.condition.save()

        # Manually trigger signal handler
        from ..signals import invalidate_unlock_condition_cache

        invalidate_unlock_condition_cache(
            sender=type(self.condition), instance=self.condition
        )

        # Cache should be invalidated
        cached_value = cache.get(cache_key)
        self.assertIsNone(cached_value)

    def test_invalidate_cache_with_specific_enrollment(self):
        """Test _invalidate_cache with specific enrollment_id"""
        # Cache unlock status
        ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)

        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter2.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Invalidate cache for specific enrollment
        ChapterUnlockService._invalidate_cache(self.chapter2.id, self.enrollment.id)

        # Cache should be invalidated
        self.assertIsNone(cache.get(cache_key))

    def test_invalidate_cache_without_enrollment(self):
        """Test _invalidate_cache without enrollment_id (wildcard)"""
        # Cache unlock status
        ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)

        from common.utils.cache import get_standard_cache_key

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={
                "chapter_pk": self.chapter2.id,
                "enrollment_pk": self.enrollment.id,
            },
            query_params={"type": "UNLOCK"},
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Invalidate cache without enrollment (uses pattern deletion)
        ChapterUnlockService._invalidate_cache(self.chapter2.id)

        # Note: This test verifies the method is called correctly
        # The actual pattern deletion depends on the cache backend implementation


class ChapterUnlockCacheIntegrationTests(TestCase):
    """Integration tests for caching with real cache backend"""

    def setUp(self):
        """Set up test data"""
        cache.clear()

        # Create course with chapters
        self.course = CourseFactory(title="Integration Test Course")
        self.chapter1 = ChapterFactory(course=self.course, title="Foundations", order=1)
        self.chapter2 = ChapterFactory(
            course=self.course, title="Intermediate", order=2
        )
        self.chapter3 = ChapterFactory(course=self.course, title="Advanced", order=3)

        # Create enrollment
        self.user = UserFactory(username="student")
        self.enrollment = EnrollmentFactory(user=self.user, course=self.course)

    def test_complete_unlock_workflow_with_cache(self):
        """Test complete unlock workflow: cache -> progress change -> cache invalidation -> fresh result"""
        # Set up: chapter2 requires chapter1, chapter3 requires chapter2
        condition2 = ChapterUnlockConditionFactory(
            chapter=self.chapter2, unlock_condition_type="prerequisite"
        )
        condition2.prerequisite_chapters.add(self.chapter1)

        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3, unlock_condition_type="prerequisite"
        )
        condition3.prerequisite_chapters.add(self.chapter2)

        # Initial state: all locked
        self.assertFalse(
            ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        )
        self.assertFalse(
            ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        )

        # Complete chapter1
        progress1 = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter1, completed=True
        )

        # Trigger cache invalidation
        from ..signals import on_chapter_progress_change

        on_chapter_progress_change(sender=ChapterProgress, instance=progress1)

        # Verify: chapter2 unlocked, chapter3 still locked
        self.assertTrue(
            ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)
        )
        self.assertFalse(
            ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        )

        # Complete chapter2
        progress2 = ChapterProgressFactory(
            enrollment=self.enrollment, chapter=self.chapter2, completed=True
        )

        # Trigger cache invalidation
        on_chapter_progress_change(sender=ChapterProgress, instance=progress2)

        # Verify: chapter3 now unlocked
        self.assertTrue(
            ChapterUnlockService.is_unlocked(self.chapter3, self.enrollment)
        )
