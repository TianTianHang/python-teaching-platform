## ADDED Requirements

### Requirement: 快照必须存储题目做题状态
题目解锁快照 (`ProblemUnlockSnapshot`) 的 `unlock_states` JSONField 必须同时存储题目的解锁状态 (`unlocked`) 和做题进度状态 (`status`),以便序列化器能够从快照直接获取所有用户特定数据,避免查询 `ProblemProgress` 表。

#### Scenario: 快照包含 status 字段
- **GIVEN** 一个课程有 10 道题目,用户已完成 3 道
- **WHEN** 系统重新计算题目解锁快照
- **THEN** `unlock_states` JSON 必须包含:
  - 已完成的 3 道题: `{"unlocked": true, "status": "solved", "reason": null}`
  - 未完成的 7 道题: `{"unlocked": true, "status": "not_started", "reason": null}` 或 `{"unlocked": false, "status": "not_started", "reason": "prerequisite"}`

#### Scenario: 快照批量查询 ProblemProgress
- **GIVEN** 一个课程有 100 道题目,用户已完成 50 道
- **WHEN** 系统重新计算题目解锁快照
- **THEN** 系统必须使用单次批量查询获取所有 50 条 `ProblemProgress` 记录
- **AND** 快照计算时间必须 <600ms (增加 <100ms)

#### Scenario: 向后兼容旧快照数据
- **GIVEN** 一个旧快照的 `unlock_states` 格式为 `{"10": {"unlocked": true, "reason": null}}` (无 `status` 字段)
- **WHEN** 序列化器读取该快照
- **THEN** 序列化器必须降级到查询 `ProblemProgress` 表获取 `status`
- **AND** 不得抛出 `KeyError` 或其他异常

### Requirement: 序列化器必须优先从快照读取 status
题目序列化器 (`ProblemSerializer`) 在序列化 `status` 字段时,必须优先从 `context['unlock_states']` 读取,仅在快照不存在或缺少 `status` 字段时才查询数据库。

#### Scenario: 快照包含 status 时直接返回
- **GIVEN** `context['unlock_states'] = {"10": {"unlocked": true, "status": "solved"}}`
- **WHEN** 序列化器序列化 ID=10 的题目
- **THEN** `get_status()` 方法必须返回 `"solved"`
- **AND** 不得查询 `ProblemProgress` 表

#### Scenario: 快照不包含 status 时查询数据库
- **GIVEN** `context['unlock_states'] = {"10": {"unlocked": true}}` (缺少 `status` 字段)
- **WHEN** 序列化器序列化 ID=10 的题目
- **THEN** `get_status()` 方法必须查询 `ProblemProgress` 表获取 `status`
- **AND** 返回查询结果或 `"not_started"` (如果记录不存在)

#### Scenario: 快照不存在时查询数据库
- **GIVEN** `context` 中没有 `unlock_states`
- **WHEN** 序列化器序列化题目
- **THEN** `get_status()` 方法必须使用原有逻辑查询 `ProblemProgress` 表

### Requirement: 序列化器必须直接从 context 读取 unlock_states
题目序列化器 (`ProblemSerializer`) 在读取解锁状态时,必须直接从 `context['unlock_states']` 获取,不再依赖 `view._use_snapshot` 标志,以解耦序列化器与 view 实例的依赖关系。

#### Scenario: 优先从 context 读取 unlock_states
- **GIVEN** `context['unlock_states'] = {"10": {"unlocked": true, "status": "solved"}}`
- **WHEN** `get_is_unlocked()` 方法序列化 ID=10 的题目
- **THEN** 方法必须从 `context['unlock_states']` 获取数据
- **AND** 返回 `problem_state['unlocked']` = `true`
- **AND** 不得检查 `view._use_snapshot` 标志

