# 分离缓存策略文档

## 概述

本文档详细说明了Python教学平台的分离缓存策略，包括缓存键设计、TTL策略、失效机制和监控方案。

## 设计目标

1. **提升缓存命中率**：全局数据跨用户共享，减少重复缓存
2. **降低内存占用**：避免为每个用户存储相同全局数据
3. **精细化失效控制**：用户状态更新不影响全局数据缓存
4. **保持API兼容性**：响应格式完全不变，前端无需修改

## 缓存层架构

### 两层缓存模型

```python
# 旧缓存模型（单一缓存）
cache_key = f"api:ChapterViewSet:{params}:user_id={user_id}"
cache_data = {
    "id": 1,
    "title": "第一章",           # 全局数据
    "content": "...",           # 全局数据
    "status": "completed",      # 用户状态
    "is_locked": false          # 用户状态
}
# 问题：100章节 × 1000用户 = 100,000缓存条目

# 新缓存模型（分离缓存）
# 全局数据缓存
global_key = f"chapter:global:{chapter_id}"
global_data = {
    "id": 1,
    "title": "第一章",
    "content": "..."
}

# 用户状态缓存
status_key = f"chapter:status:{course_id}:{user_id}"
status_data = {
    "1": {"status": "completed", "is_locked": false},
    "2": {"status": "in_progress", "is_locked": false}
}

# 优势：100全局 + 1000状态 = 1,100缓存条目（节省98.9%内存）
```

## 缓存键设计规范

### 命名规范

```
{resource}:{scope}:{identifier}:{user_id?}

- resource: 资源类型 (chapter, problem)
- scope: 缓存范围 (global, status)
- identifier: 资源标识符 (id, list:{parent_id})
- user_id: 用户标识（仅用于状态缓存）
```

### 全局数据缓存键

```python
# 单个章节
chapter:global:{chapter_id}
# 示例: chapter:global:123

# 章节列表
chapter:global:list:{course_id}
# 示例: chapter:global:list:5

# 单个问题
problem:global:{problem_id}
# 示例: problem:global:456

# 问题列表
problem:global:list:{chapter_id}
# 示例: problem:global:list:789
```

### 用户状态缓存键

```python
# 章节用户状态
chapter:status:{course_id}:{user_id}
# 示例: chapter:status:5:1001

# 问题用户状态
problem:status:{chapter_id}:{user_id}
# 示例: problem:status:789:1001
```

## TTL策略

### 全局数据TTL

```python
GLOBAL_DATA_TTL = 1800  # 30分钟

# 原因：
# - 全局数据变更频率低
# - 可以接受较长的缓存时间
# - 减少数据库查询压力
```

### 用户状态TTL

```python
USER_STATUS_TTL = 300  # 5分钟

# 原因：
# - 用户状态变更频率高
# - 需要保证数据一致性
# - 短TTL确保快速更新
```

### 特殊情况处理

```python
# 空结果保护
EMPTY_RESULT_TTL = 60  # 1分钟

# 防止缓存穿透
if data is None or data == []:
    cache.set(key, NULL_VALUE, timeout=EMPTY_RESULT_TTL)
```

## 缓存失效机制

### 失效触发器

#### 1. 用户进度变更

```python
# 信号监听
@receiver([post_save, post_delete], sender=ChapterProgress)
def on_chapter_progress_change(sender, instance, **kwargs):
    """
    用户章节进度变更 → 失效用户状态缓存
    """
    user_id = instance.enrollment.user_id
    course_id = instance.chapter.course_id
    
    # 失效用户状态缓存
    cache.delete(f"chapter:status:{course_id}:{user_id}")
    
    # 全局数据缓存不受影响
```

#### 2. 内容更新

```python
# 信号监听
@receiver(post_save, sender=Chapter)
def on_chapter_content_change(sender, instance, **kwargs):
    """
    章节内容变更 → 失效全局数据缓存
    """
    chapter_id = instance.id
    course_id = instance.course_id
    
    # 失效全局数据缓存
    cache.delete(f"chapter:global:{chapter_id}")
    cache.delete(f"chapter:global:list:{course_id}")
    
    # 用户状态缓存不受影响
```

### 失效粒度

| 操作 | 失效缓存类型 | 影响范围 |
|------|-------------|---------|
| 用户完成章节 | 用户状态缓存 | 单用户 |
| 用户解决问题 | 用户状态缓存 | 单用户 |
| 修改章节标题 | 全局数据缓存 | 所有用户 |
| 修改问题难度 | 全局数据缓存 | 所有用户 |
| 修改解锁条件 | 全局数据缓存 | 所有用户 |

## 缓存合并逻辑

### 合并策略

```python
def merge_global_and_user_status(global_data, user_status):
    """
    合并全局数据和用户状态
    
    Args:
        global_data: 全局数据列表
        user_status: 用户状态映射 {id: {status, is_locked}}
    
    Returns:
        合并后的数据列表
    """
    result = []
    
    for item in global_data:
        item_id = str(item['id'])
        status_info = user_status.get(item_id, {})
        
        # 复制全局数据
        merged = dict(item)
        
        # 合并用户状态
        merged['status'] = status_info.get('status', 'not_started')
        merged['is_locked'] = status_info.get('is_locked', True)
        
        result.append(merged)
    
    return result
```

### 降级策略

