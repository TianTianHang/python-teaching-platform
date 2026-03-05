"""
SeparatedCacheService 单元测试
"""

import unittest
from unittest.mock import patch, MagicMock

from common.services.separated_cache import SeparatedCacheService
from common.utils.cache import CacheResult


class TestSeparatedCacheService(unittest.TestCase):
    """测试 SeparatedCacheService"""

    @patch("common.services.separated_cache.get_cache")
    @patch("common.services.separated_cache.set_cache")
    def test_get_global_data_cache_miss(self, mock_set_cache, mock_get_cache):
        """测试缓存未命中时调用 data_fetcher"""
        # 模拟缓存未命中
        mock_get_cache.return_value = CacheResult.miss()

        # 模拟 fetcher
        mock_fetcher = MagicMock(return_value={"data": "test_data"})

        # 调用服务
        result, is_hit = SeparatedCacheService.get_global_data(
            cache_key="test:key", data_fetcher=mock_fetcher, ttl=1800
        )

        # 验证 fetcher 被调用
        mock_fetcher.assert_called_once()
        # 验证 set_cache 被调用
        mock_set_cache.assert_called_once_with(
            "test:key", {"data": "test_data"}, timeout=1800
        )
        # 验证返回结果
        self.assertEqual(result, {"data": "test_data"})
        self.assertFalse(is_hit)

    @patch("common.services.separated_cache.get_cache")
    @patch("common.services.separated_cache.set_cache")
    def test_get_global_data_cache_hit(self, mock_set_cache, mock_get_cache):
        """测试缓存命中时不调用 data_fetcher"""
        # 模拟缓存命中
        mock_get_cache.return_value = CacheResult.hit({"data": "cached_data"})

        # 模拟 fetcher
        mock_fetcher = MagicMock()

        # 调用服务
        result, is_hit = SeparatedCacheService.get_global_data(
            cache_key="test:key", data_fetcher=mock_fetcher, ttl=1800
        )

        # 验证 fetcher 未被调用
        mock_fetcher.assert_not_called()
        # 验证 set_cache 未被调用
        mock_set_cache.assert_not_called()
        # 验证返回缓存数据
        self.assertEqual(result, {"data": "cached_data"})
        self.assertTrue(is_hit)

    @patch("common.services.separated_cache.get_cache")
    def test_get_global_data_returns_tuple(self, mock_get_cache):
        """测试返回 (data, is_cache_hit) 格式"""
        # 测试缓存命中
        mock_get_cache.return_value = CacheResult.hit({"data": "test"})
        result, is_hit = SeparatedCacheService.get_global_data(
            cache_key="test:key", data_fetcher=lambda: None, ttl=1800
        )
        self.assertIsInstance(result, dict)
        self.assertIsInstance(is_hit, bool)
        self.assertTrue(is_hit)

    @patch("common.services.separated_cache.get_cache")
    @patch("common.services.separated_cache.set_cache")
    def test_get_user_status_with_user_id(self, mock_set_cache, mock_get_cache):
        """测试 user_id 包含在 cache key 中"""
        # 模拟缓存未命中
        mock_get_cache.return_value = CacheResult.miss()

        mock_fetcher = MagicMock(return_value={"progress": 50})

        SeparatedCacheService.get_user_status(
            cache_key="test:key", user_id=123, status_fetcher=mock_fetcher, ttl=900
        )

        # 验证 get_cache 被调用时包含 user_id
        mock_get_cache.assert_called_once()
        call_args = mock_get_cache.call_args
        # key 应该包含 user_id
        self.assertIn("user_id=123", call_args[0][0])

    @patch("common.services.separated_cache.get_cache")
    @patch("common.services.separated_cache.set_cache")
    def test_get_user_status_cache_hit(self, mock_set_cache, mock_get_cache):
        """测试用户状态缓存命中"""
        mock_get_cache.return_value = CacheResult.hit({"progress": 75})
        mock_fetcher = MagicMock()

        result, is_hit = SeparatedCacheService.get_user_status(
            cache_key="test:key", user_id=456, status_fetcher=mock_fetcher, ttl=900
        )

        mock_fetcher.assert_not_called()
        self.assertEqual(result, {"progress": 75})
        self.assertTrue(is_hit)

    @patch("common.services.separated_cache.delete_cache")
    def test_invalidate_global_deletes_cache(self, mock_delete_cache):
        """测试 invalidate_global 调用 delete_cache"""
        mock_delete_cache.return_value = True

        result = SeparatedCacheService.invalidate_global("test:key")

        mock_delete_cache.assert_called_once_with("test:key")
        self.assertTrue(result)

    @patch("common.services.separated_cache.delete_cache")
    def test_invalidate_user_status_deletes_cache(self, mock_delete_cache):
        """测试 invalidate_user_status 调用 delete_cache 且 key 包含 user_id"""
        mock_delete_cache.return_value = True

        result = SeparatedCacheService.invalidate_user_status(
            cache_key="test:key", user_id=789
        )

        mock_delete_cache.assert_called_once()
        call_args = mock_delete_cache.call_args[0][0]
        # key 应该包含 user_id
        self.assertIn("user_id=789", call_args)
        self.assertTrue(result)

    @patch("common.services.separated_cache.delete_cache")
    def test_invalidate_handles_failure_gracefully(self, mock_delete_cache):
        """测试失效操作失败时返回 False 不抛出异常"""
        mock_delete_cache.side_effect = Exception("Redis error")

        result = SeparatedCacheService.invalidate_global("test:key")

        self.assertFalse(result)

    @patch("common.services.separated_cache.get_cache")
    def test_get_global_data_null_value(self, mock_get_cache):
        """测试全局数据空值缓存"""
        mock_get_cache.return_value = CacheResult.null_value()

        result, is_hit = SeparatedCacheService.get_global_data(
            cache_key="test:key", data_fetcher=lambda: {"data": "new"}, ttl=1800
        )

        # 空值应该返回 None 且命中缓存
        self.assertIsNone(result)
        self.assertTrue(is_hit)

    @patch("common.services.separated_cache.get_cache")
    def test_get_user_status_null_value(self, mock_get_cache):
        """测试用户状态空值缓存"""
        mock_get_cache.return_value = CacheResult.null_value()

        result, is_hit = SeparatedCacheService.get_user_status(
            cache_key="test:key",
            user_id=100,
            status_fetcher=lambda: {"status": "new"},
            ttl=900,
        )

        self.assertIsNone(result)
        self.assertTrue(is_hit)


if __name__ == "__main__":
    unittest.main()
