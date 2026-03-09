# Delta Spec: cache-performance-stats

## MODIFIED Requirements

### Requirement: System SHALL maintain in-memory performance statistics per endpoint
The system SHALL aggregate cache operation statistics in memory for each endpoint, including total hits, misses, null values, total operations, average duration, and slow operation count.

#### Scenario: Initialize statistics tracker
- **WHEN** the application starts or the statistics module is imported
- **THEN** system SHALL initialize an empty statistics structure
- **AND** statistics SHALL be organized by endpoint name
- **AND** each endpoint SHALL have counters for: hits, misses, null_values, total_operations, total_duration, slow_operations

#### Scenario: Record cache hit in statistics
- **WHEN** a cache hit occurs for endpoint "CourseViewSet"
- **THEN** system SHALL increment the total_operations counter for "CourseViewSet"
- **AND** system SHALL increment the hits counter for "CourseViewSet"
- **AND** system SHALL add the operation duration to total_duration
- **AND** system SHALL update the last_reset timestamp

#### Scenario: Record slow operation in statistics
- **WHEN** a cache operation takes longer than the slow threshold (100ms)
- **THEN** system SHALL increment the slow_operations counter for that endpoint
- **AND** system SHALL record the operation duration in total_duration
- **AND** system SHALL record the operation details in Redis for analysis

#### Scenario: Record fast operation in statistics
- **WHEN** a cache operation completes in less than 100ms
- **THEN** system SHALL increment the total_operations counter
- **AND** system SHALL NOT increment the slow_operations counter
- **AND** system SHALL NOT record detailed operation details in Redis

---

### Requirement: System SHALL calculate performance metrics from statistics
The system SHALL calculate derived metrics including hit rate, miss rate, slow operation rate, average duration, and requests per second. All rate calculations SHALL use total_operations as the denominator to ensure accuracy.

#### Scenario: Calculate hit rate
- **WHEN** statistics show 850 hits, 150 misses, and 1000 total_operations for an endpoint
- **THEN** system SHALL calculate hit rate as 850 / 1000 = 0.85
- **AND** hit rate SHALL be a float between 0 and 1
- **AND** calculation SHALL use total_operations as denominator, not (hits + misses)

#### Scenario: Calculate slow operation rate
- **WHEN** statistics show 50 slow_operations and 1000 total_operations
- **THEN** system SHALL calculate slow operation rate as 50 / 1000 = 0.05 (5%)
- **AND** slow operation rate SHALL be a float between 0 and 1
- **AND** calculation SHALL use total_operations as denominator

#### Scenario: Calculate average duration
- **WHEN** statistics show 1000 total_operations with total_duration of 2500ms
- **THEN** system SHALL calculate average duration as 2500 / 1000 = 2.5ms
- **AND** average duration SHALL be in milliseconds
- **AND** calculation SHALL use total_operations as denominator to include all operations

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
  - `top_slow`: list of 5 slowest endpoints by avg_duration_ms
  - `top_miss`: list of 5 endpoints with highest miss rate

#### Scenario: Global statistics in summary
- **WHEN** generating the summary log
- **THEN** global statistics SHALL include:
  - `total_requests`: total_operations across all endpoints
  - `hit_rate`: total hits / total_operations
  - `avg_duration_ms`: total duration / total_operations
  - `total_slow_operations`: count of operations > 100ms
  - `slow_operation_rate`: total_slow_operations / total_operations

#### Scenario: Per-endpoint statistics in summary
- **WHEN** generating the summary log
- **THEN** each endpoint SHALL have:
  - `endpoint`: endpoint name
  - `hits`: number of cache hits
  - `misses`: number of cache misses
  - `total_requests`: total_operations
  - `hit_rate`: hits / total_operations
  - `avg_duration_ms`: total duration / total_operations
  - `slow_operations`: number of slow operations
  - `slow_operation_rate`: slow_operations / total_operations
