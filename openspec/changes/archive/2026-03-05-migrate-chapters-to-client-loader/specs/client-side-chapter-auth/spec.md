## ADDED Requirements

### Requirement: Client-side authentication for chapter pages
The system SHALL authenticate users on chapter pages using JWT tokens stored on the client side, without relying on server-side session validation.

#### Scenario: Successful authentication with valid token
- **WHEN** user accesses a chapter page with a valid JWT token in localStorage or cookie
- **THEN** system SHALL allow access to the page
- **AND** system SHALL fetch chapter data using the token in Authorization header

#### Scenario: Authentication failure with invalid token
- **WHEN** user accesses a chapter page with an expired or invalid JWT token
- **THEN** system SHALL receive a 401 error from the API
- **AND** system SHALL redirect user to `/auth/login` page using React Router's `redirect()`

#### Scenario: Authentication failure with missing token
- **WHEN** user accesses a chapter page without a JWT token
- **THEN** system SHALL receive a 401 error from the API
- **AND** system SHALL redirect user to `/auth/login` page

### Requirement: Client-side chapter unlock status checking
The system SHALL check chapter unlock status on the client side and return status information to the component for conditional rendering or redirection.

#### Scenario: Chapter is unlocked
- **WHEN** user accesses an unlocked chapter page
- **THEN** clientLoader SHALL fetch unlock status from `/courses/{courseId}/chapters/{chapterId}/unlock_status`
- **AND** system SHALL return `is_locked: false` in the loader data
- **AND** component SHALL render the chapter content normally

#### Scenario: Chapter is locked
- **WHEN** user accesses a locked chapter page
- **THEN** clientLoader SHALL fetch unlock status from `/courses/{courseId}/chapters/{chapterId}/unlock_status`
- **AND** system SHALL return `is_locked: true` in the loader data
- **AND** component SHALL use React Router's `useNavigate()` to redirect to `/courses/{courseId}/chapters/{chapterId}/locked`

#### Scenario: Unlock status check fails with permission error
- **WHEN** unlock status API returns 403 Forbidden
- **THEN** clientLoader SHALL treat the chapter as locked
- **AND** system SHALL return `is_locked: true` in the loader data
- **AND** component SHALL redirect to locked page

#### Scenario: Unlock status check fails with not found error
- **WHEN** unlock status API returns 404 Not Found
- **THEN** clientLoader SHALL treat the chapter as locked
- **AND** system SHALL return `is_locked: true` in the loader data
- **AND** component SHALL redirect to locked page

### Requirement: Client-side redirection based on chapter status
The system SHALL perform client-side redirection based on chapter unlock status without server-side redirects.

#### Scenario: Redirect to locked page
- **WHEN** clientLoader returns `is_locked: true`
- **THEN** component SHALL use `useNavigate()` to redirect to `/courses/{courseId}/chapters/{chapterId}/locked`
- **AND** redirection SHALL happen on the client side without server involvement

#### Scenario: No redirect for unlocked chapters
- **WHEN** clientLoader returns `is_locked: false`
- **THEN** component SHALL render the chapter content
- **AND** no redirection SHALL occur

### Requirement: Client-side error handling for chapter pages
The system SHALL handle API errors gracefully on chapter pages with appropriate user feedback.

#### Scenario: Network error during data fetching
- **WHEN** clientLoader encounters a network error
- **THEN** ErrorBoundary SHALL catch the error
- **AND** system SHALL display an error message to the user
- **AND** system SHALL provide a retry button

#### Scenario: Server error (500) during data fetching
- **WHEN** clientLoader receives a 500 error from the API
- **THEN** ErrorBoundary SHALL catch the error
- **AND** system SHALL display an error message indicating server issues
- **AND** system SHALL provide a retry button

#### Scenario: Rate limiting error (429) during data fetching
- **WHEN** clientLoader receives a 429 error from the API
- **THEN** ErrorBoundary SHALL catch the error
- **AND** system SHALL display an error message indicating too many requests
- **AND** system SHALL instruct user to wait before retrying

### Requirement: Hydration fallback for chapter pages
The system SHALL display a loading skeleton while clientLoader data is being hydrated on initial page load.

#### Scenario: Initial page load with hydration
- **WHEN** user first visits a chapter page (non-navigated)
- **THEN** system SHALL render the `HydrateFallback` component
- **AND** system SHALL display loading skeleton matching the page structure
- **AND** system SHALL replace skeleton with actual content once hydration completes

#### Scenario: Client-side navigation
- **WHEN** user navigates between chapters using client-side routing
- **THEN** system SHALL use cached data from previous loader calls if available
- **AND** system SHALL fetch fresh data if cache is stale
- **AND** system SHALL minimize loading time

### Requirement: Preserve chapter progress tracking side effects
The system SHALL continue to track chapter progress (e.g., marking as "in_progress") on the client side without blocking page rendering.

#### Scenario: Mark chapter as in-progress
- **WHEN** user accesses a chapter with status "not_started"
- **THEN** clientLoader SHALL fire a non-blocking request to mark chapter as "in_progress"
- **AND** this request SHALL NOT delay page rendering
- **AND** errors from this request SHALL be handled silently without affecting user experience

#### Scenario: Failure to mark chapter as in-progress
- **WHEN** the mark-as-in-progress request fails
- **THEN** system SHALL log the error for debugging
- **AND** system SHALL NOT display error to the user
- **AND** page SHALL render normally
