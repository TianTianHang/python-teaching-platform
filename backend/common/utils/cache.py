# utils/cache.py
import json
import time
import logging
from typing import Any, Optional, Literal, Dict, Dict, Callable
from urllib.parse import urlencode
from collections import OrderedDict
from django.core.cache import cache
from django_redis import get_redis_connection

# Import cache metrics
try:
    from common.metrics import (
        record_cache_hit,
        record_cache_miss,
        record_cache_null_value,
    )
except ImportError:
    # Fallback for when the module isn't available (e.g., during tests)
    record_cache_hit = None
    record_cache_miss = None
    record_cache_null_value = None

logger = logging.getLogger("teaching_platform.cache")


class CacheResult:
    """封装缓存结果，包含数据、状态和元信息"""

    def __init__(
        self,
        data: Any,
        status: Literal["HIT", "MISS", "NULL_VALUE"],
        cached_at: Optional[float] = None,
        ttl: Optional[int] = None,
    ):
        self.data = data
        self.status = status
        self.cached_at = cached_at
        self.ttl = ttl

    @classmethod
    def hit(
        cls, data: Any, cached_at: Optional[float] = None, ttl: Optional[int] = None
    ) -> "CacheResult":
        """创建缓存命中结果"""
        return cls(data, "HIT", cached_at, ttl)

    @classmethod
    def miss(cls) -> "CacheResult":
        """创建缓存未命中结果"""
        return cls(None, "MISS", None, None)

    @classmethod
    def null_value(
        cls, cached_at: Optional[float] = None, ttl: Optional[int] = None
    ) -> "CacheResult":
        """创建空值结果（用于缓存穿透保护）"""
        return cls(None, "NULL_VALUE", cached_at, ttl)

    def __bool__(self) -> bool:
        """用于布尔判断，HIT 和 NULL_VALUE 都返回 True"""
        return self.status in ("HIT", "NULL_VALUE")

    @property
    def is_hit(self) -> bool:
        return self.status == "HIT"

    @property
    def is_miss(self) -> bool:
        return self.status == "MISS"

    @property
    def is_null_value(self) -> bool:
        return self.status == "NULL_VALUE"


# 哨兵值标记，用于区分空值和缓存未命中
NULL_VALUE_MARKER = "__NULL_VALUE__"
EMPTY_VALUE_MARKER = "__EMPTY_VALUE__"  # 用于空列表/空字典


def set_cache(key, value, timeout=900, is_null: bool = False):  # 默认15分钟
    """设置缓存数据

    Args:
        key: 缓存键
        value: 缓存值
        timeout: 超时时间（秒）
        is_null: 是否是空值（用于缓存穿透保护）
    """
    start_time = time.time()
    try:
        current_time = time.time()

        # 检查是否是空值（空列表、空字典、None）
        is_empty = value in ([], {}, None) and not is_null

        if is_null:
            # 缓存穿透保护：使用哨兵值标记不存在的资源
            cache_data = {
                "__marker__": NULL_VALUE_MARKER,
                "cached_at": current_time,
                "ttl": timeout,
            }
            # 404/403 等错误响应使用 300 秒 TTL
            actual_timeout = min(timeout, 300)
        elif is_empty:
            # 空列表/空字典使用短 TTL (60 秒)
            cache_data = {
                "__marker__": EMPTY_VALUE_MARKER,
                "data": value,
                "cached_at": current_time,
                "ttl": 60,
            }
            actual_timeout = 60
        else:
            # 正常数据
            cache_data = value
            actual_timeout = timeout

        cache.set(
            key, json.dumps(cache_data, ensure_ascii=False, default=str), actual_timeout
        )

        duration_ms = (time.time() - start_time) * 1000
        if duration_ms > 100:
            logger.warning(
                "Slow cache set detected",
                extra={
                    "event": "cache_set",
                    "cache_key": key,
                    "duration_ms": duration_ms,
                },
            )
    except Exception:
        # 防止序列化失败导致接口异常
        pass


