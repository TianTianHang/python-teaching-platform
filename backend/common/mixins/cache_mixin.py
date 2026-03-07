# mixins/cache_mixin.py
import logging
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger("teaching_platform.cache")

# Import the CacheResult class and cache key functions
from common.utils.cache import (
    CacheResult,
    get_standard_cache_key,
    get_cache,
    set_cache,
    AdaptiveTTLCalculator,
    delete_cache_pattern,
)

# Import cache metrics (optional)
try:
    from common.metrics import (
        record_cache_hit,
        record_cache_miss,
        record_cache_null_value,
    )
except ImportError:
    record_cache_hit = None
    record_cache_miss = None
    record_cache_null_value = None

"""
统一的缓存 Mixin 模块

该模块提供了统一的缓存机制：
1. StandardCacheListMixin: 标准缓存列表 Mixin
   - 使用 get_standard_cache_key() 生成缓存键
   - 自动检测用户隔离缓存
   - 支持自适应 TTL
   - 支持按需预热

2. StandardCacheRetrieveMixin: 标准缓存详情 Mixin
   - 类似于列表Mixin，针对单个资源检索优化

3. InvalidateCacheMixin
   - 用于在 CRUD 操作时自动清除缓存
   - 使用 get_standard_cache_key()

迁移状态:
- 已完成: 所有ViewSet迁移到新系统
- 已完成: cache_warming迁移到新系统
- 已完成: 删除旧CacheListMixin和CacheRetrieveMixin类
- 已完成: signals.py 统一使用 CacheInvalidator
"""

# 导入按需预热任务（延迟导入避免循环依赖）
_warm_on_demand_cache = None


def _get_warming_task():
    """延迟获取预热任务函数，避免模块导入时的循环依赖"""
    global _warm_on_demand_cache
    if _warm_on_demand_cache is None:
        try:
            from common.cache_warming.tasks import warm_on_demand_cache

            _warm_on_demand_cache = warm_on_demand_cache
        except ImportError:
            logger.warning("Cache warming task not available")
            _warm_on_demand_cache = False
    return _warm_on_demand_cache


# 预热阈值：当剩余 TTL 少于此值时，触发按需预热
STALE_TTL_THRESHOLD = 60  # 秒


class InvalidateCacheMixin:
    cache_prefix = "api"

    def _get_parent_pks(self):
        """从 self.kwargs 中提取父资源主键（用于嵌套路由）

        DRF 嵌套路由会在 kwargs 中包含 {parent_lookup}_{lookup_field} 格式的键，
        例如: course_pk=1, chapter_pk=5 等。

        Returns:
            dict: 父资源主键字典，按字母顺序排序
        """
        parent_pks = {}
        for key, value in self.kwargs.items():
            # DRF 嵌套路由的父资源键以 _pk 结尾
            if key.endswith("_pk"):
                parent_pks[key] = str(value)
        return parent_pks

    def _get_base_cache_key(self, parent_pks=None):
        """生成基础缓存键

        Args:
            parent_pks: 父资源主键字典，用于嵌套路由
        """
        return get_standard_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            parent_pks=parent_pks,
        )

    def _invalidate_all_list_cache(self):
        """清除所有分页列表缓存（如 page=1, page=2...）

        对于嵌套路由，只清除当前父资源下的缓存。
        例如：只清除 course_pk=1 的 chapters 缓存，不影响 course_pk=2 的缓存。
        """
        parent_pks = self._get_parent_pks()
        base_key = self._get_base_cache_key(parent_pks=parent_pks)
        delete_cache_pattern(f"{base_key}:*")

    def _invalidate_detail_cache(self, pk):
        """清除单个对象缓存

        对于嵌套路由，会包含父资源主键以确保只清除正确的缓存。
        """
        parent_pks = self._get_parent_pks()
        key = get_standard_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            pk=pk,
            parent_pks=parent_pks,
        )
        from django.core.cache import cache

        cache.delete(key)

    def perform_create(self, serializer):
        instance = serializer.save()
        self._invalidate_all_list_cache()
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self._invalidate_all_list_cache()
        self._invalidate_detail_cache(instance.pk)
        return instance

    def perform_destroy(self, instance):
        pk = instance.pk
        super().perform_destroy(instance)
        self._invalidate_all_list_cache()
        self._invalidate_detail_cache(pk)


