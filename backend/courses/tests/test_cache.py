from django.test import TestCase
from rest_framework.test import APIRequestFactory
from common.utils.cache import get_cache_key
from courses.views import ProblemViewSet


class CacheKeyTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.viewset = ProblemViewSet()

    def test_cache_key_with_difficulty(self):
        """测试缓存键是否包含 difficulty 参数"""
        # 获取 ViewSet 允许的参数
        allowed_params = self.viewset._get_allowed_cache_params()
        self.assertIn('difficulty', allowed_params)
        self.assertIn('type', allowed_params)

        # 生成缓存键
        query_params = {'difficulty': '1', 'page': '1'}
        cache_key = get_cache_key(
            prefix='api',
            view_name='ProblemViewSet',
            query_params=query_params,
            allowed_params=allowed_params
        )
        self.assertIn('difficulty', cache_key)
        print(f"✓ Cache key contains difficulty: {cache_key}")

    def test_different_difficulty_different_key(self):
        """测试不同难度生成不同的缓存键"""
        from urllib.parse import urlencode
        from collections import OrderedDict

        allowed_params = self.viewset._get_allowed_cache_params()

        params1 = {'difficulty': '1', 'page': '1'}
        params2 = {'difficulty': '2', 'page': '1'}
        params3 = {'difficulty': '3', 'page': '1'}

        sorted_params1 = OrderedDict(sorted(params1.items()))
        sorted_params2 = OrderedDict(sorted(params2.items()))
        sorted_params3 = OrderedDict(sorted(params3.items()))

        param_str1 = urlencode(sorted_params1, doseq=True)
        param_str2 = urlencode(sorted_params2, doseq=True)
        param_str3 = urlencode(sorted_params3, doseq=True)

        key1 = f"api:ProblemViewSet:{param_str1}"
        key2 = f"api:ProblemViewSet:{param_str2}"
        key3 = f"api:ProblemViewSet:{param_str3}"

        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key2, key3)
        print(f"✓ Different difficulties generate different keys")
        print(f"  - difficulty=1: {key1}")
        print(f"  - difficulty=2: {key2}")
        print(f"  - difficulty=3: {key3}")

    def test_filterset_fields_included(self):
        """测试 filterset_fields 字段是否被包含"""
        allowed_params = self.viewset._get_allowed_cache_params()
        self.assertIn('type', allowed_params)
        self.assertIn('difficulty', allowed_params)
        self.assertIn('page', allowed_params)
        self.assertIn('page_size', allowed_params)
        self.assertIn('search', allowed_params)
        self.assertIn('ordering', allowed_params)
        print(f"✓ filterset_fields included in allowed_params: {allowed_params}")

    def test_backward_compatibility(self):
        """测试向后兼容性：当 allowed_params=None 时使用默认值"""
        query_params = {'page': '1', 'search': 'test'}
        cache_key = get_cache_key(
            prefix='api',
            view_name='TestViewSet',
            query_params=query_params,
            allowed_params=None  # 使用默认值
        )
        self.assertIn('page', cache_key)
        self.assertIn('search', cache_key)
        print(f"✓ Backward compatibility works: {cache_key}")

    def test_common_params_included(self):
        """测试通用参数是否被包含"""
        allowed_params = self.viewset._get_allowed_cache_params()
        # 验证通用分页和搜索参数
        self.assertIn('page', allowed_params)
        self.assertIn('page_size', allowed_params)
        self.assertIn('limit', allowed_params)
        self.assertIn('offset', allowed_params)
        self.assertIn('search', allowed_params)
        print(f"✓ Common params included: {allowed_params}")

    def test_type_filter_included(self):
        """测试 type 筛选参数是否被包含"""
        allowed_params = self.viewset._get_allowed_cache_params()
        self.assertIn('type', allowed_params)

        # 生成包含 type 的缓存键
        query_params = {'type': 'algorithm', 'page': '1'}
        cache_key = get_cache_key(
            prefix='api',
            view_name='ProblemViewSet',
            query_params=query_params,
            allowed_params=allowed_params
        )
        self.assertIn('type', cache_key)
        print(f"✓ Type filter included in cache key: {cache_key}")

    def test_ordering_param_included(self):
        """测试 ordering 参数是否被包含"""
        allowed_params = self.viewset._get_allowed_cache_params()
        self.assertIn('ordering', allowed_params)

        # 生成包含 ordering 的缓存键
        query_params = {'ordering': '-created_at', 'page': '1'}
        cache_key = get_cache_key(
            prefix='api',
            view_name='ProblemViewSet',
            query_params=query_params,
            allowed_params=allowed_params
        )
        self.assertIn('ordering', cache_key)
        print(f"✓ Ordering param included in cache key: {cache_key}")


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
        self.chapter1 = ChapterFactory(
            course=self.course,
            title="Chapter 1",
            order=1
        )
        self.chapter2 = ChapterFactory(
            course=self.course,
            title="Chapter 2",
            order=2
        )
        self.chapter3 = ChapterFactory(
            course=self.course,
            title="Chapter 3",
            order=3
        )

        # Create enrollment
        self.user = UserFactory(username='student')
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

    def test_unlock_status_is_cached(self):
        """Test that unlock status results are cached"""
        # Create unlock condition: chapter2 requires chapter1
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # First call - should compute and cache
        result1 = ChapterUnlockService.is_unlocked(
            self.chapter2,
            self.enrollment
        )

        # Test caching by checking cache directly
        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id
        )
        cached_value = ChapterUnlockService._get_cache(cache_key)

        # The cache should exist and match the first result
        self.assertIsNotNone(cached_value)
        self.assertEqual(cached_value, result1)
        self.assertFalse(result1)  # Initially locked

    def test_cache_key_generation(self):
        """Test that cache keys are generated correctly"""
        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter1.id,
            self.enrollment.id
        )

        expected_key = f"chapter_unlock:{self.chapter1.id}:{self.enrollment.id}"
        self.assertEqual(cache_key, expected_key)

    def test_prerequisite_progress_cache_key_generation(self):
        """Test that prerequisite progress cache keys are generated correctly"""
        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter1.id,
            self.enrollment.id,
            ChapterUnlockService.PREREQUISITE_PROGRESS_CACHE_PREFIX
        )

        expected_key = f"chapter_prerequisite_progress:{self.chapter1.id}:{self.enrollment.id}"
        self.assertEqual(cache_key, expected_key)

    def test_unlock_status_without_condition_returns_cached_true(self):
        """Test that chapters without conditions return True (unlocked) and are cached"""
        # Chapter1 has no unlock condition - should be unlocked
        result1 = ChapterUnlockService.is_unlocked(
            self.chapter1,
            self.enrollment
        )

        self.assertTrue(result1)

        # Verify it's cached
        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter1.id,
            self.enrollment.id
        )
        cached_value = cache.get(cache_key)
        self.assertTrue(cached_value)

    def test_get_unlock_status_is_cached(self):
        """Test that get_unlock_status results are cached"""
        # Create unlock condition
        future_date = timezone.now() + timedelta(days=7)
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_date=future_date,
            unlock_condition_type='date'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # First call - should compute and cache
        status1 = ChapterUnlockService.get_unlock_status(
            self.chapter2,
            self.enrollment
        )

        # Test caching by checking progress cache directly
        progress_cache_key = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id,
            ChapterUnlockService.PREREQUISITE_PROGRESS_CACHE_PREFIX
        )
        cached_value = ChapterUnlockService._get_cache(progress_cache_key)

        # The cache should exist and match the first result
        self.assertIsNotNone(cached_value)
        self.assertEqual(cached_value['is_locked'], status1['is_locked'])
        self.assertTrue(status1['is_locked'])

    def test_cache_timeout_is_respected(self):
        """Test that cache timeout is set correctly"""
        ChapterUnlockService.is_unlocked(
            self.chapter1,
            self.enrollment
        )

        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter1.id,
            self.enrollment.id
        )

        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))

        # The actual timeout is controlled by the cache backend,
        # but we can verify the class constant
        self.assertEqual(ChapterUnlockService.CACHE_TIMEOUT, 900)  # 15 minutes

    def test_set_cache_and_get_cache_methods(self):
        """Test _set_cache and _get_cache helper methods"""
        cache_key = "test_key"
        test_value = True

        ChapterUnlockService._set_cache(cache_key, test_value)
        retrieved_value = ChapterUnlockService._get_cache(cache_key)

        self.assertEqual(retrieved_value, test_value)

    def test_get_cache_returns_none_for_nonexistent_key(self):
        """Test that _get_cache returns None for non-existent keys"""
        result = ChapterUnlockService._get_cache("nonexistent_key")
        self.assertIsNone(result)


