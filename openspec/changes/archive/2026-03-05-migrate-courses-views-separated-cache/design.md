## Context

**当前状态**

`courses/views.py` 中的 `ChapterViewSet` 和 `ProblemViewSet` 使用直接 `cache.get/set` 实现分离缓存，存在以下问题：

1. **缓存 key 格式不标准**：`f"chapter:global:list:{course_id}"` 难以批量失效
2. **缺少 Observability**：无 Prometheus metrics 记录缓存命中率
3. **无缓存穿透保护**：未使用 `CacheResult.is_null_value`
4. **代码重复**：4 个方法重复实现相同逻辑
5. **TTL 硬编码**：每处单独设置 `timeout=1800`

**前置条件**

- ✅ Phase 1 已完成：`SeparatedCacheService`、`BusinessCacheService`、`CacheInvalidator` 已实现
- ✅ `get_standard_cache_key()` 已支持 `is_separated=True` 参数
- ✅ `CacheResult` 已支持穿透保护

**约束条件**

- 不修改 API 响应格式（保持向后兼容）
- 不修改业务逻辑（用户状态获取、数据合并）
- 迁移期间新旧 key 双写，确保缓存命中率不下降

## Goals / Non-Goals

**Goals:**

1. 迁移 4 个 ViewSet 方法的缓存实现到 `SeparatedCacheService`
2. 统一缓存 key 格式为 `{prefix}:{view_name}:SEPARATED:GLOBAL:...`
3. 自动记录 Prometheus metrics（缓存命中率、响应时间）
4. 添加缓存穿透保护（使用 `CacheResult.is_null_value`）
5. 添加 cache hit/miss 日志，便于排查问题

**Non-Goals:**

- ❌ 不迁移用户状态缓存（`_get_user_status_batch()`），延后到 Phase 3
- ❌ 不修改 `_merge_global_and_user_status()` 方法
- ❌ 不替换 `CacheMixin`（`file_management/views.py`）
- ❌ 不引入新的缓存后端

## Decisions

### 1. 双写策略 vs 纯新 key

**决策**：采用双写策略，过渡期 1 周

```python
# 新代码：使用 SeparatedCacheService
global_data, is_hit = SeparatedCacheService.get_global_data(
    cache_key="courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk={course_id}".format(course_id=course_id),
    data_fetcher=lambda: ChapterGlobalSerializer(...).data,
    ttl=1800
)

# 双写旧 key（过渡期 1 周）
cache.set(f"chapter:global:list:{course_id}", global_data, timeout=1800)
```

**理由**：
- 降低风险：新实现有问题可以快速回读到旧 key
- 用户体验：避免缓存命中率突降
- 成本低：额外一次 `cache.set()` 开销 < 1ms

**替代方案**：只写新 key
- ❌ 迁移初期缓存命中率会降到 0，影响用户体验

### 2. 使用 SeparatedCacheService vs 增强现有 mixin

**决策**：使用 `SeparatedCacheService.get_global_data()`

**理由**：
- **复用 Phase 1 成果**：服务层已实现完整的 metrics、穿透保护逻辑
- **无侵入**：不需要修改类的继承结构
- **灵活性高**：可以在任何方法中调用

**替代方案**：创建新的 CacheMixin
- ❌ 增加代码复杂度，需要维护两套缓存逻辑

### 3. Key 格式设计

**决策**：使用标准化的 key 格式

```
{prefix}:{view_name}:SEPARATED:GLOBAL[:parent_pks][:pk]
```

示例：
- `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1`
- `courses:ChapterViewSet:SEPARATED:GLOBAL:pk=5:parent_pk=1`
- `courses:ProblemViewSet:SEPARATED:GLOBAL:parent_pk=3`

**理由**：
- **可读性强**：key 含义清晰，便于排查问题
- **支持批量失效**：可以用 `delete_cache_pattern("courses:ChapterViewSet:SEPARATED:GLOBAL:*")` 批量删除
- **兼容 Phase 1**：`get_standard_cache_key()` 已支持此格式

### 4. 日志策略

**决策**：添加 cache hit/miss 日志

```python
if is_hit:
    logger.debug(f"Global cache HIT for course {course_id}")
else:
    logger.debug(f"Global cache MISS for course {course_id}, data fetched from DB")
```

**理由**：
- 便于排查缓存相关问题
- 不影响性能（debug 级别默认不输出）

### 5. 错误处理

**决策**：缓存操作失败不影响主流程

```python
# SeparatedCacheService 内部已实现：
# - get_cache 失败：抛出异常，由调用方处理
# - set_cache 失败：静默失败，记录 debug 日志
# - 穿透保护：is_null=True 时不写入缓存
```

**理由**：
- 缓存是优化手段，不应阻断正常业务逻辑
- Phase 1 已实现静默失败机制

## Risks / Trade-offs

### Risk 1: 缓存 key 格式变更导致缓存未命中

**风险**：新 key 格式与旧 key 不兼容，迁移后缓存命中率下降

