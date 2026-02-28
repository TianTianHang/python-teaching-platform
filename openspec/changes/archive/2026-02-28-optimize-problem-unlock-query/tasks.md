# 任务清单：Problem 解锁查询优化

## 概述

**核心策略**：直接复用 Chapter 的成熟快照模式，快速实现 Problem 性能优化。

**预计时间**：2-3 天（比 Chapter 快 3-4 倍，因为模式已验证）

**复用比例**：~85% 的代码逻辑直接参考 Chapter 实现

---

## Phase 1: 数据模型与基础服务（0.5 天）

### 1.1 创建 ProblemUnlockSnapshot 模型
**文件**: `backend/courses/models.py`

- [x] 添加 `ProblemUnlockSnapshot` 模型定义
  - [x] 外键字段：`course`, `enrollment`
  - [x] JSONField：`unlock_states`（格式：`{"problem_id": {"unlocked": bool, "reason": str}}`）
  - [x] 元数据字段：`computed_at`, `is_stale`, `version`
  - [x] Meta 配置：`unique_together`, `indexes`
- [x] 实现 `recompute()` 方法
  - [x] 遍历课程所有题目
  - [x] 调用 `ProblemUnlockCondition.is_unlocked(user)`（复用现有逻辑）
  - [x] 构建解锁状态 JSON
  - [x] 更新 `unlock_states`, `is_stale`, `version`
- [x] 添加模型测试
  - [x] 测试快照创建
  - [x] 测试 `recompute()` 逻辑（包括有/无前置题目的情况）
  - [x] 测试 JSON 序列化

**依赖**: 无
**预计时间**: 1.5-2 小时
**参考**: `CourseUnlockSnapshot` 实现（models.py:1158-1296）
**测试命令**: `uv run python manage.py test courses.tests.test_models`

---

### 1.2 创建数据库迁移
**文件**: `backend/courses/migrations/XXXX_add_problem_unlock_snapshot.py`

- [x] 生成迁移文件：`python manage.py makemigrations courses`
- [x] 检查生成的迁移是否正确
  - [x] 表名：`problem_unlock_snapshot`
  - [x] 所有字段定义正确
  - [x] 索引创建正确
- [x] 测试迁移执行
  - [x] 在测试数据库执行：`python manage.py migrate courses`
  - [x] 验证表结构
  - [x] 回滚测试：`python manage.py migrate courses zero`

**依赖**: 1.1
**预计时间**: 30 分钟
**测试命令**: `uv run python manage.py migrate courses && uv run python manage.py showmigrations courses`

---

### 1.3 实现 ProblemUnlockSnapshotService
**文件**: `backend/courses/services.py`

- [x] 添加 `ProblemUnlockSnapshotService` 类
  - [x] `get_or_create_snapshot(enrollment)` - 获取或创建快照
  - [x] `mark_stale(enrollment)` - 标记快照为过期
  - [x] `get_unlock_status_hybrid(course, enrollment)` - 混合查询策略
  - [x] `_compute_realtime(course, enrollment)` - 实时计算（降级）
- [x] 添加服务测试
  - [x] 测试 `get_or_create_snapshot()`
  - [x] 测试 `mark_stale()`
  - [x] 测试 `get_unlock_status_hybrid()` - 快照新鲜
  - [x] 测试 `get_unlock_status_hybrid()` - 快照过期
  - [x] 测试 `get_unlock_status_hybrid()` - 无快照
  - [x] 测试 `_compute_realtime()` - 降级逻辑

**依赖**: 1.1
**预计时间**: 2-3 小时
**参考**: `UnlockSnapshotService` 实现（services.py:506-656）
**测试命令**: `uv run python manage.py test courses.tests.test_services`

---

## Phase 2: Celery 异步任务（0.5 天）

### 2.1 创建 Problem 相关 Celery 任务
**文件**: `backend/courses/tasks.py`

- [x] 实现 `refresh_problem_unlock_snapshot(enrollment_id)` 任务
  - [x] 使用 `@shared_task` 装饰器（参考 `refresh_unlock_snapshot`）
  - [x] 配置重试策略（`max_retries=3`, `default_retry_delay=60`）
  - [x] 实现快照刷新逻辑
  - [x] 添加结构化日志
  - [x] 错误处理和重试