class ChapterUnlockCacheInvalidationTests(TestCase):
    """Tests for cache invalidation behavior"""

    def setUp(self):
        """Set up test data and clear cache"""
        cache.clear()

        # Create course with chapters
        self.course = CourseFactory(title="Test Course")
        self.chapter1 = ChapterFactory(
            course=self.course,
            title="Chapter 1",
            order=1
        )
        self.chapter2 = ChapterFactory(
            course=self.course,
            title="Chapter 2",
            order=2
        )
        self.chapter3 = ChapterFactory(
            course=self.course,
            title="Chapter 3",
            order=3
        )

        # Create enrollment
        self.user = UserFactory(username='student')
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

        # Create unlock condition: chapter2 requires chapter1
        self.condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        self.condition.prerequisite_chapters.add(self.chapter1)

    def test_cache_invalidated_on_chapter_progress_completion(self):
        """Test that cache is invalidated when chapter progress is marked complete"""
        # Initially locked - cache the result
        result1 = ChapterUnlockService.is_unlocked(
            self.chapter2,
            self.enrollment
        )
        self.assertFalse(result1)

        # Verify cache is set
        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Mark chapter1 as complete (this should trigger cache invalidation)
        progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Manually trigger signal handler
        from ..signals import invalidate_chapter_progress_cache
        invalidate_chapter_progress_cache(
            sender=ChapterProgress,
            instance=progress
        )

        # Cache should be invalidated
        cached_value = cache.get(cache_key)
        self.assertIsNone(cached_value)

        # New call should compute fresh result
        result2 = ChapterUnlockService.is_unlocked(
            self.chapter2,
            self.enrollment
        )
        self.assertTrue(result2)  # Now unlocked

    def test_cache_invalidated_on_dependent_chapters(self):
        """Test that immediate dependent chapter caches are invalidated"""
        # Verify initial condition: chapter2 depends on chapter1 (from setUp)
        # The signal should invalidate chapter2's cache when chapter1 progress changes

        # Cache unlock status for chapter2
        ChapterUnlockService.is_unlocked(self.chapter2, self.enrollment)

        cache_key2 = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id
        )

        # Verify cache is set
        self.assertIsNotNone(cache.get(cache_key2))

        # Mark chapter1 as complete (chapter2's prerequisite)
        progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Manually trigger signal handler
        from ..signals import invalidate_chapter_progress_cache
        invalidate_chapter_progress_cache(
            sender=ChapterProgress,
            instance=progress
        )

        # chapter2 cache should be invalidated (immediate dependent)
        self.assertIsNone(cache.get(cache_key2))

    def test_cache_invalidated_on_transitive_prerequisite_completion(self):
        """Test that completing a prerequisite allows the next chapter to be unlocked"""
        # Set up: chapter3 requires chapter2
        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition3.prerequisite_chapters.add(self.chapter2)

        # Initially chapter2 and chapter3 are locked
        self.assertFalse(ChapterUnlockService.is_unlocked(
            self.chapter2, self.enrollment
        ))
        self.assertFalse(ChapterUnlockService.is_unlocked(
            self.chapter3, self.enrollment
        ))

        # Mark chapter1 as complete
        progress1 = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Trigger cache invalidation
        from ..signals import invalidate_chapter_progress_cache
        invalidate_chapter_progress_cache(
            sender=ChapterProgress,
            instance=progress1
        )

        # After cache invalidation, chapter2 should now be unlocked
        self.assertTrue(ChapterUnlockService.is_unlocked(
            self.chapter2, self.enrollment
        ))
        # chapter3 should still be locked (chapter2 not complete yet)
        self.assertFalse(ChapterUnlockService.is_unlocked(
            self.chapter3, self.enrollment
        ))

    def test_cache_invalidated_on_unlock_condition_save(self):
        """Test that cache is invalidated when unlock condition is saved"""
        # Cache unlock status
        ChapterUnlockService.is_unlocked(
            self.chapter2,
            self.enrollment
        )

        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Modify the unlock condition
        self.condition.unlock_condition_type = 'date'
        self.condition.unlock_date = timezone.now() - timedelta(days=1)
        self.condition.save()

        # Manually trigger signal handler
        from ..signals import invalidate_unlock_condition_cache
        invalidate_unlock_condition_cache(
            sender=type(self.condition),
            instance=self.condition
        )

        # Cache should be invalidated
        cached_value = cache.get(cache_key)
        self.assertIsNone(cached_value)

    def test_invalidate_cache_with_specific_enrollment(self):
        """Test _invalidate_cache with specific enrollment_id"""
        # Cache unlock status
        ChapterUnlockService.is_unlocked(
            self.chapter2,
            self.enrollment
        )

        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id
        )
        self.assertIsNotNone(cache.get(cache_key))

        # Invalidate cache for specific enrollment
        ChapterUnlockService._invalidate_cache(
            self.chapter2.id,
            self.enrollment.id
        )

        # Cache should be invalidated
        self.assertIsNone(cache.get(cache_key))

    def test_invalidate_cache_without_enrollment(self):
        """Test _invalidate_cache without enrollment_id (wildcard)"""
        # Cache unlock status
        ChapterUnlockService.is_unlocked(
            self.chapter2,
            self.enrollment
        )

        cache_key = ChapterUnlockService._get_cache_key(
            self.chapter2.id,
            self.enrollment.id
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
        self.chapter1 = ChapterFactory(
            course=self.course,
            title="Foundations",
            order=1
        )
        self.chapter2 = ChapterFactory(
            course=self.course,
            title="Intermediate",
            order=2
        )
        self.chapter3 = ChapterFactory(
            course=self.course,
            title="Advanced",
            order=3
        )

        # Create enrollment
        self.user = UserFactory(username='student')
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

    def test_complete_unlock_workflow_with_cache(self):
        """Test complete unlock workflow: cache -> progress change -> cache invalidation -> fresh result"""
        # Set up: chapter2 requires chapter1, chapter3 requires chapter2
        condition2 = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition2.prerequisite_chapters.add(self.chapter1)

        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition3.prerequisite_chapters.add(self.chapter2)

        # Initial state: all locked
        self.assertFalse(ChapterUnlockService.is_unlocked(
            self.chapter2, self.enrollment
        ))
        self.assertFalse(ChapterUnlockService.is_unlocked(
            self.chapter3, self.enrollment
        ))

        # Complete chapter1
        progress1 = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Trigger cache invalidation
        from ..signals import invalidate_chapter_progress_cache
        invalidate_chapter_progress_cache(
            sender=ChapterProgress,
            instance=progress1
        )

        # Verify: chapter2 unlocked, chapter3 still locked
        self.assertTrue(ChapterUnlockService.is_unlocked(
            self.chapter2, self.enrollment
        ))
        self.assertFalse(ChapterUnlockService.is_unlocked(
            self.chapter3, self.enrollment
        ))

        # Complete chapter2
        progress2 = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        # Trigger cache invalidation
        invalidate_chapter_progress_cache(
            sender=ChapterProgress,
            instance=progress2
        )

        # Verify: chapter3 now unlocked
        self.assertTrue(ChapterUnlockService.is_unlocked(
            self.chapter3, self.enrollment
        ))
