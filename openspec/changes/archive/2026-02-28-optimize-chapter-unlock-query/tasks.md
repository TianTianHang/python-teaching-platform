# 任务清单：章节解锁查询优化

## Phase 1: 数据模型与基础服务

### 1.1 创建 CourseUnlockSnapshot 模型
**文件**: `backend/courses/models.py`

- [x] 添加 `CourseUnlockSnapshot` 模型定义
  - [x] 外键字段：`course`, `enrollment`
  - [x] JSONField：`unlock_states`
  - [x] 元数据字段：`computed_at`, `is_stale`, `version`
  - [x] Meta 配置：`unique_together`, `indexes`
- [x] 实现 `recompute()` 方法
  - [x] 遍历课程所有章节
  - [x] 调用 `ChapterUnlockService.is_unlocked()`
  - [x] 构建解锁状态 JSON
  - [x] 更新 `unlock_states`, `is_stale`, `version`
- [x] 添加模型测试
  - [x] 测试快照创建
  - [x] 测试 `recompute()` 逻辑
  - [x] 测试 JSON 序列化

**依赖**: 无
**预计时间**: 2-3 小时
**测试命令**: `uv run python manage.py test courses.tests.test_models`

---

### 1.2 创建数据库迁移
**文件**: `backend/courses/migrations/0012_courseunlocksnapshot.py`

- [x] 生成迁移文件：`python manage.py makemigrations courses`
- [x] 检查生成的迁移是否正确
  - [x] 表名：`course_unlock_snapshot`
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

### 1.3 实现 UnlockSnapshotService
**文件**: `backend/courses/services.py`

- [x] 添加 `UnlockSnapshotService` 类
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
**预计时间**: 3-4 小时
**测试命令**: `uv run python manage.py test courses.tests.test_services`

---

## Phase 2: Celery 异步任务

### 2.1 创建 tasks.py 文件
**文件**: `backend/courses/tasks.py`

- [x] 创建 `courses/tasks.py`
- [x] 实现 `refresh_unlock_snapshot(enrollment_id)` 任务
  - [x] 使用 `@shared_task` 装饰器
  - [x] 配置重试策略（`max_retries=3`, `default_retry_delay=60`）
  - [x] 实现快照刷新逻辑
  - [x] 添加结构化日志
  - [x] 错误处理和重试
  - [x] 处理 Enrollment.DoesNotExist 异常
- [x] 实现 `batch_refresh_stale_snapshots(batch_size=100)` 任务
  - [x] 查询过期快照（`is_stale=True`）
  - [x] 限制数量（`LIMIT batch_size`）
  - [x] 为每个快照触发单独的刷新任务
  - [x] 返回处理数量
  - [x] 清理 orphaned snapshots
- [x] 实现 `scheduled_snapshot_refresh()` 包装任务
  - [x] 调用 `batch_refresh_stale_snapshots`
- [x] 添加任务测试
  - [x] 测试 `refresh_unlock_snapshot()` - 成功场景
  - [x] 测试 `refresh_unlock_snapshot()` - 失败重试
  - [x] 测试 `refresh_unlock_snapshot()` - 不存在的 enrollment
  - [x] 测试 `batch_refresh_stale_snapshots()` - 空队列
  - [x] 测试 `batch_refresh_stale_snapshots()` - 正常处理
  - [x] 测试 `batch_refresh_stale_snapshots()` - 清理 orphaned snapshots

**依赖**: 1.1, 1.3
**预计时间**: 2-3 小时
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

- [ ] 添加 Beat 调度配置
  - [ ] `refresh-stale-chapter-unlock-snapshots` - 每分钟执行
  - [ ] `cleanup-old-chapter-unlock-snapshots` - 每天凌晨 2 点
- [ ] 验证配置正确性
  - [ ] 检查 Celery Beat 日志
  - [ ] 验证任务按预期调度
- [ ] 添加监控（可选）
  - [ ] Flower 集成
  - [ ] 任务执行时长监控

