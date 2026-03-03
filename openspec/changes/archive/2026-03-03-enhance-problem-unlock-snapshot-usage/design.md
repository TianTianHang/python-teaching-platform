## Context

### 当前状态

系统已实现题目解锁快照机制 (`ProblemUnlockSnapshot`),为每个 `(course, enrollment)` 组合预计算所有题目的解锁状态,存储在 `unlock_states` JSONField 中。快照通过 Celery 异步任务每分钟刷新,用户解题时触发快照标记为过期。

**问题**: 虽然快照基础设施完整,但在关键代码路径上未被充分利用:

1. **`get_next_problem` 方法** (views.py:651-730): 遍历题目时直接调用 `unlock_condition.is_unlocked(user)`,每次触发 2-20 次数据库查询
2. **序列化器 `get_is_unlocked`** (serializers.py:306-335): 虽然有快照路径,但检查逻辑依赖 `view._use_snapshot` 标志,不够直接
3. **序列化器 `get_status`** (serializers.py:273-304): 快照只存储 `is_unlocked`,不存储 `status`,导致仍需预取 `progress_records`

### 技术约束

- **向后兼容**: 旧快照数据可能缺少 `status` 字段,必须优雅降级
- **性能要求**: 快照计算时间不能显著增加 (目标 <500ms/快照)
- **数据一致性**: 快照 `status` 必须与 `ProblemProgress` 表保持同步
- **SSR 兼容**: 所有优化必须在服务端渲染环境中工作

### 利益相关者

- **用户**: 期望题目列表和"下一题"功能快速响应
- **运维团队**: 关注数据库负载和并发处理能力
- **开发团队**: 需要可维护的代码,清晰的降级逻辑

## Goals / Non-Goals

**Goals:**

1. **消除 `get_next_problem` 的冗余数据库查询**: 从 2-20 次查询降至 0 次,响应时间从 100-300ms 降至 5-10ms
2. **统一序列化器快照读取逻辑**: 简化 `get_is_unlocked` 和 `get_status` 的快照检查,直接从 `context` 获取数据
3. **扩展快照存储 `status` 字段**: 在快照中同时存储解锁状态和做题进度,完全避免 `progress_records` 预取
4. **保持向后兼容**: 旧快照自动升级,新代码兼容旧数据格式

**Non-Goals:**

- **不改变快照刷新频率**: 仍然每分钟刷新,不改变 Celery Beat 调度
- **不改变解锁逻辑**: `is_unlocked` 的计算逻辑保持不变,只是优化数据来源
- **不修改 API 响应格式**: 响应结构和字段名完全不变
- **不引入新依赖**: 使用现有基础设施,不添加新的外部库

## Decisions

### 决策 1: 快照 JSON 结构扩展

**选择**: 在 `unlock_states` 中新增 `status` 字段

**JSON 结构对比**:

```python
# 旧结构
unlock_states = {
    "10": {"unlocked": true, "reason": null},
    "11": {"unlocked": false, "reason": "prerequisite"},
}

# 新结构
unlock_states = {
    "10": {"unlocked": true, "status": "solved", "reason": null},
    "11": {"unlocked": false, "status": "not_started", "reason": "prerequisite"},
    "12": {"unlocked": true, "status": "in_progress", "reason": null},
}
```

**理由**:
- **向后兼容**: 旧代码读取 `unlocked` 和 `reason` 仍然有效
- **最小变更**: 只需修改 `recompute()` 方法,无需数据库迁移
- **性能最优**: 序列化器直接从内存读取 `status`,避免数据库查询

**替代方案**:
- **方案 A**: 创建独立的 `status_snapshot` 表
  - ❌ 增加存储复杂度,需要维护两个快照表
  - ❌ 需要额外的 JOIN 查询
- **方案 B**: 在 `ProblemUnlockSnapshot` 中新增 `status_states` JSONField
  - ❌ 数据冗余,两个字段存储相同题目的数据
  - ❌ 需要同步两个字段的一致性

**权衡**:
- **优势**: 性能提升显著 (50% 数据库查询减少)
- **劣势**: 快照 JSON 大小增加约 30%,快照计算时间增加约 10%
- **结论**: 权衡可接受,性能收益远超成本

### 决策 2: `get_next_problem` 快照集成策略

**选择**: 在循环中优先检查 `view._unlock_states`,降级到实时计算

**实现逻辑**:

