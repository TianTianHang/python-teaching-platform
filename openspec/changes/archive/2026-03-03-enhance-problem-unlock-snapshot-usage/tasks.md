## 1. 快照模型扩展

- [x] 1.1 修改 `ProblemUnlockSnapshot.recompute()` 方法,添加批量查询 `ProblemProgress`
  - 在计算解锁状态前,批量查询 `ProblemProgress.objects.filter(enrollment=self.enrollment, problem__in=problems)`
  - 构建字典 `progress_map = {pp.problem_id: pp.status for pp in progress_records}`
  - 在循环中使用 `status = progress_map.get(problem.id, 'not_started')` 获取状态

- [x] 1.2 更新 `unlock_states` JSON 结构,添加 `status` 字段
  - 修改 `new_states[str(problem.id)]` 结构为: `{"unlocked": bool, "status": str, "reason": str|null}`
  - 确保 `status` 值为 `"solved"`, `"not_started"`, `"in_progress"` 之一

- [ ] 1.3 添加单元测试验证快照包含 status
  - 创建 `tests/test_problem_unlock_snapshot.py` (如果不存在)
  - 添加测试 `test_recompute_includes_status_field()` 验证快照结构
  - 添加测试 `test_recompute_batch_query_progress()` 验证批量查询逻辑
  - 添加测试 `test_backward_compatibility_without_status()` 验证旧数据兼容性

## 2. 序列化器优化

- [x] 2.1 修改 `ProblemSerializer.get_is_unlocked()` 方法,直接从 context 读取
  - 移除对 `view._use_snapshot` 的依赖
  - 优先从 `unlock_states = self.context.get('unlock_states')` 获取数据
  - 使用 `problem_state = unlock_states.get(str(obj.id))` 查找题目状态
  - 返回 `problem_state['unlocked']` 或降级到实时计算

- [x] 2.2 修改 `ProblemSerializer.get_status()` 方法,优先从快照读取
  - 添加快照路径: 从 `context['unlock_states']` 获取 `problem_state`
  - 检查 `problem_state` 是否包含 `status` 字段
  - 如果包含,返回 `problem_state['status']`;否则降级到查询 `ProblemProgress` 表

- [ ] 2.3 添加单元测试验证序列化器快照读取
  - 添加测试 `test_get_is_unlocked_from_context()` 验证从 context 读取
  - 添加测试 `test_get_status_from_snapshot()` 验证快照读取 status
  - 添加测试 `test_get_status_fallback_to_db()` 验证降级逻辑

## 3. ViewSet 快照集成

- [x] 3.1 修改 `ProblemViewSet.get_serializer_context()` 方法,传递 unlock_states
  - 在返回 `context` 前,检查 `hasattr(self, '_unlock_states')`
  - 如果存在,添加 `context['unlock_states'] = self._unlock_states`

- [x] 3.2 优化 `ProblemViewSet.get_next_problem()` 方法,使用快照数据
  - 在循环前获取快照数据: `unlock_states = getattr(self, '_unlock_states', {})`
  - 获取快照标志: `use_snapshot = getattr(self, '_use_snapshot', False)`
  - 在 `for problem in next_qs:` 循环中:
    - 如果 `use_snapshot == True`: 从 `unlock_states.get(str(problem.id))` 获取状态
    - 如果快照中存在且 `problem_state['unlocked'] == True`: 返回该题目
    - 如果快照中不存在: 默认解锁 (向后兼容)
    - 否则降级到调用 `unlock_condition.is_unlocked(user)`

- [x] 3.3 同样优化 `has_next` 检查逻辑
  - 在检查是否存在下一个未锁定题目时,使用相同的快照逻辑

- [x] 3.4 添加集成测试验证 get_next_problem 性能
  - 创建 `tests/test_problem_viewset_snapshot.py`
  - 添加测试 `test_get_next_problem_uses_snapshot()` 验证快照路径
  - 添加测试 `test_get_next_problem_fallback_to_realtime()` 验证降级路径
  - 添加测试 `test_get_next_problem_performance()` 验证查询次数 (应为 0)

