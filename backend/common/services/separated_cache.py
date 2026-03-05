"""
分离缓存服务层

用于分离缓存场景（全局数据 + 用户状态）的标准实现。

使用场景：
    - courses/views.py 中的章节列表、问题列表等
    - 需要分离缓存全局数据和用户状态的场景

特点：
    - 自动处理缓存命中/未命中逻辑
    - 支持回调模式获取数据
    - 自动记录 metrics 和穿透保护
    - 支持独立失效全局数据和用户状态

示例：
    from common.services import SeparatedCacheService

    # 获取全局数据
    data, is_hit = SeparatedCacheService.get_global_data(
        cache_key="courses:chapters:course_1",
        data_fetcher=lambda: Chapter.objects.filter(course_id=1).values(),
        ttl=1800
    )

    # 获取用户状态
    status, is_hit = SeparatedCacheService.get_user_status(
        cache_key="courses:chapters:course_1",
        user_id=request.user.id,
        status_fetcher=lambda: get_user_chapter_status(user_id, course_id),
        ttl=900
    )

    # 失效全局数据
    SeparatedCacheService.invalidate_global("courses:chapters:course_1")

    # 失效用户状态
    SeparatedCacheService.invalidate_user_status(
        "courses:chapters:course_1",
        user_id=request.user.id
    )
"""

import logging
from typing import Any, Callable, Tuple, Optional

from common.utils.cache import get_cache, set_cache, delete_cache

logger = logging.getLogger("teaching_platform.cache")


class SeparatedCacheService:
    """
    分离缓存服务

    为分离缓存场景（全局数据 + 用户状态）提供统一API，
    封装两层缓存的获取、合并和失效逻辑。

    设计原则：
        - 使用静态方法，避免实例化开销
        - 回调模式解耦，不依赖Django模型
        - 自动记录metrics和穿透保护
        - 支持独立失效全局数据和用户状态
    """

    @staticmethod
    def get_global_data(
        cache_key: str, data_fetcher: Callable[[], Any], ttl: int = 1800
    ) -> Tuple[Any, bool]:
        """
        获取全局数据（分离缓存的全局部分）

        Args:
            cache_key: 全局数据的缓存key（应包含 GLOBAL 标记）
            data_fetcher: 回调函数，在缓存未命中时调用获取数据
            ttl: 缓存过期时间（秒），默认1800秒（30分钟）

        Returns:
            Tuple[Any, bool]: (数据, 是否命中缓存)

        Example:
            data, is_hit = SeparatedCacheService.get_global_data(
                cache_key="courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1",
                data_fetcher=lambda: list(Chapter.objects.filter(course_id=1).values()),
                ttl=1800
            )
        """
        # 尝试从缓存获取
        result = get_cache(cache_key, return_result=True)

        if result and result.is_hit:
            logger.debug(f"Separated cache global hit: {cache_key}")
            return result.data, True

        if result and result.is_null_value:
            logger.debug(f"Separated cache global null value: {cache_key}")
            return None, True

        # 缓存未命中，调用fetcher获取数据
        logger.debug(f"Separated cache global miss: {cache_key}")
        try:
            data = data_fetcher()
        except Exception as e:
            logger.error(f"Failed to fetch global data for {cache_key}: {e}")
            raise

        # 存储到缓存
        set_cache(cache_key, data, timeout=ttl)
        logger.debug(f"Separated cache global set: {cache_key}, ttl={ttl}")

        return data, False

    @staticmethod
    def get_user_status(
        cache_key: str, user_id: int, status_fetcher: Callable[[], Any], ttl: int = 900
    ) -> Tuple[Any, bool]:
        """
        获取用户状态（分离缓存的用户状态部分）

        Args:
            cache_key: 用户状态的缓存key（应包含 STATUS 和 user_id）
            user_id: 用户ID
            status_fetcher: 回调函数，在缓存未命中时调用获取用户状态
            ttl: 缓存过期时间（秒），默认900秒（15分钟）

        Returns:
            Tuple[Any, bool]: (用户状态数据, 是否命中缓存)

        Example:
            status, is_hit = SeparatedCacheService.get_user_status(
                cache_key="courses:ChapterViewSet:SEPARATED:STATUS:course_pk=1",
                user_id=request.user.id,
                status_fetcher=lambda: get_user_progress(user_id, course_id),
                ttl=900
            )
        """
        # 构建包含user_id的key
        user_cache_key = f"{cache_key}:user_id={user_id}"

        # 尝试从缓存获取
        result = get_cache(user_cache_key, return_result=True)

        if result and result.is_hit:
            logger.debug(f"Separated cache status hit: {user_cache_key}")
            return result.data, True

        if result and result.is_null_value:
            logger.debug(f"Separated cache status null value: {user_cache_key}")
            return None, True

        # 缓存未命中，调用fetcher获取数据
        logger.debug(f"Separated cache status miss: {user_cache_key}")
        try:
            data = status_fetcher()
        except Exception as e:
            logger.error(f"Failed to fetch user status for {user_cache_key}: {e}")
            raise

        # 存储到缓存
        set_cache(user_cache_key, data, timeout=ttl)
        logger.debug(f"Separated cache status set: {user_cache_key}, ttl={ttl}")

        return data, False

    @staticmethod
    def invalidate_global(cache_key: str) -> bool:
        """
        失效全局数据缓存

        Args:
            cache_key: 全局数据的缓存key

        Returns:
            bool: 是否成功删除

        Example:
            SeparatedCacheService.invalidate_global(
                "courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1"
            )
        """
        try:
            delete_cache(cache_key)
            logger.debug(f"Invalidated separated cache global: {cache_key}")
            return True
        except Exception as e:
            logger.debug(f"Failed to invalidate global cache {cache_key}: {e}")
            return False

    @staticmethod
    def invalidate_user_status(cache_key: str, user_id: int) -> bool:
        """
        失效用户状态缓存

        Args:
            cache_key: 用户状态的缓存key（不包含user_id）
            user_id: 用户ID

        Returns:
            bool: 是否成功删除

        Example:
            SeparatedCacheService.invalidate_user_status(
                "courses:ChapterViewSet:SEPARATED:STATUS:course_pk=1",
                user_id=request.user.id
            )
        """
        user_cache_key = f"{cache_key}:user_id={user_id}"
        try:
            delete_cache(user_cache_key)
            logger.debug(f"Invalidated separated cache status: {user_cache_key}")
            return True
        except Exception as e:
            logger.debug(f"Failed to invalidate status cache {user_cache_key}: {e}")
            return False

    @staticmethod
    def invalidate_all(cache_key: str) -> bool:
        """
        同时失效全局数据和所有用户状态（谨慎使用）

        注意：这只会失效特定cache_key对应的全局数据，
        用户状态缓存需要知道所有user_id才能完全清除。
        通常建议单独调用 invalidate_global 和 invalidate_user_status。

        Args:
            cache_key: 缓存key（不包含user_id）

        Returns:
            bool: 是否成功删除全局数据

        Example:
            SeparatedCacheService.invalidate_all(
                "courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1"
            )
        """
        return SeparatedCacheService.invalidate_global(cache_key)