# ============================================================================
# 新标准缓存 Mixin（使用 get_standard_cache_key）
# ============================================================================


class StandardCacheListMixin:
    """
    标准缓存列表 Mixin

    使用 get_standard_cache_key() 生成统一的缓存键，自动检测并注入 user_id。

    特性:
        - 使用 get_standard_cache_key() 统一key格式
        - 自动检测用户隔离缓存（通过 _is_user_specific_queryset()）
        - 支持自适应 TTL
        - 支持缓存穿透保护
        - 支持按需预热（stale-while-revalidate）

    示例:
        class CourseViewSet(StandardCacheListMixin, viewsets.ModelViewSet):
            cache_prefix = "courses"
            cache_timeout = 900
    """

    cache_timeout = 900  # 15分钟
    cache_prefix = "api"

    def list(self, request, *args, **kwargs):
        """带缓存的列表视图"""
        # Initialize request-level cache stats
        if not hasattr(request, "_cache_stats"):
            request._cache_stats = {
                "hits": 0,
                "misses": 0,
                "null_values": 0,
                "duration_ms": 0.0,
            }

        # 动态获取允许的查询参数
        allowed_params = self._get_allowed_cache_params()
        # 提取父资源主键（用于嵌套路由）
        parent_pks = self._get_parent_pks()

        # 自动检测是否需要用户隔离缓存
        user_id = None
        if request.user and hasattr(request.user, "id"):
            if self._is_user_specific_queryset():
                user_id = request.user.id
                # Set a flag for middleware to detect user-isolated caching
                self.cache_user_isolated = True

        # 提取查询参数
        query_params = self._extract_query_params(request.query_params, allowed_params)

        # 使用 get_standard_cache_key 生成缓存键
        cache_key = get_standard_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            parent_pks=parent_pks,
            query_params=query_params,
            user_id=user_id,
        )

        # 使用 get_cache 获取缓存（返回 CacheResult 对象）
        cached = get_cache(cache_key, return_result=True)

        if cached and cached.is_hit:
            # 缓存命中
            logger.debug(f"Cache hit for key: {cache_key}")
            return Response(cached.data)

        if cached and cached.is_null_value:
            # 缓存穿透保护：返回 404
            return Response({"detail": "Not found"}, status=404)

        # 缓存未命中，调用父类获取数据
        response = super().list(request, *args, **kwargs)

        # 检查是否是空结果
        response_data = response.data if hasattr(response, "data") else response
        is_empty = response_data in ([], {}, None)

        # 使用默认 TTL 设置缓存
        cache_timeout = 60 if is_empty else self.cache_timeout
        set_cache(cache_key, response_data, cache_timeout)

        return response

    def _is_user_specific_queryset(self) -> bool:
        """
        检测当前 ViewSet 是否使用用户隔离的 queryset

        通过检查 get_queryset() 方法是否过滤了 user 相关字段来判断。

        Returns:
            bool: 如果 queryset 包含用户过滤则返回 True
        """
        # 检查 get_queryset() 方法的源代码是否包含 user 过滤
        import inspect

        try:
            # 获取 get_queryset 方法
            get_queryset_method = getattr(self, "get_queryset", None)
            if get_queryset_method is None:
                return False

            # 获取方法源代码
            source = inspect.getsource(get_queryset_method)

            # 检查是否包含用户过滤关键字
            user_filter_patterns = [
                "filter(user",
                "filter(user'",
                ".filter(user=",
                "=self.request.user",
                "= request.user",
                "filter(enrollment__user",
                "filter(enrollment__user'",
            ]

            source_lower = source.lower()
            for pattern in user_filter_patterns:
                if pattern in source_lower:
                    return True

            return False
        except (TypeError, OSError):
            # 无法获取源代码时，保守返回 False
            return False

    def _extract_query_params(self, query_params, allowed_params):
        """
        提取并过滤查询参数

        Args:
            query_params: QueryDict 对象
            allowed_params: 允许的参数集合

        Returns:
            dict: 过滤后的查询参数字典
        """
        if not allowed_params:
            return {}

        result = {}
        for key in allowed_params:
            if key in query_params:
                value = query_params.getlist(key)
                if len(value) == 1:
                    result[key] = value[0]
                else:
                    result[key] = value
        return result

    def _get_parent_pks(self):
        """从 self.kwargs 中提取父资源主键（用于嵌套路由）

        DRF 嵌套路由会在 kwargs 中包含 {parent_lookup}_{lookup_field} 格式的键，
        例如: course_pk=1, chapter_pk=5 等。

        Returns:
            dict: 父资源主键字典，按字母顺序排序
        """
        parent_pks = {}
        for key, value in self.kwargs.items():
            # DRF 嵌套路由的父资源键以 _pk 结尾
            if key.endswith("_pk"):
                parent_pks[key] = str(value)
        return parent_pks

    def _get_allowed_cache_params(self):
        """获取应该包含在缓存键中的查询参数"""
        # 通用的分页和搜索参数
        common_params = {"page", "page_size", "limit", "offset", "search", "exclude"}

        # 从 ViewSet 获取 filterset_fields
        filter_fields = set()
        if hasattr(self, "filterset_fields"):
            if isinstance(self.filterset_fields, list):
                filter_fields = set(self.filterset_fields)
            elif isinstance(self.filterset_fields, dict):
                # filterset_fields 可能是字典格式 {'field': ['lookup']}
                filter_fields = set(self.filterset_fields.keys())

        # 从 ViewSet 获取 ordering_fields
        ordering_fields = set()
        if hasattr(self, "ordering_fields"):
            if self.ordering_fields == "__all__":
                # 如果是 __all__，则不限制（但不安全，建议明确指定）
                ordering_fields = {"ordering"}
            elif isinstance(self.ordering_fields, list):
                ordering_fields = {"ordering"}  # ordering 参数本身

        # 合并所有参数
        return common_params | filter_fields | ordering_fields