def get_cache(key, return_result: bool = False):
    """获取缓存数据

    Args:
        key: 缓存键
        return_result: 是否返回 CacheResult 对象（默认 False 保持向后兼容）
                       设为 True 时返回 CacheResult，否则返回原始数据

    Returns:
        如果 return_result=True，返回 CacheResult 对象
        否则返回原始数据（向后兼容）
    """
    start_time = time.time()
    # Extract view name from key - handle keys with varying number of parts
    key_parts = key.split(":")
    endpoint = (
        key_parts[1]
        if len(key_parts) > 1
        else (key_parts[0] if key_parts else "unknown")
    )

    try:
        data = cache.get(key)

        if data is None:
            # 记录未命中
            AdaptiveTTLCalculator.record_miss(key)
            if record_cache_miss:
                record_cache_miss(endpoint, time.time() - start_time, cache_key=key)
            return CacheResult.miss() if return_result else None

        # 反序列化数据
        parsed_data = json.loads(data)

        # 记录命中
        AdaptiveTTLCalculator.record_hit(key)

        # 检查是否是哨兵值
        if isinstance(parsed_data, dict):
            if parsed_data.get("__marker__") == NULL_VALUE_MARKER:
                if record_cache_null_value:
                    record_cache_null_value(endpoint, time.time() - start_time)
                result = CacheResult.null_value(
                    cached_at=parsed_data.get("cached_at"), ttl=parsed_data.get("ttl")
                )
                return result if return_result else None
            elif parsed_data.get("__marker__") == EMPTY_VALUE_MARKER:
                if record_cache_hit:
                    record_cache_hit(endpoint, time.time() - start_time, cache_key=key)
                result = CacheResult.hit(
                    data=parsed_data.get("data"),
                    cached_at=parsed_data.get("cached_at"),
                    ttl=parsed_data.get("ttl"),
                )
                return result if return_result else parsed_data.get("data")

        # 普通数据命中
        if record_cache_hit:
            record_cache_hit(endpoint, time.time() - start_time, cache_key=key)
        result = CacheResult.hit(parsed_data)
        return result if return_result else parsed_data

    except Exception as e:
        # 异常也记录为未命中
        AdaptiveTTLCalculator.record_miss(key)
        if record_cache_miss:
            record_cache_miss(endpoint, time.time() - start_time, cache_key=key)
        return CacheResult.miss() if return_result else None


class AdaptiveTTLCalculator:
    """自适应 TTL 计算器，基于访问频率和数据特性动态调整 TTL"""

    # 统计键前缀
    STATS_PREFIX = "cache_stats"

    @classmethod
    def get_stats_key(cls, cache_key: str) -> str:
        """获取统计数据的 Redis 键"""
        return f"{cls.STATS_PREFIX}:{cache_key}"

    @classmethod
    def calculate_ttl(cls, cache_key: str, default_ttl: int = 900) -> int:
        """计算自适应 TTL

        Args:
            cache_key: 缓存键
            default_ttl: 默认 TTL（秒）

        Returns:
            计算后的 TTL（秒）
        """
        try:
            redis_conn = get_redis_connection("default")
            stats_key = cls.get_stats_key(cache_key)
            stats = redis_conn.hgetall(stats_key)

            if not stats:
                # 首次访问，使用默认 TTL
                return default_ttl

            hits = int(stats.get(b"hits", 0))
            misses = int(stats.get(b"misses", 0))
            total_requests = hits + misses

            if total_requests == 0:
                return default_ttl

            hit_rate = hits / total_requests

            # 基于 TTL 分层策略
            if hit_rate > 0.5 and hits > 100:
                # 热点数据：30 分钟
                return 1800
            elif hit_rate > 0.2 and hits > 10:
                # 常规数据：15 分钟（默认）
                return 900
            else:
                # 冷数据：5 分钟
                return 300

        except Exception:
            return default_ttl

    @classmethod
    def record_hit(cls, cache_key: str):
        """记录缓存命中"""
        try:
            redis_conn = get_redis_connection("default")
            stats_key = cls.get_stats_key(cache_key)
            redis_conn.hincrby(stats_key, "hits", 1)
            redis_conn.hset(stats_key, "last_access", time.time())
            redis_conn.expire(stats_key, 86400)  # 统计数据保留 24 小时
        except Exception:
            pass

    @classmethod
    def record_miss(cls, cache_key: str):
        """记录缓存未命中"""
        try:
            redis_conn = get_redis_connection("default")
            stats_key = cls.get_stats_key(cache_key)
            redis_conn.hincrby(stats_key, "misses", 1)
            redis_conn.expire(stats_key, 86400)  # 统计数据保留 24 小时
        except Exception:
            pass

    @classmethod
    def get_hit_rate(cls, cache_key: str) -> Optional[float]:
        """获取指定缓存的命中率

        Returns:
            命中率 (0-1)，如果无统计数据返回 None
        """
        try:
            redis_conn = get_redis_connection("default")
            stats_key = cls.get_stats_key(cache_key)
            stats = redis_conn.hgetall(stats_key)

            if not stats:
                return None

            hits = int(stats.get(b"hits", 0))
            misses = int(stats.get(b"misses", 0))
            total = hits + misses

            return hits / total if total > 0 else 0.0
        except Exception:
            return None


