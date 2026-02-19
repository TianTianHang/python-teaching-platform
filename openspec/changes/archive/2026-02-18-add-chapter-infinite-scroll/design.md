# Infinite Scroll Design Document

## Architecture Overview

### High-Level Design
The infinite scroll implementation follows a reusable hook pattern with client-side pagination. The system maintains SSR compatibility for initial page loads while progressively enhancing the experience with infinite scroll on the client.

### Key Components
1. **useInfiniteScroll Hook** - Core logic for infinite scroll behavior
2. **InfiniteScrollList Component** - Optional wrapper component for styling
3. **Chapter List Page** - Main chapter list with infinite scroll
4. **Chapter Detail Sidebar** - Drawer sidebar with infinite scroll

## Technical Implementation Details

### useInfiniteScroll Hook Design

```typescript
interface UseInfiniteScrollOptions<T> {
  initialData: Page<T>;                      // SSR-loaded first page
  loadMore: () => Promise<Page<T>>;        // Function to fetch next page
  rootMargin?: string;                      // Intersection Observer threshold
  threshold?: number;                       // Observer sensitivity
}

interface UseInfiniteScrollReturn<T> {
  items: T[];                               // Accumulated items across pages
  loading: boolean;                         // Loading state
  error: string | null;                     // Error message if any
  hasMore: boolean;                         // More pages available
  sentinelRef: React.RefObject<HTMLDivElement>; // Ref for scroll detection
  retry: () => void;                        // Retry function for failed loads
}
```

### State Management Flow
1. **Initialization**: Hook receives `initialData` from SSR loader
2. **Accumulation**: Client-side state accumulates items from each page
3. **Detection**: Intersection Observer watches sentinel element
4. **Loading**: When sentinel comes into view, `loadMore` is called
5. **Update**: New items are appended to existing list
6. **Completion**: When `next` is null, `hasMore` becomes false

### Data Flow Diagram
```
[SSR Loader] → initialData → [useInfiniteScroll] → items
                                      ↓
                                 [Intersection Observer]
                                      ↓
                                [loadMore] → API
                                      ↓
                                [New Page] → Append
```

## Detailed Implementation Strategy

### 1. Client-Side Pagination Architecture

#### SSR-First Approach
- Server loads first page during SSR with URL parameters
- Client receives full `Page<Chapter>` as starting point
- No JavaScript required for initial render
- Progressive enhancement adds infinite scroll

#### Pagination URL Pattern
- Initial page: `/courses/{courseId}/chapters?page=1&page_size=10`
- Next page: `/courses/{courseId}/chapters?page=2&page_size=10`
- Client uses `useFetcherAction.loader()` to fetch subsequent pages

### 2. Intersection Observer Configuration

```typescript
// Using existing LazyRender pattern
const observer = new IntersectionObserver(
  (entries) => {
    const [entry] = entries;
    if (entry.isIntersecting && !loading && hasMore) {
      loadMore();
    }
  },
  {
    rootMargin: '100px',  // Start loading 100px before bottom
    threshold: 0.1,       // Trigger when 10% of sentinel is visible
  }
);
```

### 3. Error Handling Strategy

#### Retry Mechanism
- Failed requests store error message
- Retry button appears with error state
- Clicking retry re-calls `loadMore`
- Duplicate request prevention with loading flag

#### Network Error Recovery
- Graceful degradation with "Load More" fallback
- Network timeout handling (30s timeout)
- Automatic retry with exponential backoff (future enhancement)

### 4. Performance Optimizations

#### Request Deduplication
- `loading` flag prevents duplicate requests
- Request cancellation on component unmount
- `useFetcherAction` provides built-in loading states
- Page tracking prevents duplicate page loading

#### Scroll Throttling
- Intersection Observer is more efficient than scroll events
- No manual throttling needed
- Callback batching during rapid scrolling

#### Memory Management
- Items are appended but not modified
- No need for complex memoization
- Clean up observers on unmount

