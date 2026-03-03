## Why

当前并发请求增加时,`ProblemViewSet` 虽然已经实现了题目解锁快照机制,但在关键路径上未充分利用,导致大量冗余数据库查询。特别是在 `get_next_problem` 接口中,每次请求仍然会触发 2-20 次数据库查询来检查题目解锁状态,严重影响并发性能和响应速度。

## What Changes

### 核心修复项

1. **修复 `get_next_problem` 方法未使用快照** (`views.py:651-730`)
   - 当前实现: 遍历题目时直接调用 `unlock_condition.is_unlocked(user)`,每次触发数据库查询
   - 优化后: 优先从 `view._unlock_states` 读取解锁状态,完全避免数据库查询
   - 预期收益: 数据库查询减少 100%,响应时间从 100-300ms 降至 5-10ms

2. **优化序列化器快照检查逻辑** (`serializers.py:306-335`)
   - 当前实现: 依赖 `view._use_snapshot` 标志来判断是否使用快照
   - 优化后: 直接从 `context['unlock_states']` 获取快照数据,逻辑更清晰
   - 预期收益: 代码可读性提升,减少对 view 实例的依赖

3. **扩展快照存储 `status` 字段** (`models.py:1378-1443`)
   - 当前实现: 快照只存储 `is_unlocked`,序列化器仍需查询 `ProblemProgress` 获取 `status`
   - 优化后: 快照同时存储 `unlocked` 和 `status`,序列化器优先从快照读取
   - 预期收益: 快照模式下完全避免 `progress_records` 预取,数据库查询减少 50%

### 实现细节

- 修改 `ProblemUnlockSnapshot.recompute()` 方法,在计算解锁状态时同时查询并存储 `ProblemProgress.status`
- 更新 `unlock_states` JSON 结构: `{"10": {"unlocked": true, "status": "solved", "reason": null}}`
- 调整 `ProblemSerializer.get_status()` 方法,优先从快照读取 `status`
- 优化 `get_next_problem` 方法,使用快照数据替代实时计算
- 简化序列化器检查逻辑,直接从 context 获取快照数据

## Capabilities

### New Capabilities

- `problem-unlock-snapshot-status`: 题目解锁快照扩展,支持同时存储解锁状态和做题进度

### Modified Capabilities

无。本变更属于性能优化,不改变对外 API 行为和需求规格。

## Impact

### 代码变更

- `backend/courses/views.py`: 修改 `ProblemViewSet.get_next_problem()` 方法,使用快照数据
- `backend/courses/serializers.py`: 优化 `ProblemSerializer.get_status()` 和 `get_is_unlocked()` 方法
- `backend/courses/models.py`: 扩展 `ProblemUnlockSnapshot.recompute()` 方法,存储 `status` 字段

### 数据库变更

- 无需数据库迁移。`unlock_states` 字段为 JSONField,结构变更无需迁移
- 快照重新计算时会自动填充新的 `status` 字段

### API 变更

- 无 API 变更。响应结构和字段保持不变,仅优化内部实现
- 向后兼容: 旧快照数据自动升级,新快照包含 `status` 字段

### 性能影响

- **正面影响**:
  - `get_next_problem` 接口响应时间减少 95% (100-300ms → 5-10ms)
  - 题目列表接口数据库查询减少 50% (快照模式下)
  - 并发处理能力提升 10-20 倍
- **负面影响**:
  - 快照 JSON 字段大小增加约 30% (新增 `status` 字段)
  - 快照计算时间增加约 10% (需额外查询 `ProblemProgress`)
  - 总体影响: 正面收益远超负面影响

### 依赖影响

- 无新增外部依赖
- 使用现有基础设施: `ProblemUnlockSnapshot`, `ProblemProgress`, Celery 异步任务

### 兼容性

- 向后兼容: 旧快照数据缺少 `status` 时,序列化器自动降级到数据库查询
- 向前兼容: 新快照包含 `status` 字段,优化路径自动生效
