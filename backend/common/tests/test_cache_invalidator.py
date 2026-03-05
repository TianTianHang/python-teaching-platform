"""
CacheInvalidator 单元测试
"""

import unittest
from unittest.mock import patch, MagicMock

from common.utils.cache import CacheInvalidator


class TestCacheInvalidator(unittest.TestCase):
    """测试 CacheInvalidator"""

    @patch("common.utils.cache.delete_cache")
    @patch("common.utils.cache.get_standard_cache_key")
    def test_invalidate_viewset_generates_correct_key(self, mock_get_key, mock_delete):
        """测试 invalidate_viewset 生成正确的 key"""
        mock_get_key.return_value = "courses:ChapterViewSet:123"
        mock_delete.return_value = True

        result = CacheInvalidator.invalidate_viewset(
            prefix="courses", view_name="ChapterViewSet", pk=123
        )

        mock_get_key.assert_called_once_with(
            prefix="courses", view_name="ChapterViewSet", pk=123
        )
        mock_delete.assert_called_once_with("courses:ChapterViewSet:123")
        self.assertTrue(result)

    @patch("common.utils.cache.delete_cache")
    def test_invalidate_viewset_calls_delete_cache(self, mock_delete):
        """测试 invalidate_viewset 调用 delete_cache"""
        mock_delete.return_value = True

        with patch("common.utils.cache.get_standard_cache_key") as mock_get_key:
            mock_get_key.return_value = "test:key"
            CacheInvalidator.invalidate_viewset(
                prefix="test", view_name="TestViewSet", pk=1
            )

        mock_delete.assert_called_once()

    @patch("common.utils.cache.delete_cache_pattern")
    @patch("common.utils.cache.get_standard_cache_key")
    def test_invalidate_viewset_list_uses_pattern(
        self, mock_get_key, mock_delete_pattern
    ):
        """测试 invalidate_viewset_list 使用通配符模式"""
        mock_get_key.return_value = "courses:ChapterViewSet"
        mock_delete_pattern.return_value = True

        result = CacheInvalidator.invalidate_viewset_list(
            prefix="courses", view_name="ChapterViewSet"
        )

        # 验证 key 以 :* 结尾
        mock_delete_pattern.assert_called_once()
        call_args = mock_delete_pattern.call_args[0][0]
        self.assertTrue(call_args.endswith(":*"))
        self.assertTrue(result)

    @patch("common.utils.cache.delete_cache_pattern")
    def test_invalidate_viewset_list_calls_delete_pattern(self, mock_delete_pattern):
        """测试 invalidate_viewset_list 调用 delete_cache_pattern"""
        mock_delete_pattern.return_value = True

        with patch("common.utils.cache.get_standard_cache_key") as mock_get_key:
            mock_get_key.return_value = "test:ViewSet"
            CacheInvalidator.invalidate_viewset_list(prefix="test", view_name="ViewSet")

        mock_delete_pattern.assert_called_once()

    @patch("common.utils.cache.delete_cache")
    @patch("common.utils.cache.get_standard_cache_key")
    def test_invalidate_separated_cache_global_flag(self, mock_get_key, mock_delete):
        """测试 invalidate_separated_cache_global 使用 is_separated=True"""
        mock_get_key.return_value = (
            "courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1"
        )
        mock_delete.return_value = True

        result = CacheInvalidator.invalidate_separated_cache_global(
            prefix="courses", view_name="ChapterViewSet", parent_pks={"course_pk": 1}
        )

        mock_get_key.assert_called_once()
        call_kwargs = mock_get_key.call_args[1]
        self.assertTrue(call_kwargs.get("is_separated"))
        self.assertEqual(call_kwargs.get("separated_type"), "GLOBAL")
        mock_delete.assert_called_once()
        self.assertTrue(result)

    @patch("common.utils.cache.delete_cache")
    @patch("common.utils.cache.get_standard_cache_key")
    def test_invalidate_separated_cache_user_status_includes_user_id(
        self, mock_get_key, mock_delete
    ):
        """测试 invalidate_separated_cache_user_status 包含 user_id"""
        mock_get_key.return_value = (
            "courses:ChapterViewSet:SEPARATED:STATUS:course_pk=1:user_id=123"
        )
        mock_delete.return_value = True

        result = CacheInvalidator.invalidate_separated_cache_user_status(
            prefix="courses",
            view_name="ChapterViewSet",
            user_id=123,
            parent_pks={"course_pk": 1},
        )

        mock_get_key.assert_called_once()
        call_kwargs = mock_get_key.call_args[1]
        self.assertEqual(call_kwargs.get("user_id"), 123)
        self.assertTrue(call_kwargs.get("is_separated"))
        self.assertEqual(call_kwargs.get("separated_type"), "STATUS")
        mock_delete.assert_called_once()
        self.assertTrue(result)

    @patch("common.utils.cache.delete_cache")
    def test_invalidate_handles_missing_cache_gracefully(self, mock_delete):
        """测试 delete_cache 抛出异常时不抛出"""
        mock_delete.side_effect = Exception("Redis connection error")

        with patch("common.utils.cache.get_standard_cache_key") as mock_get_key:
            mock_get_key.return_value = "test:key"
            result = CacheInvalidator.invalidate_viewset(
                prefix="test", view_name="ViewSet", pk=1
            )

        # 应该返回 False 而不是抛出异常
        self.assertFalse(result)

    @patch("common.utils.cache.delete_cache_pattern")
    def test_invalidate_list_handles_failure_gracefully(self, mock_delete_pattern):
        """测试 delete_cache_pattern 抛出异常时不抛出"""
        mock_delete_pattern.side_effect = Exception("Redis error")

        with patch("common.utils.cache.get_standard_cache_key") as mock_get_key:
            mock_get_key.return_value = "test:ViewSet"
            result = CacheInvalidator.invalidate_viewset_list(
                prefix="test", view_name="ViewSet"
            )

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
