## Why

当前 `/api/v1/courses/{id}/chapters/` 端点在高并发场景（25 并发）下存在严重的性能问题：

### 现状分析
1. **复杂的多重查询**：每次请求需要 5 次数据库查询 + 2 次 prefetch_related
2. **昂贵的 EXISTS 子查询**：`_annotate_is_locked()` 方法为每个章节执行 2 个 EXISTS 子查询（检查前置章节和解锁日期）
3. **Many-to-Many JOIN 开销**：每个子查询都需要 JOIN `chapter_unlock_condition_prerequisite_chapters` 中间表
4. **数组匹配性能问题**：`prerequisite_chapters__id__in=completed_chapter_ids` 在 PostgreSQL 中对数组 NOT IN 查询优化有限

### 性能数据（估算）
- 单个课程 30 章节 → 60 次 EXISTS 子查询评估
- 25 并发 → **1500 次子查询评估/秒**
- 单请求延迟：200-500ms
- 数据库连接池压力：MAX_CONNS=20 < 并发数=25，导致请求排队

### 根本原因
解锁状态是**计算密集型**而非**查询密集型**的操作。当前方案每次请求都重新计算，缺乏缓存机制。

## What Changes

### 核心策略
采用**课程级解锁状态快照表 + 混合查询策略**：
- 添加 `CourseUnlockSnapshot` 模型预计算解锁状态
- 使用 Celery 异步刷新快照（允许最终一致性）
- ViewSet 层优先使用快照，stale 时降级到实时计算

### 修改代码

#### 1. 新增模型
**`backend/courses/models.py`**
- 添加 `CourseUnlockSnapshot` 模型
- 字段：
  - `course`, `enrollment`（外键）
  - `unlock_states`（JSONField：`{"chapter_id": {"locked": bool, "reason": str|null}}`）
  - `computed_at`, `is_stale`, `version`

#### 2. 新增服务类
**`backend/courses/services.py`**
- 添加 `UnlockSnapshotService` 类：
  - `get_or_create_snapshot(enrollment)` - 获取或创建快照
  - `recompute_snapshot(snapshot)` - 重新计算解锁状态
  - `mark_stale(enrollment)` - 标记快照为过期
  - `get_unlock_status_hybrid(course, enrollment)` - 混合查询策略

#### 3. Celery 异步任务
**`backend/courses/tasks.py`**（新建）
- `refresh_unlock_snapshot(enrollment_id)` - 刷新单个快照
- `batch_refresh_stale_snapshots(batch_size=100)` - 批量刷新过期快照
- `scheduled_snapshot_refresh` - 定时任务（每分钟执行）

#### 4. 信号处理器
**`backend/courses/signals.py`**（新建）
- 监听 `ChapterProgress.post_save` 信号
- 当用户完成章节时，标记相关快照为 `stale=True`
- 触发异步刷新任务

#### 5. ViewSet 优化
**`backend/courses/views.py`**
- 修改 `ChapterViewSet.get_queryset()`：
  - 优先使用快照数据（避免复杂注解）
  - 快照不存在或 stale 时，降级到原有 `_annotate_is_locked()` 逻辑
  - 移除不必要的 `prefetch_related`（快照模式下不需要）

#### 6. 数据库迁移
**`backend/courses/migrations/XXXX_add_unlock_snapshot.py`**（新建）
- 创建 `course_unlock_snapshot` 表
- 添加索引：`(course, enrollment)`, `(is_stale, computed_at)`, `(enrollment)`

### 性能目标
- **查询次数**：从 5 次降低到 2 次/请求
- **EXISTS 子查询**：从 60 次降低到 0 次
- **单请求延迟**：从 200-500ms 降低到 20-50ms（**10-20 倍提升**）
- **25 并发数据库负载**：从 ~12500 次子查询/秒 降低到 ~50 次简单查询/秒
- **实时性**：最终一致性，最长 1 分钟延迟（可配置）

### 不包含
- 章节依赖关系图的传递闭包预计算（作为 Phase 2 优化）
- PostgreSQL 物化视图（需要单独评估）
- 前端缓存策略变更（保持现有 15 分钟缓存）

## Capabilities

### New Capabilities
- **解锁状态快照查询**：提供预计算的章节解锁状态
- **异步状态刷新**：通过 Celery 后台任务更新快照
- **混合查询降级**：快照过期时自动降级到实时计算