**依赖**: 2.1
**预计时间**: 1 小时
**测试命令**:
```bash
# 启动 Celery beat
celery -A backend beat -l debug

# 查看已注册任务
celery -A backend inspect registered
```

---

## Phase 3: 信号处理

### 3.1 创建 signals.py 文件
**文件**: `backend/courses/signals.py`

- [x] 创建 `courses/signals.py`
- [x] 实现 `mark_snapshot_stale_on_progress_update()` 信号处理器
  - [x] 监听 `ChapterProgress.post_save` 信号
  - [x] 检查 `completed=True` 条件
  - [x] 调用 `UnlockSnapshotService.mark_stale()`
  - [x] 添加错误处理（不抛出异常）
  - [x] 添加调试日志
- [x] 添加信号测试
  - [x] 测试章节完成时快照被标记为 stale
  - [x] 测试信号处理器异常不影响主流程
  - [x] 测试批量更新的性能

**依赖**: 1.3
**预计时间**: 2 小时
**测试命令**: `uv run python manage.py test courses.tests.test_signals`

---

### 3.2 连接信号到 AppConfig
**文件**: `backend/courses/apps.py`

- [x] 修改 `CoursesConfig.ready()` 方法
  - [x] 导入 `courses.signals`
  - [x] 验证信号在应用启动时连接
- [x] 添加集成测试
  - [x] 测试应用启动后信号正常工作
  - [x] 测试信号只连接一次

**依赖**: 3.1
**预计时间**: 30 分钟
**测试命令**: `uv run python manage.py check && uv run python manage.py test courses.tests.test_apps`

---

## Phase 4: ViewSet 优化

### 4.1 修改 ChapterViewSet.get_queryset()
**文件**: `backend/courses/views.py`

- [ ] 修改 `get_queryset()` 方法
  - [ ] 添加快照查询逻辑
  - [ ] 判断快照是否存在和新鲜
  - [ ] 快照模式：简化查询，跳过复杂注解
  - [ ] 降级模式：保持原有逻辑
- [ ] 添加实例变量
  - [ ] `_use_snapshot` - 是否使用快照
  - [ ] `_unlock_states` - 快照数据
- [ ] 优化 prefetch_related
  - [ ] 快照模式：跳过不必要的预取
  - [ ] 降级模式：保持原有预取
- [ ] 添加 ViewSet 测试
  - [ ] 测试快照模式查询
  - [ ] 测试降级模式查询
  - [ ] 测试并发场景

**依赖**: 1.3, 2.1
**预计时间**: 3-4 小时
**测试命令**: `uv run python manage.py test courses.tests.test_views`

---

### 4.2 优化 Serializer
**文件**: `backend/courses/serializers.py`

- [ ] 修改 `ChapterSerializer.get_is_locked()` 方法
  - [ ] 优先使用快照数据（`view._use_snapshot`）
  - [ ] 从 `view._unlock_states` 读取
  - [ ] 降级到注解（`is_locked_db`）
  - [ ] 最终降级到 service 计算
- [ ] 优化 `ChapterSerializer.get_prerequisite_progress()` 方法
  - [ ] 考虑是否需要调整（可能不需要）
- [ ] 添加 Serializer 测试
  - [ ] 测试快照模式序列化
  - [ ] 测试降级模式序列化
  - [ ] 验证响应格式一致

**依赖**: 4.1
**预计时间**: 2-3 小时
**测试命令**: `uv run python manage.py test courses.tests.test_serializers`

---

## Phase 5: 监控与可观测性

### 5.1 添加结构化日志
**文件**: `backend/courses/services.py`, `tasks.py`, `views.py`

- [ ] 在关键位置添加日志
  - [ ] `UnlockSnapshotService.get_unlock_status_hybrid()` - 记录 source
  - [ ] `refresh_unlock_snapshot()` - 记录任务执行
  - [ ] `ChapterViewSet.get_queryset()` - 记录查询模式
