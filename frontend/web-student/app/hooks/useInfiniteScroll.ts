import { useState, useCallback, useRef, useEffect } from "react";
import { useFetcher } from "react-router";
import type { Page } from "~/types/page";

/**
 * Options for the useInfiniteScroll hook
 */
export interface UseInfiniteScrollOptions<T> {
  /** Initial page data from SSR loader or loader data */
  initialData: Page<T>;
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

/**
 * Return type for the useInfiniteScroll hook
 */
export interface UseInfiniteScrollReturn<T> {
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

/**
 * A custom hook that implements infinite scroll functionality using Intersection Observer.
 *
 * @template T - The type of items in the paginated list
 *
 * @example
 * ```tsx
 * // For direct Page data
 * const infiniteScroll = useInfiniteScroll({
 *   initialData: loaderData.chapters,
 *   getNextPageUrl: (page, pageSize) =>
 *     `/courses/${courseId}/chapters?page=${page}&page_size=${pageSize}`,
 * });
 *
 * // For loader data that needs extraction
 * const infiniteScroll = useInfiniteScroll({
 *   initialData: loaderData,
 *   extractData: (data) => data.chapters,
 *   getNextPageUrl: (page, pageSize) =>
 *     `/courses/${courseId}/chapters?page=${page}&page_size=${pageSize}`,
 * });
 *
 * return (
 *   <div>
 *     {infiniteScroll.items.map(item => <Item key={item.id} {...item} />)}
 *     <div ref={infiniteScroll.sentinelRef} />
 *     {infiniteScroll.loading && <Spinner />}
 *     {infiniteScroll.error && <Button onClick={infiniteScroll.retry}>Retry</Button>}
 *     {!infiniteScroll.hasMore && <div>All items loaded</div>}
 *   </div>
 * );
 * ```
 */
export function useInfiniteScroll<T>({
  initialData,
  extractData,
  getNextPageUrl,
  rootMargin = "100px",
  threshold = 0.1,
  timeout = 30000,
}: UseInfiniteScrollOptions<T>): UseInfiniteScrollReturn<T> {
  // Extract Page data from initial data
  const pageData = initialData;
  const initialPageSize = pageData?.page_size || 10;

  // State for accumulated items and pagination
  const [items, setItems] = useState<T[]>(pageData.results);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [hasMore, setHasMore] = useState(pageData.next !== null);
  const [error, setError] = useState<string | null>(null);

  // Ref for the sentinel element
  const sentinelRef = useRef<HTMLDivElement>(null);

  // Ref to track processed data and prevent duplicate processing
  const processedDataRef = useRef<string | null>(null);

  // Use raw fetcher for dynamic URL handling
  const fetcher = useFetcher<Page<T>>();

  // Load more function - builds URL dynamically
  const loadMore = useCallback(() => {
    if (fetcher.state !== "idle" || !hasMore) return;

    const nextPage = currentPage + 1;
    const url = getNextPageUrl(nextPage, pageSize);

    // Load the data using the fetcher
    fetcher.load(url);
  }, [fetcher.state, hasMore, currentPage, pageSize, getNextPageUrl]);

  // Handle fetcher completion
  useEffect(() => {
    if (fetcher.state === "idle" && fetcher.data) {
      // Create a unique identifier for the current data
      const dataKey = JSON.stringify(fetcher.data);

      // Only process if this is new data (prevents duplicate processing)
      if (processedDataRef.current !== dataKey) {
        processedDataRef.current = dataKey;

        // Data loaded successfully
        const newData = extractData ? extractData(fetcher.data) : fetcher.data;
        setItems((prev) => [...prev, ...newData.results]);
        setCurrentPage((prev) => prev + 1);
        setHasMore(newData.next !== null);
        setError(null);
      }
    }
  }, [fetcher.state, fetcher.data, extractData]);

  // Handle fetcher error
  useEffect(() => {
    if (fetcher.state === "idle" && fetcher.data === undefined) {
      // Check if this is an error state
      // Note: This is a simple error detection. You might need more sophisticated error handling
    }
  }, [fetcher.state]);

  // Retry function
  const retry = useCallback(() => {
    setError(null);
    loadMore();
  }, [loadMore]);

  // Intersection Observer setup
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && fetcher.state !== "submitting" && hasMore && !error) {
          loadMore();
        }
      },
      {
        rootMargin,
        threshold,
      }
    );

    observer.observe(sentinel);

    return () => {
      observer.disconnect();
    };
  }, [fetcher.state, hasMore, error, loadMore, rootMargin, threshold]);

  return {
    items,
    loading: fetcher.state !== "idle",
    error,
    hasMore,
    sentinelRef,
    retry,
    currentPage,
    pageSize,
  };
}

export default useInfiniteScroll;