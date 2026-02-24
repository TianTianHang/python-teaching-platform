# Delta: chapter-prerequisites Specification

This document contains changes to the [chapter-prerequisites](../../specs/chapter-prerequisites/spec.md) specification.

## MODIFIED Requirements

### Requirement: Database is_locked calculation
The system SHALL calculate `is_locked` status at the database level using `annotate()` to avoid N+1 queries in chapter list endpoints. **All user roles (including instructors and admins) receive the annotation to unify query paths.**

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
- **THEN** `is_locked_db` annotation is added with value `False` for all chapters
- **AND** this unifies the query path across all user roles
- **AND** `is_locked` field returns `False` from serializer

#### Scenario: Unauthenticated user
- **WHEN** an unauthenticated user requests chapter list
- **THEN** `is_locked_db` annotation is added with value `False` for all chapters
- **AND** `is_locked` field returns `False` from serializer

---

### Requirement: Chapter queryset optimization
The ChapterViewSet.get_queryset() SHALL add `is_locked_db` annotation for all authenticated users to unify query paths and avoid fallback queries.

#### Scenario: Student user queryset
- **WHEN** a student requests chapter list
- **THEN** queryset includes `is_locked_db` annotation
- **AND** annotation uses subqueries to determine locking status
- **AND** annotation uses cached `completed_chapter_ids` from `self._completed_chapter_ids`

#### Scenario: Instructor user queryset
- **WHEN** an instructor requests chapter list
- **THEN** queryset includes `is_locked_db` annotation with value `False`
- **AND** no locking subqueries are executed
- **AND** query path is unified with student users

#### Scenario: Query structure with annotations
- **WHEN** student chapter list is queried
- **THEN** the generated SQL SHALL include:
  - EXISTS subquery for unmet prerequisites (uses cached `completed_chapter_ids`)
  - EXISTS subquery for future unlock dates
  - Case statement combining conditions

#### Scenario: Cache reuse in _annotate_is_locked
- **WHEN** `_annotate_is_locked()` is called
- **THEN** the method reuses `self._completed_chapter_ids` cache
- **AND** does not execute duplicate database query for completed chapters

---

### Requirement: Chapter serializer is_locked field
The ChapterSerializer SHALL use database-calculated `is_locked` when available, and use context-provided enrollment for fallback cases to avoid duplicate queries.

#### Scenario: Using database annotation
- **WHEN** the chapter object has `is_locked_db` attribute
- **THEN** `get_is_locked()` SHALL return `obj.is_locked_db`
- **AND** no service layer calls or additional queries are made

#### Scenario: Fallback to service layer with context enrollment
- **WHEN** the chapter object does not have `is_locked_db` attribute
- **THEN** `get_is_locked()` SHALL use `enrollment` from serializer context
- **AND** no duplicate enrollment query is made

#### Scenario: Chapter without unlock condition
- **WHEN** a chapter has no unlock condition
- **THEN** `get_is_locked()` SHALL return `False`
- **AND** this SHALL be determined efficiently without unnecessary checks

---

### Requirement: Chapter list endpoint performance
The chapter list API SHALL minimize database queries by reusing cached data and passing context to serializers.

#### Scenario: Student user with locked chapters
- **WHEN** a student requests `/api/courses/{course_id}/chapters/`
- **THEN** the endpoint returns all chapters with correct `is_locked` status
- **AND** `enrollment` is passed to serializer context (no duplicate query)
- **AND** `completed_chapter_ids` is reused in `_annotate_is_locked` (no duplicate query)

#### Scenario: Query count after optimization
- **WHEN** a student requests chapter list with 14 chapters
- **THEN** total database queries SHALL be < 25
- **AND** no duplicate queries for `completed_chapter_ids` or `enrollment`

#### Scenario: Instructor user
- **WHEN** an instructor requests chapter list
- **THEN** all chapters are returned with `is_locked: false`
- **AND** `is_locked_db` annotation is added (value False) for unified query path

#### Scenario: Unauthenticated user
- **WHEN** an unauthenticated user requests chapter list
- **THEN** all chapters are returned with `is_locked: false`
- **AND** `is_locked_db` annotation is added (value False) for unified query path

---

### Requirement: Serializer context enrichment
The ChapterViewSet SHALL pass `enrollment` and `completed_chapter_ids` to serializer context to avoid duplicate queries in serializer methods.

#### Scenario: Context includes enrollment
- **WHEN** `get_serializer_context()` is called
- **THEN** context includes `enrollment` if available from `get_queryset()`
- **AND** context includes `completed_chapter_ids` from cache

#### Scenario: Serializer uses context enrollment
- **WHEN** serializer needs to check enrollment status
- **THEN** serializer uses `context['enrollment']`
- **AND** no duplicate enrollment query is made
