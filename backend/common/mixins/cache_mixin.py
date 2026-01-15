# mixins/cache_mixin.py
from rest_framework.response import Response
from ..utils.cache import get_cache_key, get_cache, set_cache, delete_cache_pattern


class CacheListMixin:
    cache_timeout = 900  # 15分钟
    cache_prefix = "api"

    def list(self, request, *args, **kwargs):
        # 动态获取允许的查询参数
        allowed_params = self._get_allowed_cache_params()

        cache_key = get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            query_params=request.query_params,
            allowed_params=allowed_params
        )
        cached = get_cache(cache_key)
        if cached is not None:
            print("use cache")
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        set_cache(cache_key, response.data, self.cache_timeout)
        return response

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
        cache_key = get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            pk=pk
        )
        cached = get_cache(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().retrieve(request, *args, **kwargs)
        set_cache(cache_key, response.data, self.cache_timeout)
        return response


class InvalidateCacheMixin:
    cache_prefix = "api"

    def _get_base_cache_key(self):
        return get_cache_key(prefix=self.cache_prefix, view_name=self.__class__.__name__)

    def _invalidate_all_list_cache(self):
        """清除所有分页列表缓存（如 page=1, page=2...）"""
        base_key = self._get_base_cache_key()
        delete_cache_pattern(f"{base_key}:*")

    def _invalidate_detail_cache(self, pk):
        """清除单个对象缓存"""
        key = get_cache_key(prefix=self.cache_prefix, view_name=self.__class__.__name__, pk=pk)
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