**缓解**：
- 双写策略：同时写入新旧两个 key
- 过渡期 1 周后移除旧 key 写入
- 监控：观察 `cache_requests_total` 指标，如命中率下降 > 10% 则回滚

### Risk 2: 用户状态缓存未迁移导致不一致

**风险**：全局数据用新 key，用户状态用旧 key，合并逻辑可能出问题

**缓解**：
- Scope 明确：本 change 只迁移全局数据缓存
- TODO 注释：标记用户状态缓存在 Phase 3 迁移
- 集成测试：验证全局数据 + 用户状态的合并逻辑正确

### Risk 3: Prometheus metrics 前缀变化

**风险**：Grafana dashboard 使用旧 key 前缀，迁移后监控图失效

**缓解**：
- 过渡期：同时记录新旧两套 metrics
- Dashboard 更新：同步更新 Grafana 查询
- 1 周后移除旧 metrics 记录

### Trade-off: 灵活性 vs 简洁性

**选择**：优先灵活性，接受额外参数

```python
# 灵活但参数多
SeparatedCacheService.get_global_data(
    cache_key="...",        # 自定义 key
    data_fetcher=lambda: ...,  # 数据获取回调
    ttl=1800                # 可配置 TTL
)

# 不灵活但简洁
get_chapter_list_cache(course_id)  # 硬编码
```

**理由**：服务层价值在于封装通用逻辑，保留灵活性便于未来扩展

## Migration Plan

### 步骤 1: 准备测试

1. 更新 `backend/courses/tests/test_views.py` 中的 mock 期望
2. 添加集成测试：`test_separated_cache_migration`
3. 创建测试辅助函数：`mock_separated_cache_service()`

### 步骤 2: 迁移 ChapterViewSet.list()

```python
# 旧代码 (line 456-468)
global_cache_key = f"chapter:global:list:{course_id}"
global_data = cache.get(global_cache_key)
if global_data is None:
    chapters = Chapter.objects.filter(course_id=course_id)...
    global_data = ChapterGlobalSerializer(chapters, many=True).data
    cache.set(global_cache_key, global_data, timeout=1800)

# 新代码
from common.services import SeparatedCacheService

cache_key = get_standard_cache_key(
    prefix="courses",
    view_name="ChapterViewSet",
    parent_pks={"course_pk": course_id},
    is_separated=True
)
global_data, is_hit = SeparatedCacheService.get_global_data(
    cache_key=cache_key,
    data_fetcher=lambda: ChapterGlobalSerializer(
        Chapter.objects.filter(course_id=course_id).select_related("course").order_by("order"),
        many=True
    ).data,
    ttl=1800
)

# 双写旧 key（过渡期）
cache.set(f"chapter:global:list:{course_id}", global_data, timeout=1800)

# 添加日志
if is_hit:
    logger.debug(f"Global cache HIT for course {course_id}")
else:
    logger.debug(f"Global cache MISS for course {course_id}, data fetched from DB")
```

### 步骤 3: 迁移其他 3 个方法

- `ChapterViewSet.retrieve()`：同上，key 格式 `courses:ChapterViewSet:SEPARATED:GLOBAL:pk={chapter_id}:parent_pk={course_id}`
- `ProblemViewSet.list()`：同上，key 格式 `courses:ProblemViewSet:SEPARATED:GLOBAL:parent_pk={chapter_id}`
- `ProblemViewSet.retrieve()`：同上，key 格式 `courses:ProblemViewSet:SEPARATED:GLOBAL:pk={problem_id}:parent_pk={chapter_id}`

### 步骤 4: 验证

1. 运行单元测试：`pytest backend/courses/tests/test_views.py -v -k "chapter or problem"`
2. 运行集成测试：`pytest backend/courses/tests/test_cache_integration.py -v`
3. 手动测试：
   - 访问 `/api/courses/1/chapters/`
   - 访问 `/api/courses/1/chapters/5/`
   - 检查 Redis 中 key 是否正确创建
   - 检查 Prometheus metrics

### 步骤 5: 监控与回滚

**监控指标**：
- 缓存命中率：`rate(cache_requests_total{key_prefix=~"courses:.*"}[5m])`
- 响应时间：`rate(http_request_duration_seconds{path=~"/api/courses/.*chapters"}[5m])`

**回滚条件**：
- 缓存命中率下降 > 10%
- 响应时间增加 > 20%
- 功能错误（数据不一致）

**回滚方式**：`git revert <commit>`

## Open Questions

### Q1: 过渡期结束后是否需要清理旧 key？

**选项**：
- **A**：使用 `delete_cache_pattern()` 批量清理旧 key
- **B**：等待 TTL 过期（30 分钟后自动失效）

**倾向**：选择 A，理由：
- 及时清理旧 key 释放 Redis 内存
- 避免旧 key 残留导致监控数据混乱

**待确认**：清理时机（1 周后的某个凌晨？）

### Q2: 是否需要在过渡期添加监控告警？

**选项**：
- **A**：添加缓存命中率告警（阈值 < 50%）
- **B**：不添加告警，人工监控

**倾向**：选择 A，理由：
- 及时发现问题
- 降低回滚风险

**待确认**：告警阈值设置