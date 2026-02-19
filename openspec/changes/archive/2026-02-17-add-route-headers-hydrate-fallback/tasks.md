# Tasks: Add Route Headers and Hydrate Fallback

## Phase 1: Infrastructure

- [x] Create `~/components/HydrateFallback/SkeletonHome.tsx`
  - Use MUI `Skeleton` components matching home page layout
  - Include course cards skeleton, unfinished problems skeleton
  - Match spacing and sizing from actual page

- [x] Create `~/components/HydrateFallback/SkeletonHome.tsx`
  - Use MUI `Skeleton` components matching home page layout
  - Include course cards skeleton, unfinished problems skeleton
  - Match spacing and sizing from actual page

- [x] Create `~/components/HydrateFallback/SkeletonProblems.tsx`
  - Create skeleton list items for problems table
  - Match filter section skeleton
  - Include pagination skeleton

- [x] Create `~/components/HydrateFallback/SkeletonProfile.tsx`
  - Create user profile header skeleton
  - Create progress cards skeleton
  - Match actual profile page structure

- [x] Create `~/components/HydrateFallback/index.ts`
  - Barrel export all skeleton components
  - Re-export from `~/components/HydrateFallback`

## Phase 2: Implement Headers

- [x] Add `headers()` to `_layout.membership.tsx`
  - Export `headers()` function with 1-hour public cache
  - Test cache headers in browser DevTools
  - Verify no authentication data is leaked in cached response

- [x] Add `headers()` to `_layout.problems.tsx`
  - Export `headers()` function with 5-minute public cache
  - Add `Vary: Accept-Encoding` header
  - Test cache behavior with different query parameters

- [x] Add `headers()` to `_layout.home.tsx`
  - Export `headers()` function with 2-minute private cache
  - Ensure `private` directive is set for user-specific content
  - Test cache doesn't leak between users

- [x] Add `headers()` to `_layout.profile.tsx`
  - Export `headers()` function with 2-minute private cache
  - Verify cache respects authentication state

## Phase 3: Implement HydrateFallback

- [x] Add `clientLoader` and `HydrateFallback` to `_layout.home.tsx`
  - Implement `clientLoader` with `hydrate = true`
  - Export `HydrateFallback` using `SkeletonHome`
  - Test skeleton appears on first load
  - Verify data loads correctly after hydration

- [x] Add `clientLoader` and `HydrateFallback` to `_layout.problems.tsx`
  - Implement `clientLoader` with `hydrate = true`
  - Export `HydrateFallback` using `SkeletonProblems`
  - Test with different filter states
  - Verify pagination state preserved

- [x] Add `clientLoader` and `HydrateFallback` to `_layout.profile.tsx`
  - Implement `clientLoader` with `hydrate = true`
  - Export `HydrateFallback` using `SkeletonProfile`
  - Test skeleton matches actual layout

## Phase 4: Testing and Documentation

- [x] Create cache header verification tests
  - Test membership page returns correct headers
  - Test problems page returns correct headers
  - Test home page returns private cache directive

- [x] Manual testing checklist
  - [x] Verify cache headers in Chrome DevTools Network tab
  - [x] Test that cached pages show "from disk cache" on reload
  - [x] Verify skeleton appears on first page load (Ctrl+Shift+R)
  - [x] Test that authenticated content uses `private` cache
  - [x] Run Lighthouse audit and verify performance improvement

- [x] Update documentation
  - Document cache strategy in CLAUDE.md
  - Add comments to cache configuration explaining durations
  - Update API documentation if needed

- [x] Run `openspec validate add-route-headers-hydrate-fallback --strict --no-interactive`
  - Fix any validation errors

## Dependencies

- No external dependencies required (React Router v7 and MUI already in use)

## Rollback Plan

If issues arise:
1. Remove `headers()` exports - routes will work without caching
2. Remove `HydrateFallback` exports - routes will show blank during hydration
3. Delete skeleton components - no impact on other functionality
