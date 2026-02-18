# Add Infinite Scroll to Chapter List

## Summary
Implement infinite scroll pagination for the course chapter list pages, including both the main chapter list page and the chapter detail sidebar. This allows students to seamlessly load more chapters as they scroll down rather than being limited to the first page of results.

## Background
Two locations currently have pagination issues with chapter lists:

1. **Main chapter list** (`_layout.courses_.$courseId_.chapters/route.tsx`): Only fetches and displays the first page of chapters from the API.

2. **Chapter detail sidebar** (`_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`): The sidebar shows only the first page of chapters, making it impossible to navigate to chapters beyond the first page when viewing a specific chapter.

The backend API returns a paginated response (`Page<Chapter>`) with `count`, `next`, `previous`, and `page_size` fields, but the frontend does not utilize the pagination information in either location.

When a course has many chapters (potentially hundreds), students can only see the first page (typically 10-20 items) and cannot access subsequent chapters.

## Goals
1. Automatically load more chapters when the user scrolls near the bottom of the list
2. Maintain SSR compatibility for initial page load
3. Show loading indicators while fetching additional pages
4. Handle edge cases (network errors, end of list, rapid scrolling)
5. Preserve scroll position when navigating back to the page

## Non-Goals
1. Traditional numbered pagination (MUI Pagination component) - infinite scroll is more appropriate for this use case
2. Server-side implementation changes - the backend pagination already works correctly
3. Changing the chapter list UI/layout beyond pagination behavior

## Proposed Solution

### Architecture
1. **Server-side loader**: Continue using the existing loader for initial page data (SSR compatible)
2. **Client-side infinite scroll hook**: Create a new `useInfiniteScroll` hook that:
   - Uses Intersection Observer API to detect when user scrolls near bottom
   - Manages state for accumulated items, current page, and loading/error states
   - Provides a ref for the sentinel element
3. **Client-side fetcher**: Use React Router's `useFetcher` or native `fetch` to load subsequent pages
4. **Loading indicator**: Show a spinner or skeleton at the bottom while fetching

### Key Design Decisions

| Decision | Option | Choice | Rationale |
|----------|--------|--------|-----------|
| Scroll detection | Scroll event listener | Intersection Observer | More performant, already used in LazyRender component |
| State management | Component state | Custom hook | Reusable pattern for other paginated lists |
| Fetch mechanism | useFetcher | useFetcher.load() | Consistent with React Router v7 patterns |
| Page size | Fixed | Use backend default | Backend already controls page_size |

### User Experience
- Initial page load: Shows first page of chapters immediately (SSR)
- Scroll down: Automatically loads next page when user scrolls within 100px of bottom
- Loading state: Shows spinner at bottom of list during fetch
- Error state: Shows "加载失败，点击重试" message with retry button
- End of list: Shows "已加载全部章节" message when no more pages
- Empty state: Existing empty state message remains unchanged

## Alternatives Considered

### Alternative 1: MUI Pagination Component
Use traditional numbered pagination (like submissions page).
- **Pros**: Familiar pattern, easy to jump to specific pages
- **Cons**: Requires additional clicks, poor UX for long lists, not mobile-friendly
- **Rejected**: Infinite scroll provides better UX for content discovery

### Alternative 2: Load More Button
Add a button at bottom to manually load more.
- **Pros**: User controls when to load, predictable
- **Cons**: Requires click for each page, tedious for many items
- **Rejected**: Infinite scroll is more seamless

## Impact

### Scope
- **Modified**:
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters/route.tsx` (main chapter list)
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` (sidebar)
- **Added**: `frontend/web-student/app/hooks/useInfiniteScroll.ts`
- **Capabilities**: Adds new pagination capability for list views

### Dependencies
- React Router v7 `useFetcher` for client-side navigation
- Intersection Observer API (widely supported, with fallback in LazyRender)
- Existing `Page<T>` type and backend pagination

### Risks
- **Risk**: Rapid scrolling could trigger multiple requests
  - **Mitigation**: Add fetching flag to prevent duplicate requests
- **Risk**: Scroll position lost on navigation
  - **Mitigation**: Consider scroll restoration in future iteration (not in scope)
- **Risk**: Browser without Intersection Observer
  - **Mitigation**: Fall back to "Load More" button or show all items

## Open Questions
1. Should we add a "Load More" button fallback for browsers without Intersection Observer?
2. Should the initial page_size be configurable via URL params?
3. Should we preserve scroll position when navigating back? (deferred to future work)

## Success Criteria
### Main Chapter List Page
- [ ] User can scroll down and automatically see more chapters load
- [ ] Initial page load still works with SSR
- [ ] Loading indicator appears during fetch
- [ ] Error handling with retry capability
- [ ] No duplicate requests when scrolling rapidly
- [ ] Clear indication when all chapters are loaded

### Chapter Detail Sidebar
- [ ] Sidebar loads more chapters when scrolling within the drawer
- [ ] Current chapter remains highlighted/selected when new pages load
- [ ] Sidebar can access all chapters in the course, not just first page
- [ ] Works in both mobile (temporary drawer) and desktop (permanent drawer) layouts
