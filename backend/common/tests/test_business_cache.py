"""
BusinessCacheService 单元测试
"""

import unittest
from unittest.mock import patch, MagicMock

from common.services.business_cache import BusinessCacheService
from common.utils.cache import CacheResult


class TestBusinessCacheService(unittest.TestCase):
    """测试 BusinessCacheService"""

    @patch("common.services.business_cache.get_cache")
    @patch("common.services.business_cache.set_cache")
    def test_cache_result_cache_miss(self, mock_set_cache, mock_get_cache):
        """测试缓存未命中时调用 fetcher"""
        mock_get_cache.return_value = CacheResult.miss()
        mock_fetcher = MagicMock(return_value={"result": "data"})

        result = BusinessCacheService.cache_result(
            cache_key="test:key", fetcher=mock_fetcher, timeout=300
        )

        mock_fetcher.assert_called_once()
        mock_set_cache.assert_called_once_with(
            "test:key", {"result": "data"}, timeout=300
        )
        self.assertEqual(result, {"result": "data"})

    @patch("common.services.business_cache.get_cache")
    @patch("common.services.business_cache.set_cache")
    def test_cache_result_cache_hit(self, mock_set_cache, mock_get_cache):
        """测试缓存命中时不调用 fetcher"""
        mock_get_cache.return_value = CacheResult.hit({"result": "cached"})
        mock_fetcher = MagicMock()

        result = BusinessCacheService.cache_result(
            cache_key="test:key", fetcher=mock_fetcher, timeout=300
        )

        mock_fetcher.assert_not_called()
        mock_set_cache.assert_not_called()
        self.assertEqual(result, {"result": "cached"})

    @patch("common.services.business_cache.get_standard_cache_key")
    @patch("common.services.business_cache.get_cache")
    @patch("common.services.business_cache.set_cache")
    def test_cache_snapshot_generates_correct_key(
        self, mock_set_cache, mock_get_cache, mock_get_key
    ):
        """测试 cache_snapshot 生成正确的 key"""
        mock_get_key.return_value = "courses:CourseUnlockSnapshot:123:user_id=456"
        mock_get_cache.return_value = CacheResult.miss()
        mock_fetcher = MagicMock(return_value={"snapshot": "data"})

        BusinessCacheService.cache_snapshot(
            prefix="courses",
            entity_type="CourseUnlockSnapshot",
            entity_id=123,
            user_id=456,
            fetcher=mock_fetcher,
        )

        # 验证 get_standard_cache_key 被正确调用
        mock_get_key.assert_called_once_with(
            prefix="courses", view_name="CourseUnlockSnapshot", pk=123, user_id=456
        )

    @patch("common.services.business_cache.get_standard_cache_key")
    @patch("common.services.business_cache.get_cache")
    @patch("common.services.business_cache.set_cache")
    def test_cache_snapshot_default_timeout(
        self, mock_set_cache, mock_get_cache, mock_get_key
    ):
        """测试 cache_snapshot 使用默认 timeout=300"""
        mock_get_key.return_value = "test:key"
        mock_get_cache.return_value = CacheResult.miss()
        mock_fetcher = MagicMock(return_value={"data": "test"})

        BusinessCacheService.cache_snapshot(
            prefix="courses",
            entity_type="CourseUnlockSnapshot",
            entity_id=1,
            fetcher=mock_fetcher,
        )

        # 验证使用默认 timeout=300
        mock_set_cache.assert_called_once()
        call_kwargs = mock_set_cache.call_args[1]
        self.assertEqual(call_kwargs.get("timeout"), 300)

    @patch("common.services.business_cache.get_standard_cache_key")
    @patch("common.services.business_cache.get_cache")
    @patch("common.services.business_cache.set_cache")
    def test_cache_execution_result_generates_correct_key(
        self, mock_set_cache, mock_get_cache, mock_get_key
    ):
        """测试 cache_execution_result 生成包含 'CodeExecution' 的 key"""
        mock_get_key.return_value = "business:CodeExecution:123"
        mock_get_cache.return_value = CacheResult.miss()
        mock_fetcher = MagicMock(return_value={"output": "result"})

        BusinessCacheService.cache_execution_result(
            submission_id=123, fetcher=mock_fetcher
        )

        mock_get_key.assert_called_once_with(
            prefix="business", view_name="CodeExecution", pk=123
        )

    @patch("common.services.business_cache.get_cache")
    @patch("common.services.business_cache.set_cache")
    def test_custom_timeout_override(self, mock_set_cache, mock_get_cache):
        """测试自定义 timeout 参数正确传递"""
        mock_get_cache.return_value = CacheResult.miss()
        mock_fetcher = MagicMock(return_value="data")

        BusinessCacheService.cache_result(
            cache_key="test:key", fetcher=mock_fetcher, timeout=600
        )

        mock_set_cache.assert_called_once_with("test:key", "data", timeout=600)

    @patch("common.services.business_cache.delete_cache")
    def test_invalidate_result(self, mock_delete_cache):
        """测试 invalidate_result 调用 delete_cache"""
        mock_delete_cache.return_value = True

        result = BusinessCacheService.invalidate_result("test:key")

        mock_delete_cache.assert_called_once_with("test:key")
        self.assertTrue(result)

    @patch("common.services.business_cache.get_standard_cache_key")
    @patch("common.services.business_cache.delete_cache")
    def test_invalidate_snapshot(self, mock_delete_cache, mock_get_key):
        """测试 invalidate_snapshot 生成正确的 key 并删除"""
        mock_get_key.return_value = "courses:CourseUnlockSnapshot:123:user_id=456"
        mock_delete_cache.return_value = True

        result = BusinessCacheService.invalidate_snapshot(
            prefix="courses",
            entity_type="CourseUnlockSnapshot",
            entity_id=123,
            user_id=456,
        )

        mock_get_key.assert_called_once_with(
            prefix="courses", view_name="CourseUnlockSnapshot", pk=123, user_id=456
        )
        mock_delete_cache.assert_called_once_with(
            "courses:CourseUnlockSnapshot:123:user_id=456"
        )
        self.assertTrue(result)

    @patch("common.services.business_cache.get_standard_cache_key")
    @patch("common.services.business_cache.delete_cache")
    def test_invalidate_execution_result(self, mock_delete_cache, mock_get_key):
        """测试 invalidate_execution_result 删除执行结果缓存"""
        mock_get_key.return_value = "business:CodeExecution:123"
        mock_delete_cache.return_value = True

        result = BusinessCacheService.invalidate_execution_result(submission_id=123)

        mock_get_key.assert_called_once_with(
            prefix="business", view_name="CodeExecution", pk=123
        )
        mock_delete_cache.assert_called_once_with("business:CodeExecution:123")
        self.assertTrue(result)

    @patch("common.services.business_cache.get_cache")
    def test_cache_result_null_value(self, mock_get_cache):
        """测试空值缓存返回 None"""
        mock_get_cache.return_value = CacheResult.null_value()
        mock_fetcher = MagicMock()

        result = BusinessCacheService.cache_result(
            cache_key="test:key", fetcher=mock_fetcher
        )

        mock_fetcher.assert_not_called()
        self.assertIsNone(result)

    @patch("common.services.business_cache.delete_cache")
    def test_invalidate_handles_failure_gracefully(self, mock_delete_cache):
        """测试失效操作失败时返回 False"""
        mock_delete_cache.side_effect = Exception("Redis error")

        result = BusinessCacheService.invalidate_result("test:key")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