```python
def get_with_fallback(cache_key, query_fn, ttl):
    """
    获取缓存，支持降级
    
    1. 尝试从缓存获取
    2. 缓存未命中，执行查询函数
    3. 回填缓存
    4. 返回数据
    """
    data = cache.get(cache_key)
    
    if data is None:
        # 缓存未命中，从数据库查询
        data = query_fn()
        
        # 回填缓存
        cache.set(cache_key, data, timeout=ttl)
    
    return data
```

## 性能优化

### 批量查询

```python
# 优化前：N+1查询
for chapter in chapters:
    status = get_user_status(chapter.id, user.id)  # N次查询

# 优化后：批量查询
chapter_ids = [c.id for c in chapters]
statuses = get_user_status_batch(chapter_ids, user.id)  # 1次查询
```

### Redis Pipeline

```python
# 使用Redis Pipeline批量获取
pipe = cache.client.pipeline()
for key in keys:
    pipe.get(key)
results = pipe.execute()
```

### 预取优化

```python
# Django ORM预取
queryset = Chapter.objects.prefetch_related(
    'unlock_condition__prerequisite_chapters'
).select_related('course')
```

## 监控指标

### 缓存命中率

```python
# 监控指标
GLOBAL_CACHE_HIT_RATE = target > 90%
USER_STATUS_CACHE_HIT_RATE = target > 80%

# 计算方式
hit_rate = cache_hits / (cache_hits + cache_misses) * 100%
```

### 内存占用

```python
# 监控指标
CACHE_ENTRY_COUNT = target < 0.1% of old strategy
MEMORY_USAGE = target < 1% of Redis max memory

# 计算方式
entries = len(cache.keys("chapter:*")) + len(cache.keys("problem:*"))
```

### 响应时间

```python
# 监控指标
CACHE_HIT_RESPONSE_TIME = target < 5ms
CACHE_MISS_RESPONSE_TIME = target < 50ms
AVERAGE_RESPONSE_TIME = target < 30ms
```

## 故障排查

### 缓存未命中

**症状：**
- 缓存命中率低
- 数据库查询频繁

**排查步骤：**
1. 检查缓存键是否正确
2. 检查TTL是否过短
3. 检查缓存容量是否足够
4. 检查缓存失效是否过于频繁

**解决方案：**
```bash
# Redis CLI检查缓存
redis-cli
> KEYS chapter:global:*
> TTL chapter:global:123
> GET chapter:global:123
```

### 数据不一致

**症状：**
- 用户看到过期数据
- 状态更新不生效

**排查步骤：**
1. 检查信号处理器是否正常工作
2. 检查缓存失效逻辑是否正确
3. 检查TTL设置是否合理

**解决方案：**
```python
# 手动清除缓存
cache.delete(f"chapter:status:{course_id}:{user_id}")

# 或清除所有匹配的缓存
cache.delete_pattern(f"chapter:status:{course_id}:*")
```

### 内存泄漏

**症状：**
- Redis内存持续增长
- 缓存条目数异常

**排查步骤：**
1. 检查是否有缓存未设置TTL
2. 检查是否有缓存未被失效
3. 检查是否有缓存键泄漏

**解决方案：**
```bash
# 查看内存使用
redis-cli INFO memory

# 查看键数量
redis-cli DBSIZE

# 查看键分布
redis-cli --scan --pattern "chapter:*" | wc -l
```

## 最佳实践

### 1. 缓存键设计

```python
# ✓ 好的缓存键设计
"chapter:global:123"           # 清晰、有层级、易于管理
"problem:status:456:1001"     # 包含所有必要信息

# ✗ 不好的缓存键设计
"cache_123"                   # 无语义、难管理
"chapter_user_123_456_789"    # 格式不统一
```

### 2. TTL设置

```python
# ✓ 好的TTL设置
GLOBAL_CACHE_TTL = 1800       # 全局数据长TTL
USER_STATUS_TTL = 300         # 用户状态短TTL

# ✗ 不好的TTL设置
ALL_CACHE_TTL = 60            # 所有缓存短TTL，命中率低
ALL_CACHE_TTL = 86400         # 所有缓存长TTL，数据过期
```

### 3. 失效策略

```python
# ✓ 好的失效策略
# 精细化失效，只失效必要的缓存
def on_progress_change(instance):
    cache.delete(f"status:{user_id}")

# ✗ 不好的失效策略
# 粗暴失效，影响面过大
def on_any_change(instance):
    cache.flush_all()  # 失效所有缓存
```

### 4. 错误处理

```python
# ✓ 好的错误处理
try:
    data = cache.get(key)
    if data is None:
        data = db_query()
        cache.set(key, data, ttl)
except Exception as e:
    logger.error(f"Cache error: {e}")
    data = db_query()  # 降级到数据库

# ✗ 不好的错误处理
data = cache.get(key)  # 缓存失败就报错
```

## 迁移指南

### 从旧缓存迁移到新缓存

1. **并行运行**：新旧缓存策略同时运行
2. **灰度切换**：通过feature flag控制
3. **监控观察**：观察缓存命中率和性能
4. **完全切换**：确认无问题后完全切换
5. **清理旧缓存**：等待旧缓存自动过期

```python
# Feature flag控制
SEPARATED_CACHE_ENABLED = os.getenv('SEPARATED_CACHE_ENABLED', 'false')

if SEPARATED_CACHE_ENABLED == 'true':
    # 使用新分离缓存策略
    return separated_cache_logic()
else:
    # 使用旧缓存策略
    return old_cache_logic()
```

## 相关文档

- [API文档](./separated-cache-api.md)
- [运维文档](./operations.md)
- [设计文档](../openspec/changes/separate-cache-global-user/design.md)
