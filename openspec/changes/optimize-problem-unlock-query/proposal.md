## Why

当前 `/api/v1/courses/{id}/problems/` 和 `/api/v1/chapters/{id}/problems/` 端点在高并发场景下存在严重的性能问题，且比 Chapter 的问题更为严重：

### 现状分析

1. **真正的 N+1 查询问题**：`ProblemSerializer.get_is_unlocked()` 对每个 problem 调用 `unlock_condition.is_unlocked(user)`
2. **Model 层的遗留代码**：`ProblemUnlockCondition.is_unlocked()` 在 Model 层，未优化
3. **复杂的嵌套循环**：对每个前置 problem 查询 `ProblemProgress` 和 `Submission`
4. **无数据库层优化**：不像 Chapter 有 `_annotate_is_locked()` 的 EXISTS 子查询

### 性能数据（估算）

假设一个课程有 50 个算法题：

- **基础查询**：1 次（problems 表）
- **prefetch_related**：2 次（unlock_conditions, progress_records）
- **N+1 查询**：50 次（每个 problem 调用 `is_unlocked()`）
  - 每个 `is_unlocked()` 循环所有前置题
  - 假设平均 3 个前置题，每个检查 Progress + Submission
  - **额外查询**：50 × 3 × 2 = **300 次**

**总计**：~353 次查询/请求 😱

**25 并发场景**：353 × 25 = **8825 次查询/秒**

### 与 Chapter 对比

| 指标 | Chapter (优化后) | Problem (当前) |
|------|-----------------|---------------|
| 查询次数 | 2-5 次 | 300+ 次 |
| EXISTS 子查询 | 0 次 (快照模式) | N/A (Python 层) |
| 单请求延迟 | 20-500ms | 500-2000ms |
| 并发支持 | 100+ | 10-15 |

### 根本原因

Problem 的解锁检查在 **Python 层循环执行**，而不是数据库层批量处理。与 Chapter 不同，Problem 没有任何数据库层优化。

## What Changes

### 核心策略

**直接复用 Chapter 的成熟快照模式**：
- 添加 `ProblemUnlockSnapshot` 模型（参考 `CourseUnlockSnapshot`）
- 使用 `ProblemUnlockSnapshotService`（参考 `UnlockSnapshotService`）
- 使用 Celery 异步刷新（复用现有任务模式）
- ViewSet 和 Serializer 集成（参考 Chapter 实现）

### 修改代码

#### 1. 新增模型
**`backend/courses/models.py`**

- 添加 `ProblemUnlockSnapshot` 模型（参考 `CourseUnlockSnapshot`）
  - 字段：`enrollment`, `course`, `unlock_states`, `computed_at`, `is_stale`, `version`
  - 方法：`recompute()` - 调用 Problem 解锁逻辑
  - Meta 配置：索引、unique_together

**注意**：考虑未来统一性，可能创建 `ContentUnlockSnapshot` 替代独立的表（Phase 2）

#### 2. 新增服务类
**`backend/courses/services.py`**

- 添加 `ProblemUnlockSnapshotService` 类（参考 `UnlockSnapshotService`）
  - `get_or_create_snapshot(enrollment)` - 获取或创建快照
  - `mark_stale(enrollment)` - 标记快照为过期
  - `get_unlock_status_hybrid(course, enrollment)` - 混合查询策略
  - `_compute_realtime(course, enrollment)` - 实时计算（降级）

**或扩展** `UnlockSnapshotService` 支持 `content_type` 参数（避免重复）

#### 3. Celery 异步任务
**`backend/courses/tasks.py`**

- 添加 `refresh_problem_unlock_snapshot(enrollment_id)` - 刷新单个快照
  - 参考 `refresh_unlock_snapshot` 实现
  - 调用 `ProblemUnlockSnapshot.objects.get_or_create()`
  - 调用 `snapshot.recompute()`

- 添加 `batch_refresh_stale_problem_snapshots(batch_size=200)` - 批量刷新
  - 注意：Problem 数量更多，batch_size 可以更大（200 vs Chapter 的 100）