#### Scenario: unlock_states 不存在时降级
- **GIVEN** `context` 中没有 `unlock_states`
- **WHEN** `get_is_unlocked()` 方法执行
- **THEN** 方法必须降级到调用 `unlock_condition.is_unlocked(user)`
- **AND** 返回计算结果或 `true` (如果无解锁条件)

### Requirement: get_next_problem 必须使用快照数据
`ProblemViewSet.get_next_problem()` 方法在查找下一个未锁定题目时,必须优先使用快照数据 (`view._unlock_states`),仅在快照不存在或过期时才降级到实时计算 `unlock_condition.is_unlocked(user)`。

#### Scenario: 快照模式下遍历题目使用快照数据
- **GIVEN** 用户已访问题目列表,`view._unlock_states` 已设置
- **AND** `view._use_snapshot = true`
- **WHEN** 用户请求 `/problems/next?type=algorithm&id=10`
- **THEN** 系统必须从 `view._unlock_states` 读取后续题目的解锁状态
- **AND** 不得调用 `unlock_condition.is_unlocked(user)` 方法
- **AND** 数据库查询次数必须为 0 (除了获取 queryset)

#### Scenario: 快照过期时降级到实时计算
- **GIVEN** `view._use_snapshot = false` (快照过期或不存在)
- **WHEN** 用户请求 `/problems/next?type=algorithm&id=10`
- **THEN** 系统必须调用 `unlock_condition.is_unlocked(user)` 检查每个题目
- **AND** 返回第一个未锁定的题目

#### Scenario: 快照中没有题目时默认解锁
- **GIVEN** `view._unlock_states = {"11": {"unlocked": true}}` (不包含题目 ID=12)
- **WHEN** 遍历到 ID=12 的题目
- **THEN** 系统必须默认该题目已解锁
- **AND** 将其作为下一个题目返回

### Requirement: ViewSet 必须传递 unlock_states 到 serializer context
`ProblemViewSet` 在调用序列化器时,必须在 `get_serializer_context()` 方法中将 `view._unlock_states` 传递到 `context['unlock_states']`,以便序列化器能够直接访问快照数据。

#### Scenario: 快照存在时传递 unlock_states
- **GIVEN** `view._unlock_states = {"10": {"unlocked": true, "status": "solved"}}`
- **WHEN** `get_serializer_context()` 方法执行
- **THEN** 返回的 `context` 必须包含 `context['unlock_states']` = `view._unlock_states`

#### Scenario: 快照不存在时不传递 unlock_states
- **GIVEN** `view` 没有 `_unlock_states` 属性
- **WHEN** `get_serializer_context()` 方法执行
- **THEN** 返回的 `context` 不得包含 `unlock_states` 键

### Requirement: 快照计算必须在异步任务中执行
题目解锁快照的重新计算 (`ProblemUnlockSnapshot.recompute()`) 必须在 Celery 异步任务中执行,不得阻塞用户请求,以确保系统响应时间不受影响。

#### Scenario: 用户解题后异步刷新快照
- **GIVEN** 用户完成一道题,`ProblemProgress.status` 更新为 `"solved"`
- **WHEN** `ProblemProgress` 保存时触发 `post_save` 信号
- **THEN** 系统必须标记快照为过期 (`is_stale = true`)
- **AND** 触发异步任务 `refresh_problem_unlock_snapshot.delay(enrollment_id)`
- **AND** 不得阻塞当前 HTTP 请求

#### Scenario: 定时任务批量刷新过期快照
- **GIVEN** 系统中有 50 个过期快照 (`is_stale = true`)
- **WHEN** Celery Beat 每分钟执行 `batch_refresh_stale_problem_snapshots()`
- **THEN** 系统必须批量获取 50 个过期快照
- **AND** 为每个快照触发单独的异步任务 `refresh_problem_unlock_snapshot.delay()`
- **AND** 每个任务的计算时间必须 <600ms

## MODIFIED Requirements

无。本变更为新增能力,不修改现有需求规格。

## REMOVED Requirements

无。本变更为性能优化,不移除现有功能。
