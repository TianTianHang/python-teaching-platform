## ADDED Requirements

### Requirement: 统一缓存失效 API

缓存失效 SHALL 使用 `CacheInvalidator` 提供的统一 API，确保所有缓存失效操作使用标准 key 格式。

#### Scenario: 使用 CacheInvalidator 失效章节解锁缓存
- **WHEN** 调用 `ChapterUnlockService._invalidate_cache(chapter_id, enrollment_id)`
- **THEN** 使用 `CacheInvalidator.invalidate_separated_cache_user_status()` 失效缓存

#### Scenario: 缓存失效使用标准 key 格式
- **WHEN** 缓存失效被调用
- **THEN** 生成的 key 格式为 `courses:ChapterUnlockService:UNLOCK:chapter_pk={...}:enrollment_pk={...}`

### Requirement: 清理遗留缓存方法

遗留的缓存方法 SHALL 被删除，以减少代码复杂度。

#### Scenario: 删除 _get_cache_key 方法
- **WHEN** 代码中不再使用 `ChapterUnlockService._get_cache_key()`
- **THEN** 该方法被删除

#### Scenario: 删除 _set_cache / _get_cache 方法
- **WHEN** 代码中不再使用直接 cache.get/set 调用
- **THEN** 这些方法被删除

#### Scenario: 删除遗留缓存常量
- **WHEN** 不再需要旧格式的缓存 key
- **THEN** `UNLOCK_CACHE_PREFIX` 和 `PREREQUISITE_PROGRESS_CACHE_PREFIX` 常量被删除