- [x] 实现 `batch_refresh_stale_problem_snapshots(batch_size=200)` 任务
  - [x] 查询过期快照（`is_stale=True`）
  - [x] 限制数量（`LIMIT batch_size`）
  - [x] 为每个快照触发单独的刷新任务
  - [x] 返回处理数量
- [x] 实现 `scheduled_problem_snapshot_refresh()` 包装任务
  - [x] 调用 `batch_refresh_stale_problem_snapshots`
- [x] 添加任务测试
  - [x] 测试 `refresh_problem_unlock_snapshot()` - 成功场景
  - [x] 测试 `refresh_problem_unlock_snapshot()` - 失败重试
  - [x] 测试 `batch_refresh_stale_problem_snapshots()` - 空队列
  - [x] 测试 `batch_refresh_stale_problem_snapshots()` - 正常处理

**依赖**: 1.1, 1.3
**预计时间**: 1.5-2 小时
**参考**: `refresh_unlock_snapshot` 和 `batch_refresh_stale_snapshots` 实现（tasks.py:7-112）
**测试命令**:
```bash
# 启动 Celery worker（开发环境）
celery -A backend worker -l debug

# 运行测试
uv run python manage.py test courses.tests.test_tasks
```

---

### 2.2 配置 Celery Beat 调度
**文件**: `backend/core/celery.py` 或 `backend/core/settings.py`

- [x] 添加 Beat 调度配置
  - [x] `refresh-stale-problem-unlock-snapshots` - 每分钟执行
  - [x] `cleanup-old-problem-unlock-snapshots` - 每天凌晨 3 点执行
- [x] 验证配置正确性
  - [x] 配置格式正确
  - [x] 任务路径正确
- [ ] 添加监控（可选）
  - [ ] Flower 集成
  - [ ] 任务执行时长监控

**依赖**: 2.1
**预计时间**: 30 分钟
**参考**: Chapter Beat 配置（celery.py 或 settings.py）
**测试命令**:
```bash
# 启动 Celery beat
celery -A backend beat -l debug

# 查看已注册任务
celery -A backend inspect registered
```

---

## Phase 3: 信号处理（0.25 天）

### 3.1 添加 Problem 信号处理器
**文件**: `backend/courses/signals.py`

- [x] 实现 `mark_problem_snapshot_stale_on_progress_update()` 信号处理器
  - [x] 监听 `ProblemProgress.post_save` 信号
  - [x] 检查 `status='solved'` 条件
  - [x] 调用 `ProblemUnlockSnapshotService.mark_stale()`
  - [x] 添加错误处理（不抛出异常）
  - [x] 添加调试日志
- [x] 添加信号测试
  - [x] 测试解题时快照被标记为 stale
  - [x] 测试信号处理器异常不影响主流程
  - [x] 测试批量更新的性能

**依赖**: 1.3
**预计时间**: 1 小时
**参考**: `mark_snapshot_stale_on_progress_update` 实现（signals.py:234-275）
**测试命令**: `uv run python manage.py test courses.tests.test_signals`

---

### 3.2 验证信号连接
**文件**: `backend/courses/apps.py`

- [x] 验证 `courses.signals` 已在 `CoursesConfig.ready()` 中导入
  - [x] Chapter 实现已包含此导入
  - [x] Problem 信号处理器在同一文件中，无需额外配置
- [x] 添加集成测试
  - [x] 测试应用启动后信号正常工作

**依赖**: 3.1
**预计时间**: 15 分钟
**测试命令**: `uv run python manage.py check && uv run python manage.py test courses.tests.test_apps`

---

## Phase 4: ViewSet 优化（0.5 天）

### 4.1 修改 ProblemViewSet.get_queryset()
**文件**: `backend/courses/views.py`

- [x] 修改 `get_queryset()` 方法
  - [x] 添加快照查询逻辑（参考 ChapterViewSet）
  - [x] 判断快照是否存在和新鲜
  - [x] 快照模式：设置 `self._use_snapshot = True`, `self._unlock_states`
  - [x] 降级模式：保持原有逻辑
