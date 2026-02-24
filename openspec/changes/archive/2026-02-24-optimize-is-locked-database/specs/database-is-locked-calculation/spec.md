## ADDED Requirements

### Requirement: Database is_locked calculation
The system SHALL calculate `is_locked` status at the database level using `annotate()` to avoid N+1 queries in chapter list endpoints.

#### Scenario: Student user with prerequisite chapters
- **WHEN** a student requests chapter list with prerequisite unlock conditions
- **THEN** the system calculates `is_locked` status using a single database query with annotations
- **AND** `is_locked_db` field is added to the queryset with correct locking status

#### Scenario: Student user with date unlock conditions
- **WHEN** a student requests chapter list with date unlock conditions
- **THEN** the system checks `unlock_date` against current time using database-level Exists subquery
- **AND** returns correct `is_locked` status

#### Scenario: Student user with both prerequisite and date conditions
- **WHEN** a student requests chapter list with 'all' unlock condition type
- **THEN** the system checks both prerequisite completion and unlock date
- **AND** returns `is_locked=True` if either condition is not met

#### Scenario: Chapter without unlock condition
- **WHEN** a student requests chapter list without unlock conditions
- **THEN** `is_locked_db` should be `False`
- **AND** no unnecessary subqueries are performed

#### Scenario: Instructor user
- **WHEN** an instructor requests chapter list
- **THEN** no `is_locked` annotations are added (instructors see all chapters)
- **AND** `is_locked` field returns `False` from serializer

#### Scenario: Unauthenticated user
- **WHEN** an unauthenticated user requests chapter list
- **THEN** no `is_locked` annotations are added
- **AND** `is_locked` field returns `False` from serializer

## MODIFIED Requirements

### Requirement: Chapter list performance
**MODIFIED** from "no performance requirements" to specific performance targets.

The chapter list API SHALL execute no more than 3 database queries regardless of the number of chapters returned.

#### Scenario: Performance with 10 chapters
- **WHEN** a student requests a list of 10 chapters
- **THEN** total database queries SHALL be <= 3
- **AND** no individual chapter queries are performed

#### Scenario: Performance with 50 chapters
- **WHEN** a student requests a list of 50 chapters
- **THEN** total database queries SHALL be <= 3
- **AND** response time shall be < 500ms

### Requirement: Chapter serialization
**MODIFIED** to support database annotation fallback.

The ChapterSerializer SHALL use `is_locked_db` from database annotation when available, and fall back to service layer for compatibility.

#### Scenario: Using database annotation
- **WHEN** chapter object has `is_locked_db` attribute
- **THEN** `get_is_locked()` returns the value directly
- **AND** no service layer calls are made

#### Scenario: Fallback to service layer
- **WHEN** chapter object does not have `is_locked_db` attribute
- **THEN** `get_is_locked()` falls back to `ChapterUnlockService.is_unlocked()`
- **AND** existing functionality is preserved

### Requirement: Prerequisite progress field
**MODIFIED** to remain unchanged but avoid N+1 when combined with is_locked.

The `prerequisite_progress` field SHALL continue to work as before, but list queries shall avoid additional queries when `is_locked` is calculated via database.

#### Scenario: Prerequisite progress with is_locked
- **WHEN** chapter has unlock conditions and `is_locked` is calculated via database
- **THEN** `prerequisite_progress` SHALL continue to use service layer and caching
- **AND** total queries remain within performance targets

## REMOVED Requirements

### Requirement: Service layer is_locked calls in list endpoint
**Reason**: Performance optimization requires moving this calculation to database layer to avoid N+1 queries
**Migration**: All chapter list endpoints now use database annotations, eliminating the need for service calls during serialization

### Requirement: Exists queries in serializer
**Reason**: These queries cause N+1 problems and are now replaced by database-level calculations
**Migration**: Removed from serializer logic, performed at query level instead