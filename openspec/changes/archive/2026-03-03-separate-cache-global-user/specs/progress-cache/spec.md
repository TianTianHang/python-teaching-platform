# progress-cache Specification Changes

## MODIFIED Requirements

### Requirement: Chapter Progress Cache Invalidation

The system SHALL automatically invalidate user state caches when `ChapterProgress` records are created, updated, or deleted, ensuring that users see the most current progress status. Global data caches SHALL NOT be invalidated by user progress changes.

#### Scenario: Chapter marked as completed updates cache

- **WHEN** a user marks a chapter as completed via the `mark_as_completed` API
- **THEN** the chapter user state cache SHALL be invalidated
- **AND** the chapter progress list cache SHALL be invalidated
- **AND** the enrollment detail cache SHALL be invalidated
- **AND** the chapter global data cache SHALL NOT be invalidated
- **AND** subsequent API calls SHALL return the updated completed status

#### Scenario: Chapter progress unmarked updates cache

- **WHEN** a user unmarks a chapter as completed (sets `completed=false`)
- **THEN** the chapter user state cache SHALL be invalidated
- **AND** the chapter progress list cache SHALL be invalidated
- **AND** the enrollment detail cache SHALL be invalidated
- **AND** the chapter global data cache SHALL NOT be invalidated
- **AND** subsequent API calls SHALL return the updated in-progress status

#### Scenario: Chapter progress deletion updates cache

- **WHEN** a chapter progress record is deleted
- **THEN** the chapter user state cache SHALL be invalidated
- **AND** the chapter progress list cache SHALL be invalidated
- **AND** the enrollment detail cache SHALL be invalidated
- **AND** the chapter global data cache SHALL NOT be invalidated

#### Scenario: Consistency with ProblemProgress pattern

- **WHEN** implementing the cache invalidation logic
- **THEN** the implementation SHALL follow the same pattern as `ProblemProgress` signal handler
- **AND** SHALL use Django signals (`post_save`, `post_delete`) for automatic triggering
- **AND** SHALL use targeted cache key deletion for user state cache
- **AND** SHALL NOT use `delete_cache_pattern` for global data cache invalidation
- **AND** SHALL only invalidate caches specific to the user whose progress changed

#### Scenario: Targeted user state cache invalidation

- **WHEN** a user's chapter progress changes
- **THEN** only that user's state cache SHALL be invalidated
- **AND** other users' state caches SHALL NOT be affected
- **AND** the cache key format SHALL be `chapter:status:{course_id}:{user_id}`
- **AND** only the specific cache key for the affected user SHALL be deleted