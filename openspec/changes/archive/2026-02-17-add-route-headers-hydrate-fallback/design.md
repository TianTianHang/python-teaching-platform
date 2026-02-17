# Design: Route Headers and Hydrate Fallback Implementation

## Architecture Overview

This change adds React Router v7's `headers()` and `HydrateFallback` exports to improve performance and user experience through HTTP caching and loading states.

## Component Architecture

### 1. HydrateFallback Components

```
frontend/web-student/app/components/HydrateFallback/
├── index.ts                    # Barrel exports
├── SkeletonHome.tsx           # Home dashboard loading skeleton
├── SkeletonProblems.tsx       # Problems list loading skeleton
├── SkeletonProfile.tsx        # Profile page loading skeleton
└── SkeletonExamResults.tsx    # Exam results loading skeleton
```

Each skeleton component:
- Uses MUI `Skeleton` variants matching the actual page layout
- Matches the visual structure of the corresponding page
- Uses consistent spacing and sizing tokens

### 2. Headers Implementation

The `headers()` function is added directly to route modules:

```tsx
export function headers({ loaderHeaders }: Route.HeadersArgs) {
  return {
    "Cache-Control": getCacheControl(routeType),
  };
}

function getCacheControl(routeType: RouteType): string {
  switch (routeType) {
    case "public-static": return "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400";
    case "public-dynamic": return "public, max-age=300, s-maxage=600, stale-while-revalidate=3600";
    case "private-user": return "private, max-age=120, must-revalidate";
    default: return "no-cache, no-store, must-revalidate";
  }
}
```

### 3. Header Function Pattern

## Route Modifications

### Modified Routes

| Route | Headers Added | HydrateFallback Added | Cache Duration |
|-------|---------------|----------------------|----------------|
| `_layout.membership.tsx` | Yes | No | 1 hour public |
| `_layout.problems.tsx` | Yes | Yes | 5 min public |
| `_layout.home.tsx` | Yes | Yes | 2 min private |
| `_layout.profile.tsx` | Yes | Yes | 2 min private |
| `_layout.courses.$courseId.exams.tsx` | No | Yes | No cache |
| `_layout.courses.$courseId.exams.$examId.tsx` | No | Yes | No cache |

### Header Function Pattern

Each route's `headers()` function will:

1. Check if the route should be cached
2. Return appropriate `Cache-Control` header
3. Optionally set `Vary` header for cache variations (e.g., `Vary: Cookie`)

```tsx
export function headers(): Route.HeadersFunction {
  return {
    "Cache-Control": "public, max-age=300, s-maxage=600",
    "Vary": "Accept-Encoding",
  };
}
```

### HydrateFallback Pattern

Routes with slow loaders will implement:

1. `clientLoader` with `hydrate = true`
2. `HydrateFallback` component export
3. Skeleton UI matching page structure

```tsx
export async function clientLoader({ serverLoader }: Route.ClientLoaderArgs) {
  return await serverLoader();
}
clientLoader.hydrate = true as const;

export function HydrateFallback() {
  return <SkeletonHome />;
}

export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  // Existing loader logic
});
```

## Integration Points

### 1. Root Layout

The root layout (`_layout.tsx`) should NOT add caching headers since:
- Authentication status is managed via cookies
- User-specific navigation requires fresh data
- The layout wraps all child routes

### 2. Existing `data()` Usage

Some routes already use `data()` with headers for session management. The `headers()` export will:
- Coexist with `data()` headers
- Be merged by React Router (route headers take precedence for response headers)
- Not interfere with `Set-Cookie` headers

## Testing Strategy

### 1. Cache Header Verification

```typescript
// Test: Verify cache headers are set correctly
test("membership page sets public cache headers", async () => {
  const response = await request("/", {
    headers: { cookie: "" }
  });
  expect(response.headers.get("Cache-Control")).toContain("public");
  expect(response.headers.get("Cache-Control")).toContain("max-age=3600");
});
```

### 2. HydrateFallback Rendering

```typescript
// Test: HydrateFallback renders during hydration
test("home page shows skeleton during hydration", async () => {
  const html = await getHomeHtml();
  expect(html).toContain("SkeletonHome");
});
```

### 3. Manual Testing Checklist

- [ ] Verify Cache-Control headers in browser DevTools
- [ ] Confirm stale content is served during revalidation
- [ ] Test that skeleton appears on first page load
- [ ] Verify authenticated pages use `private` cache directive
- [ ] Test cache invalidation after mutations (actions)

## Performance Impact

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LCP (Membership) | ~2.5s | ~1.2s | ~52% |
| Server Requests (High Traffic) | 100% | ~30% | ~70% reduction |
| Time to First Byte (Cached) | ~800ms | ~50ms (CDN) | ~94% |

### Trade-offs

1. **Staleness vs Performance**: Short cache durations (2-5 min) balance freshness with performance
2. **Bundle Size**: Each skeleton adds ~1-2KB gzipped to the bundle
3. **Memory**: Browser cache uses more memory (acceptable trade-off)

## Migration Path

### Phase 1: Core Infrastructure
1. Create `~/config/cache.ts` with cache configurations
2. Create `~/components/HydrateFallback/` skeleton components
3. Update spec documentation

### Phase 2: Route Implementation
1. Add `headers()` to membership page (simplest case)
2. Add `HydrateFallback` to home page
3. Add both to problems page

### Phase 3: Verification
1. Browser DevTools verification
2. Lighthouse performance testing
3. Load testing for cache effectiveness
