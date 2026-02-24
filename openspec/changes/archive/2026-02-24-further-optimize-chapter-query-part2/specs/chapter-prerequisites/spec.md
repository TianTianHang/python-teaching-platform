# Delta: chapter-prerequisites Specification

This document contains changes to the [chapter-prerequisites](../../specs/chapter-prerequisites/spec.md) specification.

## MODIFIED Requirements

### Requirement: Database is_locked calculation
The system SHALL calculate `is_locked` status at the database level using `annotate()` to avoid N+1 queries in chapter list endpoints.

#### Scenario: Student user with prerequisite chapters
- **WHEN** a student requests chapter list with prerequisite unlock conditions
- **THEN** the system calculates `is_locked` status using a single database query with annotations
- **AND** `is_locked_db` field is added to the queryset with correct locking status
- **AND** prerequisite_chapters are prefetched with to_attr to avoid N+1 queries

#### Scenario: Student user with date unlock conditions
- **WHEN** a student requests chapter list with date unlock conditions
- **THEN** the system checks `unlock_date` against current time using database-level Exists subquery
- **AND** returns correct `is_locked` status
- **AND** no additional queries for prerequisite chapters are executed

#### Scenario: Student user with both prerequisite and date conditions
- **WHEN** a student requests chapter list with 'all' unlock condition type
- **THEN** the system checks both prerequisite completion and unlock date
- **AND** returns `is_locked=True` if either condition is not met
- **AND** uses cached completed_chapter_ids for performance

#### Scenario: Chapter without unlock condition
- **WHEN** a student requests chapter list without unlock conditions
- **THEN** `is_locked_db` should be `False`
- **AND** no unnecessary subqueries are performed
- **AND** prefetch_related with to_attr does not add overhead

#### Scenario: Query optimization with to_attr
- **WHEN** the system prefetches prerequisite chapters
- **THEN** data is stored in `to_attr='prerequisite_chapters_all'`
- **AND** serializers access data from memory, not database queries
- **AND** total queries for 14 chapters are < 15

---

### Requirement: Chapter queryset optimization
The ChapterViewSet.get_queryset() SHALL optimize queries using to_attr prefetches to eliminate N+1 queries.

#### Scenario: Student user queryset with optimized prefetches
- **WHEN** a student requests chapter list
- **THEN** queryset includes `is_locked_db` annotation
- **AND** annotation uses cached `completed_chapter_ids` from `self._completed_chapter_ids`
- **AND** `unlock_condition__prerequisite_chapters` is prefetched with to_attr
- **AND** no individual chapter queries are executed

#### Scenario: Prefetch with to_attr implementation
- **WHEN** get_queryset is executed
- **THEN** the system creates:
  ```python
  Prefetch(
      'unlock_condition__prerequisite_chapters',
      queryset=Chapter.objects.select_related('course'),
      to_attr='prerequisite_chapters_all'
  )
  ```
- **AND** this prefetch is accessible via `obj.unlock_condition.prerequisite_chapters_all`
- **AND** serializers use this data instead of `.all()` methods

#### Scenario: Removal of instructor/admin checks
- **WHEN** a student requests chapter list
- **THEN** no `_is_instructor_or_admin()` check is performed
- **AND** system assumes all users are students
- **AND** this reduces unnecessary database queries

---

### Requirement: Chapter serializer is_locked field
The ChapterSerializer SHALL use database-calculated `is_locked` and optimized prefetch data to avoid queries.

#### Scenario: Using database annotation
- **WHEN** the chapter object has `is_locked_db` attribute
- **THEN** `get_is_locked()` SHALL return `obj.is_locked_db`
- **AND** no service layer calls or additional queries are made

#### Scenario: Using optimized prerequisite data
- **WHEN** `ChapterUnlockConditionSerializer.get_prerequisite_chapters()` is called
- **THEN** it uses `obj.prerequisite_chapters_all` from to_attr
- **AND** no database queries are executed
- **AND** data is returned from memory

#### Scenario: Chapter without unlock condition
- **WHEN** a chapter has no unlock condition
- **THEN** `get_is_locked()` SHALL return `False`
- **AND** this SHALL be determined efficiently without unnecessary checks

---

### Requirement: Query performance optimization
The chapter list API SHALL eliminate all N+1 queries to achieve < 15 total queries.

#### Scenario: Query count verification
- **WHEN** a student requests chapter list with 14 chapters
- **THEN** total database queries SHALL be < 15
- **AND** no duplicate queries for `completed_chapter_ids` or `enrollment`
- **AND** no N+1 queries for prerequisite chapters

#### Scenario: Performance comparison
- **WHEN** comparing before and after optimization
- **THEN** query count SHALL reduce from 34 to < 15
- **AND** response time SHALL improve by 50%+
- **AND** memory usage remains acceptable

#### Scenario: Serialization performance
- **WHEN** serializing chapter list with unlock conditions
- **THEN** all prerequisite chapter data is loaded in initial prefetch
- **AND** serialization does not trigger additional database queries
- **AND** the system can handle 100+ chapters efficiently