def delete_cache(key: str) -> bool:
    """
    删除单个缓存键

    Args:
        key: 缓存键

    Returns:
        bool: 是否成功删除（True表示删除成功或key不存在，False表示删除失败）
    """
    try:
        cache.delete(key)
        return True
    except Exception as e:
        logger.debug(f"Failed to delete cache {key}: {e}")
        return False


def delete_cache_pattern(pattern):
    """
    删除所有匹配 pattern 的 Redis key（支持通配符 *）
    """
    redis_conn = get_redis_connection("default")

    # Add the database prefix that Django Redis uses
    # Based on the debug output, keys are stored with ":1:" prefix
    db_pattern = f"*:1:{pattern}"

    cursor = 0
    found_keys = []
    while True:
        cursor, keys = redis_conn.scan(cursor=cursor, match=db_pattern, count=100)
        found_keys.extend(keys)
        if cursor == 0:
            break

    if found_keys:
        redis_conn.delete(*found_keys)


def invalidate_dir_cache(user_id, path):
    """
    清除指定用户在指定路径的目录缓存。
    同时清除该路径的所有父路径缓存（因为父目录内容也变了）。
    """
    from django.core.cache import cache
    import hashlib

    # 标准化路径
    path = path.rstrip("/") or "/"

    # 生成当前路径 key 并删除
    def make_key(p):
        raw = f"dir_cache:user:{user_id}:path:{p}"
        return "file_dir:" + hashlib.md5(raw.encode()).hexdigest()

    # 删除当前路径缓存
    cache.delete(make_key(path))
    # 可选：递归删除所有父路径缓存（更彻底）
    parts = [part for part in path.split("/") if part]
    current = ""
    for i in range(len(parts)):
        current = "/" + "/".join(parts[: i + 1])
        cache.delete(make_key(current))
    # 别忘了根目录
    cache.delete(make_key("/"))


def get_standard_cache_key(
    prefix: str,
    view_name: str,
    pk: Optional[int] = None,
    parent_pks: Optional[Dict[str, int]] = None,
    query_params: Optional[Dict] = None,
    user_id: Optional[int] = None,
    is_separated: bool = False,
    separated_type: Optional[str] = None,
) -> str:
    """
    生成标准化的缓存key

    统一缓存key命名规范，支持分离缓存标记，确保所有key格式一致。

    Args:
        prefix: 缓存键前缀，如 "courses"
        view_name: 视图名称，如 "ChapterViewSet"
        pk: 主键（可选）
        parent_pks: 父资源主键字典，如 {"course_pk": 1}
        query_params: 查询参数（可选）
        user_id: 用户ID（可选）
        is_separated: 是否是分离缓存（默认False）
        separated_type: 分离缓存类型，"GLOBAL" 或 "STATUS"（is_separated=True时有效）

    Returns:
        str: 标准化的缓存key

    格式:
        - 普通缓存: {prefix}:{view_name}[:parent_keys][:pk][:params][:user_id]
        - 分离缓存全局: {prefix}:{view_name}:SEPARATED:GLOBAL[:parent_keys][:pk]
        - 分离缓存用户: {prefix}:{view_name}:SEPARATED:STATUS[:parent_keys][:pk]:user_id={user_id}

    Examples:
        >>> get_standard_cache_key("courses", "ChapterViewSet", pk=1)
        'courses:ChapterViewSet:1'

        >>> get_standard_cache_key("courses", "ChapterViewSet", parent_pks={"course_pk": 1})
        'courses:ChapterViewSet:course_pk=1'

        >>> get_standard_cache_key("courses", "ChapterViewSet", parent_pks={"course_pk": 1}, is_separated=True, separated_type="GLOBAL")
        'courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1'

        >>> get_standard_cache_key("courses", "ChapterViewSet", parent_pks={"course_pk": 1}, user_id=123, is_separated=True, separated_type="STATUS")
        'courses:ChapterViewSet:SEPARATED:STATUS:course_pk=1:user_id=123'
    """
    key_parts = [prefix, view_name]

    # 添加分离缓存标记
    if is_separated:
        key_parts.append("SEPARATED")
        if separated_type:
            key_parts.append(separated_type)

    # 添加父资源主键（按字母顺序排序以保证一致性）
    if parent_pks:
        sorted_parent_pks = OrderedDict(sorted(parent_pks.items()))
        for key, value in sorted_parent_pks.items():
            key_parts.append(f"{key}={value}")

    # 添加主键
    if pk is not None:
        key_parts.append(str(pk))

    # 添加查询参数
    if query_params:
        sorted_params = OrderedDict(sorted(query_params.items()))
        param_str = urlencode(sorted_params, doseq=True)
        if param_str:
            key_parts.append(param_str)

    # 添加用户ID
    if user_id is not None:
        key_parts.append(f"user_id={user_id}")

    return ":".join(key_parts)