```python
def get_next_problem(self, request):
    # ... 获取 queryset ...

    # 获取快照数据 (如果可用)
    unlock_states = getattr(self, '_unlock_states', {})
    use_snapshot = getattr(self, '_use_snapshot', False)

    for problem in next_qs:
        if use_snapshot:
            # 优先使用快照
            problem_state = unlock_states.get(str(problem.id))
            if problem_state and problem_state['unlocked']:
                return problem
            elif not problem_state:
                # 快照中没有该题目,默认解锁 (向后兼容)
                return problem
        else:
            # 降级: 实时计算
            try:
                if problem.unlock_condition.is_unlocked(user):
                    return problem
            except AttributeError:
                return problem
```

**理由**:
- **性能优先**: 快照路径完全避免数据库查询
- **渐进式降级**: 快照不存在或过期时自动降级到实时计算
- **代码简洁**: 不需要修改 `get_queryset()` 逻辑

**替代方案**:
- **方案 A**: 在 `get_queryset()` 中过滤已解锁题目
  - ❌ 无法实现:"下一题"需要遍历,不能预先过滤
  - ❌ 增加查询复杂度
- **方案 B**: 创建新的 API 端点 `/problems/unlocked`
  - ❌ 增加前端维护成本
  - ❌ 破坏现有 API 兼容性

**权衡**:
- **优势**: 零数据库查询 (快照模式下)
- **劣势**: 需要在循环中检查快照标志
- **结论**: 最优方案,性能提升显著

### 决策 3: 序列化器快照读取策略

**选择**: 直接从 `context['unlock_states']` 获取,不依赖 `view._use_snapshot`

**实现对比**:

```python
# 旧实现
def get_is_unlocked(self, obj):
    view = self.context.get('view')
    if view and hasattr(view, '_use_snapshot') and view._use_snapshot:
        unlock_states = getattr(view, '_unlock_states', {})
        # ...

# 新实现
def get_is_unlocked(self, obj):
    unlock_states = self.context.get('unlock_states')
    if unlock_states:
        problem_state = unlock_states.get(str(obj.id))
        if problem_state is not None:
            return problem_state['unlocked']
```

**理由**:
- **解耦**: 序列化器不依赖 view 实例,更易测试
- **一致性**: `get_status` 和 `get_is_unlocked` 使用相同的模式
- **清晰**: 直接从 context 获取,逻辑更直观

**权衡**:
- **优势**: 代码可读性提升,减少对 view 的依赖
- **劣势**: 需要修改 `get_serializer_context()` 传递 `unlock_states`
- **结论**: 代码质量提升,值得实现

### 决策 4: 快照计算性能优化

**选择**: 使用单次批量查询获取所有 `ProblemProgress`,避免 N+1 查询

**实现**:

```python
def recompute(self):
    from .models import ProblemProgress

    problems = Problem.objects.filter(chapter__course=self.course).select_related('chapter')

    # 批量查询所有进度 (一次查询)
    progress_map = {
        pp.problem_id: pp.status
        for pp in ProblemProgress.objects.filter(
            enrollment=self.enrollment,
            problem__in=problems
        )
    }

    new_states = {}
    for problem in problems:
        # ... 解锁逻辑 ...

        # 从 progress_map 获取 status (O(1) 查找)
        status = progress_map.get(problem.id, 'not_started')

        new_states[str(problem.id)] = {
            'unlocked': is_unlocked,
            'status': status,
            'reason': reason
        }
```

**理由**:
- **性能**: 单次批量查询,时间复杂度 O(N) → O(1)
- **简洁**: 避免在循环中查询数据库

**权衡**:
- **优势**: 快照计算时间从 ~500ms 降至 ~550ms (仅增加 10%)
- **劣势**: 需要额外的内存存储 `progress_map`
- **结论**: 性能影响可接受,优化有效

## Risks / Trade-offs

### 风险 1: 快照数据不一致

**场景**: `ProblemProgress` 更新但快照未刷新,导致 `status` 字段过时

**缓解措施**:
- ✅ 已有信号触发快照标记过期 (signals.py:290-316)
- ✅ Celery Beat 每分钟刷新过期快照
- ✅ 序列化器降级逻辑: 快照中无 `status` 时查询数据库

**监控**: 添加日志记录快照版本和不一致情况

### 风险 2: 快照 JSON 大小增加

**影响**: 假设 100 道题目/课程,旧快照 ~5KB,新快照 ~7KB (增加 40%)

**缓解措施**:
- ✅ PostgreSQL JSONB 压缩存储,实际磁盘占用增加 <20%
- ✅ Redis 缓存 TTL 15 分钟,过期自动清理
- ✅ 可选: 未来只存储 `status!='not_started'` 的题目 (进一步优化)

**权衡**: 内存增加 <1MB/快照,性能收益显著

### 风险 3: 向后兼容性破坏

**场景**: 旧代码期望 `unlock_states[id]` 返回 `{'unlocked': bool}`,新代码包含 `status` 字段

