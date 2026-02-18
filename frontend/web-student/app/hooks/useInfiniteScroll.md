# useInfiniteScroll Hook

A custom React hook that implements infinite scroll functionality using Intersection Observer API.

## Features

- Automatic loading of more items when scrolling near the bottom
- Built-in loading states and error handling
- Support for extracting data from complex loader responses
- Configurable scroll detection thresholds
- Prevention of duplicate requests
- TypeScript support

## Usage

### Basic Usage (Direct Page Data)

```tsx
const infiniteScroll = useInfiniteScroll({
  initialData: loaderData.chapters,
  getNextPageUrl: (page, pageSize) =>
    `/courses/${courseId}/chapters?page=${page}&page_size=${pageSize}`,
});
```

### Advanced Usage (With Data Extraction)

When your loader returns complex data (e.g., `{ chapters, course }`), use the `extractData` function:

```tsx
const infiniteScroll = useInfiniteScroll({
  initialData: loaderData,
  extractData: (data) => data.chapters,
  getNextPageUrl: (page, pageSize) =>
    `/courses/${courseId}/chapters?page=${page}&page_size=${pageSize}`,
});
```

## API Reference

### Options

```typescript
interface UseInfiniteScrollOptions<T> {
  /** Initial page data from SSR loader or loader data */
  initialData: Page<T> | { [key: string]: any };
  /** Function to extract Page data from loader data */
  extractData?: (data: any) => Page<T>;
  /** Function to build the URL for fetching the next page */
  getNextPageUrl: (currentPage: number, pageSize: number) => string;
  /** Root margin for Intersection Observer (default: '100px') */
  rootMargin?: string;
  /** Threshold for Intersection Observer (default: 0.1) */
  threshold?: number;
  /** Timeout in milliseconds (default: 30000) */
  timeout?: number;
}
```

### Return Value

```typescript
interface UseInfiniteScrollReturn<T> {
  /** Accumulated items across all loaded pages */
  items: T[];
  /** Current loading state */
  loading: boolean;
  /** Error message if any */
  error: string | null;
  /** Whether more pages are available */
  hasMore: boolean;
  /** Ref for the sentinel element for scroll detection */
  sentinelRef: React.RefObject<HTMLDivElement | null>;
  /** Function to retry loading the last failed page */
  retry: () => void;
  /** Current page number */
  currentPage: number;
  /** Page size being used */
  pageSize: number;
}
```

## Example Implementation

```tsx
function ChapterListPage({ loaderData, params }: Route.ComponentProps) {
  const infiniteScroll = useInfiniteScroll({
    initialData: loaderData,
    extractData: (data) => data.chapters,
    getNextPageUrl: (page, pageSize) =>
      `/courses/${params.courseId}/chapters?page=${page}&page_size=${pageSize}`,
  });

  return (
    <List>
      {infiniteScroll.items.map((chapter) => (
        <ListItem key={chapter.id}>
          <ListItemText primary={chapter.title} />
        </ListItem>
      ))}

      {/* Sentinel for scroll detection */}
      <Box ref={infiniteScroll.sentinelRef} />

      {/* Loading state */}
      {infiniteScroll.loading && <CircularProgress />}

      {/* Error state */}
      {infiniteScroll.error && (
        <Box>
          <Typography color="error">{infiniteScroll.error}</Typography>
          <Button onClick={infiniteScroll.retry}>重试</Button>
        </Box>
      )}

      {/* End of list */}
      {!infiniteScroll.hasMore && (
        <Typography>已加载全部章节</Typography>
      )}
    </List>
  );
}
```

## Notes

- The hook uses React Router's `useFetcher` for client-side data fetching
- Intersection Observer is used for performant scroll detection
- The `extractData` function allows flexibility with different loader response structures
- Loading state prevents duplicate requests
- Error handling includes retry functionality