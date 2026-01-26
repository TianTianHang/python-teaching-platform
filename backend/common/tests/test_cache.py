from django.test import TestCase
from common.utils.cache import get_cache_key


class GetCacheKeyTestCase(TestCase):
    """测试 get_cache_key() 函数的各种场景"""

    def test_backward_compatibility_no_parent_pks(self):
        """测试向后兼容性：不传递 parent_pks 时仍能正常工作"""
        query_params = {'page': '1', 'search': 'test'}
        cache_key = get_cache_key(
            prefix='api',
            view_name='TestViewSet',
            query_params=query_params,
            allowed_params={'page', 'search'}
        )
        self.assertEqual(cache_key, 'api:TestViewSet:page=1&search=test')
        print(f"✓ Backward compatibility (no parent_pks): {cache_key}")

    def test_parent_pks_single(self):
        """测试单个父资源主键"""
        parent_pks = {'course_pk': '1'}
        cache_key = get_cache_key(
            prefix='api',
            view_name='ChapterViewSet',
            parent_pks=parent_pks
        )
        self.assertEqual(cache_key, 'api:ChapterViewSet:course_pk=1')
        print(f"✓ Single parent_pk: {cache_key}")

    def test_parent_pks_multiple_sorted(self):
        """测试多个父资源主键按字母顺序排序"""
        # 顺序不同但应该生成相同的 key（按字母排序）
        parent_pks1 = {'course_pk': '1', 'chapter_pk': '5'}
        parent_pks2 = {'chapter_pk': '5', 'course_pk': '1'}

        key1 = get_cache_key(prefix='api', view_name='ProblemViewSet', parent_pks=parent_pks1)
        key2 = get_cache_key(prefix='api', view_name='ProblemViewSet', parent_pks=parent_pks2)

        self.assertEqual(key1, key2)
        self.assertEqual(key1, 'api:ProblemViewSet:chapter_pk=5:course_pk=1')
        print(f"✓ Multiple parent_pks sorted: {key1}")

    def test_parent_pks_with_query_params(self):
        """测试父资源主键与查询参数组合"""
        parent_pks = {'course_pk': '2'}
        query_params = {'page': '1'}

        cache_key = get_cache_key(
            prefix='api',
            view_name='ChapterViewSet',
            parent_pks=parent_pks,
            query_params=query_params,
            allowed_params={'page'}
        )
        self.assertEqual(cache_key, 'api:ChapterViewSet:course_pk=2:page=1')
        print(f"✓ Parent_pks with query_params: {cache_key}")

    def test_parent_pks_with_pk(self):
        """测试父资源主键与主键组合"""
        parent_pks = {'course_pk': '1', 'chapter_pk': '5'}

        cache_key = get_cache_key(
            prefix='api',
            view_name='ProblemViewSet',
            parent_pks=parent_pks,
            pk=10
        )
        self.assertEqual(cache_key, 'api:ProblemViewSet:chapter_pk=5:course_pk=1:10')
        print(f"✓ Parent_pks with pk: {cache_key}")

    def test_parent_pks_isolation_different_parents(self):
        """测试不同父资源生成不同的缓存键"""
        parent_pks1 = {'course_pk': '1'}
        parent_pks2 = {'course_pk': '2'}

        key1 = get_cache_key(prefix='api', view_name='ChapterViewSet', parent_pks=parent_pks1)
        key2 = get_cache_key(prefix='api', view_name='ChapterViewSet', parent_pks=parent_pks2)

        self.assertNotEqual(key1, key2)
        print(f"✓ Different parent_pks generate different keys:")
        print(f"  - course_pk=1: {key1}")
        print(f"  - course_pk=2: {key2}")

    def test_parent_pks_complete_example(self):
        """测试完整的嵌套路由缓存键生成"""
        parent_pks = {'course_pk': '1', 'chapter_pk': '5'}
        query_params = {'page': '1', 'page_size': '10'}

        cache_key = get_cache_key(
            prefix='api',
            view_name='ProblemViewSet',
            parent_pks=parent_pks,
            query_params=query_params,
            allowed_params={'page', 'page_size'}
        )
        self.assertEqual(cache_key, 'api:ProblemViewSet:chapter_pk=5:course_pk=1:page=1&page_size=10')
        print(f"✓ Complete nested route example: {cache_key}")

    def test_empty_parent_pks(self):
        """测试空 parent_pks 字典不影响缓存键"""
        cache_key1 = get_cache_key(prefix='api', view_name='TestViewSet')
        cache_key2 = get_cache_key(prefix='api', view_name='TestViewSet', parent_pks={})

        self.assertEqual(cache_key1, cache_key2)
        self.assertEqual(cache_key1, 'api:TestViewSet')
        print(f"✓ Empty parent_pks dict: {cache_key1}")

    def test_parent_pks_none(self):
        """测试 parent_pks=None 与不传递 parent_pks 结果相同"""
        cache_key1 = get_cache_key(prefix='api', view_name='TestViewSet')
        cache_key2 = get_cache_key(prefix='api', view_name='TestViewSet', parent_pks=None)

        self.assertEqual(cache_key1, cache_key2)
        self.assertEqual(cache_key1, 'api:TestViewSet')
        print(f"✓ parent_pks=None equivalent to not passing it: {cache_key1}")
