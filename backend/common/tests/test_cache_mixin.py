from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.response import Response
from unittest.mock import patch, MagicMock
from common.utils.cache import (
    get_standard_cache_key,
    get_cache,
    delete_cache_pattern,
    set_cache,
)


User = get_user_model()


# 简单的 Mock ViewSet 用于测试
class MockChapterViewSet:
    """模拟 ChapterViewSet 用于测试嵌套路由缓存"""

    def __init__(self):
        self.kwargs = {}

    def _get_parent_pks(self):
        """从 self.kwargs 中提取父资源主键"""
        parent_pks = {}
        for key, value in self.kwargs.items():
            if key.endswith("_pk"):
                parent_pks[key] = str(value)
        return parent_pks


class MockProblemViewSet:
    """模拟 ProblemViewSet 用于测试双重嵌套路由缓存"""

    def __init__(self):
        self.kwargs = {}

    def _get_parent_pks(self):
        """从 self.kwargs 中提取父资源主键"""
        parent_pks = {}
        for key, value in self.kwargs.items():
            if key.endswith("_pk"):
                parent_pks[key] = str(value)
        return parent_pks


class NestedRouteCacheIntegrationTestCase(TestCase):
    """集成测试：嵌套路由缓存隔离"""

    def setUp(self):
        """设置测试环境"""
        self.factory = APIRequestFactory()
        # 清理所有可能存在的缓存
        delete_cache_pattern("api:*")

    def tearDown(self):
        """清理测试环境"""
        delete_cache_pattern("api:*")

    def test_nested_route_different_parent_different_cache(self):
        """测试不同父资源生成不同的缓存键

        /api/v1/courses/1/chapters 和 /api/v1/courses/2/chapters 应该有不同的缓存键
        """
        # 模拟 /api/v1/courses/1/chapters
        viewset1 = MockChapterViewSet()
        viewset1.kwargs = {"course_pk": "1"}

        # 模拟 /api/v1/courses/2/chapters
        viewset2 = MockChapterViewSet()
        viewset2.kwargs = {"course_pk": "2"}

        # 生成缓存键
        parent_pks1 = viewset1._get_parent_pks()
        parent_pks2 = viewset2._get_parent_pks()

        key1 = get_standard_cache_key(
            prefix="api",
            view_name="ChapterViewSet",
            parent_pks=parent_pks1,
            query_params={"page": "1"},
        )

        key2 = get_standard_cache_key(
            prefix="api",
            view_name="ChapterViewSet",
            parent_pks=parent_pks2,
            query_params={"page": "1"},
        )

        # 验证两个缓存键不同
        self.assertNotEqual(key1, key2)
        self.assertIn("course_pk=1", key1)
        self.assertIn("course_pk=2", key2)
        print(f"✓ Different parent resources generate different cache keys:")
        print(f"  - /courses/1/chapters: {key1}")
        print(f"  - /courses/2/chapters: {key2}")

    def test_doubly_nested_route_cache_key(self):
        """测试双重嵌套路由的缓存键

        /api/v1/courses/1/chapters/5/problems 应该包含两个父资源主键
        """
        # 模拟 /api/v1/courses/1/chapters/5/problems
        viewset = MockProblemViewSet()
        viewset.kwargs = {"course_pk": "1", "chapter_pk": "5"}

        # 生成缓存键
        parent_pks = viewset._get_parent_pks()
        cache_key = get_standard_cache_key(
            prefix="api",
            view_name="ProblemViewSet",
            parent_pks=parent_pks,
            query_params={"page": "1"},
        )

        # 验证缓存键包含两个父资源主键
        self.assertIn("chapter_pk=5", cache_key)
        self.assertIn("course_pk=1", cache_key)
        self.assertEqual(
            cache_key, "api:ProblemViewSet:chapter_pk=5:course_pk=1:page=1"
        )
        print(f"✓ Doubly nested route cache key: {cache_key}")

    def test_nested_route_cache_isolation(self):
        """测试嵌套路由缓存的隔离性

        确保一个父资源的缓存不会被另一个父资源访问到
        """
        # 为 course_pk=1 设置缓存
        parent_pks1 = {"course_pk": "1"}
        key1 = get_standard_cache_key(
            prefix="api",
            view_name="ChapterViewSet",
            parent_pks=parent_pks1,
            query_params={"page": "1"},
        )
        set_cache(key1, {"course_id": 1, "chapters": [1, 2, 3]}, timeout=60)

        # 尝试从 course_pk=2 获取缓存
        parent_pks2 = {"course_pk": "2"}
        key2 = get_standard_cache_key(
            prefix="api",
            view_name="ChapterViewSet",
            parent_pks=parent_pks2,
            query_params={"page": "1"},
        )

        cached = get_cache(key2)

        # 验证 course_pk=2 的缓存是 None（没有被 course_pk=1 的缓存污染）
        self.assertIsNone(cached)
        print(f"✓ Nested route cache isolation verified:")
        print(f"  - key1 (course_pk=1): {key1}")
        print(f"  - key2 (course_pk=2): {key2}")
        print(f"  - key2 cache is None (not polluted by key1)")

    def test_top_level_route_still_works(self):
        """测试非嵌套（顶层）路由的缓存仍然正常工作

        确保向后兼容性：不使用 parent_pks 的代码仍然正常工作
        """
        # 生成不带 parent_pks 的缓存键
        cache_key = get_standard_cache_key(
            prefix="api",
            view_name="CourseViewSet",
            query_params={"page": "1"},
        )

        # 设置缓存
        set_cache(cache_key, {"courses": [1, 2, 3]}, timeout=60)

        # 获取缓存
        cached = get_cache(cache_key)

        # 验证缓存正常工作
        self.assertIsNotNone(cached)
        self.assertEqual(cached, {"courses": [1, 2, 3]})
        self.assertEqual(cache_key, "api:CourseViewSet:page=1")
        print(f"✓ Top-level route cache still works: {cache_key}")

    def test_parent_pks_sorted_alphabetically(self):
        """测试父资源主键按字母顺序排序

        确保 kwargs 顺序不影响缓存键生成
        """
        # 不同顺序的 kwargs 应该生成相同的缓存键
        parent_pks1 = {"course_pk": "1", "chapter_pk": "5"}
        parent_pks2 = {"chapter_pk": "5", "course_pk": "1"}

        key1 = get_standard_cache_key(
            prefix="api",
            view_name="ProblemViewSet",
            parent_pks=parent_pks1,
            query_params={"page": "1"},
        )

        key2 = get_standard_cache_key(
            prefix="api",
            view_name="ProblemViewSet",
            parent_pks=parent_pks2,
            query_params={"page": "1"},
        )

        self.assertEqual(key1, key2)
        print(f"✓ Parent pks sorted alphabetically: {key1}")


