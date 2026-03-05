# Separated Cache Service

## ADDED Requirements

### Requirement: Separated cache must provide unified API for global and user-specific data

The system SHALL provide a `SeparatedCacheService` that encapsulates the pattern of caching global data separately from user-specific status, enabling cross-user data sharing while maintaining personalized state.

#### Scenario: Get global data with cache miss

- **WHEN** global data is requested via `SeparatedCacheService.get_global_data()` and the cache is empty
- **THEN** the service SHALL call the provided `data_fetcher` callback to retrieve data from the database
- **AND** the service SHALL store the data in cache with the specified TTL
- **AND** the service SHALL return the fetched data along with a flag indicating cache miss
- **AND** the service SHALL record a cache miss metric for the endpoint

#### Scenario: Get global data with cache hit

- **WHEN** global data is requested via `SeparatedCacheService.get_global_data()` and valid cached data exists
- **THEN** the service SHALL return the cached data along with a flag indicating cache hit
- **AND** the service SHALL record a cache hit metric for the endpoint
- **AND** the service SHALL NOT call the `data_fetcher` callback

### Requirement: User-specific status must be cached separately with user isolation

The system SHALL cache user-specific status separately from global data, ensuring that each user's status is isolated and identified by `user_id` in the cache key.

#### Scenario: Get user status with cache miss

- **WHEN** user status is requested via `SeparatedCacheService.get_user_status()` for a specific `user_id` and the cache is empty
- **THEN** the service SHALL call the provided `status_fetcher` callback to retrieve user-specific data
- **AND** the service SHALL store the data in cache with a cache key that includes `user_id`
- **AND** the service SHALL return the fetched status data

#### Scenario: Get user status with cache hit

- **WHEN** user status is requested via `SeparatedCacheService.get_user_status()` for a specific `user_id` and valid cached data exists
- **THEN** the service SHALL return the cached status data without calling the `status_fetcher`

### Requirement: Separated cache must support independent invalidation

The system SHALL provide methods to invalidate global cache and user-specific cache independently, allowing fine-grained cache control.

#### Scenario: Invalidate global cache without affecting user status

- **WHEN** `SeparatedCacheService.invalidate_global()` is called with a global cache key
- **THEN** the service SHALL delete only the global data cache
- **AND** the service SHALL NOT affect any user-specific status caches

#### Scenario: Invalidate user status without affecting global data

- **WHEN** `SeparatedCacheService.invalidate_user_status()` is called with a base key and `user_id`
- **THEN** the service SHALL delete only the status cache for that specific user
- **AND** the service SHALL NOT affect the global data cache or other users' status caches

### Requirement: Separated cache must integrate with existing cache infrastructure

The system SHALL use the existing `get_cache()`, `set_cache()`, and `delete_cache()` functions from `common.utils.cache`, ensuring compatibility with CacheResult, metrics, and penetration protection.

#### Scenario: Automatic CacheResult support

- **WHEN** `SeparatedCacheService.get_global_data()` retrieves cached data
- **THEN** the service SHALL use `get_cache(return_result=True)` to obtain a CacheResult object
- **AND** the service SHALL check `result.is_hit` to determine if the cache was hit
- **AND** the service SHALL check `result.is_null_value` to handle penetration-protected null values

#### Scenario: Automatic Prometheus metrics

- **WHEN** `SeparatedCacheService` performs cache operations (get/set/delete)
- **THEN** the underlying cache utilities SHALL automatically record Prometheus metrics
- **AND** the service SHALL NOT manually record metrics (delegated to `utils/cache.py`)
