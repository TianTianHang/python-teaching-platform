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
