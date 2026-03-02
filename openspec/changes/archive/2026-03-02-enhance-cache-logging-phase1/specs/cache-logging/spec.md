# Cache Logging Capability Specification

## ADDED Requirements

### Requirement: Cache operations SHALL be logged with structured data
The system SHALL record a structured log entry for every cache operation (hit, miss, null_value) that includes the event type, endpoint identifier, operation status, and duration in milliseconds.

#### Scenario: Cache hit logging
- **WHEN** a cache read operation results in a hit
- **THEN** system SHALL log an INFO level entry with:
  - `event`: "cache_hit"
  - `endpoint`: the view or service name (e.g., "CourseViewSet")
  - `status`: "hit"
  - `duration_ms`: operation duration in milliseconds
  - `hit_rate`: current hit rate for this endpoint (0-1)

#### Scenario: Cache miss logging
- **WHEN** a cache read operation results in a miss
- **THEN** system SHALL log an INFO level entry with:
  - `event`: "cache_miss"
  - `endpoint`: the view or service name
  - `status`: "miss"
  - `duration_ms`: operation duration in milliseconds

#### Scenario: Cache null value logging
- **WHEN** a cache read returns a cached null value (penetration protection)
- **THEN** system SHALL log an INFO level entry with:
  - `event`: "cache_null_value"
  - `endpoint`: the view or service name
  - `status`: "null_value"
  - `duration_ms`: operation duration in milliseconds

---

### Requirement: Slow cache operations SHALL trigger warning logs
The system SHALL detect and log cache operations that exceed the performance threshold (100ms) as WARNING level entries.

#### Scenario: Slow cache hit detection
- **WHEN** a cache hit operation takes longer than 100ms
- **THEN** system SHALL log a WARNING level entry with:
  - `event`: "cache_slow_operation"
  - `endpoint`: the view or service name
  - `operation`: "get"
  - `duration_ms`: actual operation duration
  - `threshold_ms`: 100

#### Scenario: Slow cache miss detection
- **WHEN** a cache miss operation takes longer than 100ms
- **THEN** system SHALL log a WARNING level entry with:
  - `event`: "cache_slow_operation"
  - `endpoint`: the view or service name
  - `operation`: "get"
  - `duration_ms`: actual operation duration

---

### Requirement: Cache logs SHALL be written to a dedicated file
The system SHALL write cache-related log entries to a dedicated `cache.log` file using JSON format for structured parsing.

#### Scenario: Log file creation
- **WHEN** the application starts and cache operations occur
- **THEN** system SHALL create `backend/logs/cache.log` if it doesn't exist
- **AND** log entries SHALL be in JSON format with proper timestamp and level

#### Scenario: Log file rotation
- **WHEN** cache.log reaches 10MB in size
- **THEN** system SHALL rotate the log file
- **AND** system SHALL keep up to 10 rotated log files
- **AND** rotated files SHALL be named with timestamp suffix (e.g., cache.log.2026-03-01)

---

### Requirement: Cache logging SHALL NOT break existing Prometheus metrics
The system SHALL maintain all existing Prometheus metric collection functionality while adding logging capabilities.

#### Scenario: Metrics and logs coexist
- **WHEN** a cache operation occurs
- **THEN** Prometheus metrics SHALL be updated as before
- **AND** log entry SHALL be created
- **AND** both operations SHALL be independent (logging failure SHALL NOT affect metrics)

#### Scenario: Logging failure handling
- **WHEN** log writing fails (e.g., disk full, permission error)
- **THEN** system SHALL catch the exception
- **AND** Prometheus metrics SHALL continue to be recorded
- **AND** cache operation SHALL complete normally

---

### Requirement: Cache hit rate SHALL be included in context
The system SHALL calculate and include the current hit rate for each endpoint in cache operation logs.

#### Scenario: Hit rate calculation on hit
- **WHEN** recording a cache hit
- **THEN** system SHALL query Prometheus metrics for total requests
- **AND** calculate hit rate = hits / (hits + misses + null_values)
- **AND** include hit_rate in log entry

#### Scenario: Hit rate calculation on miss
- **WHEN** recording a cache miss
- **THEN** system SHALL calculate and include the updated hit rate
- **AND** hit_rate SHALL reflect the current state after this operation

---

### Requirement: Cache mixin logs SHALL include performance metadata
The cache mixin (CacheListMixin, CacheRetrieveMixin) SHALL log cache operations with additional metadata including TTL, cache key prefix, and response status.

#### Scenario: Cache hit in mixin
- **WHEN** a cached response is returned from cache mixin
- **THEN** system SHALL log at INFO level with:
  - `cache_key`: the full cache key
  - `view_name`: the view class name
  - `cache_prefix`: the cache prefix (e.g., "api")
  - `status`: the cache result status (HIT/MISS/NULL_VALUE)
  - `ttl`: remaining TTL in seconds (if available)
  - `duration_ms`: time taken to retrieve from cache

#### Scenario: Cache miss in mixin
- **WHEN** cache is missed in mixin and data is fetched from database
- **THEN** system SHALL log at INFO level with:
  - `cache_key`: the cache key that was attempted
  - `view_name`: the view class name
  - `status`: "MISS"
  - `adaptive_ttl`: the calculated TTL for this cache entry
