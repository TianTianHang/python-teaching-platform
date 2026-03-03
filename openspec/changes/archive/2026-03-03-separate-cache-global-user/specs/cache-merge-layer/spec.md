# cache-merge-layer Specification

## Purpose

实现缓存合并层能力，在API响应时合并全局数据缓存和用户状态缓存，生成完整的响应数据，支持降级策略确保高可用性。

## ADDED Requirements

### Requirement: Merge global and user state data

系统 SHALL 在API响应时合并全局数据和用户状态，生成完整的响应对象。

#### Scenario: Merge chapter global and user state

- **WHEN** API返回章节列表或详情
- **THEN** 系统 SHALL 从全局缓存获取章节基础信息（title, content等）
- **AND** 系统 SHALL 从用户状态缓存获取用户状态（status, is_locked等）
- **AND** 系统 SHALL 合并两者生成完整响应
- **AND** 响应格式 SHALL 与原有格式保持一致

#### Scenario: Merge problem global and user state

- **WHEN** API返回问题列表或详情
- **THEN** 系统 SHALL 从全局缓存获取问题基础信息（title, content等）
- **AND** 系统 SHALL 从用户状态缓存获取用户状态（status, is_unlocked等）
- **AND** 系统 SHALL 合并两者生成完整响应
- **AND** 响应格式 SHALL 与原有格式保持一致

### Requirement: Merge performance optimization

系统 SHALL 优化合并性能，确保合并延迟低于5ms。

#### Scenario: Redis pipeline for batch merge

- **WHEN** 合并多个资源的全局数据和用户状态
- **THEN** 系统 SHALL 使用 Redis pipeline 批量查询
- **AND** 系统 SHALL 在一次网络往返中获取所有数据
- **AND** 合并延迟 SHALL 低于 5ms

#### Scenario: Parallel cache query

- **WHEN** 需要同时获取全局数据和用户状态
- **THEN** 系统 MAY 并行查询两层缓存
- **AND** 系统 SHALL 在两者都返回后执行合并

### Requirement: Graceful degradation on cache miss

系统 SHALL 在任一层缓存未命中时，降级到数据库查询，不影响服务可用性。

#### Scenario: Global cache miss fallback

- **WHEN** 全局数据缓存未命中
- **THEN** 系统 SHALL 查询数据库获取全局数据
- **AND** 系统 SHALL 回填全局数据缓存
- **AND** 系统 SHALL 继续获取用户状态（从缓存或数据库）
- **AND** 系统 SHALL 合并数据返回完整响应

#### Scenario: User state cache miss fallback

- **WHEN** 用户状态缓存未命中
- **THEN** 系统 SHALL 查询数据库或快照获取用户状态
- **AND** 系统 SHALL 回填用户状态缓存
- **AND** 系统 SHALL 继续使用全局数据缓存
- **AND** 系统 SHALL 合并数据返回完整响应

#### Scenario: Both cache miss fallback

- **WHEN** 全局数据和用户状态缓存都未命中
- **THEN** 系统 SHALL 查询数据库获取所有数据
- **AND** 系统 SHALL 分别回填两层缓存
- **AND** 系统 SHALL 返回完整响应

### Requirement: Cache merge logging and metrics

系统 SHALL 记录缓存合并的性能指标和日志，用于监控和优化。

#### Scenario: Merge duration metrics

- **WHEN** 完成缓存合并
- **THEN** 系统 SHALL 记录合并耗时
- **AND** 系统 SHALL 记录全局数据缓存命中状态
- **AND** 系统 SHALL 记录用户状态缓存命中状态
- **AND** 系统 SHALL 记录最终响应大小

#### Scenario: Degradation logging

- **WHEN** 发生缓存未命中需要降级
- **THEN** 系统 SHALL 记录降级事件
- **AND** 系统 SHALL 记录降级原因（全局未命中、用户状态未命中、双未命中）
- **AND** 系统 SHALL 记录数据库查询耗时

### Requirement: Merge layer consistency

系统 SHALL 确保合并后的数据一致性，避免部分更新导致的不一致。

#### Scenario: Atomic merge operation

- **WHEN** 执行缓存合并
- **THEN** 系统 SHALL 在单次请求中完成合并
- **AND** 系统 SHALL 不在合并过程中更新缓存
- **AND** 合并结果 SHALL 是一致的时间点快照

#### Scenario: Handle partial cache update

- **WHEN** 合并过程中检测到缓存更新
- **THEN** 系统 MAY 使用旧数据完成合并
- **OR** 系统 MAY 重新查询缓存
- **AND** 系统 SHALL 记录事件用于分析

### Requirement: Merge layer API compatibility

系统 SHALL 保持API响应格式与原有格式完全一致，前端无需修改。

#### Scenario: List API response format

- **WHEN** 返回章节或问题列表
- **THEN** 响应格式 SHALL 与分离缓存前完全一致
- **AND** 字段顺序 SHALL 保持不变
- **AND** 字段类型 SHALL 保持不变

#### Scenario: Detail API response format

- **WHEN** 返回章节或问题详情
- **THEN** 响应格式 SHALL 与分离缓存前完全一致
- **AND** 字段顺序 SHALL 保持不变
- **AND** 字段类型 SHALL 保持不变