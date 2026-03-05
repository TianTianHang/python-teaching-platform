# 迁移 courses/views.py 的分离缓存到统一服务层

## Why

**当前问题**

`courses/views.py` 中的 `ChapterViewSet` 和 `ProblemViewSet` 使用直接 `cache.get/set` 实现分离缓存（全局数据 + 用户状态），存在以下问题：

1. **缺少 Observability**：无 Prometheus metrics 记录缓存命中率
2. **无缓存穿透保护**：未使用 `CacheResult.is_null_value`，容易被缓存击穿
3. **Key 格式不规范**：使用 `f"chapter:global:list:{course_id}"` 格式，难以批量失效
4. **代码重复**：4 个方法（list/retrieve × 2 ViewSets）重复实现相同逻辑
5. **TTL 硬编码**：`timeout=1800` 分散在代码中，难以统一调整

**为什么现在迁移**

- ✅ Phase 1 已完成：`SeparatedCacheService`、`BusinessCacheService`、`CacheInvalidator` 服务层已实现
- ✅ 后续依赖：Phase 3-4 需要基于统一的缓存失效机制
- ✅ 风险可控：只替换缓存实现，不改变业务逻辑，保持 API 兼容

## What Changes

**迁移范围**（4 个 ViewSet 方法）

| 文件 | 方法 | 当前 Key 格式 | 新 Key 格式 |
|------|------|---------------|-------------|
| `courses/views.py` | `ChapterViewSet.list()` | `chapter:global:list:{course_id}` | `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk={course_id}` |
| `courses/views.py` | `ChapterViewSet.retrieve()` | `chapter:global:{chapter_id}` | `courses:ChapterViewSet:SEPARATED:GLOBAL:pk={chapter_id}:parent_pk={course_id}` |
| `courses/views.py` | `ProblemViewSet.list()` | `problem:global:list:{chapter_id}` | `courses:ProblemViewSet:SEPARATED:GLOBAL:parent_pk={chapter_id}` |
| `courses/views.py` | `ProblemViewSet.retrieve()` | `problem:global:{problem_id}` | `courses:ProblemViewSet:SEPARATED:GLOBAL:pk={problem_id}:parent_pk={chapter_id}` |

**代码变更**

1. **移除直接 cache 调用**：
   ```python
   # 旧代码
   global_cache_key = f"chapter:global:list:{course_id}"
   global_data = cache.get(global_cache_key)
   if global_data is None:
       global_data = ChapterGlobalSerializer(chapters, many=True).data
       cache.set(global_cache_key, global_data, timeout=1800)

   # 新代码
   global_data, is_hit = SeparatedCacheService.get_global_data(
       cache_key="courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk={course_id}".format(course_id=course_id),
       data_fetcher=lambda: ChapterGlobalSerializer(
           Chapter.objects.filter(course_id=course_id).select_related("course").order_by("order"),
           many=True
       ).data,
       ttl=1800
   )
   ```

2. **添加 cache hit/miss 日志**：
   ```python
   if is_hit:
       logger.debug(f"Global cache HIT for course {course_id}")
   else:
       logger.debug(f"Global cache MISS for course {course_id}, data fetched from DB")
   ```

3. **自动记录 Prometheus metrics**：
   - `SeparatedCacheService.get_global_data()` 内部调用 `get_cache(return_result=True)`，自动记录：
     - `cache_requests_total{operation="get", key_prefix="courses:ChapterViewSet"}`
     - `cache_operation_duration_seconds{operation="get"}`

4. **缓存穿透保护**：
   - 使用 `CacheResult.is_null_value` 标记空值，防止缓存击穿

5. **保持业务逻辑不变**：
   - 用户状态获取逻辑（`_get_user_status_batch()`）保持不变
   - 数据合并逻辑（`_merge_global_and_user_status()`）保持不变
   - 分页响应逻辑保持不变

**不迁移的内容**

- ❌ `_get_user_status_batch()` 方法：用户状态缓存迁移到 Phase 3
- ❌ `_merge_global_and_user_status()` 方法：纯业务逻辑，不涉及缓存
- ❌ CacheMixin（`file_management/views.py`）：继续用于标准 ViewSet

## Capabilities

### New Capabilities
- 无新增 capabilities，本 change 是迁移现有功能到新 API

### Modified Capabilities
- 无修改 capabilities，缓存能力已由 Phase 1 提供

## Dependencies

**依赖 Phase 1**（unified-cache-service-layer）
- ✅ `SeparatedCacheService.get_global_data()` 已实现
- ✅ `get_standard_cache_key()` 已支持 `is_separated=True`
- ✅ `CacheResult` 已支持穿透保护

**依赖现有基础设施**
- ✅ `ChapterGlobalSerializer`、`ProblemGlobalSerializer` 已存在
- ✅ `Prometheus metrics`（`cache_requests_total`, `cache_operation_duration_seconds`）已配置

## Impact

**代码变更**
- `backend/courses/views.py`：修改 4 个方法（约 80 行代码替换）

**测试变更**
- `backend/courses/tests/test_views.py`：更新缓存相关的 mock 期望
  - 旧：`mock_cache.get.return_value = None`
  - 新：`mock_get_cache.return_value = CacheResult(...)`

**兼容性影响**
- ✅ API 兼容：请求/响应格式不变
- ✅ 缓存兼容：旧缓存 key 在 TTL 过期前仍然有效，但新代码使用新 key
- ⚠️ 监控影响：需要更新 Grafana dashboard 中的缓存 key 过滤器
  - 旧：`key_prefix="chapter:global"`
  - 新：`key_prefix="courses:ChapterViewSet:SEPARATED"`

