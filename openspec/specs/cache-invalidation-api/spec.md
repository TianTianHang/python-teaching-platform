# Cache Invalidation API

## ADDED Requirements

### Requirement: Cache invalidation API must provide type-safe methods for ViewSet cache invalidation

The system SHALL provide a `CacheInvalidator` class with static methods that encapsulate cache invalidation logic for ViewSet-based caching, reducing errors from manual cache key construction.

#### Scenario: Invalidate single ViewSet instance cache

- **WHEN** `CacheInvalidator.invalidate_viewset()` is called with prefix, view_name, pk, optional parent_pks, and optional user_id
- **THEN** the service SHALL generate a standardized cache key using `get_standard_cache_key()` with user_id if provided
- **AND** the service SHALL delete the cache entry using `delete_cache()`
- **AND** the service SHALL handle the case where the cache key does not exist (no error thrown)

#### Scenario: Invalidate user-specific ViewSet instance cache

- **WHEN** `CacheInvalidator.invalidate_viewset()` is called with user_id parameter
- **THEN** the service SHALL include the user_id in the cache key generation
- **AND** the service SHALL only invalidate cache for the specified user
- **AND** the service SHALL NOT affect cache entries for other users

#### Scenario: Invalidate all ViewSet list caches

- **WHEN** `CacheInvalidator.invalidate_viewset_list()` is called with prefix, view_name, optional parent_pks, and optional user_id
- **THEN** the service SHALL generate a base cache key using `get_standard_cache_key()` with user_id if provided
- **AND** the service SHALL construct a pattern wildcard by appending `:*` to the base key
- **AND** the service SHALL delete all cache entries matching the pattern using `delete_cache_pattern()`

#### Scenario: Invalidate user-specific ViewSet list caches

- **WHEN** `CacheInvalidator.invalidate_viewset_list()` is called with user_id parameter
- **THEN** the service SHALL generate a cache key pattern that includes the user_id
- **AND** the service SHALL only invalidate cache entries for the specified user
- **AND** the service SHALL NOT affect cache entries for other users

#### Scenario: Backward compatibility - invalidation without user_id

- **WHEN** `CacheInvalidator.invalidate_viewset()` or `invalidate_viewset_list()` is called WITHOUT user_id parameter
- **THEN** the service SHALL generate cache keys without user_id (global cache)
- **AND** the service SHALL maintain backward compatibility with existing code
- **AND** the service SHALL NOT raise errors for missing user_id parameter

### Requirement: Cache invalidation API must support separated cache invalidation

The system SHALL provide specific methods for invalidating global and user-specific parts of separated caches independently.

#### Scenario: Invalidate separated cache global data

- **WHEN** `CacheInvalidator.invalidate_separated_cache_global()` is called with prefix, view_name, pk, and optional parent_pks
- **THEN** the service SHALL generate a standardized cache key with `is_separated=True` flag
- **AND** the service SHALL delete only the global data cache
- **AND** the service SHALL NOT affect user-specific status caches

#### Scenario: Invalidate separated cache user status

- **WHEN** `CacheInvalidator.invalidate_separated_cache_user_status()` is called with prefix, view_name, user_id, pk, and optional parent_pks
- **THEN** the service SHALL generate a standardized cache key with `is_separated=True` flag and `user_id`
- **AND** the service SHALL delete only the user-specific status cache
- **AND** the service SHALL NOT affect the global data cache

### Requirement: Cache invalidation must handle nested resource keys correctly

The system SHALL correctly construct cache keys for nested resources (e.g., chapters within courses) by including parent resource keys in the cache key.

#### Scenario: Invalidate nested resource cache

- **WHEN** `CacheInvalidator.invalidate_viewset()` is called with parent_pks={"course_pk": 1, "chapter_pk": 5}
- **THEN** the service SHALL include the parent keys in the generated cache key
- **AND** the service SHALL delete the cache entry that matches the nested resource pattern

### Requirement: Cache invalidation must integrate with existing cache utilities

The system SHALL use `delete_cache()` and `delete_cache_pattern()` from `common.utils.cache`, ensuring compatibility with the existing cache infrastructure.

#### Scenario: Use delete_cache for single key deletion

- **WHEN** `CacheInvalidator` needs to delete a single cache entry
- **THEN** the service SHALL call `delete_cache(key)` from `common.utils.cache`
- **AND** the underlying utility SHALL handle Redis key deletion with proper prefix handling

#### Scenario: Use delete_cache_pattern for wildcard deletion

- **WHEN** `CacheInvalidator` needs to delete multiple cache entries matching a pattern
- **THEN** the service SHALL call `delete_cache_pattern(pattern)` from `common.utils.cache`
- **AND** the underlying utility SHALL scan Redis for matching keys and delete them

### Requirement: Cache invalidation API must be safe to call when cache does not exist

The system SHALL not raise errors when attempting to invalidate non-existent cache entries, making it safe to call invalidation methods proactively (e.g., in signals).

#### Scenario: Invalidate non-existent cache key

- **WHEN** `CacheInvalidator.invalidate_viewset()` is called for a cache key that does not exist
- **THEN** the service SHALL complete without raising an exception
- **AND** the service SHALL log a debug message indicating the key was not found

### Requirement: Cache invalidation must support batch operations

The system SHALL provide methods to invalidate multiple related cache entries in a single operation for efficiency.

#### Scenario: Invalidate all caches for a course

- **WHEN** `CacheInvalidator.invalidate_course_caches(course_id)` is called
- **THEN** the service SHALL delete all list and detail caches for the course
- **AND** the service SHALL delete caches for all chapters and problems belonging to the course
- **AND** the service SHALL use pattern matching to efficiently delete all related keys

### Requirement: 统一缓存失效 API

缓存失效 SHALL 使用 `CacheInvalidator` 提供的统一 API，确保所有缓存失效操作使用标准 key 格式。

#### Scenario: 使用 CacheInvalidator 失效章节解锁缓存

- **WHEN** 调用 `ChapterUnlockService._invalidate_cache(chapter_id, enrollment_id)`
- **THEN** 使用 `CacheInvalidator.invalidate_viewset_list()` 失效缓存
- **AND** 生成的 key 格式使用标准化的 `get_standard_cache_key()` 格式

#### Scenario: 缓存失效使用标准 key 格式

- **WHEN** 缓存失效被调用
- **THEN** 生成的 key 格式为 `courses:ChapterUnlockService:chapter_pk={...}:enrollment_pk={...}:...`
- **AND** 不再使用旧格式的 `chapter_unlock:{id}:{id}` 模式

### Requirement: 清理遗留缓存方法

遗留的缓存方法 SHALL 被删除，以减少代码复杂度。

#### Scenario: 删除 _get_cache_key 方法

- **WHEN** 代码中不再使用 `ChapterUnlockService._get_cache_key()`
- **THEN** 该方法被删除
- **AND** 所有调用点迁移到使用 `get_standard_cache_key()`

#### Scenario: 删除 _set_cache / _get_cache 方法

- **WHEN** 代码中不再使用直接 cache.get/set 调用
- **THEN** `_set_cache()` 和 `_get_cache()` 方法被删除
- **AND** 所有缓存操作迁移到 `BusinessCacheService.cache_result()`

#### Scenario: 删除遗留缓存常量

- **WHEN** 不再需要旧格式的缓存 key
- **THEN** `UNLOCK_CACHE_PREFIX` 和 `PREREQUISITE_PROGRESS_CACHE_PREFIX` 常量被删除
- **AND** 不再有硬编码的缓存 key 前缀
