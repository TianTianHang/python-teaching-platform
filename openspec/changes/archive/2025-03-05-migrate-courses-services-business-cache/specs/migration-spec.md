## ADDED Requirements

### Requirement: ChapterUnlockService 使用 BusinessCacheService 缓存

`ChapterUnlockService` SHALL 使用 `BusinessCacheService.cache_result()` 缓存章节解锁状态。

#### Scenario: 缓存命中时直接返回结果
- **WHEN** 调用 `ChapterUnlockService.is_unlocked(chapter, enrollment)` 且缓存中存在有效数据
- **THEN** 直接返回缓存数据，不执行数据库查询

#### Scenario: 缓存未命中时计算并缓存结果
- **WHEN** 调用 `ChapterUnlockService.is_unlocked(chapter, enrollment)` 且缓存中无数据
- **THEN** 执行 `_compute_unlock_status()` 计算解锁状态，缓存结果并返回

#### Scenario: 缓存 key 使用标准格式
- **WHEN** 生成缓存 key
- **THEN** 使用 `get_standard_cache_key(prefix="courses", view_name="ChapterUnlockService", parent_pks={...}, params={...})` 生成标准 key

### Requirement: get_user_chapter_status 使用 BusinessCacheService 缓存

`get_user_chapter_status()` SHALL 使用 `BusinessCacheService.cache_result()` 缓存用户章节状态。

#### Scenario: 缓存命中时直接返回结果
- **WHEN** 调用 `get_user_chapter_status(course_id, user_id, chapter_ids)` 且缓存中存在有效数据
- **THEN** 直接返回缓存数据，不执行数据库查询

#### Scenario: 缓存未命中时从数据库获取并缓存
- **WHEN** 调用 `get_user_chapter_status(course_id, user_id, chapter_ids)` 且缓存中无数据
- **THEN** 从数据库查询用户章节状态，缓存结果并返回

### Requirement: get_user_problem_status 使用 BusinessCacheService 缓存

`get_user_problem_status()` SHALL 使用 `BusinessCacheService.cache_result()` 缓存用户问题状态。

#### Scenario: 缓存命中时直接返回结果
- **WHEN** 调用 `get_user_problem_status(chapter_id, user_id)` 且缓存中存在有效数据
- **THEN** 直接返回缓存数据，不执行数据库查询

#### Scenario: 缓存未命中时从数据库获取并缓存
- **WHEN** 调用 `get_user_problem_status(chapter_id, user_id)` 且缓存中无数据
- **THEN** 从数据库查询用户问题状态，缓存结果并返回

### Requirement: 缓存操作记录日志

缓存操作 SHALL 记录 hit/miss 日志以便调试和监控。

#### Scenario: 缓存命中时记录 debug 日志
- **WHEN** 缓存命中
- **THEN** 记录 debug 级别日志，包含 cache key 和 "HIT" 标识

#### Scenario: 缓存未命中时记录 debug 日志
- **WHEN** 缓存未命中
- **THEN** 记录 debug 级别日志，包含 cache key 和 "MISS" 标识

### Requirement: API 兼容性

缓存迁移 SHALL 保持 API 兼容，不改变函数签名和返回值。

#### Scenario: 函数签名保持不变
- **WHEN** 调用被迁移的方法
- **THEN** 函数参数和返回值与迁移前完全一致

#### Scenario: 缓存行为一致
- **WHEN** 相同输入多次调用被迁移的方法
- **THEN** 返回结果与迁移前完全一致