**性能影响**
- ✅ 预期性能改善：服务层开销 < 1μs（Phase 1 已验证）
- ✅ 缓存命中率保持：业务逻辑不变，缓存行为一致

## Migration Plan

**步骤 1：准备测试**
1. 更新 `test_views.py` 中的测试用例，mock `SeparatedCacheService.get_global_data`
2. 添加集成测试：验证新旧 key 格式都能正常工作（过渡期）

**步骤 2：迁移代码**
1. 修改 `ChapterViewSet.list()`：
   - 替换 cache.get/set → SeparatedCacheService.get_global_data
   - 添加 cache hit/miss 日志
   - 更新缓存 key 格式
2. 修改 `ChapterViewSet.retrieve()`：同上
3. 修改 `ProblemViewSet.list()`：同上
4. 修改 `ProblemViewSet.retrieve()`：同上

**步骤 3：验证**
1. 运行单元测试：`pytest backend/courses/tests/test_views.py -v`
2. 运行集成测试：`pytest backend/courses/tests/test_cache_integration.py -v`
3. 手动测试：
   - 访问 `/api/courses/{course_id}/chapters/`，验证返回数据正确
   - 访问 `/api/courses/{course_id}/chapters/{chapter_id}/`，验证返回数据正确
   - 检查 Prometheus metrics：`curl http://localhost:9090/metrics | grep cache_requests_total`

**步骤 4：监控**
1. 观察缓存命中率：`rate(cache_requests_total{operation="get"}[5m])`
2. 观察响应时间：`rate(http_request_duration_seconds{path=~"/api/courses/.*"}[5m])`
3. 检查日志中的 cache hit/miss 消息

**回滚计划**
- 如果缓存命中率下降 > 10%，回滚到旧实现
- 如果响应时间增加 > 20%，回滚到旧实现
- 回滚方式：`git revert <commit>`

## Risks / Trade-offs

### Risk 1: 缓存 key 格式变更导致缓存未命中

**风险**：新 key 格式导致所有现有缓存失效，短期 cache hit rate 下降

**缓解**：
- **双写策略**：在过渡期，同时写入新旧两个 key
  ```python
  # 代码实现
  global_data, is_hit = SeparatedCacheService.get_global_data(...)

  # 双写旧 key（过渡期）
  cache.set(f"chapter:global:list:{course_id}", global_data, timeout=1800)
  ```
- **灰度发布**：先在 10% 流量上使用新实现，观察 1 小时后全量
- **TTL 缩短**：过渡期将 TTL 从 1800 秒缩短到 600 秒，加快旧 key 过期

### Risk 2: 用户状态缓存逻辑未迁移导致不一致

**风险**：全局数据用新 key，用户状态用旧 key，导致合并逻辑混乱

**缓解**：
- **Scope 明确**：本 change 只迁移全局数据缓存，用户状态缓存保持不变
- **注释标记**：在代码中添加 TODO 注释，标记用户状态缓存在 Phase 3 迁移
- **测试覆盖**：添加集成测试，验证全局数据 + 用户状态的合并逻辑正确

### Risk 3: Prometheus metrics key 前缀变化影响监控

**风险**：Grafana dashboard 使用旧 key 前缀（`chapter:global`），迁移后监控图失效

**缓解**：
- **Metrics 兼容**：在 `SeparatedCacheService.get_global_data()` 中添加旧 key 前缀的 tag
  ```python
  # 添加 legacy_key_prefix 标签
  cache_metrics.labels(
      operation="get",
      key_prefix="chapter:global",  # 旧前缀
      key_type="global_data",
      status="hit"
  ).inc()
  ```
- **Dashboard 更新**：同步更新 Grafana dashboard，增加新 key 前缀的查询
- **过渡期**：同时记录新旧两套 metrics（1 周），然后移除旧 metrics

## Open Questions

### Q1: 是否需要保持旧缓存 key 的兼容性？

**问题**：迁移后是否需要继续支持旧的缓存 key 格式？

**选项**：
- **A**：双写新旧 key，完全兼容（过渡期 1 周）
- **B**：只写新 key，旧 key 自然过期（TTL 30 分钟后失效）

**倾向**：选择 A，理由：
- 降低风险：如果新实现有问题，可以快速回滚
- 用户体验：避免缓存命中率突降影响响应时间
- 成本低：双写只是额外一次 `cache.set()`，开销 < 1ms

**决策**：使用双写策略，过渡期 1 周，然后移除旧 key 写入逻辑

### Q2: 是否需要添加灰度发布机制？

**问题**：是否需要逐步放量（10% → 50% → 100%）？

**选项**：
- **A**：一次性全量发布（简单）
- **B**：灰度发布（安全）

**倾向**：选择 A，理由：
- 风险可控：已有双写策略和回滚计划
- 复杂度低：无需引入 feature flag 系统
- 测试充分：单元测试 + 集成测试 + 手动测试覆盖

**决策**：一次性全量发布，但密切监控前 2 小时的指标

### Q3: 缓存 TTL 是否需要调整？

**问题**：全局数据缓存当前 TTL=1800（30 分钟），是否需要优化？

**选项**：
- **A**：保持 1800 秒（当前值）
- **B**：延长到 3600 秒（1 小时），减少 cache miss
- **C**：缩短到 900 秒（15 分钟），提高数据新鲜度

**倾向**：选择 A，理由：
- 当前 TTL 已经过生产验证，无需贸然调整
- 章节内容变化频率低，30 分钟 TTL 合理
- 如果需要调整，应该在 Phase 3 中基于监控数据决策

**决策**：保持 TTL=1800 秒不变
