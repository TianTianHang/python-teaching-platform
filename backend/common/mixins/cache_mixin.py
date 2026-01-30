# mixins/cache_mixin.py
import logging
from rest_framework.response import Response
from ..utils.cache import get_cache_key, get_cache, set_cache, delete_cache_pattern

logger = logging.getLogger(__name__)


class CacheListMixin:
    cache_timeout = 900  # 15分钟
    cache_prefix = "api"
  
    def list(self, request, *args, **kwargs):
        # 动态获取允许的查询参数
        allowed_params = self._get_allowed_cache_params()
        # 提取父资源主键（用于嵌套路由）
        parent_pks = self._get_parent_pks()

        # Include user_id in cache key to prevent shared caching between users
        user_id = getattr(request.user, 'id', None) if request.user and hasattr(request.user, 'id') else None

        cache_key = get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            query_params=request.query_params,
            allowed_params=allowed_params,
            parent_pks=parent_pks,
            extra_params={'user_id': user_id}
        )
        cached = get_cache(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit", extra={
                'cache_key': cache_key,
                'view_name': self.__class__.__name__,
                'cache_prefix': self.cache_prefix
            })
            # Handle both Response objects and raw data
            if hasattr(cached, 'data'):
                return cached
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        # Handle Response objects for caching
        cache_data = response.data if hasattr(response, 'data') else response
        set_cache(cache_key, cache_data, self.cache_timeout)
        return response

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
            if key.endswith('_pk'):
                parent_pks[key] = str(value)
        return parent_pks

    def _get_allowed_cache_params(self):
        """获取应该包含在缓存键中的查询参数"""
        # 通用的分页和搜索参数
        common_params = {'page', 'page_size', 'limit', 'offset', 'search'}

        # 从 ViewSet 获取 filterset_fields
        filter_fields = set()
        if hasattr(self, 'filterset_fields'):
            if isinstance(self.filterset_fields, list):
                filter_fields = set(self.filterset_fields)
            elif isinstance(self.filterset_fields, dict):
                # filterset_fields 可能是字典格式 {'field': ['lookup']}
                filter_fields = set(self.filterset_fields.keys())

        # 从 ViewSet 获取 ordering_fields
        ordering_fields = set()
        if hasattr(self, 'ordering_fields'):
            if self.ordering_fields == '__all__':
                # 如果是 __all__，则不限制（但不安全，建议明确指定）
                ordering_fields = {'ordering'}
            elif isinstance(self.ordering_fields, list):
                ordering_fields = {'ordering'}  # ordering 参数本身

        # 合并所有参数
        return common_params | filter_fields | ordering_fields


class CacheRetrieveMixin:
    cache_timeout = 900
    cache_prefix = "api"

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = kwargs.get(lookup_url_kwarg)
        # 提取父资源主键（用于嵌套路由）
        parent_pks = self._get_parent_pks()
        cache_key = get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            pk=pk,
            parent_pks=parent_pks
        )
        cached = get_cache(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().retrieve(request, *args, **kwargs)
        set_cache(cache_key, response.data, self.cache_timeout)
        return response

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
            if key.endswith('_pk'):
                parent_pks[key] = str(value)
        return parent_pks


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
            if key.endswith('_pk'):
                parent_pks[key] = str(value)
        return parent_pks

    def _get_base_cache_key(self, parent_pks=None):
        """生成基础缓存键

        Args:
            parent_pks: 父资源主键字典，用于嵌套路由
        """
        return get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            parent_pks=parent_pks
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
        key = get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            pk=pk,
            parent_pks=parent_pks
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