- [x] 添加实例变量
  - [x] `_use_snapshot` - 是否使用快照
  - [x] `_unlock_states` - 快照数据
- [x] 保持现有 prefetch_related（兼容其他字段）
- [ ] 添加 ViewSet 测试
  - [ ] 测试快照模式查询
  - [ ] 测试降级模式查询
  - [ ] 测试并发场景

**依赖**: 1.3, 2.1
**预计时间**: 2-3 小时
**参考**: `ChapterViewSet.get_queryset()` 实现（views.py:99-167）
**测试命令**: `uv run python manage.py test courses.tests.test_views`

---

### 4.2 修改 ProblemViewSet.get_serializer_context()
**文件**: `backend/courses/views.py`

- [x] 修改 `get_serializer_context()` 方法
  - [x] 传递 `_enrollment` 到 context
  - [x] 传递 `_use_snapshot` 到 context
  - [x] 传递 `_unlock_states` 到 context
- [ ] 添加测试
  - [ ] 验证 context 数据正确传递

**依赖**: 4.1
**预计时间**: 30 分钟
**参考**: `ChapterViewSet.get_serializer_context()` 实现（views.py:169-190）

---

## Phase 5: Serializer 适配（0.25 天）

### 5.1 修改 ProblemSerializer.get_is_unlocked()
**文件**: `backend/courses/serializers.py`

- [x] 修改 `get_is_unlocked()` 方法
  - [x] 优先使用快照数据（`view._use_snapshot + view._unlock_states`）
  - [x] 降级到原有逻辑（`unlock_condition.is_unlocked(user)`）
  - [x] 处理 edge cases（快照数据缺失等）
- [ ] 添加 Serializer 测试
  - [ ] 测试快照模式序列化
  - [ ] 测试降级模式序列化
  - [ ] 验证响应格式一致

**依赖**: 4.1
**预计时间**: 1-1.5 小时
**参考**: `ChapterSerializer.get_is_locked()` 实现（serializers.py:149-184）
**测试命令**: `uv run python manage.py test courses.tests.test_serializers`

---

## Phase 6: 测试与验证（0.5 天）

### 6.1 单元测试
**文件**: `backend/courses/tests/`

- [ ] 模型测试：`test_models.py`
  - [ ] `ProblemUnlockSnapshotTest`
  - [ ] 测试 CRUD 操作
  - [ ] 测试 `recompute()` 逻辑
- [ ] 服务测试：`test_services.py`
  - [ ] `ProblemUnlockSnapshotServiceTest`
  - [ ] 测试所有方法
- [ ] 任务测试：`test_tasks.py`
  - [ ] `ProblemCeleryTasksTest`
  - [ ] 测试异步任务
- [ ] 信号测试：`test_signals.py`
  - [ ] `ProblemSignalsTest`
  - [ ] 测试信号触发

**依赖**: Phase 1-5
**预计时间**: 2-3 小时
**测试命令**: `uv run python manage.py test courses.tests`

---

### 6.2 集成测试
**文件**: `backend/courses/tests/test_integration.py`（扩展）

- [ ] 端到端测试
  - [ ] 测试完整的解锁流程（解题 → 快照更新）
  - [ ] 测试快照创建 → 过期 → 刷新
  - [ ] 测试并发场景（25 并发）
- [ ] API 测试
  - [ ] `GET /api/v1/courses/{id}/problems/` - 快照模式
  - [ ] `GET /api/v1/courses/{id}/problems/` - 降级模式
  - [ ] `POST /api/v1/problems/{id}/submissions/` - 触发刷新
- [ ] 性能测试
  - [ ] 对比优化前后的查询性能
  - [ ] 验证性能提升目标（10-50 倍）

**依赖**: 6.1
**预计时间**: 2-3 小时
**测试命令**:
```bash
# 运行集成测试
uv run python manage.py test courses.tests.test_integration

# 运行性能测试
uv run python manage.py test courses.tests.test_performance
```

---

