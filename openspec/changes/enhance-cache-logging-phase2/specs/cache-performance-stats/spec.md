# Cache Performance Stats Capability Specification

## ADDED Requirements

### Requirement: System SHALL maintain in-memory performance statistics per endpoint
The system SHALL aggregate cache operation statistics in memory for each endpoint, including total hits, misses, null values, average duration, and slow operation count.

#### Scenario: Initialize statistics tracker
- **WHEN** the application starts or the statistics module is imported
- **THEN** system SHALL initialize an empty statistics structure
- **AND** statistics SHALL be organized by endpoint name
- **AND** each endpoint SHALL have counters for: hits, misses, null_values, total_duration, slow_operations

#### Scenario: Record cache hit in statistics
- **WHEN** a cache hit occurs for endpoint "CourseViewSet"
- **THEN** system SHALL increment the hits counter for "CourseViewSet"
- **AND** system SHALL add the operation duration to total_duration
- **AND** system SHALL update the last_reset timestamp

#### Scenario: Record slow operation in statistics
- **WHEN** a cache operation takes longer than the slow threshold (100ms)
- **THEN** system SHALL increment the slow_operations counter for that endpoint
- **AND** system SHALL record the operation duration in total_duration

---

### Requirement: System SHALL calculate performance metrics from statistics
The system SHALL calculate derived metrics including hit rate, miss rate, average duration, and requests per second.

#### Scenario: Calculate hit rate
- **WHEN** statistics show 850 hits and 150 misses for an endpoint
- **THEN** system SHALL calculate hit rate as 850 / (850 + 150) = 0.85
- **AND** hit rate SHALL be a float between 0 and 1

#### Scenario: Calculate average duration
- **WHEN** statistics show 1000 operations with total_duration of 2500ms
- **THEN** system SHALL calculate average duration as 2500 / 1000 = 2.5ms
- **AND** average duration SHALL be in milliseconds

#### Scenario: Handle zero division
- **WHEN** calculating metrics for an endpoint with no operations
- **THEN** system SHALL return None or 0 for all metrics
- **AND** system SHALL NOT raise a ZeroDivisionError

---

### Requirement: System SHALL generate periodic performance summary logs
The system SHALL generate a comprehensive performance summary log every minute containing global and per-endpoint statistics.

#### Scenario: Generate summary log
- **WHEN** the periodic summary task executes (every 60 seconds)
- **THEN** system SHALL generate a log entry with:
  - `event`: "cache_performance_summary"
  - `timestamp`: current ISO 8601 timestamp
  - `period`: "60s"
  - `global`: aggregate statistics across all endpoints
  - `endpoints`: dictionary with per-endpoint statistics
  - `top_slow`: list of 5 slowest endpoints
  - `top_miss`: list of 5 endpoints with highest miss rate

#### Scenario: Global statistics in summary
- **WHEN** generating the summary log
- **THEN** global statistics SHALL include:
  - `total_requests`: sum of all hits + misses + null_values
  - `hit_rate`: total hits / total requests
  - `avg_duration_ms`: total duration / total requests
  - `total_slow_operations`: count of operations > 100ms

#### Scenario: Per-endpoint statistics in summary
- **WHEN** generating the summary log
- **THEN** each endpoint SHALL have:
  - `endpoint`: endpoint name
  - `hits`: number of cache hits
  - `misses`: number of cache misses
  - `hit_rate`: hits / (hits + misses)
  - `avg_duration_ms`: average duration in milliseconds
  - `slow_operations`: number of slow operations

#### Scenario: Reset statistics after summary
- **WHEN** the performance summary log is generated
- **THEN** system SHALL reset all counters to 0
- **AND** system SHALL update the last_reset timestamp

---

### Requirement: System SHALL track cache performance per HTTP request
The system SHALL collect cache statistics for each HTTP request and include them in the request log.

#### Scenario: Collect cache stats in request
- **WHEN** a request executes cache operations through CacheMixin
- **THEN** system SHALL collect statistics in `request._cache_stats` dictionary
- **AND** statistics SHALL include: hits, misses, duration_ms, endpoint

#### Scenario: Log request cache performance
- **WHEN** the request completes and LoggingMiddleware processes it
- **THEN** IF `request._cache_stats` exists
- **AND** system SHALL log an INFO entry with:
  - `event`: "request_cache_stats"
  - `request_id`: the request ID
  - `endpoint`: the view name
  - `cache_hits`: number of cache hits during request
  - `cache_misses`: number of cache misses during request
  - `cache_hit_rate`: hits / (hits + misses)
  - `cache_duration_ms`: total cache operation duration

#### Scenario: Request without cache operations
- **WHEN** a request completes without any cache operations
- **THEN** system SHALL NOT log cache performance
- **AND** request log SHALL remain unchanged

---

### Requirement: System SHALL provide statistics query API
The system SHALL provide a programmatic API to query current statistics for monitoring and debugging.

#### Scenario: Query all endpoint statistics
- **WHEN** calling `get_all_endpoint_stats()`
- **THEN** system SHALL return a dictionary with all endpoints
- **AND** each endpoint SHALL have full statistics: hits, misses, hit_rate, avg_duration_ms

#### Scenario: Query single endpoint statistics
- **WHEN** calling `get_endpoint_stats('CourseViewSet')`
- **THEN** system SHALL return statistics only for 'CourseViewSet'
- **AND** return value SHALL include all metrics for that endpoint
- **AND** if endpoint doesn't exist, return None or empty dict

#### Scenario: Query global statistics
- **WHEN** calling `get_global_stats()`
- **THEN** system SHALL return aggregate statistics across all endpoints
- **AND** return value SHALL include: total_requests, hit_rate, avg_duration_ms, total_slow_operations
