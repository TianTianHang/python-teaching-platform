## MODIFIED Requirements

### Requirement: Chapter serializer is_locked field
**MODIFIED** to support database annotation with service fallback.

The ChapterSerializer SHALL use database-calculated `is_locked` when available, and fall back to service layer for edge cases.

#### Scenario: Using database annotation
- **WHEN** the chapter object has `is_locked_db` attribute
- **THEN** `get_is_locked()` SHALL return `obj.is_locked_db`
- **AND** no service layer calls or additional queries are made

#### Scenario: Fallback to service layer
- **WHEN** the chapter object does not have `is_locked_db` attribute
- **THEN** `get_is_locked()` SHALL call `ChapterUnlockService.is_unlocked()`
- **AND** maintain backward compatibility with existing behavior

#### Scenario: Chapter without unlock condition
- **WHEN** a chapter has no unlock condition
- **THEN** `get_is_locked()` SHALL return `False`
- **AND` this SHALL be determined efficiently without unnecessary checks

### Requirement: Prerequisite progress field behavior
**MODIFIED** to remain unchanged in functionality but avoid N+1 when combined with is_locked.

The `prerequisite_progress` field SHALL continue to provide detailed progress information using service layer caching.

#### Scenario: Prerequisite progress with database is_locked
- **WHEN** a chapter has unlock conditions and `is_locked` is calculated via database
- **THEN** `prerequisite_progress` SHALL continue to work as before
- **AND` service layer caching SHALL be used to avoid repeated queries

#### Scenario: Prerequisite progress format consistency
- **WHEN** requesting prerequisite progress for a locked chapter
- **THEN` the SHALL return JSON with `total`, `completed`, and `remaining` fields
- **AND` the format SHALL match existing API contract

#### Scenario: No prerequisite progress for unlocked chapters
- **WHEN** a chapter is unlocked or has no unlock conditions
- **THEN** `prerequisite_progress` SHALL return `null`
- **AND` no unnecessary progress calculations SHALL be performed

### Requirement: Performance test requirements
**MODIFIED** to include database annotation performance benchmarks.

The chapter list performance tests SHALL verify database annotation effectiveness.

#### Scenario: Performance test with annotations
- **WHEN** running `test_chapter_list_with_prefetch_verify`
- **THEN` the test SHALL verify that < 5 progress queries are executed
- **AND` the test SHALL verify that < 3 enrollment queries are executed

#### Scenario: Query count verification
- **WHEN** testing chapter list performance
- **THEN` the system SHALL count queries by type (progress, enrollment, unlock)
- **AND` verify that total queries are within specified limits

## ADDED Requirements

### Requirement: Serializer field resolution priority
The ChapterSerializer SHALL clearly define field resolution priority for is_locked.

#### Scenario: Field resolution order
- **WHEN** resolving `is_locked` field
- **THEN** the priority SHALL be: 1) `is_locked_db` annotation, 2) service layer fallback
- **AND` this SHALL be documented in code comments

### Requirement: Debug information for serializers
The serializer SHALL provide debug information when database annotation is unavailable.

#### Scenario: Missing annotation warning
- **WHEN** service layer fallback is used
- **THEN` the system SHALL log a warning indicating database annotation was not available
- **AND` help identify cases where optimization is not working