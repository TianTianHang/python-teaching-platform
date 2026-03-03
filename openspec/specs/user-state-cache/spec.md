# user-state-cache Specification

## Purpose
TBD - created by archiving change separate-cache-global-user. Update Purpose after archive.
## Requirements
### Requirement: User state cache key generation

系统 SHALL 为用户状态生成独立的缓存键，包含用户标识，实现按用户隔离。

#### Scenario: Chapter user state cache key

- **WHEN** 系统缓存章节用户状态
- **THEN** 缓存键 SHALL 使用格式 `chapter:status:{course_id}:{user_id}`
- **AND** 缓存键 SHALL 包含 `user_id`
- **AND** 不同用户的缓存 SHALL 相互隔离

#### Scenario: Problem user state cache key

- **WHEN** 系统缓存问题用户状态
- **THEN** 缓存键 SHALL 使用格式 `problem:status:{chapter_id}:{user_id}`
- **AND** 缓存键 SHALL 包含 `user_id`
- **AND** 不同用户的缓存 SHALL 相互隔离

### Requirement: User state cache TTL

系统 SHALL 为用户状态设置较短的缓存过期时间，确保数据一致性。

#### Scenario: Default TTL for user state

- **WHEN** 系统设置用户状态缓存
- **THEN** 默认 TTL SHALL 为 300 秒（5分钟）
- **AND** 可通过配置调整 TTL

#### Scenario: User state cache auto-refresh

- **WHEN** 用户状态缓存即将过期（剩余 TTL < 60秒）
- **THEN** 系统 MAY 触发异步刷新任务
- **AND** 用户请求 SHALL 不被阻塞

### Requirement: User state cache invalidation

系统 SHALL 在用户状态变更时立即失效用户状态缓存，确保数据一致性。

#### Scenario: Chapter progress update invalidates user state cache

- **WHEN** 用户完成章节或更新章节进度
- **THEN** 系统 SHALL 失效该用户的章节状态缓存
- **AND** 系统 SHALL 不影响其他用户的缓存
- **AND** 系统 SHALL 不失效全局数据缓存

#### Scenario: Problem progress update invalidates user state cache

- **WHEN** 用户解决问题或更新问题进度
- **THEN** 系统 SHALL 失效该用户的问题状态缓存
- **AND** 系统 SHALL 不影响其他用户的缓存
- **AND** 系统 SHALL 不失效全局数据缓存

#### Scenario: Enrollment change invalidates user state cache

- **WHEN** 用户注册或取消注册课程
- **THEN** 系统 SHALL 失效该用户的所有章节和问题状态缓存
- **AND** 系统 SHALL 不影响其他用户的缓存

### Requirement: Batch user state retrieval

系统 SHALL 支持批量获取多个资源的用户状态，减少缓存查询次数。

#### Scenario: Batch get chapter user status

- **WHEN** 需要获取多个章节的用户状态
- **THEN** 系统 SHALL 使用 Redis MGET 批量获取
- **AND** 系统 SHALL 在一次网络往返中获取所有状态
- **AND** 系统 SHALL 返回章节ID到状态的映射

#### Scenario: Batch get problem user status

- **WHEN** 需要获取多个问题的用户状态
- **THEN** 系统 SHALL 使用 Redis MGET 批量获取
- **AND** 系统 SHALL 在一次网络往返中获取所有状态
- **AND** 系统 SHALL 返回问题ID到状态的映射

### Requirement: Snapshot status field extension

系统 SHALL 扩展现有的快照模型，增加 `status` 字段，存储用户状态。

#### Scenario: CourseUnlockSnapshot status field

- **WHEN** 系统创建或更新课程解锁快照
- **THEN** 快照的 `unlock_states` 字段 SHALL 包含 `status` 子字段
- **AND** `status` SHALL 包含值：`not_started`, `in_progress`, `completed`
- **AND** 系统 SHALL 兼容旧格式（无 `status` 字段）

#### Scenario: ProblemUnlockSnapshot status field

- **WHEN** 系统创建或更新问题解锁快照
- **THEN** 快照的 `unlock_states` 字段 SHALL 包含 `status` 子字段
- **AND** `status` SHALL 包含值：`not_started`, `in_progress`, `solved`, `failed`
- **AND** 系统 SHALL 兼容旧格式（无 `status` 字段）

### Requirement: User state cache fallback

系统 SHALL 在用户状态缓存未命中时，从快照或数据库获取数据，并回填缓存。

#### Scenario: Cache miss fallback to snapshot

- **WHEN** 用户状态缓存未命中
- **THEN** 系统 SHALL 从快照获取用户状态
- **AND** 系统 SHALL 回填缓存
- **AND** 系统 SHALL 设置 TTL 为 300 秒

#### Scenario: Snapshot miss fallback to database

- **WHEN** 快照不存在或已过期
- **THEN** 系统 SHALL 从数据库查询用户状态
- **AND** 系统 SHALL 更新快照
- **AND** 系统 SHALL 回填缓存

### Requirement: User state cache metrics

系统 SHALL 记录用户状态缓存的命中率、更新频率等指标，用于监控和优化。

#### Scenario: Cache hit metrics

- **WHEN** 用户状态缓存命中
- **THEN** 系统 SHALL 记录缓存命中事件
- **AND** 系统 SHALL 记录缓存键前缀 `status`
- **AND** 系统 SHALL 记录用户ID

#### Scenario: Cache invalidation metrics

- **WHEN** 用户状态缓存失效
- **THEN** 系统 SHALL 记录缓存失效事件
- **AND** 系统 SHALL 记录失效原因（用户进度更新、注册变更等）