### 5. Client-Side Fetching with useFetcherAction

#### Hook Implementation
```typescript
// Initial page from SSR
const [currentPage, setCurrentPage] = useState(1);
const [pageSize] = useState(10); // Can be made configurable

// Build action URL with pagination params
const actionUrl = `/courses/${courseId}/chapters?page=${currentPage}&page_size=${pageSize}`;

const infiniteScroll = useFetcherAction<Page<Chapter>, string>({
  action: actionUrl,
  method: 'GET',
  onSuccess: (newPage) => {
    // Append new items to accumulated list
    setItems(prev => [...prev, ...newPage.results]);
    setLoading(false);

    // Update page counter for next request
    if (newPage.next) {
      const nextPage = extractPageFromUrl(newPage.next);
      setCurrentPage(nextPage);
    }
  },
  onError: (error) => {
    setError(error);
    setLoading(false);
  },
});

// Load more function - triggered by Intersection Observer
const loadMore = useCallback(() => {
  if (loading || !hasMore) return;

  infiniteScroll.loader(); // No payload needed for GET requests
}, [loading, hasMore, infiniteScroll]);

// Determine if more pages exist
const hasMore = currentPageData?.next !== null;
```

### 6. UI Component Design

#### Loading State
```tsx
<Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
  <CircularProgress size={24} />
</Box>
```

#### Error State
```tsx
<Box sx={{ textAlign: 'center', my: 2 }}>
  <Typography color="error" sx={{ mb: 1 }}>
    加载失败
  </Typography>
  <Button variant="outlined" onClick={() => loadMore()}>
    重试
  </Button>
</Box>
```

#### End of List
```tsx
<Typography color="text.secondary" sx={{ textAlign: 'center', my: 2 }}>
  已加载全部 {items.length} 条
</Typography>
```

## Implementation Considerations

### 1. SSR Compatibility
- Initial render works without JavaScript
- Hydration matches SSR rendered content
- Progressive enhancement doesn't break layout

### 2. Mobile Responsiveness
- Same logic for mobile and desktop
- Drawer scroll height constraints considered
- Touch scrolling performance optimized

### 3. Accessibility
- Semantic HTML with proper roles
- Keyboard navigation for load more button
- Screen reader announcements for loading states

### 4. Edge Cases Handled
- Empty initial data
- Single page of results
- Rapid scrolling scenarios
- Network interruptions
- Component unmount during fetch

### 5. Future Extensibility
- Configurable page size via URL params
- Virtual scrolling for 1000+ items
- Scroll position restoration
- Prefetching for better UX

## Integration Points

### 1. Existing Components
- Uses `Page<T>` type from `~/types/page`
- Leverages `useFetcher` from React Router
- Consistent with `LazyRender` component pattern
- MUI theming system for styling

### 2. API Layer
- No changes to backend API required
- Uses existing paginated endpoints
- `next` field determines if more pages exist
- Standard error handling from HTTP client

### 3. Route Integration
- Main chapter list route enhancement
- Chapter detail sidebar enhancement
- Maintains existing URL structure
- Preserves current navigation behavior

## Testing Strategy

### Unit Testing
- Hook functionality in isolation
- Intersection Observer behavior mocking
- State transition testing
- Error scenarios coverage
- `useFetcherAction` integration testing

### Integration Testing
- SSR + hydration flow
- Component interaction testing
- Error boundary scenarios
- Performance testing with large lists

### Manual Testing
- Cross-browser compatibility
- Mobile touch scrolling
- Network error simulation
- Rapid scroll scenarios
- Accessibility validation

## Performance Metrics

### Target Benchmarks
- Initial render: < 100ms
- Page load: < 500ms
- Scroll response: < 50ms
- Memory usage: Linear with page count

### Optimization Areas
- Large list virtualization (future)
- Image lazy loading (future)
- Prefetching (future)
- Debouncing rapid scrolls (if needed)
