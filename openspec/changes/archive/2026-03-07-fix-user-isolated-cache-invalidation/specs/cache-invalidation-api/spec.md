# Cache Invalidation API - Delta Spec

## MODIFIED Requirements

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