- 添加 `scheduled_problem_snapshot_refresh` - 定时任务
  - 调度频率：30 秒（Problem 更频繁访问，需要更短间隔）

#### 4. 信号处理器
**`backend/courses/signals.py`**

- 添加 `@receiver(post_save, sender=ProblemProgress)`
  - `mark_problem_snapshot_stale_on_progress_update()`
  - 参考 `mark_snapshot_stale_on_progress_update()` 实现
  - 当 `status='solved'` 时标记快照为过期

#### 5. ViewSet 优化
**`backend/courses/views.py`**

- 修改 `ProblemViewSet.get_queryset()`：
  - 尝试获取快照（参考 `ChapterViewSet.get_queryset()`）
  - Fresh snapshot：设置 `self._use_snapshot = True`, `self._unlock_states`
  - Stale/No snapshot：降级到原有逻辑

- 修改 `ProblemViewSet.get_serializer_context()`：
  - 传递 `_use_snapshot`, `_unlock_states` 到 Serializer

#### 6. Serializer 适配
**`backend/courses/serializers.py`**

- 修改 `ProblemSerializer.get_is_unlocked()`：
  - 优先使用快照数据（`view._use_snapshot + view._unlock_states`）
  - 降级到 `unlock_condition.is_unlocked(user)`（原有逻辑）

#### 7. 数据库迁移
**`backend/courses/migrations/XXXX_add_problem_unlock_snapshot.py`**

- 创建 `problem_unlock_snapshot` 表
- 添加索引：`(course, enrollment)`, `(is_stale, computed_at)`, `(enrollment)`

### 性能目标

- **查询次数**：从 300+ 次降低到 2-5 次/请求（-98%+）
- **N+1 查询**：从 300+ 次降低到 0 次
- **单请求延迟**：从 500-2000ms 降低到 50-100ms（-90%+）
- **并发支持**：从 10-15 并发提升到 100+ 并发
- **实时性**：最终一致性，最长 30 秒延迟（比 Chapter 更短）

### 不包含

