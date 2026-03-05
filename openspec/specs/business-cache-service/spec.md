# Business Cache Service

## ADDED Requirements

### Requirement: Business cache service must provide standardized API for service layer caching

The system SHALL provide a `BusinessCacheService` that offers a consistent interface for caching results from business logic operations (e.g., snapshots, computations, external API calls) in `services.py`.

#### Scenario: Cache business logic result with miss

- **WHEN** a business operation result is requested via `BusinessCacheService.cache_result()` and the cache is empty
- **THEN** the service SHALL call the provided `fetcher` callback to execute the business logic
- **AND** the service SHALL store the result in cache with the specified timeout
- **AND** the service SHALL return the fetched result

#### Scenario: Cache business logic result with hit

- **WHEN** a business operation result is requested via `BusinessCacheService.cache_result()` and valid cached data exists
- **THEN** the service SHALL return the cached result without calling the `fetcher` callback
- **AND** the service SHALL NOT execute the business logic

### Requirement: Business cache must support operation-specific methods

The system SHALL provide convenience methods for common business operations (e.g., `cache_snapshot()`, `cache_execution_result()`) that encapsulate standard caching patterns.

#### Scenario: Cache enrollment snapshot

- **WHEN** an enrollment snapshot is requested via `BusinessCacheService.cache_snapshot(enrollment_id, fetcher)`
- **THEN** the service SHALL generate a standardized cache key using `get_standard_cache_key()` with prefix "business", view_name "UnlockSnapshot", and the provided `enrollment_id`
- **AND** the service SHALL use the cache to fetch or compute the snapshot
- **AND** the service SHALL apply a default timeout of 300 seconds (5 minutes)

#### Scenario: Cache code execution result

- **WHEN** a code execution result is requested via `BusinessCacheService.cache_execution_result(submission_id, fetcher)`
- **THEN** the service SHALL generate a standardized cache key using `get_standard_cache_key()` with prefix "business", view_name "CodeExecution", and the provided `submission_id`
- **AND** the service SHALL use the cache to fetch or compute the execution result

### Requirement: Business cache must handle empty results correctly

The system SHALL cache empty results (empty lists, empty dicts) with appropriate TTL to prevent repeated expensive operations that return no data.

#### Scenario: Cache empty snapshot result

- **WHEN** a business operation returns an empty result (e.g., empty list `{}`)
- **THEN** `BusinessCacheService` SHALL cache the empty result using `set_cache()` which automatically applies short TTL (60 seconds) for empty values
- **AND** subsequent requests SHALL receive the empty cached result until TTL expires

### Requirement: Business cache must integrate with cache infrastructure

The system SHALL use `get_cache()` and `set_cache()` from `common.utils.cache`, ensuring automatic metrics recording and penetration protection.

#### Scenario: Automatic metrics integration

- **WHEN** `BusinessCacheService` performs cache operations
- **THEN** the underlying cache utilities SHALL automatically record Prometheus metrics (cache_requests_total, cache_operation_duration_seconds)
- **AND** the service SHALL NOT manually record metrics

#### Scenario: Null value handling for non-existent resources

- **WHEN** a business operation indicates a resource does not exist (e.g., enrollment not found)
- **THEN** `BusinessCacheService` MAY use `set_cache(key, value, is_null=True)` to cache a null value marker
- **AND** subsequent requests SHALL return the cached null value (404) until TTL expires (default 300 seconds)
- **AND** this SHALL prevent cache penetration attacks

### Requirement: Business cache must support custom timeouts

The system SHALL allow callers to specify custom cache timeouts, with sensible defaults for different operation types.

#### Scenario: Custom timeout for long-running computation

- **WHEN** a caller specifies a custom timeout parameter (e.g., `timeout=600` for 10 minutes)
- **THEN** `BusinessCacheService` SHALL use the custom timeout instead of the default
- **AND** the service SHALL pass the timeout to `set_cache()`