### Modified Capabilities
- **章节列表查询**：优化后的性能，API 接口保持不变
  - 请求：`GET /api/v1/courses/{id}/chapters/`
  - 响应：字段不变（`is_locked`, `prerequisite_progress` 等）
- **章节完成操作**：完成后异步触发快照更新
  - 请求：`POST /api/v1/courses/{id}/chapters/{id}/mark_as_completed/`
  - 响应：延迟增加 < 50ms（异步触发 Celery 任务）

## Impact

### 受影响代码
- **新增文件**：
  - `backend/courses/tasks.py` - Celery 任务定义
  - `backend/courses/signals.py` - 信号处理器
  - `backend/courses/migrations/XXXX_add_unlock_snapshot.py` - 数据库迁移

- **修改文件**：
  - `backend/courses/models.py` - 添加 `CourseUnlockSnapshot` 模型
  - `backend/courses/services.py` - 添加 `UnlockSnapshotService`
  - `backend/courses/views.py` - 优化 `ChapterViewSet.get_queryset()`
  - `backend/courses/apps.py` - 连接信号处理器
  - `backend/core/celery.py` - 注册 Celery 任务（如果需要）

### 数据库影响
- **新增表**：`course_unlock_snapshot`
  - 预估大小：`(enrollments × courses)` 行
  - 假设 1000 用户 × 10 课程 = 10,000 行
  - 单行大小：~2KB（JSON unlock_states）
  - 总存储：~20MB（可接受）
- **索引开销**：3 个 B-tree 索引
- **迁移时间**：< 1 秒（新表，无需数据迁移）

### 性能影响
- **读取性能**：显著提升（10-20 倍）
- **写入性能**：轻微降低（完成章节时需要标记 stale + 触发 Celery 任务，< 50ms）
- **数据库连接占用**：显著降低（查询从 200ms 降至 20ms，连接释放更快）
- **Redis 使用**：略微增加（Celery broker 存储任务队列）

### 可扩展性提升
- **并发支持**：从 25 并发提升到 100+ 并发（仅需调整连接池）
- **用户规模**：快照表大小随 enrollments 线性增长，但查询性能保持 O(1)
- **课程规模**：单课程章节数增加时，性能提升更明显（避免 O(n) 子查询）

### 风险与缓解
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **数据不一致** | 用户完成章节后，解锁状态延迟更新 | 1. 混合查询策略（stale 时降级到实时计算）<br>2. 关键操作后同步刷新（可选） |
| **快照计算失败** | Celery 任务失败导致快照过期 | 1. 任务重试机制（max_retries=3）<br>2. 自动降级到实时计算<br>3. 监控告警 |
| **迁移风险** | 新表创建失败 | 1. 事务性迁移（Django 默认）<br>2. 回滚预案 |
| **Celery 负载** | 大量用户完成章节时任务堆积 | 1. 批量刷新策略<br>2. 任务优先级队列<br>3. 监控任务队列长度 |

### 向后兼容性
- ✅ API 接口完全不变
- ✅ 响应格式完全不变
- ✅ 现有客户端无需修改
- ✅ 保留旧逻辑作为 fallback

## Rollout Plan

### Phase 1: 开发与测试（1-2 天）
- [ ] 实现 `CourseUnlockSnapshot` 模型
- [ ] 实现 `UnlockSnapshotService`
- [ ] 实现 Celery 任务
- [ ] 实现信号处理器
- [ ] 修改 `ChapterViewSet`
- [ ] 编写单元测试
- [ ] 编写集成测试

### Phase 2: 灰度发布（1-2 天）
- [ ] 部署到测试环境
- [ ] 压力测试（25 → 50 → 100 并发）
- [ ] 监控性能指标
- [ ] 数据一致性验证
- [ ] 生产环境灰度（10% → 50% → 100%）

### Phase 3: 监控与优化（持续）
- [ ] 添加性能监控（响应时间 p50/p95/p99）
- [ ] 添加业务监控（快照命中率、降级率）
- [ ] 根据实际负载调整刷新频率
- [ ] 优化 Celery 任务调度

### Phase 4: 清理与文档（可选）
- [ ] 移除未使用的代码
- [ ] 更新技术文档
- [ ] 编写运维手册