- [ ] 使用 JSON 格式日志
  - [ ] 包含上下文信息（course_id, enrollment_id, user_id）
  - [ ] 包含性能指标（latency_ms）
  - [ ] 包含元数据（snapshot_version, source）

**依赖**: 1.3, 2.1, 4.1
**预计时间**: 1-2 小时
**验证方式**: 查看日志输出，验证 JSON 格式和字段完整性

---

### 5.2 添加性能监控（可选）
**文件**: 新建 `backend/courses/metrics.py` 或集成到现有监控

- [ ] 添加 Prometheus 指标（可选）
  - [ ] `chapter_unlock_snapshot_hits_total` - 快照命中计数
  - [ ] `chapter_unlock_refresh_duration_seconds` - 刷新任务时长
  - [ ] `chapter_unlock_stale_snapshots_total` - 过期快照数量
- [ ] 配置 Prometheus exporter（如果项目已使用）
- [ ] 添加 Grafana 仪表板（可选）

**依赖**: 5.1
**预计时间**: 2-4 小时（取决于现有监控基础设施）
**验证方式**: 访问 `/metrics` 端点，验证指标导出

---

## Phase 6: 测试与验证

### 6.1 单元测试
**文件**: `backend/courses/tests/`

- [ ] 模型测试：`test_models.py`
  - [ ] `CourseUnlockSnapshotTest`
  - [ ] 测试 CRUD 操作
  - [ ] 测试 `recompute()` 逻辑
- [ ] 服务测试：`test_services.py`
  - [ ] `UnlockSnapshotServiceTest`
  - [ ] 测试所有方法
- [ ] 任务测试：`test_tasks.py`
  - [ ] `CeleryTasksTest`
  - [ ] 测试异步任务
- [ ] 信号测试：`test_signals.py`
  - [ ] `SignalsTest`
  - [ ] 测试信号触发

**依赖**: Phase 1-5
**预计时间**: 4-6 小时
**测试命令**: `uv run python manage.py test courses.tests`

---

### 6.2 集成测试
**文件**: `backend/courses/tests/test_integration.py`

- [ ] 端到端测试
  - [ ] 测试完整的解锁流程
  - [ ] 测试快照创建 → 过期 → 刷新
  - [ ] 测试并发场景（25 并发）
- [ ] API 测试
  - [ ] `GET /api/v1/courses/{id}/chapters/` - 快照模式
  - [ ] `GET /api/v1/courses/{id}/chapters/` - 降级模式
  - [ ] `POST /api/v1/courses/{id}/chapters/{id}/mark_as_completed/` - 触发刷新
- [ ] 性能测试
  - [ ] 对比优化前后的查询性能
  - [ ] 验证性能提升目标（10-20 倍）

**依赖**: Phase 1-5
**预计时间**: 4-6 小时
**测试命令**:
```bash
# 运行集成测试
uv run python manage.py test courses.tests.test_integration

# 运行性能测试
uv run python manage.py test courses.tests.test_performance
```

---

### 6.3 压力测试
**文件**: 新建 `backend/courses/tests/test_load.py` 或使用 locust

- [ ] 使用 Django test client 模拟 25 并发
  - [ ] 测试章节列表 API
  - [ ] 测试章节完成 API
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
**预计时间**: 4-6 小时
**测试命令**:
```bash
# 并发测试
uv run python manage.py test courses.tests.test_load

# Locust 测试
locust -f locustfile.py --host=http://localhost:8000
```

---

## Phase 7: 部署与监控

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
  - [ ] 测试章节列表 API
  - [ ] 测试章节完成 API
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
  - [ ] 25 并发
  - [ ] 50 并发
  - [ ] 100 并发
- [ ] 验证性能目标
  - [ ] 查询次数降低 60%+
  - [ ] 响应时间降低 80%+
  - [ ] 无错误和异常

**依赖**: 7.1
**预计时间**: 2-4 小时

