# Cache Key Analytics Capability Specification

## ADDED Requirements

### Requirement: System SHALL identify and report hot cache keys
The system SHALL analyze cache access patterns and identify the most frequently accessed cache keys (hot keys).

#### Scenario: Generate hot keys list
- **WHEN** analyzing cache logs for a day
- **THEN** system SHALL calculate access count for each unique cache_key
- **AND** generate a list of Top 100 hot keys sorted by access frequency
- **AND** include in the daily report

#### Scenario: Hot key entry details
- **WHEN** a cache key is identified as hot
- **THEN** analytics SHALL include:
  - `cache_key`: the key pattern
  - `access_count`: number of accesses
  - `hit_count`: number of hits
  - `miss_count`: number of misses
  - `hit_rate`: hit_count / access_count
  - `avg_duration_ms`: average access duration

#### Scenario: Hot key threshold detection
- **WHEN** a key's access count > (mean + 2 * std_dev)
- **THEN** system SHALL flag it as "statistically significant"
- **AND** highlight it in the report

---

### Requirement: System SHALL identify and report cold cache keys
The system SHALL identify cache keys that are rarely accessed and may be wasting memory.

#### Scenario: Generate cold keys list
- **WHEN** analyzing cache logs for a day
- **THEN** system SHALL identify keys with access_count < 10
- **AND** filter keys that were created more than 7 days ago
- **AND** generate a list of cold keys

#### Scenario: Cold key recommendations
- **WHEN** a key is identified as cold
- **THEN** report SHALL include:
  - `cache_key`: the key pattern
  - `access_count`: number of accesses (low)
  - `last_access_time`: most recent access
  - `age_days`: how long the key has existed
  - `recommendation`: "Consider reducing TTL or removing from cache"

#### Scenario: Exclude system keys from cold analysis
- **WHEN** analyzing cold keys
- **THEN** system SHALL exclude keys matching patterns like `session:*`, `csrf:*`, `warming:*`
- **AND** only analyze application data keys

---

### Requirement: System SHALL analyze cache key patterns
The system SHALL categorize cache keys by patterns to understand data distribution.

#### Scenario: Group keys by prefix
- **WHEN** analyzing cache keys
- **THEN** system SHALL group keys by their prefix (e.g., "api:", "query:", "session:")
- **AND** calculate statistics for each group:
  - Total keys in group
  - Total accesses
  - Hit rate
  - Memory usage estimate

#### Scenario: Key pattern distribution
- **WHEN** generating key analytics
- **THEN** report SHALL include distribution table:
  ```
  Pattern        | Count  | Hit Rate | Access %
  api:CourseViewSet | 1,234 | 92%     | 35%
  api:ChapterViewSet| 567   | 88%     | 15%
  ```

---

### Requirement: System SHALL track cache key churn
The system SHALL monitor the rate at which cache keys are created and evicted.

#### Scenario: Calculate key churn rate
- **WHEN** analyzing cache logs
- **THEN** system SHALL count:
  - `new_keys`: keys first seen on this day
  - `evicted_keys`: keys that disappeared (expired or evicted)
  - `churn_rate`: (new_keys + evicted_keys) / total_keys

#### Scenario: High churn alert
- **WHEN** churn rate > 50%
- **THEN** report SHALL include a warning
- **AND** suggest: "Consider increasing TTL to reduce churn"

---

### Requirement: Key analytics SHALL be queryable via management command
The system SHALL provide a command to analyze cache keys for any time period.

#### Scenario: Analyze keys for specific date
- **WHEN** running `python manage.py analyze_cache_keys --date 2026-03-01`
- **THEN** system SHALL output hot/cold key analysis for that date
- **AND** display results in console with tabular format

#### Scenario: Analyze keys by endpoint
- **WHEN** running `python manage.py analyze_cache_keys --endpoint CourseViewSet`
- **THEN** system SHALL filter analysis to only keys matching that endpoint
- **AND** show top keys for that endpoint

#### Scenario: Export key analytics to CSV
- **WHEN** running `python manage.py analyze_cache_keys --export keys.csv`
- **THEN** system SHALL export detailed key statistics to CSV file
- **AND** CSV SHALL include: key, access_count, hit_count, miss_count, hit_rate, avg_duration