class CacheInvalidator:
    """
    统一的缓存失效API

    提供类型安全的方法来失效ViewSet和分离缓存。

    设计原则：
        - 使用静态方法，避免实例化开销
        - 封装key构造逻辑，确保一致性
        - 失效操作静默失败，不影响业务逻辑

    Examples:
        # 失效单个ViewSet实例缓存
        CacheInvalidator.invalidate_viewset(
            prefix="courses",
            view_name="ChapterViewSet",
            pk=chapter_id
        )

        # 失效用户隔离的ViewSet实例缓存
        CacheInvalidator.invalidate_viewset(
            prefix="api",
            view_name="EnrollmentViewSet",
            pk=enrollment_id,
            user_id=user_id
        )

        # 失效ViewSet列表缓存
        CacheInvalidator.invalidate_viewset_list(
            prefix="courses",
            view_name="ChapterViewSet"
        )

        # 失效用户隔离的ViewSet列表缓存
        CacheInvalidator.invalidate_viewset_list(
            prefix="api",
            view_name="EnrollmentViewSet",
            user_id=user_id
        )

        # 失效分离缓存全局数据
        CacheInvalidator.invalidate_separated_cache_global(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": course_id}
        )

        # 失效分离缓存用户状态
        CacheInvalidator.invalidate_separated_cache_user_status(
            prefix="courses",
            view_name="ChapterViewSet",
            user_id=user_id,
            parent_pks={"course_pk": course_id}
        )
    """

    @staticmethod
    def invalidate_viewset(
        prefix: str,
        view_name: str,
        pk: int,
        parent_pks: Optional[Dict[str, int]] = None,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        失效单个ViewSet实例的缓存

        何时传递 user_id：
            - 当 ViewSet 使用用户隔离缓存时（get_queryset 中过滤了 user）
            - 当缓存键包含 user_id 时，必须传递此参数才能正确失效
            - 不传递：失效全局缓存（适用于所有用户共享的对象）
            - 传递 user_id：失效特定用户的缓存（推荐用于用户隔离的场景）

        Args:
            prefix: 缓存前缀
            view_name: 视图名称
            pk: 主键
            parent_pks: 父资源主键字典（可选）
            user_id: 用户ID（可选，用于失效用户隔离缓存）
                     当ViewSet使用用户隔离缓存时，必须传递此参数以确保只失效该用户的缓存

        Returns:
            bool: 是否成功删除

        Examples:
            # 失效全局缓存对象
            CacheInvalidator.invalidate_viewset(
                prefix="courses",
                view_name="ChapterViewSet",
                pk=chapter_id
            )

            # 失效用户隔离的对象
            CacheInvalidator.invalidate_viewset(
                prefix="api",
                view_name="EnrollmentViewSet",
                pk=enrollment_id,
                user_id=user.id
            )
        """
        cache_key = get_standard_cache_key(
            prefix=prefix,
            view_name=view_name,
            pk=pk,
            parent_pks=parent_pks,
            user_id=user_id,
        )

        try:
            delete_cache(cache_key)
            logger.debug(f"Invalidated viewset cache: {cache_key}")
            return True
        except Exception as e:
            logger.debug(f"Failed to invalidate viewset cache {cache_key}: {e}")
            return False

    @staticmethod
    def invalidate_viewset_list(
        prefix: str,
        view_name: str,
        parent_pks: Optional[Dict[str, int]] = None,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        失效ViewSet列表的缓存（使用通配符匹配）

        何时传递 user_id：
            - 当 ViewSet 使用用户隔离缓存时（get_queryset 中过滤了 user）
            - 例如：EnrollmentViewSet、ChapterProgressViewSet、ProblemProgressViewSet
            - 不传递：失效所有用户的缓存（适用于全局缓存）
            - 传递 user_id：只失效该用户的缓存（推荐用于用户隔离的场景）

        Args:
            prefix: 缓存前缀
            view_name: 视图名称
            parent_pks: 父资源主键字典（可选）
            user_id: 用户ID（可选，用于失效用户隔离缓存）

        Returns:
            bool: 是否成功删除

        Examples:
            # 失效全局缓存（所有用户）
            CacheInvalidator.invalidate_viewset_list(
                prefix="courses",
                view_name="CourseViewSet"
            )

            # 失效特定用户的缓存
            CacheInvalidator.invalidate_viewset_list(
                prefix="api",
                view_name="EnrollmentViewSet",
                user_id=user.id
            )
        """
        # 构建模式以匹配所有可能的 query_params 组合
        if parent_pks:
            sorted_parent_pks = OrderedDict(sorted(parent_pks.items()))
            parent_key_str = ":".join(
                [f"{k}={v}" for k, v in sorted_parent_pks.items()]
            )
            if user_id:
                # 模式: prefix:view_name:parent_pks*user_id=X
                # 匹配: prefix:view_name:parent_pks:query_params:user_id=X
                # 以及:  prefix:view_name:parent_pks:user_id=X (无 query_params)
                pattern = f"{prefix}:{view_name}:{parent_key_str}*user_id={user_id}"
            else:
                # 模式: prefix:view_name:parent_pks:*
                # 匹配所有 query_params 和 user_id 组合
                pattern = f"{prefix}:{view_name}:{parent_key_str}:*"
        else:
            if user_id:
                # 模式: prefix:view_name:*user_id=X
                # 匹配: prefix:view_name:query_params:user_id=X
                # 以及:  prefix:view_name:user_id=X (无 query_params)
                pattern = f"{prefix}:{view_name}*user_id={user_id}"
            else:
                # 模式: prefix:view_name:*
                # 匹配所有 query_params 和 user_id 组合
                pattern = f"{prefix}:{view_name}:*"

        try:
            delete_cache_pattern(pattern)
            logger.debug(f"Invalidated viewset list cache: {pattern}")
            return True
        except Exception as e:
            logger.debug(f"Failed to invalidate viewset list cache {pattern}: {e}")
            return False

    @staticmethod
    def invalidate_separated_cache_global(
        prefix: str,
        view_name: str,
        pk: Optional[int] = None,
        parent_pks: Optional[Dict[str, int]] = None,
    ) -> bool:
        """
        失效分离缓存的全局数据

        Args:
            prefix: 缓存前缀
            view_name: 视图名称
            pk: 主键（可选）
            parent_pks: 父资源主键字典（可选）

        Returns:
            bool: 是否成功删除
        """
        cache_key = get_standard_cache_key(
            prefix=prefix,
            view_name=view_name,
            pk=pk,
            parent_pks=parent_pks,
            is_separated=True,
            separated_type="GLOBAL",
        )

        try:
            delete_cache(cache_key)
            logger.debug(f"Invalidated separated cache global: {cache_key}")
            return True
        except Exception as e:
            logger.debug(
                f"Failed to invalidate separated cache global {cache_key}: {e}"
            )
            return False

    @staticmethod
    def invalidate_separated_cache_user_status(
        prefix: str,
        view_name: str,
        user_id: int,
        pk: Optional[int] = None,
        parent_pks: Optional[Dict[str, int]] = None,
    ) -> bool:
        """
        失效分离缓存的用户状态

        Args:
            prefix: 缓存前缀
            view_name: 视图名称
            user_id: 用户ID
            pk: 主键（可选）
            parent_pks: 父资源主键字典（可选）

        Returns:
            bool: 是否成功删除
        """
        cache_key = get_standard_cache_key(
            prefix=prefix,
            view_name=view_name,
            pk=pk,
            parent_pks=parent_pks,
            user_id=user_id,
            is_separated=True,
            separated_type="STATUS",
        )

        try:
            delete_cache(cache_key)
            logger.debug(f"Invalidated separated cache user status: {cache_key}")
            return True
        except Exception as e:
            logger.debug(
                f"Failed to invalidate separated cache user status {cache_key}: {e}"
            )
            return False
