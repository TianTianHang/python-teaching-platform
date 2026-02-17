# Proposal: Add Route Headers and Hydrate Fallback for Improved Browsing Experience

## Summary

Add React Router v7 `headers` and `HydrateFallback` exports to frequently accessed routes to improve browsing experience through HTTP caching and better first-screen loading states.

## Motivation

Currently, the application does not leverage React Router's route-level caching headers or hydration fallback UI. This leads to:
1. **No browser/CDN caching** for static-looking pages - every SSR request regenerates HTML
2. **Poor first-screen UX** - users see blank or broken layouts while client loaders complete
3. **Unnecessary server load** - frequently accessed pages like home, problems list, and membership are regenerated on every visit

By implementing `headers` for cache control and `HydrateFallback` for loading states, we can:
- Reduce server load through browser and CDN caching
- Improve perceived performance with skeleton UI during hydration
- Provide smoother user experience on first visit and navigation

## Goals

1. Add `headers()` function to frequently accessed routes for HTTP caching
2. Add `HydrateFallback` components to routes with slow-loading data
3. Create reusable fallback components for consistent loading UI
4. Document caching strategy for different page types

## Non-Goals

1. Implementing full service worker/PWA caching (out of scope)
2. Changing backend caching behavior (already handled via DRF cache mixins)
3. Modifying the root layout headers (authentication requires no-cache)

## Scope

### Affected Routes

The following routes will be modified:

1. **Public/Frequently Accessed Routes** (add `headers` for caching):
   - `/_layout.membership.tsx` - Membership page (static content)
   - `/problems` (via `/_layout.problems.tsx`) - Problems list (short cache)
   - `/home` (via `/_layout.home.tsx`) - Home dashboard (short cache)

2. **Routes with Slow Loaders** (add `HydrateFallback`):
   - `/_layout.home.tsx` - Multiple parallel API calls
   - `/_layout.problems.tsx` - Paginated problems list
   - `/_layout.profile.tsx` - User profile data
   - `/_layout.courses.$courseId.exams.tsx` - Exams list with progress data

### New Components

1. `~/components/HydrateFallback/SkeletonHome.tsx` - Home page loading skeleton
2. `~/components/HydrateFallback/SkeletonProblems.tsx` - Problems list loading skeleton
3. `~/components/HydrateFallback/SkeletonProfile.tsx` - Profile page loading skeleton

## Implementation Approach

### 1. Cache Strategy for Different Page Types

| Page Type | Cache Strategy | Duration | Rationale |
|-----------|---------------|----------|-----------|
| Membership | Public cache | 1 hour | Static pricing content |
| Problems List | Short cache | 5 minutes | High traffic, quick staleness tolerance |
| Home Dashboard | Private cache | 2 minutes | User-specific, but acceptable staleness |
| Exam Results | No cache | 0 min | Always fresh data required |

### 2. Headers Implementation Pattern

```tsx
export function headers({ loaderHeaders }: Route.HeadersArgs) {
  return {
    "Cache-Control": "public, max-age=300, s-maxage=600",
  };
}
```

### 3. HydrateFallback Implementation Pattern

```tsx
export function HydrateFallback() {
  return <SkeletonHome />;
}

export async function clientLoader({ serverLoader }: Route.ClientLoaderArgs) {
  clientLoader.hydrate = true as const;
  return await serverLoader();
}
```

## Alternatives Considered

1. **Using `shouldRevalidate` for all routes** - More complex, not needed for simple caching
2. **Implementing service worker caching** - Overkill, adds significant complexity
3. **Using CDN-only caching** - Doesn't help browser cache hit rate

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Stale data shown to users | Use conservative cache durations (2-5 min for dynamic content) |
| Authenticated content cached publicly | Only cache truly public content, use `private` directive for user-specific pages |
| Increased bundle size | Skeleton components are small, code-split by route |
| Cache invalidation complexity | Keep cache durations short enough that manual invalidation isn't needed |

## Dependencies

- React Router v7 (already in use)
- MUI Skeleton components (already in use)

## Success Criteria

1. Lighthouse scores improve (especially Performance and LCP metrics)
2. Reduced server load on frequently accessed routes
3. Visual loading states are present on all slow-loading routes
4. Cache headers are correctly set and verified via browser DevTools
5. No regression in data freshness for user-specific content

## Open Questions

1. **Should problem detail pages be cached?** - Depends on how frequently problems are updated
2. **Should we add `clientLoader` to more routes?** - Could be a follow-up enhancement
3. **What cache duration for exam results?** - Currently proposing no-cache to ensure fresh grades