class StandardCacheRetrieveMixin:
    """
    标准缓存详情 Mixin

    使用 get_standard_cache_key() 生成统一的缓存键，自动检测并注入 user_id。

    特性:
        - 使用 get_standard_cache_key() 统一key格式
        - 自动检测用户隔离缓存（通过 _is_user_specific_queryset()）
        - 支持自适应 TTL
        - 支持缓存穿透保护
        - 支持按需预热（stale-while-revalidate）

    示例:
        class CourseViewSet(StandardCacheRetrieveMixin, viewsets.ModelViewSet):
            cache_prefix = "courses"
            cache_timeout = 900
    """

    cache_timeout = 900
    cache_prefix = "api"

    def retrieve(self, request, *args, **kwargs):
        """带缓存的详情视图"""
        # Initialize request-level cache stats
        if not hasattr(request, "_cache_stats"):
            request._cache_stats = {
                "hits": 0,
                "misses": 0,
                "null_values": 0,
                "duration_ms": 0.0,
            }

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = kwargs.get(lookup_url_kwarg)

        # 提取父资源主键（用于嵌套路由）
        parent_pks = self._get_parent_pks()

        # 自动检测是否需要用户隔离缓存
        user_id = None
        if request.user and hasattr(request.user, "id"):
            if self._is_user_specific_queryset():
                user_id = request.user.id

        # Get allowed params for cache key
        allowed_params = self._get_allowed_cache_params()
        query_params = self._extract_query_params(request.query_params, allowed_params)

        # 使用 get_standard_cache_key 生成缓存键
        cache_key = get_standard_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            pk=pk,
            parent_pks=parent_pks,
            query_params=query_params,
            user_id=user_id,
        )

        # 使用 get_cache 获取缓存（返回 CacheResult 对象）
        cached = get_cache(cache_key, return_result=True)

        if cached and cached.is_hit:
            # 缓存命中
            logger.debug(f"Cache hit for key: {cache_key}")
            return Response(cached.data)

        if cached and cached.is_null_value:
            # 缓存穿透保护：返回 404
            return Response({"detail": "Not found"}, status=404)

        # 缓存未命中，调用父类获取数据
        response = super().retrieve(request, *args, **kwargs)

        # 检查是否是空结果
        response_data = response.data if hasattr(response, "data") else response
        is_empty = response_data in ([], {}, None)

        # 使用默认 TTL 设置缓存
        cache_timeout = 60 if is_empty else self.cache_timeout
        set_cache(cache_key, response_data, cache_timeout)

        return response

    def _is_user_specific_queryset(self) -> bool:
        """
        检测当前 ViewSet 是否使用用户隔离的 queryset

        通过检查 get_queryset() 方法是否过滤了 user 相关字段来判断。

        Returns:
            bool: 如果 queryset 包含用户过滤则返回 True
        """
        # 检查 get_queryset() 方法的源代码是否包含 user 过滤
        import inspect

        try:
            # 获取 get_queryset 方法
            get_queryset_method = getattr(self, "get_queryset", None)
            if get_queryset_method is None:
                return False

            # 获取方法源代码
            source = inspect.getsource(get_queryset_method)

            # 检查是否包含用户过滤关键字
            user_filter_patterns = [
                "filter(user",
                "filter(user'",
                ".filter(user=",
                "=self.request.user",
                "= request.user",
                "filter(enrollment__user",
                "filter(enrollment__user'",
            ]

            source_lower = source.lower()
            for pattern in user_filter_patterns:
                if pattern in source_lower:
                    return True

            return False
        except (TypeError, OSError):
            # 无法获取源代码时，保守返回 False
            return False

    def _extract_query_params(self, query_params, allowed_params):
        """
        提取并过滤查询参数

        Args:
            query_params: QueryDict 对象
            allowed_params: 允许的参数集合

        Returns:
            dict: 过滤后的查询参数字典
        """
        if not allowed_params:
            return {}

        result = {}
        for key in allowed_params:
            if key in query_params:
                value = query_params.getlist(key)
                if len(value) == 1:
                    result[key] = value[0]
                else:
                    result[key] = value
        return result

    def _get_parent_pks(self):
        """从 self.kwargs 中提取父资源主键（用于嵌套路由）

        DRF 嵌套路由会在 kwargs 中包含 {parent_lookup}_{lookup_field} 格式的键，
        例如: course_pk=1, chapter_pk=5 等。

        Returns:
            dict: 父资源主键字典，按字母顺序排序
        """
        parent_pks = {}
        for key, value in self.kwargs.items():
            # DRF 嵌套路由的父资源键以 _pk 结尾
            if key.endswith("_pk"):
                parent_pks[key] = str(value)
        return parent_pks

    def _get_allowed_cache_params(self):
        """获取应该包含在缓存键中的查询参数"""
        # 通用的分页和搜索参数
        common_params = {"page", "page_size", "limit", "offset", "search", "exclude"}

        # 从 ViewSet 获取 filterset_fields
        filter_fields = set()
        if hasattr(self, "filterset_fields"):
            if isinstance(self.filterset_fields, list):
                filter_fields = set(self.filterset_fields)
            elif isinstance(self.filterset_fields, dict):
                # filterset_fields 可能是字典格式 {'field': ['lookup']}
                filter_fields = set(self.filterset_fields.keys())

        # 从 ViewSet 获取 ordering_fields
        ordering_fields = set()
        if hasattr(self, "ordering_fields"):
            if self.ordering_fields == "__all__":
                # 如果是 __all__，则不限制（但不安全，建议明确指定）
                ordering_fields = {"ordering"}
            elif isinstance(self.ordering_fields, list):
                ordering_fields = {"ordering"}  # ordering 参数本身

        # 合并所有参数
        return common_params | filter_fields | ordering_fields