class CacheInvalidationIntegrationTestCase(TestCase):
    """集成测试：嵌套路由缓存失效"""

    def setUp(self):
        """设置测试环境"""
        delete_cache_pattern("api:*")

    def tearDown(self):
        """清理测试环境"""
        delete_cache_pattern("api:*")

    def test_nested_invalidation_doesnt_affect_other_parents(self):
        """测试嵌套路由的缓存失效不影响其他父资源

        当 course_pk=1 的章节发生变化时，只清除 course_pk=1 的缓存，
        不影响 course_pk=2 的缓存
        """
        # 为 course_pk=1 和 course_pk=2 设置缓存
        parent_pks1 = {"course_pk": "1"}
        key1 = get_standard_cache_key(
            prefix="api",
            view_name="ChapterViewSet",
            parent_pks=parent_pks1,
            query_params={"page": "1"},
        )

        parent_pks2 = {"course_pk": "2"}
        key2 = get_standard_cache_key(
            prefix="api",
            view_name="ChapterViewSet",
            parent_pks=parent_pks2,
            query_params={"page": "1"},
        )

        set_cache(key1, {"course_id": 1, "data": "chapters_for_course_1"}, timeout=60)
        set_cache(key2, {"course_id": 2, "data": "chapters_for_course_2"}, timeout=60)

        # 验证两个缓存都存在
        self.assertIsNotNone(get_cache(key1))
        self.assertIsNotNone(get_cache(key2))

        # 模拟 course_pk=1 的缓存失效
        base_key = get_standard_cache_key(
            prefix="api", view_name="ChapterViewSet", parent_pks=parent_pks1
        )
        delete_cache_pattern(f"{base_key}:*")

        # 验证 course_pk=1 的缓存已被清除
        self.assertIsNone(get_cache(key1))

        # 验证 course_pk=2 的缓存仍然存在（没有被清除）
        self.assertIsNotNone(get_cache(key2))
        print(f"✓ Nested cache invalidation only affects target parent:")
        print(f"  - key1 (course_pk=1) was cleared")
        print(f"  - key2 (course_pk=2) still has data")


