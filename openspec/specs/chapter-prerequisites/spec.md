# chapter-prerequisites Specification

## Purpose
TBD - created by archiving change add-chapter-prerequisites. Update Purpose after archive.
## Requirements
### Requirement: Chapter Unlock Condition Model
The system SHALL provide a `ChapterUnlockCondition` model to define prerequisites that must be met before a chapter becomes accessible to a student.

#### Scenario: Instructor creates chapter with single prerequisite
Given an instructor is creating a chapter "Advanced Loops"
And there exists a chapter "Basic Loops" in the same course
When the instructor sets "Basic Loops" as a prerequisite
Then the `ChapterUnlockCondition` model is created with `prerequisite_chapters` containing "Basic Loops"
And the chapter "Advanced Loops" is locked for students who haven't completed "Basic Loops"

#### Scenario: Instructor creates chapter with multiple prerequisites
Given an instructor is creating a chapter "Object-Oriented Programming"
And there exist chapters "Variables", "Functions", and "Classes" in the same course
When the instructor sets all three as prerequisites
Then the `ChapterUnlockCondition` model is created with all three in `prerequisite_chapters`
And the chapter is only unlocked after ALL three prerequisites are completed

#### Scenario: Instructor sets time-based unlock condition
Given an instructor is creating a chapter
When the instructor sets an `unlock_date` of 2025-03-01
Then the chapter is locked before that date regardless of prerequisite completion
And the chapter unlocks after that date if prerequisites are also met

#### Scenario: Chapter without unlock condition
Given an instructor creates a chapter without setting any unlock conditions
Then the chapter is accessible to all enrolled students immediately
And no `ChapterUnlockCondition` record exists for that chapter

#### Scenario: Unlock condition type 'prerequisite' only checks prerequisites
Given an instructor creates a chapter with `unlock_condition_type='prerequisite'`
And the instructor sets "Chapter 1" as a prerequisite
And the instructor sets an `unlock_date` in the future
When a student has completed "Chapter 1" but the current date is before the unlock date
Then the chapter is unlocked (only prerequisites are checked)
And the unlock date is ignored

#### Scenario: Unlock condition type 'date' only checks unlock date
Given an instructor creates a chapter with `unlock_condition_type='date'`
And the instructor sets "Chapter 1" as a prerequisite
And the instructor sets an `unlock_date` in the past
When a student has not completed "Chapter 1" but the current date is past the unlock date
Then the chapter is unlocked (only date is checked)
And the prerequisites are ignored

#### Scenario: Unlock condition type 'all' checks both conditions
Given an instructor creates a chapter with `unlock_condition_type='all'` (default)
And the instructor sets "Chapter 1" as a prerequisite
And the instructor sets an `unlock_date` in the future
When a student has completed "Chapter 1" but the current date is before the unlock date
Then the chapter remains locked
And both prerequisites and date must be satisfied

#### Scenario: Instructor attempts to set chapter as its own prerequisite
Given an instructor is editing a chapter's unlock conditions
When the instructor tries to add the same chapter as its own prerequisite
Then the system raises a `ValidationError`
And the error message indicates that a chapter cannot depend on itself
And the unlock condition is not saved

#### Scenario: Instructor creates circular dependency
Given chapter "A" has chapter "B" as a prerequisite
When the instructor tries to set chapter "A" as a prerequisite for chapter "B"
Then the system raises a `ValidationError`
And the error message indicates a circular dependency was detected
And the unlock condition is not saved

#### Scenario: Instructor creates dependency chain exceeding depth limit
Given there is a chain of 6 chapters where each depends on the previous (A→B→C→D→E→F)
When the instructor tries to create an unlock condition on chapter "F" with chapter "E" as prerequisite
Then the system raises a `ValidationError`
And the error message indicates the dependency chain is too deep (max depth: 5)
And the unlock condition is not saved

---

### Requirement: Chapter Unlock Status Service
The system SHALL provide a service to determine whether a chapter is unlocked for a specific student enrollment.

#### Scenario: Student checks unlock status for locked chapter
Given a student has not completed chapter "Basic Loops"
And chapter "Advanced Loops" has "Basic Loops" as a prerequisite
When the system checks if "Advanced Loops" is unlocked for this student
Then the result is `False`
And the system returns information about which prerequisites are incomplete

#### Scenario: Student checks unlock status after completing prerequisites
Given a student has completed all prerequisite chapters
When the system checks unlock status
Then the result is `True`
And the chapter is accessible via API

#### Scenario: Student checks unlock status before unlock date
Given a student has completed all prerequisites
But the current date is before the `unlock_date`
When the system checks unlock status
Then the result is `False`
And the system returns information about the unlock date

#### Scenario: Admin bypasses unlock check
Given an administrator or instructor checks unlock status
When the system checks unlock status for an admin/instructor
Then the result is always `True`
And all chapters are accessible regardless of unlock conditions