### 6.3 压力测试
**文件**: `backend/courses/tests/test_load.py` 或使用 locust

- [ ] 使用 Django test client 模拟 25 并发
  - [ ] 测试 Problem 列表 API
  - [ ] 测试解题提交 API
  - [ ] 验证无异常和死锁
- [ ] 使用 locust（可选）
  - [ ] 编写 locustfile
  - [ ] 配置用户行为
  - [ ] 执行压力测试
  - [ ] 收集性能指标
- [ ] 数据库性能分析
  - [ ] 使用 `django-silk` 分析查询
  - [ ] 使用 `EXPLAIN ANALYZE` 验证查询计划
  - [ ] 验证索引使用情况

**依赖**: 6.2
**预计时间**: 2-3 小时
**测试命令**:
```bash
# 并发测试
uv run python manage.py test courses.tests.test_load

# Locust 测试
locust -f locustfile.py --host=http://localhost:8000
```

---

## Phase 7: 部署与监控（0.5 天）

### 7.1 测试环境部署
**环境**: staging

- [ ] 部署代码
  - [ ] 合并代码到 staging 分支
  - [ ] 执行 CI/CD 流程
  - [ ] 验证部署成功
- [ ] 执行数据库迁移
  - [ ] 备份数据库
  - [ ] 执行迁移：`python manage.py migrate`
  - [ ] 验证表结构
- [ ] 重启服务
  - [ ] 重启 Django 应用
  - [ ] 重启 Celery worker
  - [ ] 重启 Celery beat
- [ ] 冒烟测试
  - [ ] 测试 Problem 列表 API
  - [ ] 测试解题提交 API
  - [ ] 验证快照创建

**依赖**: Phase 1-6
**预计时间**: 2-3 小时（包括等待部署）

---

### 7.2 性能验证（测试环境）
**环境**: staging

- [ ] 收集基线指标
  - [ ] API 响应时间（p50, p95, p99）
  - [ ] 数据库查询次数
  - [ ] 数据库连接池使用率
  - [ ] Celery 任务执行时长
- [ ] 执行压力测试
  - [ ] 10 并发
  - [ ] 25 并发
  - [ ] 50 并发
  - [ ] 100 并发
- [ ] 验证性能目标
  - [ ] 查询次数降低 98%+（从 300+ 到 2-5）
  - [ ] 响应时间降低 90%+（从 500-2000ms 到 50-100ms）
  - [ ] 无错误和异常

**依赖**: 7.1
**预计时间**: 2-3 小时

---

### 7.3 生产环境灰度发布
**环境**: production

- [ ] 阶段 1：10% 流量
  - [ ] 监控错误率和延迟
  - [ ] 验证数据一致性
- [ ] 阶段 2：50% 流量
  - [ ] 继续监控指标
  - [ ] 准备回滚预案
- [ ] 阶段 3：100% 流量
  - [ ] 全量上线
  - [ ] 持续监控
  - [ ] 编写上线报告

**依赖**: 7.2
**预计时间**: 1-2 天（观察期）

---

## Phase 8: 文档与清理（0.25 天）

### 8.1 技术文档
**文件**: `docs/` 或项目 Wiki

- [ ] 更新 API 文档（如行为有变化）
- [ ] 更新运维手册
  - [ ] Problem 快照表维护指南
  - [ ] Celery 任务监控
  - [ ] 故障排查指南
- [ ] 对比 Chapter 和 Problem 优化
  - [ ] 记录相似点和差异
  - [ ] 记录配置差异（刷新频率、批量大小等）

**依赖**: 7.3
**预计时间**: 1-1.5 小时

---

### 8.2 代码清理
**文件**: 受影响的所有文件

- [ ] 移除调试代码和注释
- [ ] 统一代码风格（black, isort）
- [ ] 移除未使用的导入
- [ ] 更新 docstring
- [ ] 代码审查：确保无遗留问题

**依赖**: 7.3
**预计时间**: 30-45 分钟
**验证命令**:
```bash
# 代码格式化
black backend/courses
isort backend/courses

# 类型检查（如果使用）
mypy backend/courses
```

