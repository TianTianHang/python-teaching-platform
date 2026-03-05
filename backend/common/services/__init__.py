"""
统一Cache服务层

本模块提供标准化的缓存服务接口，封装缓存操作的重复逻辑，
包括metrics记录、穿透保护、自适应TTL等功能。

主要服务类：
- SeparatedCacheService: 用于分离缓存场景（全局数据 + 用户状态）
- BusinessCacheService: 用于业务逻辑层缓存（services.py中的快照、执行结果等）
- CacheInvalidator: 统一的缓存失效API（在utils/cache.py中定义）

使用决策树：
1. ViewSet list/retrieve → 使用 CacheMixin
2. 分离缓存（全局+用户状态） → 使用 SeparatedCacheService
3. 业务逻辑缓存 → 使用 BusinessCacheService
4. 缓存失效 → 使用 CacheInvalidator

示例：
    from common.services import SeparatedCacheService, BusinessCacheService
    from common.utils.cache import CacheInvalidator

    # 分离缓存 - 获取全局数据
    data, is_hit = SeparatedCacheService.get_global_data(
        cache_key="courses:chapters:course_1",
        data_fetcher=lambda: Chapter.objects.filter(course_id=1).values(),
        ttl=1800
    )

    # 业务缓存 - 缓存执行结果
    result = BusinessCacheService.cache_execution_result(
        cache_key="execution:submission_123",
        fetcher=lambda: run_code(submission),
        timeout=300
    )

    # 缓存失效
    CacheInvalidator.invalidate_viewset(
        prefix="courses",
        view_name="ChapterViewSet",
        pk=chapter_id
    )
"""

from .separated_cache import SeparatedCacheService
from .business_cache import BusinessCacheService

__all__ = [
    "SeparatedCacheService",
    "BusinessCacheService",
]
