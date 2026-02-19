# Tasks

## Implementation Tasks

### Phase 1: Update Chapter List Loader
- [x] Modify `_layout.courses_.$courseId_.chapters/route.tsx` loader
  - [x] Add page and page_size URL parameters parsing
  - [x] Similar to submissions page pattern (lines 11-32)
  - [x] Return full Page<Chapter> object including next, previous, count
  - [x] Maintain SSR compatibility with existing URL structure

### Phase 2: Create Reusable Infinite Scroll Hook
- [x] Create `useInfiniteScroll.ts` hook in `frontend/web-student/app/hooks/`
  - [x] Define hook interface with generic type support
  - [x] Implement Intersection Observer based scroll detection
  - [x] Add state management for items, currentPage, pageSize, loading, error
  - [x] Build pagination URL with `page` and `page_size` parameters
  - [x] Implement `hasMore` logic based on `next` field from Page type
  - [x] Use `useFetcherAction.loader()` for GET requests with pagination
  - [x] Add loading state to prevent duplicate requests
  - [x] Export hook interface and return type

### Phase 3: Update Chapter List Pages
- [x] Modify `_layout.courses_.$courseId_.chapters/route.tsx` (main chapter list)
  - [x] Import `useInfiniteScroll` hook
  - [x] Add client-side state for accumulated chapters
  - [x] Implement `loadMore` function using `useFetcherAction`
  - [x] Add sentinel element at bottom of list for Intersection Observer
  - [x] Add loading indicator (spinner) at bottom during fetch
  - [x] Add error message with retry button for failed requests
  - [x] Add "已加载全部章节" message when `hasMore` is false
  - [x] Ensure SSR initial load still works correctly

- [x] Modify `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` (sidebar)
  - [x] Import `useInfiniteScroll` hook
  - [x] Extract sidebar list into separate component or apply hook to sidebarContent
  - [x] Add client-side state for accumulated chapters in sidebar
  - [x] Implement `loadMore` function for sidebar chapters
  - [x] Add sentinel element within the Drawer/List for scroll detection
  - [x] Ensure current chapter remains highlighted when new pages load
  - [x] Test with both mobile (temporary) and desktop (permanent) drawer variants

### Phase 5: Add Styling and Polish
- [x] Design loading indicator component
  - [x] Use MUI `CircularProgress` for spinner
  - [x] Add proper spacing and alignment
- [x] Design error message component
  - [x] Use MUI `Button` for retry action
  - [x] Add appropriate error message text
- [x] Design end-of-list indicator
  - [x] Subtle text indicating all items loaded
  - [x] Consistent spacing with loading state

### Phase 6: Testing and Validation
- [x] Manual testing scenarios (main chapter list)
  - [x] Scroll slowly - should load each page sequentially
  - [x] Scroll rapidly - should not trigger duplicate requests
  - [x] Network error - should show error message with retry
  - [x] Empty list - should show empty state message
  - [x] Single page - should not show loading indicator
  - [x] SSR hydration - should work without client-side JS errors
  - [x] Browser compatibility - verify Intersection Observer fallback

- [x] Manual testing scenarios (sidebar)
  - [x] Scroll within sidebar drawer - should load more chapters
  - [x] Current chapter remains highlighted when new pages load
  - [x] Click on newly loaded chapter navigates correctly
  - [x] Mobile temporary drawer - infinite scroll works
  - [x] Desktop permanent drawer - infinite scroll works
  - [x] Sidebar shows all chapters when course has many (50+) chapters

## Notes

### Implementation Hints
- Use `useRef` for sentinel element to avoid re-renders
- Use `useCallback` for loadMore function to maintain stable reference
- The `next` field from `Page<Chapter>` can be used to detect if more pages exist
- Consider using a 100px rootMargin for Intersection Observer to preload slightly early

### Potential Extensions (Out of Scope)
- Scroll position restoration on navigation back
- Configurable page_size via URL params
- Virtual scrolling for very large lists (1000+ items)

### Status
✅ **COMPLETED**: All implementation and testing tasks completed successfully. Infinite scroll pagination is now fully functional for both main chapter list and sidebar.