---

## Phase 9: 统一优化（可选，Phase 2）

### 9.1 评估统一方案
**文件**: 设计文档

- [ ] 对比 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot`
- [ ] 评估统一为 `ContentUnlockSnapshot` 的可行性
- [ ] 评估抽象服务层的收益
- [ ] 编写统一优化提案

**依赖**: 8.2
**预计时间**: 2-3 小时

---

### 9.2 实施统一优化
**文件**: 多个文件

- [ ] 创建 `ContentUnlockSnapshot` 模型
- [ ] 迁移现有快照数据
- [ ] 创建通用服务层
- [ ] 更新 Chapter 和 Problem 代码
- [ ] 更新测试
- [ ] 灰度发布

**依赖**: 9.1
**预计时间**: 3-5 天

---

## 任务执行顺序建议

### 快速通道（2-3 天）

**Day 1 上午** (3-4 小时):
- 1.1 → 1.2 → 1.3（模型、迁移、服务）

**Day 1 下午** (3-4 小时):
- 2.1 → 2.2 → 3.1（Celery 任务和信号）

**Day 2 上午** (3-4 小时):
- 4.1 → 4.2 → 5.1（ViewSet 和 Serializer）

**Day 2 下午** (3-4 小时):
- 6.1 → 6.2（单元测试和集成测试）

**Day 3 上午** (2-3 小时):
- 6.3 → 7.1 → 7.2（压力测试和测试环境部署）

**Day 3 下午 - Day 5** (观察期):
- 7.3（生产环境灰度发布）

**Day 6** (可选):
- 8.1 → 8.2（文档和清理）

---

## 详细时间估算

| Phase | 任务 | 预计时间 | 备注 |
|-------|------|----------|------|
| Phase 1 | 数据模型与基础服务 | 4-5.5 小时 | 复用 Chapter 设计 |
| Phase 2 | Celery 异步任务 | 2-2.5 小时 | 复用 Chapter 任务 |
| Phase 3 | 信号处理 | 1.25 小时 | 复用 Chapter 信号 |
| Phase 4 | ViewSet 优化 | 2.5-3.5 小时 | 复用 Chapter ViewSet |
| Phase 5 | Serializer 适配 | 1-1.5 小时 | 复用 Chapter Serializer |
| Phase 6 | 测试与验证 | 6-9 小时 | 可并行部分测试 |
| Phase 7 | 部署与监控 | 6-8 小时 | 包括等待时间 |
| Phase 8 | 文档与清理 | 1.5-2.5 小时 | |
| Phase 9 | 统一优化（可选） | 3-5 天 | Phase 2 工作 |
| **总计（Phase 1-8）** | | **24.75-34.25 小时** | |
| **总计（含 Phase 9）** | | **3-8 天** | 取决于是否统一 |

---

## 快速参考：Chapter vs Problem 任务对比

| 任务 | Chapter 时间 | Problem 时间 | 节省 |
|------|-------------|-------------|------|
| 模型 + 迁移 | 3.5 小时 | 2 小时 | -43% |
| 服务层 | 4.5 小时 | 3 小时 | -33% |
| Celery 任务 | 3 小时 | 2 小时 | -33% |
| 信号处理 | 2.5 小时 | 1.25 小时 | -50% |
| ViewSet + Serializer | 6 小时 | 4 小时 | -33% |
| 测试 | 10 小时 | 6 小时 | -40% |
| 部署 | 8 小时 | 6 小时 | -25% |
| **总计** | **37.5 小时** | **24.25 小时** | **-35%** |

**结论**：由于模式已验证，Problem 实现比 Chapter 快 35%。

---

## 验收标准

### 功能验收

- [ ] 所有单元测试通过（100% 覆盖率目标）
- [ ] 所有集成测试通过
- [ ] API 响应格式不变（向后兼容）
- [ ] Problem 解锁逻辑与原有实现一致
- [ ] 快照模式返回正确解锁状态
- [ ] 降级模式返回正确数据

### 性能验收

- [ ] 查询次数降低 98%+（从 300+ 到 2-5）
- [ ] N+1 查询消除（0 个额外查询）
- [ ] API 延迟降低 90%+（从 500-2000ms 到 50-100ms）
- [ ] 支持 100+ 并发请求
- [ ] 数据库连接池无压力

### 数据一致性验收

- [ ] 快照与实时计算一致性 > 99%
- [ ] 不一致窗口 < 30 秒
- [ ] 无数据丢失或损坏
- [ ] 重试机制工作正常

### 运维验收

- [ ] Celery 任务正常运行
- [ ] 快照自动创建和刷新（30 秒间隔）
- [ ] 信号触发工作正常
- [ ] 日志完整可查询
- [ ] 监控指标正常
- [ ] 有回滚预案

---

## 关键文件参考清单

### 需要修改的文件

1. **`backend/courses/models.py`**
   - 添加 `ProblemUnlockSnapshot` 类（参考 `CourseUnlockSnapshot`）

2. **`backend/courses/services.py`**
   - 添加 `ProblemUnlockSnapshotService` 类（参考 `UnlockSnapshotService`）

3. **`backend/courses/tasks.py`**
   - 添加 `refresh_problem_unlock_snapshot()` 函数
   - 添加 `batch_refresh_stale_problem_snapshots()` 函数
   - 添加 `scheduled_problem_snapshot_refresh()` 函数

4. **`backend/courses/signals.py`**
   - 添加 `mark_problem_snapshot_stale_on_progress_update()` 函数

5. **`backend/courses/views.py`**
   - 修改 `ProblemViewSet.get_queryset()` 方法
   - 修改 `ProblemViewSet.get_serializer_context()` 方法

6. **`backend/courses/serializers.py`**
   - 修改 `ProblemSerializer.get_is_unlocked()` 方法

7. **`backend/core/celery.py`** 或 **`backend/core/settings.py`**
   - 添加 Problem Beat 调度配置

### 需要创建的文件

1. **`backend/courses/migrations/XXXX_add_problem_unlock_snapshot.py`**
   - 数据库迁移文件

### 参考文件（Chapter 实现）

1. **`models.py:1158-1296`** - `CourseUnlockSnapshot`
2. **`services.py:506-656`** - `UnlockSnapshotService`
3. **`tasks.py:7-112`** - Celery 任务
4. **`signals.py:234-275`** - 信号处理器
5. **`views.py:99-190`** - `ChapterViewSet`
6. **`serializers.py:149-184`** - `ChapterSerializer.get_is_locked()`

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **性能不如预期** | 低 | 中 | 已有 Chapter 验证，Problem 收益更大 |
| **数据不一致** | 低 | 高 | 混合查询策略 + 更短刷新间隔 |
| **Celery 任务堆积** | 中 | 中 | 更大批量大小（200）+ 监控 |
| **遗留代码复杂** | 中 | 低 | 保持 `is_unlocked()` 不变，仅内部调用 |
| **迁移失败** | 低 | 高 | 事务性迁移 + 回滚预案 |
| **测试覆盖不足** | 中 | 中 | 参考 Chapter 测试，复用测试模式 |

---

## 后续优化方向

### Phase 2: 统一快照表

- [ ] 合并 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot`
- [ ] 创建 `ContentUnlockSnapshot` 统一表
- [ ] 节省 30-40% 代码重复

### Phase 3: 抽象服务层

- [ ] 创建通用 `UnlockSnapshotService`
- [ ] 支持 Chapter, Problem, Quiz, Exam
- [ ] 统一接口和行为

### Phase 4: 智能刷新

- [ ] 根据用户活跃度动态调整刷新频率
- [ ] 根据内容类型调整刷新策略
- [ ] 进一步减少无效计算

---

## 总结

**核心优势**：
- ✅ 模式已验证（Chapter）
- ✅ 快速实现（2-3 天）
- ✅ 低风险（85% 复用）
- ✅ 高收益（10-50 倍性能提升）

**关键成功因素**：
1. 严格参考 Chapter 实现
2. 保持简单（避免过度设计）
3. 充分测试（复用 Chapter 测试模式）
4. 渐进式发布（灰度 + 监控）
