# Cache Invalidation API

## ADDED Requirements

### Requirement: Cache invalidation API must provide type-safe methods for ViewSet cache invalidation

The system SHALL provide a `CacheInvalidator` class with static methods that encapsulate cache invalidation logic for ViewSet-based caching, reducing errors from manual cache key construction.

#### Scenario: Invalidate single ViewSet instance cache

- **WHEN** `CacheInvalidator.invalidate_viewset()` is called with prefix, view_name, pk, and optional parent_pks
- **THEN** the service SHALL generate a standardized cache key using `get_standard_cache_key()`
- **AND** the service SHALL delete the cache entry using `delete_cache()`
- **AND** the service SHALL handle the case where the cache key does not exist (no error thrown)

#### Scenario: Invalidate all ViewSet list caches

- **WHEN** `CacheInvalidator.invalidate_viewset_list()` is called with prefix, view_name, and optional parent_pks
- **THEN** the service SHALL generate a base cache key using `get_standard_cache_key()` without query parameters
- **AND** the service SHALL construct a pattern wildcard by appending `:*` to the base key
- **AND** the service SHALL delete all cache entries matching the pattern using `delete_cache_pattern()`

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
