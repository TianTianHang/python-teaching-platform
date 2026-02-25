# Specification: unlock-status-api-enhancement

## ADDED Requirements

### Requirement: unlock_status API with chapter information
The system SHALL return chapter basic information along with unlock status in the `unlock_status` API response.

#### Scenario: Request unlock status for locked chapter
- **WHEN** a user requests `/api/v1/courses/{courseId}/chapters/{chapterId}/unlock_status` endpoint
- **THEN** the system returns a response with `chapter` object containing basic information
- **AND** the `chapter` object includes `id`, `title`, `order`, and `course_title` fields
- **AND** existing fields (`is_locked`, `reason`, `prerequisite_progress`, etc.) remain unchanged
- **AND** the response does not include sensitive data like `content` or other locked fields

#### Scenario: Request unlock status for unlocked chapter
- **WHEN** a user requests unlock status for an unlocked chapter
- **THEN** the system returns the same response format with `chapter` object
- **AND** `is_locked` field is `false`
- **AND** the `chapter` object contains all required basic information

#### Scenario: Response format consistency
- **WHEN** the API is called multiple times for the same chapter
- **THEN** the `chapter` object has the same structure in all responses
- **AND** no additional queries are executed (leveraging existing caching mechanism)
- **AND** response time remains consistent with current implementation

#### Scenario: SSR compatibility
- **WHEN** the API is called during server-side rendering in `locked.tsx`
- **THEN** the API works without browser-specific dependencies
- **AND** the response contains all required data for rendering the lock screen
- **AND** the system maintains caching behavior to ensure fast SSR response

#### Scenario: Backend caching preservation
- **WHEN** `ChapterUnlockService.get_unlock_status()` is called
- **THEN** the result remains cached with the existing TTL strategy
- **AND** the additional `chapter` information does not affect cache key generation
- **AND** cache hits continue to provide performance benefits

---

### Requirement: ChapterUnlockStatus type enhancement
The frontend TypeScript interface `ChapterUnlockStatus` SHALL include optional `chapter` field with chapter basic information.

#### Scenario: TypeScript interface declaration
- **WHEN** defining `ChapterUnlockStatus` in `frontend/web-student/app/types/course.ts`
- **THEN** add optional `chapter` field with the correct type structure
- **AND** the interface remains backward compatible with existing code
- **AND** type checking enforces the correct structure for the `chapter` field

#### Scenario: Frontend type safety
- **WHEN** frontend code accesses the `chapter` field
- **THEN** TypeScript provides autocomplete and type checking
- **AND** accessing undefined `chapter` is safely handled with null checks
- **AND** all required properties (`id`, `title`, `order`, `course_title`) are properly typed

#### Scenario: Migration compatibility
- **WHEN** existing pages that consume `ChapterUnlockStatus` are updated
- **THEN** new `chapter` field is optional and existing code continues to work
- **AND** gradual migration is possible across different pages
- **AND** no runtime errors occur on pages that haven't been updated yet

---

### Requirement: API response performance
The enhanced `unlock_status` API SHALL maintain or improve response times while providing additional data.

#### Scenario: Query count verification
- **WHEN** measuring database queries for the `unlock_status` API
- **THEN** total queries SHALL remain the same as the current implementation
- **AND** no additional queries are executed for the `chapter` object (already fetched)
- **AND** the `get_object()` call provides the chapter data without extra cost

#### Scenario: Response time analysis
- **WHEN** comparing response times before and after the enhancement
- **THEN** response time SHALL NOT increase by more than 10ms
- **AND** cache-hit response times remain consistent
- **AND** serialization overhead from additional fields is negligible

#### Scenario: Memory usage impact
- **WHEN** measuring memory usage during API response serialization
- **THEN** memory increase SHALL be minimal (under 1KB per request)
- **AND** the additional data does not cause memory issues in production
- **AND** garbage collection continues to work efficiently