def mock_standard_cache_service(mock_get_cache=None, mock_set_cache=None):
    """
    测试辅助函数：Mock 标准缓存服务

    Args:
        mock_get_cache: 可选的 get_cache mock，默认返回 None (缓存未命中)
        mock_set_cache: 可选的 set_cache mock

    Returns:
        tuple: (mock_get_cache, mock_set_cache)
    """
    if mock_get_cache is None:
        mock_get_cache = MagicMock(return_value=None)
    if mock_set_cache is None:
        mock_set_cache = MagicMock()

    return mock_get_cache, mock_set_cache


class StandardCacheListMixinTestCase(TestCase):
    """单元测试：StandardCacheListMixin"""

    def setUp(self):
        self.factory = APIRequestFactory()
        delete_cache_pattern("api:*")

    def tearDown(self):
        delete_cache_pattern("api:*")

    @patch("common.mixins.cache_mixin.get_cache")
    @patch("common.mixins.cache_mixin.set_cache")
    def test_list_cache_hit(self, mock_set_cache, mock_get_cache):
        """测试列表视图缓存命中"""
        from common.mixins.cache_mixin import StandardCacheListMixin

        mock_get_cache.return_value = MagicMock(
            is_hit=True, is_null_value=False, data={"courses": [{"id": 1}]}
        )

        class TestViewSet(StandardCacheListMixin):
            cache_prefix = "api"
            cache_timeout = 900

            def get_queryset(self):
                return []

            def list(self, request, *args, **kwargs):
                return Response({"courses": [{"id": 1}]})

        viewset = TestViewSet()
        viewset.request = MagicMock()
        viewset.request.user = MagicMock()
        viewset.request.user.id = 1
        viewset.request.query_params = {}
        viewset.request._cache_stats = {
            "hits": 0,
            "misses": 0,
            "null_values": 0,
            "duration_ms": 0.0,
        }

        with patch.object(viewset, "_get_parent_pks", return_value={}):
            with patch.object(viewset, "_get_allowed_cache_params", return_value=set()):
                with patch.object(
                    viewset, "_is_user_specific_queryset", return_value=False
                ):
                    response = viewset.list(viewset.request)

        self.assertEqual(response.data, {"courses": [{"id": 1}]})
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_not_called()

    @patch("common.mixins.cache_mixin.get_cache")
    @patch("common.mixins.cache_mixin.set_cache")
    def test_list_cache_miss(self, mock_set_cache, mock_get_cache):
        """测试列表视图缓存未命中"""
        from common.mixins.cache_mixin import StandardCacheListMixin
        from rest_framework.response import Response

        mock_get_cache.return_value = MagicMock(
            is_hit=False, is_null_value=False, data=None
        )
        mock_set_cache.return_value = None

        class TestViewSet(StandardCacheListMixin):
            cache_prefix = "api"
            cache_timeout = 900

            def get_queryset(self):
                return []

            def list(self, request, *args, **kwargs):
                return Response({"courses": [{"id": 1}]})

        viewset = TestViewSet()
        viewset.request = MagicMock()
        viewset.request.user = MagicMock()
        viewset.request.user.id = 1
        viewset.request.query_params = {}
        viewset.request._cache_stats = {
            "hits": 0,
            "misses": 0,
            "null_values": 0,
            "duration_ms": 0.0,
        }

        with patch.object(viewset, "_get_parent_pks", return_value={}):
            with patch.object(viewset, "_get_allowed_cache_params", return_value=set()):
                with patch.object(
                    viewset, "_is_user_specific_queryset", return_value=False
                ):
                    response = viewset.list(viewset.request)

        self.assertEqual(response.data, {"courses": [{"id": 1}]})
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()

    @patch("common.mixins.cache_mixin.get_cache")
    def test_list_cache_null_value(self, mock_get_cache):
        """测试列表视图缓存穿透保护（null value）"""
        from common.mixins.cache_mixin import StandardCacheListMixin
        from rest_framework.response import Response

        mock_get_cache.return_value = MagicMock(
            is_hit=False, is_null_value=True, data=None
        )

        class TestViewSet(StandardCacheListMixin):
            cache_prefix = "api"
            cache_timeout = 900

            def get_queryset(self):
                return []

            def list(self, request, *args, **kwargs):
                return Response({"courses": []})

        viewset = TestViewSet()
        viewset.request = MagicMock()
        viewset.request.user = MagicMock()
        viewset.request.user.id = 1
        viewset.request.query_params = {}
        viewset.request._cache_stats = {
            "hits": 0,
            "misses": 0,
            "null_values": 0,
            "duration_ms": 0.0,
        }

        with patch.object(viewset, "_get_parent_pks", return_value={}):
            with patch.object(viewset, "_get_allowed_cache_params", return_value=set()):
                with patch.object(
                    viewset, "_is_user_specific_queryset", return_value=False
                ):
                    response = viewset.list(viewset.request)

        self.assertEqual(response.status_code, 404)

    def test_is_user_specific_queryset_detects_user_filter(self):
        """测试 _is_user_specific_queryset 能检测到用户过滤"""
        from common.mixins.cache_mixin import StandardCacheListMixin

        class UserSpecificViewSet(StandardCacheListMixin):
            cache_prefix = "api"

            def get_queryset(self):
                return self.queryset.filter(user=self.request.user)

        viewset = UserSpecificViewSet()
        result = viewset._is_user_specific_queryset()
        self.assertTrue(result)

    def test_is_user_specific_queryset_no_user_filter(self):
        """测试 _is_user_specific_queryset 对无用户过滤返回 False"""
        from common.mixins.cache_mixin import StandardCacheListMixin

        class NonUserSpecificViewSet(StandardCacheListMixin):
            cache_prefix = "api"

            def get_queryset(self):
                return self.queryset.all()

        viewset = NonUserSpecificViewSet()
        result = viewset._is_user_specific_queryset()
        self.assertFalse(result)

    def test_extract_query_params(self):
        """测试查询参数提取"""
        from common.mixins.cache_mixin import StandardCacheListMixin

        class TestViewSet(StandardCacheListMixin):
            pass

        viewset = TestViewSet()
        query_params = {
            "page": "1",
            "page_size": "10",
            "search": "test",
            "invalid": "value",
        }
        allowed_params = {"page", "page_size", "search"}

        result = viewset._extract_query_params(query_params, allowed_params)

        self.assertEqual(result, {"page": "1", "page_size": "10", "search": "test"})
        self.assertNotIn("invalid", result)

    def test_get_parent_pks_nested_route(self):
        """测试嵌套路由父资源主键提取"""
        from common.mixins.cache_mixin import StandardCacheListMixin

        class TestViewSet(StandardCacheListMixin):
            pass

        viewset = TestViewSet()
        viewset.kwargs = {"course_pk": "1", "chapter_pk": "5", "id": "10"}

        result = viewset._get_parent_pks()

        self.assertEqual(result, {"course_pk": "1", "chapter_pk": "5"})


