# utils/cache.py
import json
from urllib.parse import urlencode
from collections import OrderedDict
from django.core.cache import cache
from django_redis import get_redis_connection


def get_cache_key(prefix, view_name=None, pk=None, query_params=None, allowed_params=None, parent_pks=None):
    """生成带查询参数（含分页）的缓存 key

    Args:
        prefix: 缓存键前缀
        view_name: 视图名称
        pk: 主键
        query_params: 查询参数
        allowed_params: 允许包含在缓存键中的参数列表（如果为 None，使用默认列表）
        parent_pks: 父资源主键字典，用于嵌套路由（如 {"course_pk": 1, "chapter_pk": 5}）
    """
    key_parts = [prefix]
    if view_name:
        key_parts.append(view_name)

    # 添加父资源主键（按字母顺序排序以保证一致性）
    if parent_pks:
        sorted_parent_pks = OrderedDict(sorted(parent_pks.items()))
        for key, value in sorted_parent_pks.items():
            key_parts.append(f"{key}={value}")

    if pk is not None:
        key_parts.append(str(pk))

    if query_params:
        # 如果没有提供 allowed_params，使用默认的通用参数列表（向后兼容）
        if allowed_params is None:
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
    path = path.rstrip('/') or '/'

    # 生成当前路径 key 并删除
    def make_key(p):
        raw = f"dir_cache:user:{user_id}:path:{p}"
        return "file_dir:" + hashlib.md5(raw.encode()).hexdigest()

    # 删除当前路径缓存
    cache.delete(make_key(path))
    # 可选：递归删除所有父路径缓存（更彻底）
    parts = [part for part in path.split('/') if part]
    current = ''
    for i in range(len(parts)):
        current = '/' + '/'.join(parts[:i+1])
        cache.delete(make_key(current))
    # 别忘了根目录
    cache.delete(make_key('/'))