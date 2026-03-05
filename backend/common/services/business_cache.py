"""
业务缓存服务层

用于业务逻辑层缓存（services.py中的快照、执行结果等）的标准实现。

使用场景：
    - courses/services.py 中的快照缓存（CourseUnlockSnapshot, ProblemUnlockSnapshot）
    - 代码执行结果缓存
    - 业务计算结果缓存

特点：
    - 提供通用的 cache_result() 方法
    - 提供针对特定场景的便利方法（cache_snapshot, cache_execution_result）
    - 自动记录 metrics 和穿透保护
    - 标准化 key 生成

示例：
    from common.services import BusinessCacheService

    # 通用缓存
    result = BusinessCacheService.cache_result(
        cache_key="business:my_data:user_123",
        fetcher=lambda: expensive_computation(),
        timeout=300
    )

    # 缓存快照
    snapshot = BusinessCacheService.cache_snapshot(
        prefix="courses",
        entity_type="CourseUnlockSnapshot",
        entity_id=course_id,
        user_id=request.user.id,
        fetcher=lambda: get_course_snapshot(course_id, user_id),
        timeout=300
    )

    # 缓存代码执行结果
    execution_result = BusinessCacheService.cache_execution_result(
        submission_id=submission.id,
        fetcher=lambda: execute_code(submission),
        timeout=600
    )
"""

import logging
from typing import Any, Callable, Optional, Dict

from common.utils.cache import (
    get_cache,
    set_cache,
    delete_cache,
    get_standard_cache_key,
)

logger = logging.getLogger("teaching_platform.cache")


class BusinessCacheService:
    """
    业务缓存服务

    为业务逻辑层提供标准缓存接口，封装metrics和穿透保护。

    设计原则：
        - 使用静态方法，避免实例化开销
        - 回调模式解耦，不依赖业务逻辑
        - 自动记录metrics和穿透保护
        - 标准化key生成，支持模式匹配
    """

    # 默认TTL配置
    DEFAULT_SNAPSHOT_TTL = 300  # 5分钟
    DEFAULT_EXECUTION_TTL = 600  # 10分钟
    DEFAULT_RESULT_TTL = 900  # 15分钟

    @staticmethod
    def cache_result(
        cache_key: str, fetcher: Callable[[], Any], timeout: int = 900
    ) -> Any:
        """
        通用缓存方法

        获取缓存数据，如果未命中则调用fetcher获取并缓存。

        Args:
            cache_key: 缓存key
            fetcher: 回调函数，在缓存未命中时调用获取数据
            timeout: 缓存过期时间（秒），默认900秒（15分钟）

        Returns:
            Any: 缓存的数据

        Example:
            result = BusinessCacheService.cache_result(
                cache_key="business:expensive_computation:user_123",
                fetcher=lambda: expensive_computation(user_id),
                timeout=300
            )
        """
        # 尝试从缓存获取
        result = get_cache(cache_key, return_result=True)

        if result and result.is_hit:
            logger.debug(f"Business cache hit: {cache_key}")
            return result.data

        if result and result.is_null_value:
            logger.debug(f"Business cache null value: {cache_key}")
            return None

        # 缓存未命中，调用fetcher获取数据
        logger.debug(f"Business cache miss: {cache_key}")
        try:
            data = fetcher()
        except Exception as e:
            logger.error(f"Failed to fetch business data for {cache_key}: {e}")
            raise

        # 存储到缓存
        set_cache(cache_key, data, timeout=timeout)
        logger.debug(f"Business cache set: {cache_key}, ttl={timeout}")

        return data

    @staticmethod
    def cache_snapshot(
        prefix: str,
        entity_type: str,
        entity_id: int,
        user_id: Optional[int] = None,
        fetcher: Optional[Callable[[], Any]] = None,
        timeout: int = 300,
        **kwargs,
    ) -> Any:
        """
        缓存快照数据（如 CourseUnlockSnapshot, ProblemUnlockSnapshot）

        Args:
            prefix: key前缀，如 "courses"
            entity_type: 实体类型，如 "CourseUnlockSnapshot"
            entity_id: 实体ID
            user_id: 用户ID（可选，用于用户特定的快照）
            fetcher: 回调函数，在缓存未命中时调用获取数据
            timeout: 缓存过期时间（秒），默认300秒（5分钟）
            **kwargs: 额外的key参数

        Returns:
            Any: 快照数据

        Example:
            snapshot = BusinessCacheService.cache_snapshot(
                prefix="courses",
                entity_type="CourseUnlockSnapshot",
                entity_id=course_id,
                user_id=request.user.id,
                fetcher=lambda: get_course_snapshot(course_id, request.user.id),
                timeout=300
            )
        """
        cache_key = get_standard_cache_key(
            prefix=prefix,
            view_name=entity_type,
            pk=entity_id,
            user_id=user_id,
            **kwargs,
        )

        return BusinessCacheService.cache_result(
            cache_key=cache_key, fetcher=fetcher or (lambda: None), timeout=timeout
        )

    @staticmethod
    def cache_execution_result(
        submission_id: int, fetcher: Callable[[], Any], timeout: int = 600
    ) -> Any:
        """
        缓存代码执行结果

        Args:
            submission_id: 提交ID
            fetcher: 回调函数，在缓存未命中时调用执行代码
            timeout: 缓存过期时间（秒），默认600秒（10分钟）

        Returns:
            Any: 执行结果

        Example:
            result = BusinessCacheService.cache_execution_result(
                submission_id=submission.id,
                fetcher=lambda: code_executor.execute(submission),
                timeout=600
            )
        """
        cache_key = get_standard_cache_key(
            prefix="business", view_name="CodeExecution", pk=submission_id
        )

        return BusinessCacheService.cache_result(
            cache_key=cache_key, fetcher=fetcher, timeout=timeout
        )

    @staticmethod
    def invalidate_result(cache_key: str) -> bool:
        """
        失效指定的业务缓存

        Args:
            cache_key: 缓存key

        Returns:
            bool: 是否成功删除

        Example:
            BusinessCacheService.invalidate_result(
                "business:expensive_computation:user_123"
            )
        """
        try:
            delete_cache(cache_key)
            logger.debug(f"Invalidated business cache: {cache_key}")
            return True
        except Exception as e:
            logger.debug(f"Failed to invalidate business cache {cache_key}: {e}")
            return False

    @staticmethod
    def invalidate_snapshot(
        prefix: str,
        entity_type: str,
        entity_id: int,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> bool:
        """
        失效快照缓存

        Args:
            prefix: key前缀
            entity_type: 实体类型
            entity_id: 实体ID
            user_id: 用户ID（可选）
            **kwargs: 额外的key参数

        Returns:
            bool: 是否成功删除

        Example:
            BusinessCacheService.invalidate_snapshot(
                prefix="courses",
                entity_type="CourseUnlockSnapshot",
                entity_id=course_id,
                user_id=user_id
            )
        """
        cache_key = get_standard_cache_key(
            prefix=prefix,
            view_name=entity_type,
            pk=entity_id,
            user_id=user_id,
            **kwargs,
        )

        return BusinessCacheService.invalidate_result(cache_key)

    @staticmethod
    def invalidate_execution_result(submission_id: int) -> bool:
        """
        失效代码执行结果缓存

        Args:
            submission_id: 提交ID

        Returns:
            bool: 是否成功删除

        Example:
            BusinessCacheService.invalidate_execution_result(submission_id=123)
        """
        cache_key = get_standard_cache_key(
            prefix="business", view_name="CodeExecution", pk=submission_id
        )

        return BusinessCacheService.invalidate_result(cache_key)