class StandardCacheRetrieveMixinTestCase(TestCase):
    """单元测试：StandardCacheRetrieveMixin"""

    def setUp(self):
        self.factory = APIRequestFactory()
        delete_cache_pattern("api:*")

    def tearDown(self):
        delete_cache_pattern("api:*")

    @patch("common.mixins.cache_mixin.get_cache")
    @patch("common.mixins.cache_mixin.set_cache")
    def test_retrieve_cache_hit(self, mock_set_cache, mock_get_cache):
        """测试详情视图缓存命中"""
        from common.mixins.cache_mixin import StandardCacheRetrieveMixin

        mock_get_cache.return_value = MagicMock(
            is_hit=True, is_null_value=False, data={"id": 1, "name": "Course 1"}
        )

        class TestViewSet(StandardCacheRetrieveMixin):
            cache_prefix = "api"
            cache_timeout = 900

            def get_queryset(self):
                return []

            def retrieve(self, request, *args, **kwargs):
                return Response({"id": 1, "name": "Course 1"})

        viewset = TestViewSet()
        viewset.request = MagicMock()
        viewset.request.user = MagicMock()
        viewset.request.user.id = 1
        viewset.request.query_params = {}
        viewset.request._cache_stats = {
            "hits": 0,
            "misses": 0,
            "null_values": 0,
            "duration_ms": 0.0,
        }
        viewset.lookup_url_kwarg = "pk"

        with patch.object(viewset, "_get_parent_pks", return_value={}):
            with patch.object(viewset, "_get_allowed_cache_params", return_value=set()):
                with patch.object(
                    viewset, "_is_user_specific_queryset", return_value=False
                ):
                    response = viewset.retrieve(viewset.request, pk="1")

        self.assertEqual(response.data, {"id": 1, "name": "Course 1"})
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_not_called()

    @patch("common.mixins.cache_mixin.get_cache")
    @patch("common.mixins.cache_mixin.set_cache")
    def test_retrieve_cache_miss(self, mock_set_cache, mock_get_cache):
        """测试详情视图缓存未命中"""
        from common.mixins.cache_mixin import StandardCacheRetrieveMixin
        from rest_framework.response import Response

        mock_get_cache.return_value = MagicMock(
            is_hit=False, is_null_value=False, data=None
        )
        mock_set_cache.return_value = None

        class TestViewSet(StandardCacheRetrieveMixin):
            cache_prefix = "api"
            cache_timeout = 900

            def get_queryset(self):
                return []

            def retrieve(self, request, *args, **kwargs):
                return Response({"id": 1, "name": "Course 1"})

        viewset = TestViewSet()
        viewset.request = MagicMock()
        viewset.request.user = MagicMock()
        viewset.request.user.id = 1
        viewset.request.query_params = {}
        viewset.request._cache_stats = {
            "hits": 0,
            "misses": 0,
            "null_values": 0,
            "duration_ms": 0.0,
        }
        viewset.lookup_url_kwarg = "pk"

        with patch.object(viewset, "_get_parent_pks", return_value={}):
            with patch.object(viewset, "_get_allowed_cache_params", return_value=set()):
                with patch.object(
                    viewset, "_is_user_specific_queryset", return_value=False
                ):
                    response = viewset.retrieve(viewset.request, pk="1")

        self.assertEqual(response.data, {"id": 1, "name": "Course 1"})
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()

    @patch("common.mixins.cache_mixin.get_cache")
    def test_retrieve_cache_null_value(self, mock_get_cache):
        """测试详情视图缓存穿透保护（null value）"""
        from common.mixins.cache_mixin import StandardCacheRetrieveMixin
        from rest_framework.response import Response

        mock_get_cache.return_value = MagicMock(
            is_hit=False, is_null_value=True, data=None
        )

        class TestViewSet(StandardCacheRetrieveMixin):
            cache_prefix = "api"
            cache_timeout = 900

            def get_queryset(self):
                return []

            def retrieve(self, request, *args, **kwargs):
                return Response({"id": 1})

        viewset = TestViewSet()
        viewset.request = MagicMock()
        viewset.request.user = MagicMock()
        viewset.request.user.id = 1
        viewset.request.query_params = {}
        viewset.request._cache_stats = {
            "hits": 0,
            "misses": 0,
            "null_values": 0,
            "duration_ms": 0.0,
        }
        viewset.lookup_url_kwarg = "pk"

        with patch.object(viewset, "_get_parent_pks", return_value={}):
            with patch.object(viewset, "_get_allowed_cache_params", return_value=set()):
                with patch.object(
                    viewset, "_is_user_specific_queryset", return_value=False
                ):
                    response = viewset.retrieve(viewset.request, pk="1")

        self.assertEqual(response.status_code, 404)

    def test_retrieve_cache_key_includes_pk(self):
        """测试详情视图缓存键包含主键"""
        from common.mixins.cache_mixin import StandardCacheRetrieveMixin

        class TestViewSet(StandardCacheRetrieveMixin):
            cache_prefix = "api"

        viewset = TestViewSet()
        viewset.kwargs = {"pk": "1"}
        viewset.lookup_url_kwarg = "pk"

        parent_pks = viewset._get_parent_pks()
        cache_key = get_standard_cache_key(
            prefix=viewset.cache_prefix,
            view_name="TestViewSet",
            pk="1",
            parent_pks=parent_pks,
        )

        self.assertIn("pk=1", cache_key)
        self.assertIn("TestViewSet", cache_key)
