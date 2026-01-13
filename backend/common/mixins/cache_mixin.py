# mixins/cache_mixin.py
from rest_framework.response import Response
from ..utils.cache import get_cache_key, get_cache, set_cache, delete_cache_pattern


class CacheListMixin:
    cache_timeout = 900  # 15分钟
    cache_prefix = "api"

    def list(self, request, *args, **kwargs):
       
        cache_key = get_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            query_params=request.query_params
        )
        cached = get_cache(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        set_cache(cache_key, response.data, self.cache_timeout)
        return response


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