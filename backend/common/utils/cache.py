# utils/cache.py
import json
from urllib.parse import urlencode
from collections import OrderedDict
from django.core.cache import cache
from django_redis import get_redis_connection


def get_cache_key(prefix, view_name=None, pk=None, query_params=None):
    """生成带查询参数（含分页）的缓存 key"""
    key_parts = [prefix]
    if view_name:
        key_parts.append(view_name)
    if pk is not None:
        key_parts.append(str(pk))

    if query_params:
        # 只保留常用可缓存参数（按需调整）
        allowed_params = {'page', 'page_size', 'limit', 'offset', 'search', 'ordering', 'status', 'type'}
        filtered = {k: v for k, v in query_params.items() if k in allowed_params}
        if filtered:
            sorted_params = OrderedDict(sorted(filtered.items()))
            param_str = urlencode(sorted_params, doseq=True)
            key_parts.append(param_str)

    return ":".join(key_parts)


def set_cache(key, value, timeout=900):  # 默认15分钟
    try:
        cache.set(key, json.dumps(value, ensure_ascii=False, default=str), timeout)
    except Exception:
        # 防止序列化失败导致接口异常
        pass


def get_cache(key):
    try:
        data = cache.get(key)
        return json.loads(data) if data is not None else None
    except Exception:
        return None


def delete_cache_pattern(pattern):
    """
    删除所有匹配 pattern 的 Redis key（支持通配符 *）
    """
    redis_conn = get_redis_connection("default")
    cursor = 0
    while True:
        cursor, keys = redis_conn.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            redis_conn.delete(*keys)
        if cursor == 0:
            break