## 4. 性能测试与验证

- [x] 4.1 创建性能基准测试
  - 使用 `django.test.utils.override_settings` 关闭缓存
  - 测试 `get_next_problem` 在无快照模式下的响应时间
  - 测试 `get_next_problem` 在快照模式下的响应时间
  - 验证快照模式下响应时间 <20ms

- [x] 4.2 创建数据库查询计数测试
  - 使用 `django.test.TestCase.assertNumQueries()`
  - 验证快照模式下 `get_next_problem` 查询次数为 0 (除 queryset 外)
  - 验证序列化器在快照模式下不查询 `ProblemProgress` 表

- [ ] 4.3 创建并发测试
  - 使用 `concurrent.futures.ThreadPoolExecutor` 模拟 100 并发请求
  - 验证快照模式下无数据库连接耗尽问题
  - 验证响应时间 P99 <50ms

## 5. 兼容性测试

- [x] 5.1 测试旧快照数据兼容性
  - 手动创建旧格式快照: `{"10": {"unlocked": true, "reason": null}}` (无 status)
  - 验证序列化器 `get_status()` 降级到数据库查询
  - 验证序列化器不抛出 `KeyError` 异常

- [x] 5.2 测试 API 响应格式不变
  - 使用单元测试验证序列化器输出格式
  - 验证响应 JSON 结构包含 `id`, `title`, `has_next` 字段
  - 验证字段类型和名称与优化前完全一致

- [ ] 5.3 测试前后端兼容性
  - 使用前端 SSR 模式测试题目列表加载
  - 验证 `status` 和 `is_unlocked` 字段正确显示
  - 验证"下一题"功能正常工作

## 6. 文档与监控

- [x] 6.1 更新代码注释
  - 在 `ProblemUnlockSnapshot.recompute()` 添加注释说明批量查询优化
  - 在 `ProblemSerializer` 方法添加快照路径说明
  - 在 `ProblemViewSet.get_next_problem()` 添加快照逻辑注释

- [ ] 6.2 添加性能监控日志
  - 在 `get_next_problem()` 添加日志记录快照命中/未命中
  - 在序列化器添加日志记录快照降级次数
  - 使用 `django.utils.timezone.now()` 记录响应时间

- [ ] 6.3 创建性能监控 Dashboard (可选)
  - 使用 Grafana + Prometheus 配置监控面板
  - 监控指标: `get_next_problem` 响应时间 P50/P95/P99
  - 监控指标: 快照命中率,数据库查询次数

## 7. 部署准备

- [ ] 7.1 准备灰度发布配置
  - 创建 Django setting `PROBLEM_SNAPSHOT_STATUS_ENABLED = True`
  - 使用特性开关控制新逻辑启用

- [ ] 7.2 准备回滚脚本
  - 创建 `management/command/rollback_snapshot_status.py`
  - 实现 `FLUSHDB` 清理 Redis 缓存
  - 实现重启 Django 和 Celery Worker 命令

- [ ] 7.3 准备数据迁移脚本 (可选)
  - 创建 `management/command/regenerate_all_snapshots.py`
  - 批量重新生成所有快照,填充 `status` 字段
  - 用于手动触发快照升级

## 8. 验收与发布

- [ ] 8.1 运行完整测试套件
  - 执行 `uv run python manage.py test courses.tests`
  - 验证所有单元测试通过
  - 验证所有集成测试通过

- [ ] 8.2 执行性能回归测试
  - 使用 `locust` 或 `pytest-benchmark` 运行负载测试
  - 验证 100 并发用户下响应时间 <50ms P99
  - 验证数据库查询量减少 >40%

- [ ] 8.3 部署到测试环境
  - 合并代码到 `develop` 分支
  - 部署到测试环境
  - 团队内部验证功能正确性

- [ ] 8.4 小范围灰度发布
  - 启用 10% 流量使用新逻辑
  - 监控错误日志和性能指标 24 小时
  - 收集用户反馈

- [ ] 8.5 全量发布
  - 逐步扩大到 100% 流量
  - 持续监控性能指标 7 天
  - 准备回滚方案
