# global-data-cache Specification

## Purpose

实现全局数据缓存能力，将章节、问题等静态内容（title, content, order等）跨用户共享缓存，提升缓存命中率，降低内存占用。

## ADDED Requirements

### Requirement: Global data cache key generation

系统 SHALL 为全局数据生成独立的缓存键，不包含用户标识，支持跨用户共享。

#### Scenario: Chapter global data cache key

- **WHEN** 系统缓存章节全局数据
- **THEN** 缓存键 SHALL 使用格式 `chapter:global:{chapter_id}`
- **AND** 缓存键 SHALL 不包含 `user_id`
- **AND** 所有用户访问同一章节时 SHALL 共享同一缓存

#### Scenario: Problem global data cache key

- **WHEN** 系统缓存问题全局数据
- **THEN** 缓存键 SHALL 使用格式 `problem:global:{problem_id}`
- **AND** 缓存键 SHALL 不包含 `user_id`
- **AND** 所有用户访问同一问题时 SHALL 共享同一缓存

### Requirement: Global data cache TTL

系统 SHALL 为全局数据设置较长的缓存过期时间，减少缓存失效频率。

#### Scenario: Default TTL for global data

- **WHEN** 系统设置全局数据缓存
- **THEN** 默认 TTL SHALL 为 1800 秒（30分钟）
- **AND** 可通过配置调整 TTL

#### Scenario: Empty result TTL for global data

- **WHEN** 全局数据查询结果为空
- **THEN** 系统 SHALL 使用较短的 TTL（60秒）
- **AND** 防止缓存穿透

### Requirement: Global data cache invalidation

系统 SHALL 仅在全局数据变更时失效全局缓存，用户状态变更不影响全局缓存。

#### Scenario: Chapter content update invalidates global cache

- **WHEN** 章节内容（title, content, order等）被修改
- **THEN** 系统 SHALL 失效该章节的全局数据缓存
- **AND** 系统 SHALL 失效该章节所属课程的章节列表缓存
- **AND** 系统 SHALL 不失效用户状态缓存

#### Scenario: Problem content update invalidates global cache

- **WHEN** 问题内容（title, content, difficulty等）被修改
- **THEN** 系统 SHALL 失效该问题的全局数据缓存
- **AND** 系统 SHALL 失效该问题所属章节的问题列表缓存
- **AND** 系统 SHALL 不失效用户状态缓存

#### Scenario: User progress update does not invalidate global cache

- **WHEN** 用户完成章节或解决问题
- **THEN** 系统 SHALL 不失效全局数据缓存
- **AND** 系统 SHALL 仅失效用户状态缓存

### Requirement: Global data serializer

系统 SHALL 提供独立的全局数据序列化器，仅包含静态字段，不包含用户状态字段。

#### Scenario: ChapterGlobalSerializer fields

- **WHEN** 使用 `ChapterGlobalSerializer` 序列化章节数据
- **THEN** 序列化器 SHALL 包含字段：`id`, `course`, `course_title`, `title`, `content`, `order`, `created_at`, `updated_at`
- **AND** 序列化器 SHALL 不包含字段：`status`, `is_locked`, `prerequisite_progress`

#### Scenario: ProblemGlobalSerializer fields

- **WHEN** 使用 `ProblemGlobalSerializer` 序列化问题数据
- **THEN** 序列化器 SHALL 包含字段：`id`, `chapter`, `type`, `title`, `content`, `difficulty`, `created_at`, `updated_at`
- **AND** 序列化器 SHALL 不包含字段：`status`, `is_unlocked`, `unlock_condition_description`

### Requirement: Global data cache metrics

系统 SHALL 记录全局数据缓存的命中率、内存占用等指标，用于监控和优化。

#### Scenario: Cache hit metrics

- **WHEN** 全局数据缓存命中
- **THEN** 系统 SHALL 记录缓存命中事件
- **AND** 系统 SHALL 记录缓存键前缀 `global`
- **AND** 系统 SHALL 记录响应时间

#### Scenario: Cache miss metrics

- **WHEN** 全局数据缓存未命中
- **THEN** 系统 SHALL 记录缓存未命中事件
- **AND** 系统 SHALL 记录查询数据库的耗时