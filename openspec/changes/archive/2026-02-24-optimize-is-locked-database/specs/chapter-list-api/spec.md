## MODIFIED Requirements

### Requirement: Chapter list endpoint
**MODIFIED** to include database-level is_locked calculation.

The chapter list endpoint SHALL return chapters with `is_locked` status calculated at the database level for improved performance.

#### Scenario: Student user with locked chapters
- **WHEN** a student requests `/api/courses/{course_id}/chapters/`
- **THEN** the endpoint returns all chapters with correct `is_locked` status
- **AND** locked chapters are not filtered out (visible but marked as locked)
- **AND** total database queries are limited to 3

#### Scenario: Student user with unlocked chapters
- **WHEN** a student requests chapter list after completing prerequisites
- **THEN** chapters with satisfied prerequisites return `is_locked: false`
- **AND** chapters without prerequisites return `is_locked: false`

#### Scenario: Instructor user
- **WHEN** an instructor requests chapter list
- **THEN** all chapters are returned with `is_locked: false`
- **AND** no database-level locking calculations are performed

#### Scenario: Unauthenticated user
- **WHEN** an unauthenticated user requests chapter list
- **THEN** all chapters are returned with `is_locked: false`
- **AND** no database-level locking calculations are performed

### Requirement: Chapter queryset optimization
**MODIFIED** to use selective annotation based on user role.

The ChapterViewSet.get_queryset() SHALL add `is_locked_db` annotation only for student users.

#### Scenario: Student user queryset
- **WHEN** a student requests chapter list
- **THEN** queryset includes `is_locked_db` annotation
- **AND` annotation uses subqueries to determine locking status

#### Scenario: Instructor user queryset
- **WHEN** an instructor requests chapter list
- **THEN** queryset does not include `is_locked_db` annotation
- **AND` performance is optimized for full chapter visibility

#### Scenario: Query structure with annotations
- **WHEN** student chapter list is queried
- **THEN** the generated SQL SHALL include:
  - EXISTS subquery for unmet prerequisites
  - EXISTS subquery for future unlock dates
  - Case statement combining conditions

### Requirement: Pagination compatibility
**MODIFIED** to maintain pagination performance with database annotations.

The chapter list SHALL support pagination while maintaining the performance benefits of database-level calculations.

#### Scenario: Paginated chapter list
- **WHEN** a student requests page 2 of chapters with pagination
- **THEN** pagination SHALL work correctly
- **AND** total queries SHALL remain <= 3 regardless of page size

#### Scenario: Large result sets
- **WHEN** a course has 100+ chapters
- **THEN** database annotations SHALL efficiently calculate is_locked for all chapters
- **AND` response time SHALL be < 1 second for any page

## ADDED Requirements

### Requirement: Query debugging
The system SHALL provide debugging output for database queries to facilitate performance monitoring.

#### Scenario: Debug SQL output
- **WHEN** DEBUG mode is enabled
- **THEN** the system SHALL log the generated SQL for annotated queries
- **AND** logs SHALL be available in stderr for debugging

### Requirement: Cache compatibility
The chapter list endpoint SHALL maintain compatibility with existing caching mechanisms.

#### Scenario: Cached response
- **WHEN** a chapter list request is cached
- **THEN` the cached response SHALL include correct `is_locked` status
- **AND` cache SHALL be invalidated when ChapterProgress or ChapterUnlockCondition changes