- 统一 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot` 为单表（Phase 2 优化）
- 抽象通用服务层（Phase 2 优化）
- PostgreSQL 物化视图（暂不需要）
- 前端缓存策略变更（保持现有 15 分钟缓存）

## Capabilities

### New Capabilities

- **Problem 解锁状态快照查询**：提供预计算的题目解锁状态
- **异步状态刷新**：通过 Celery 后台任务更新快照
- **混合查询降级**：快照过期时自动降级到实时计算

### Modified Capabilities

- **Problem 列表查询**：优化后的性能，API 接口保持不变
  - 请求：`GET /api/v1/courses/{id}/problems/`
  - 请求：`GET /api/v1/chapters/{id}/problems/`
  - 响应：字段不变（`is_unlocked`, `unlock_condition_description` 等）

- **Problem 解决操作**：提交代码后异步触发快照更新
  - 请求：`POST /api/v1/problems/{id}/submissions/`
  - 影响：ProblemProgress 更新 → 标记快照 stale → Celery 刷新

## Impact

### 受影响代码

- **新增文件**：
  - `backend/courses/migrations/XXXX_add_problem_unlock_snapshot.py` - 数据库迁移

- **修改文件**：
  - `backend/courses/models.py` - 添加 `ProblemUnlockSnapshot` 模型
  - `backend/courses/services.py` - 添加/扩展 `ProblemUnlockSnapshotService`
  - `backend/courses/tasks.py` - 添加 Problem 快照刷新任务
  - `backend/courses/signals.py` - 添加 Problem 信号处理器
  - `backend/courses/views.py` - 优化 `ProblemViewSet.get_queryset()`
  - `backend/courses/serializers.py` - 优化 `ProblemSerializer.get_is_unlocked()`

### 数据库影响

- **新增表**：`problem_unlock_snapshot`
  - 预估大小：`(enrollments × courses)` 行
  - 假设 1000 用户 × 10 课程 = 10,000 行
  - 单行大小：~4KB（50 problems × 80 bytes/problem）
  - 总存储：~40MB（可接受）

- **索引开销**：3 个 B-tree 索引
- **迁移时间**：< 1 秒（新表，无需数据迁移）

### 性能影响

- **读取性能**：显著提升（10-50 倍）
- **写入性能**：轻微降低（Problem 更新时标记 stale + 触发 Celery，< 50ms）
- **数据库连接占用**：显著降低（查询从 500ms+ 降至 50ms）
- **Redis 使用**：略微增加（Celery broker 存储任务队列）

### 可扩展性提升

- **并发支持**：从 10-15 并发提升到 100+ 并发
- **用户规模**：快照表大小随 enrollments 线性增长，但查询性能保持 O(1)
- **题目规模**：单课程题目数增加时，性能提升更明显（避免 O(n) Python 循环）

### 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **数据不一致** | 用户解题后，解锁状态延迟更新 | 1. 混合查询策略（stale 时降级到实时计算）<br>2. 更短刷新间隔（30 秒 vs Chapter 1 分钟）<br>3. 关键操作后同步刷新（可选） |
| **快照计算失败** | Celery 任务失败导致快照过期 | 1. 任务重试机制（max_retries=3）<br>2. 自动降级到实时计算<br>3. 监控告警 |
| **遗留代码复杂** | `ProblemUnlockCondition.is_unlocked()` 逻辑复杂 | 1. 保持现有逻辑不变，在 recompute() 中调用<br>2. Phase 2 优化时再重构 |
| **迁移风险** | 新表创建失败 | 1. 事务性迁移（Django 默认）<br>2. 回滚预案 |

### 向后兼容性

- ✅ API 接口完全不变
- ✅ 响应格式完全不变
- ✅ 现有客户端无需修改
- ✅ 保留旧逻辑作为 fallback
- ✅ `ProblemUnlockCondition.is_unlocked()` 保持不变（仅内部调用）

## Rollout Plan

### Phase 1: 开发与测试（1-2 天）

- [ ] 实现 `ProblemUnlockSnapshot` 模型
- [ ] 实现 `ProblemUnlockSnapshotService`（或扩展现有服务）
- [ ] 实现 Celery 任务（refresh + batch + scheduled）
- [ ] 实现信号处理器
- [ ] 修改 `ProblemViewSet`
- [ ] 修改 `ProblemSerializer`
- [ ] 编写单元测试
- [ ] 编写集成测试

### Phase 2: 验证与对比（1 天）

- [ ] 部署到测试环境
- [ ] 压力测试（10 → 25 → 50 → 100 并发）
- [ ] 对比 Chapter 和 Problem 优化效果
- [ ] 验证数据一致性
- [ ] 收集性能指标

### Phase 3: 生产环境灰度（1-2 天）

- [ ] 10% 流量
- [ ] 50% 流量
- [ ] 100% 流量
- [ ] 持续监控

### Phase 4: 统一优化（可选，Phase 2）

- [ ] 评估统一 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot`
- [ ] 设计抽象服务层
- [ ] 重构代码减少重复
- [ ] 添加其他可解锁内容类型（Quiz, Exam）

## 与 Chapter 优化的对比

| 维度 | Chapter 优化 | Problem 优化（本次） |
|------|-------------|---------------------|
| **现有优化** | 有 EXISTS 子查询（已优化） | 无优化（纯 N+1） |
| **问题严重性** | 中等 | 严重 |
| **优化收益** | 高（10-20 倍） | 极高（10-50 倍） |
| **刷新频率** | 1 分钟 | 30 秒 |
| **批量大小** | 100 | 200 |
| **实现复杂度** | 中等 | 低（直接复制） |
| **风险** | 中等 | 低（模式已验证） |

## 参考文档

- Chapter 优化提案：`openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/proposal.md`
- Chapter 优化设计：`openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/design.md`
- Chapter 优化任务：`openspec/changes/archive/2026-02-28-optimize-chapter-unlock-query/tasks.md`
