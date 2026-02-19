# infinite-pagination Specification

## Purpose
TBD - created by archiving change add-chapter-infinite-scroll. Update Purpose after archive.
## Requirements
### Requirement: Infinite Scroll Hook
The system SHALL provide a `useInfiniteScroll` hook that manages client-side infinite scroll behavior for paginated data.

#### Scenario: Hook initializes with initial page data
Given a component has received initial page data from a server-side loader
When the component uses the `useInfiniteScroll` hook
Then the hook accepts the initial data as a parameter
And the hook returns the accumulated items list
And the hook returns a sentinel ref for scroll detection
And the hook returns loading, error, and hasMore state flags

#### Scenario: Hook detects scroll to bottom
Given a user is viewing a list with more pages available
When the user scrolls within the detection threshold (100px) of the bottom
Then the hook invokes the loadMore callback
And the hook sets loading state to true
And the hook prevents duplicate calls while loading

#### Scenario: Hook accumulates fetched pages
Given a list has loaded the first page with 10 items
And the user scrolls to trigger loading page 2
When page 2 returns 10 more items
Then the hook appends the new items to the existing list
And the total items count becomes 20
And the items remain in order (page 1 items, then page 2 items)

#### Scenario: Hook handles end of pagination
Given a list has loaded all available pages
When the last page is loaded
Then the hook sets hasMore to false
And the scroll detection is disabled
And no further requests are made on scroll

#### Scenario: Hook handles fetch errors
Given a network error occurs while loading more items
When the error is received
Then the hook sets error state with the error message
And the hook allows retry by calling loadMore again
And the loading state is reset to false

### Requirement: Chapter List Infinite Scroll
The chapter list page SHALL automatically load more chapters when the user scrolls near the bottom of the list.

#### Scenario: Initial page load shows first page
Given a course has 30 chapters total
And the API page_size is 10
When a student navigates to the chapter list page
Then the server-side loader fetches page 1 (chapters 1-10)
And the page renders with SSR showing the first 10 chapters
And no loading indicator is shown initially

#### Scenario: Scrolling triggers next page load
Given a student is viewing the chapter list with chapters 1-10 displayed
And more chapters exist (chapters 11-30)
When the student scrolls to within 100px of the list bottom
Then a loading spinner appears at the bottom of the list
And the client fetches page 2 (chapters 11-20)
And when page 2 loads, chapters 11-20 are appended to the list
And the loading spinner disappears

#### Scenario: Multiple pages load on continuous scroll
Given a student scrolls continuously down the chapter list
When the user passes the threshold for each page
Then each page is loaded sequentially
And all pages (1, 2, 3) are accumulated in the displayed list
And the student can scroll through all 30 chapters seamlessly

#### Scenario: End of list indicator
Given a student has scrolled through all 30 chapters
When the last page (page 3) is loaded
Then a subtle "已加载全部章节" message appears at the bottom
And no loading spinner is shown
And no further requests are made on scroll

#### Scenario: Network error with retry
Given a student is scrolling to load more chapters
And a network error occurs while fetching page 2
When the error is detected
Then an error message "加载失败，点击重试" appears with a retry button
And the list shows the previously loaded chapters (page 1)
And clicking the retry button re-attempts to fetch page 2

#### Scenario: Rapid scrolling does not duplicate requests
Given a student scrolls rapidly to the bottom
When multiple scroll events fire within a short period
Then only one request is made per page
And the loading flag prevents duplicate requests
And all pages are loaded exactly once

#### Scenario: Empty list shows appropriate message
Given a course has no chapters
When a student navigates to the chapter list page
Then the existing "暂无章节" empty state message is displayed
And no infinite scroll behavior is triggered

### Requirement: Chapter Detail Sidebar Infinite Scroll
The chapter detail page sidebar SHALL support infinite scroll to load all course chapters, allowing navigation to any chapter from within the chapter detail view.

#### Scenario: Sidebar initial load shows first page
Given a student is viewing chapter 5 of a 30-chapter course
When the chapter detail page loads
Then the sidebar fetches and displays the first page of chapters (chapters 1-10)
And chapter 5 is highlighted as the current chapter
And chapters 1-10 are clickable for navigation

#### Scenario: Sidebar scroll loads more chapters
Given a student is viewing the chapter detail page
And the sidebar shows chapters 1-10
When the student scrolls within the sidebar drawer to near the bottom
Then the sidebar fetches page 2 (chapters 11-20)
And the new chapters are appended to the sidebar list
And the current chapter (5) remains highlighted

#### Scenario: Sidebar provides access to all chapters
Given a course has 50 chapters total
And a student is viewing chapter 45
When the student opens the chapter detail page
Then chapter 45 may not be initially visible (only page 1 shown)
When the student scrolls in the sidebar
Then all 50 chapters can be loaded and displayed
And the student can click and navigate to chapter 45 or any other chapter

#### Scenario: Current chapter remains highlighted during pagination
Given a student is viewing chapter 15
And chapter 15 is on page 2 (chapters 11-20)
When the sidebar loads page 1 initially (chapters 1-10)
And then loads page 2 when the student scrolls
Then chapter 15 is highlighted with "action.selected" background
And chapter 15 has bold text styling
And the highlight persists as more pages load

#### Scenario: Mobile and desktop sidebar both support infinite scroll
Given a student is viewing the chapter detail page on a mobile device
When the temporary drawer is open and scrolled
Then more chapters load as expected
Given a student is viewing the chapter detail page on a desktop device
When the permanent drawer sidebar is scrolled
Then more chapters load as expected

### Requirement: Loading State Indicators
The system SHALL provide visual feedback during infinite scroll loading operations.

#### Scenario: Loading spinner appears during fetch
Given a user scrolls to trigger loading more items
When the fetch request is in progress
Then a MUI CircularProgress spinner appears at the bottom of the list
And the spinner is centered horizontally
And the spinner has appropriate vertical spacing

#### Scenario: Error state shows retry option
Given a fetch request fails with an error
When the error is received
Then an error message is displayed
And a "重试" button is provided
And clicking the button re-invokes the loadMore function
And the button uses MUI Button component with appropriate styling

#### Scenario: End of list shows completion message
Given all pages have been loaded
When hasMore is false
Then a subtle "已加载全部 {count} 条" message is displayed
And the message uses MUI Typography with secondary color
And the message is centered with appropriate spacing