---

### Requirement: Chapter API Filtering
The API SHALL filter out locked chapters from list and retrieve responses for student users using database-level queries to avoid loading all chapters into memory.

#### Scenario: Student lists course chapters
Given a course has chapters "Chapter 1", "Chapter 2", and "Chapter 3"
And "Chapter 3" requires completion of "Chapter 1" and "Chapter 2"
And a student has only completed "Chapter 1"
When the student requests the chapter list via API
Then the response includes only "Chapter 1" and "Chapter 2"
And "Chapter 3" is not included in the response

#### Scenario: Student attempts to access locked chapter directly
Given a student has not completed the prerequisites for "Chapter 3"
When the student attempts to retrieve "Chapter 3" directly via API
Then the API returns a 403 Forbidden error
And the error message indicates the chapter is locked
And the error message lists unmet prerequisites

#### Scenario: Instructor lists course chapters
Given an instructor requests the chapter list for a course
When the API responds
Then all chapters are included regardless of unlock conditions
And unlock condition information is included in the response

#### Scenario: API filtering uses database-level queries
Given a course has 100 chapters with various unlock conditions
And a student requests the chapter list via API
When the API executes the query
Then the filtering is performed at the database level using SQL WHERE/EXISTS clauses
And the response does NOT load all chapters into Python memory before filtering
And the query executes in O(1) memory complexity relative to chapter count

---

### Requirement: Chapter Unlock Status Endpoint
The API SHALL provide an endpoint to query unlock status without returning chapter content.

#### Scenario: Student queries unlock status
Given a student wants to know when a chapter will be unlocked
When the student calls the `unlock_status` action on the chapter endpoint
Then the response includes:
- `is_locked`: boolean indicating lock status
- `prerequisite_progress`: object with completed/total counts
- `remaining_prerequisites`: list of incomplete prerequisites
- `unlock_date`: datetime if applicable, or null
- `time_until_unlock`: seconds until unlock if date-based

#### Scenario: Student queries unlock status for unlocked chapter
Given a chapter is unlocked for a student (all prerequisites completed)
When the student queries unlock status
Then the response indicates `is_locked: false`
And `prerequisite_progress` shows all prerequisites complete

---

### Requirement: Frontend Locked Chapter Display
The frontend SHALL display visual indicators for locked chapters and show prerequisite progress.

#### Scenario: Student views chapter list with locked chapters
Given a course has locked chapters
When a student views the chapter list
Then locked chapters display a lock icon
And locked chapters show the number of prerequisites required (e.g., "Complete 2 more chapters")
And locked chapters are not clickable/navigable

#### Scenario: Student hovers over locked chapter
Given a student hovers over a locked chapter in the list
When the hover tooltip is shown
Then it displays which chapters need to be completed
And it shows progress towards completion (e.g., "2/3 prerequisites completed")

#### Scenario: Student navigates to locked chapter directly
Given a student attempts to navigate directly to a locked chapter URL
When the page loads
Then a lock screen is displayed
And the lock screen shows prerequisite information
And no chapter content is shown

#### Scenario: All prerequisites completed
Given a student completes the final prerequisite for a chapter
When the chapter list is refreshed
Then the previously locked chapter no longer shows the lock icon
And the chapter is clickable and accessible

---

### Requirement: Chapter Progress Cache Invalidation
The system SHALL invalidate unlock status cache when prerequisite completion status changes.

#### Scenario: Student completes prerequisite chapter
Given a chapter's unlock status is cached
When the student completes a prerequisite chapter
And `ChapterProgress.completed` is set to `True`
Then the cache entry for the dependent chapter is invalidated
And subsequent unlock checks return the updated status

#### Scenario: Instructor modifies unlock conditions
Given a chapter's unlock conditions are cached
When an instructor adds or removes prerequisites
Then the cache entries for affected chapters are invalidated
And students see updated lock status on next request

---

### Requirement: Admin Interface for Unlock Conditions
The admin interface SHALL allow instructors to manage chapter unlock conditions.

#### Scenario: Instructor adds unlock condition via admin
Given an instructor is editing a chapter in the admin interface
When the instructor opens the "Unlock Conditions" inline
Then they can select prerequisite chapters from a multi-select dropdown
And they can optionally set an unlock date using a date/time picker
And they can choose the unlock condition type

#### Scenario: Instructor removes unlock condition
Given a chapter has an unlock condition
When the instructor deletes the unlock condition in admin
Then the chapter becomes immediately accessible to all students
And the `ChapterUnlockCondition` record is deleted

#### Scenario: Admin displays dependent chapters
Given an instructor is viewing a chapter
And that chapter is a prerequisite for other chapters
When the instructor views the chapter detail
Then the admin displays a list of dependent chapters
And shows which chapters would be affected if this chapter were modified

---

