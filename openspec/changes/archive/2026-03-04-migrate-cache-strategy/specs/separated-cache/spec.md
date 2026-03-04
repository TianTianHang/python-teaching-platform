## ADDED Requirements

### Requirement: Global data cache shared across users

系统 SHALL 将不包含用户状态的数据（如章节标题、内容、排序）缓存到全局缓存中，实现跨用户共享。

缓存 Key 格式：
- 列表缓存：`{resource}:global:list:{parent_id}`
- 详情缓存：`{resource}:global:{id}`

#### Scenario: Chapter list global cache hit

- **WHEN** 用户请求章节列表
- **AND** 全局缓存中存在 `chapter:global:list:{course_id}`
- **THEN** 系统返回缓存的全局数据
- **AND** 不查询数据库获取章节基础信息

#### Scenario: Chapter detail global cache miss

- **WHEN** 用户请求章节详情
- **AND** 全局缓存中不存在 `chapter:global:{chapter_id}`
- **THEN** 系统从数据库查询章节数据
- **AND** 将全局数据存入缓存，TTL 为 30 分钟

### Requirement: User status cache isolated per user

系统 SHALL 将用户状态数据（如完成状态、进度、锁定状态）缓存到用户独立缓存中，实现按用户隔离。

缓存 Key 格式：
- `{resource}:status:{parent_id}:{user_id}`

#### Scenario: User status cache isolated

- **WHEN** 用户 A 完成章节 X
- **AND** 用户 B 尚未完成章节 X
- **THEN** 用户 A 的状态缓存显示已完成
- **AND** 用户 B 的状态缓存显示未完成
- **AND** 两个缓存 Key 不同

### Requirement: Fine-grained cache invalidation

系统 SHALL 在用户状态变更时仅清除该用户的缓存，不影响其他用户的缓存。

#### Scenario: User progress invalidates only own cache

- **WHEN** 用户 A 完成章节 X
- **THEN** 系统仅清除 `chapter:status:{course_id}:{user_A_id}`
- **AND** 不清除用户 B 的 `chapter:status:{course_id}:{user_B_id}`

#### Scenario: Content change invalidates global cache

- **WHEN** 管理员修改章节 X 的标题
- **THEN** 系统清除 `chapter:global:{chapter_id}`
- **AND** 系统清除 `chapter:global:list:{course_id}`
- **AND** 不清除任何用户状态缓存

### Requirement: Legacy cache strategy removed

系统 SHALL 不再使用旧的统一缓存策略（CacheListMixin 的 user-bound cache key）。

#### Scenario: No api: prefixed cache keys for Chapter

- **WHEN** 用户请求章节列表或详情
- **THEN** 系统 SHALL NOT 生成 `api:ChapterViewSet:{user_id}:...` 格式的缓存 Key
- **AND** 系统使用 `chapter:global:*` 或 `chapter:status:*` 格式

#### Scenario: No duplicate signal handlers

- **WHEN** ChapterProgress 模型保存
- **THEN** 系统仅执行一个缓存失效信号处理器
- **AND** 该处理器使用细粒度失效策略