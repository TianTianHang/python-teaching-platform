## ADDED Requirements

### Requirement: Chapter Progress Cache Invalidation

The system SHALL automatically invalidate related caches when `ChapterProgress` records are created, updated, or deleted, ensuring that users see the most current progress status.

#### Scenario: Chapter marked as completed updates cache

- **WHEN** a user marks a chapter as completed via the `mark_as_completed` API
- **THEN** the chapter list cache SHALL be invalidated
- **AND** the chapter detail cache SHALL be invalidated
- **AND** the chapter progress list cache SHALL be invalidated
- **AND** the enrollment detail cache SHALL be invalidated
- **AND** subsequent API calls SHALL return the updated completed status

#### Scenario: Chapter progress unmarked updates cache

- **WHEN** a user unmarks a chapter as completed (sets `completed=false`)
- **THEN** the chapter list cache SHALL be invalidated
- **AND** the chapter detail cache SHALL be invalidated
- **AND** the chapter progress list cache SHALL be invalidated
- **AND** the enrollment detail cache SHALL be invalidated
- **AND** subsequent API calls SHALL return the updated in-progress status

#### Scenario: Chapter progress deletion updates cache

- **WHEN** a chapter progress record is deleted
- **THEN** the chapter list cache SHALL be invalidated
- **AND** the chapter detail cache SHALL be invalidated
- **AND** the chapter progress list cache SHALL be invalidated
- **AND** the enrollment detail cache SHALL be invalidated

#### Scenario: Consistency with ProblemProgress pattern

- **WHEN** implementing the cache invalidation logic
- **THEN** the implementation SHALL follow the same pattern as `ProblemProgress` signal handler
- **AND** SHALL use Django signals (`post_save`, `post_delete`) for automatic triggering
- **AND** SHALL use `delete_cache_pattern` for cache invalidation