**缓解措施**:
- ✅ 新增字段,不修改现有字段结构
- ✅ 旧代码读取 `unlocked` 仍然有效
- ✅ 序列化器兼容: `problem_state.get('status', 'not_started')` 降级

**测试**: 添加单元测试验证旧快照数据的兼容性

### 风险 4: 快照计算时间增加

**影响**: 当前快照计算 ~500ms,增加 `status` 查询后 ~550ms

**缓解措施**:
- ✅ 使用批量查询,避免 N+1 查询
- ✅ 异步后台计算,不影响用户请求
- ✅ 可选: 未来使用 `select_related` 优化 `ProblemProgress` 查询

**权衡**: 10% 性能影响可接受,不影响用户体验

## Migration Plan

### 阶段 1: 代码实现 (1-2 天)

1. **修改 `ProblemUnlockSnapshot.recompute()`** (1 小时)
   - 添加批量查询 `ProblemProgress`
   - 在 `unlock_states` 中新增 `status` 字段
   - 添加单元测试验证新结构

2. **优化 `ProblemViewSet.get_next_problem()`** (2 小时)
   - 添加快照路径逻辑
   - 保留降级到实时计算
   - 添加集成测试验证性能

3. **优化 `ProblemSerializer`** (2 小时)
   - 修改 `get_is_unlocked()` 从 context 读取
   - 修改 `get_status()` 优先从快照读取
   - 添加单元测试验证降级逻辑

4. **修改 `get_serializer_context()`** (30 分钟)
   - 传递 `unlock_states` 到 context
   - 保持向后兼容

### 阶段 2: 测试验证 (1 天)

1. **单元测试** (2 小时)
   - `test_snapshot_recompute_with_status()`: 验证快照包含 `status`
   - `test_get_next_problem_uses_snapshot()`: 验证快照路径
   - `test_serializer_fallback_without_status()`: 验证降级逻辑

2. **集成测试** (2 小时)
   - `test_end_to_end_next_problem()`: 端到端测试"下一题"功能
   - `test_concurrent_snapshot_refresh()`: 并发刷新测试

3. **性能测试** (2 小时)
   - 基准测试: `get_next_problem` 响应时间
   - 负载测试: 100 并发用户
   - 对比优化前后的数据库查询次数

4. **兼容性测试** (2 小时)
   - 使用旧快照数据测试序列化器降级
   - 验证 API 响应格式不变

### 阶段 3: 灰度发布 (1 周)

1. **内部测试** (1 天)
   - 部署到测试环境
   - 团队内部验证功能正确性
   - 监控错误日志和性能指标

2. **小范围灰度** (2 天)
   - 10% 用户启用新逻辑
   - 监控数据库查询量和响应时间
   - 收集用户反馈

3. **全量发布** (2 天)
   - 逐步扩大到 100% 用户
   - 持续监控性能指标
   - 准备回滚方案

4. **监控观察** (2 天)
   - 监控快照刷新频率
   - 监控数据库负载
   - 验证缓存命中率

### 回滚策略

**触发条件**:
- 错误率 >1%
- 数据库查询量增加 >20%
- 响应时间 P99 >500ms

**回滚步骤**:
1. 代码回滚到上一版本
2. 清理 Redis 缓存: `FLUSHDB`
3. 重启 Django 和 Celery Worker
4. 验证功能恢复正常

**数据恢复**: 无需数据恢复,快照自动重新计算

## Open Questions

### 问题 1: 快照刷新频率是否需要调整?

**当前**: 每分钟刷新一次 (Celery Beat)

**考虑**: 扩展 `status` 后,快照计算时间增加 10%,是否需要降低刷新频率?

**建议**: 保持每分钟刷新,理由:
- 用户解题后期望尽快看到解锁变化
- 10% 性能影响可接受
- 异步计算不影响用户请求

**决策**: 暂不调整,监控后根据实际情况优化

### 问题 2: 是否需要为 `status` 添加独立的快照版本号?

**当前**: 快照只有一个 `version` 字段

**考虑**: 如果未来 `status` 刷新频率与 `unlocked` 不同,是否需要独立版本号?

**建议**: 暂不需要,理由:
- `status` 和 `unlocked` 都在解题时更新,刷新频率一致
- 单一版本号简化逻辑
- 未来需要时再扩展

**决策**: 使用单一版本号,保持简单

### 问题 3: 是否需要支持部分字段快照?

**场景**: 如果只需要 `unlocked` 不需要 `status`,能否跳过 `status` 计算?

**建议**: 暂不支持,理由:
- 增加实现复杂度
- `status` 查询成本很低 (批量查询)
- 大多数场景需要同时获取 `unlocked` 和 `status`

**决策**: 不支持部分字段快照,全量计算