---

### 7.3 生产环境灰度发布
**环境**: production

- [ ] 阶段 1：10% 流量
  - [ ] 启用功能开关（可选）
  - [ ] 监控错误率和延迟
  - [ ] 验证数据一致性
- [ ] 阶段 2：50% 流量
  - [ ] 扩大流量比例
  - [ ] 继续监控指标
  - [ ] 准备回滚预案
- [ ] 阶段 3：100% 流量
  - [ ] 全量上线
  - [ ] 持续监控
  - [ ] 编写上线报告

**依赖**: 7.2
**预计时间**: 2-3 天（观察期）

---

## Phase 8: 文档与清理

### 8.1 技术文档
**文件**: `docs/` 或项目 Wiki

- [ ] 更新 API 文档（如果行为有变化）
- [ ] 编写运维手册
  - [ ] 快照表维护指南
  - [ ] Celery 任务监控
  - [ ] 故障排查指南
- [ ] 更新架构文档
  - [ ] 描述优化后的架构
  - [ ] 添加数据流图

**依赖**: 7.3
**预计时间**: 2-3 小时

---

### 8.2 代码清理
**文件**: 受影响的所有文件

- [ ] 移除调试代码和注释
- [ ] 统一代码风格（black, isort）
- [ ] 移除未使用的导入
- [ ] 更新 docstring
- [ ] 代码审查：确保无遗留问题

**依赖**: 7.3
**预计时间**: 1-2 小时
**验证命令**:
```bash
# 代码格式化
black backend/courses
isort backend/courses

# 类型检查（如果使用）
mypy backend/courses
```

---

## 任务执行顺序建议

### Sprint 1（Day 1-2）
- 1.1 → 1.2 → 1.3（模型、迁移、服务）

### Sprint 2（Day 3）
- 2.1 → 2.2 → 3.1 → 3.2（Celery 任务和信号）

### Sprint 3（Day 4）
- 4.1 → 4.2（ViewSet 和 Serializer 优化）

### Sprint 4（Day 5）
- 5.1 → 6.1 → 6.2（监控和测试）

### Sprint 5（Day 6）
- 6.3 → 7.1 → 7.2（压力测试和测试环境部署）

### Sprint 6（Day 7-9）
- 7.3（生产环境灰度发布）

### Sprint 7（Day 10）
- 8.1 → 8.2（文档和清理）

---

## 总预计时间

| Phase | 任务 | 预计时间 |
|-------|------|----------|
| Phase 1 | 数据模型与基础服务 | 6-8 小时 |
| Phase 2 | Celery 异步任务 | 3-4 小时 |
| Phase 3 | 信号处理 | 2.5 小时 |
| Phase 4 | ViewSet 优化 | 5-7 小时 |
| Phase 5 | 监控与可观测性 | 3-6 小时 |
| Phase 6 | 测试与验证 | 12-18 小时 |
| Phase 7 | 部署与监控 | 6-10 小时 |
| Phase 8 | 文档与清理 | 3-5 小时 |
| **总计** | | **40.5-58.5 小时** |

**约 5-8 个工作日**（取决于测试覆盖率和复杂度）

---

## 验收标准

### 功能验收
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] API 响应格式不变（向后兼容）
- [ ] 快照覆盖率 > 95%（enrollments）

### 性能验收
- [ ] 查询次数降低 60%+（从 5 次降至 2 次）
- [ ] EXISTS 子查询降至 0 次
- [ ] API 延迟降低 80%+（从 200-500ms 降至 20-50ms）
- [ ] 25 并发场景无异常

### 数据一致性验收
- [ ] 快照与实时计算一致性 > 99%
- [ ] 不一致窗口 < 1 分钟
- [ ] 无数据丢失或损坏

### 运维验收
- [ ] Celery 任务正常运行
- [ ] 快照自动创建和刷新
- [ ] 日志完整可查询
- [ ] 监控指标正常
- [ ] 有回滚预案
