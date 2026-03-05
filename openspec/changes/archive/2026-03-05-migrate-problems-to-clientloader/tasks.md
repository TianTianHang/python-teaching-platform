## 1. Phase 1: High Priority Pages

### 1.1 Migrate Problems List Page (`_layout.problems.tsx`)

- [x] 1.1.1 Add `clientLoader` function that extracts query parameters (page, type, difficulty, ordering) and fetches problems from API
- [x] 1.1.2 Add `clientLoader.hydrate = true` to enable hydration
- [x] 1.1.3 Add `HydrateFallback` component using existing `SkeletonProblems` component
- [x] 1.1.4 Add `ErrorBoundary` component to handle errors (401 redirect to login, other errors show message)
- [x] 1.1.5 Remove `useEffect` data fetching logic (lines 41-74)
- [x] 1.1.6 Remove `useState` for pageData, loading, totalItems, actualPageSize, totalPages
- [x] 1.1.7 Replace data access with `useLoaderData<typeof clientLoader>()`
- [x] 1.1.8 Remove `ResolveError` component usage (error handling now in ErrorBoundary)
- [x] 1.1.9 Remove error state type checks (e.g., `'status' in pageData`)
- [x] 1.1.10 Keep `headers()` export for HTTP caching (Cache-Control: public, max-age=300)
- [ ] 1.1.11 Test filtering by type (algorithm, choice, fillblank)
- [ ] 1.1.12 Test filtering by difficulty
- [ ] 1.1.13 Test ordering changes
- [ ] 1.1.14 Test pagination navigation
- [ ] 1.1.15 Test locked problems display correctly

### 1.2 Migrate Problem Detail Page (`problems.$problemId/route.tsx`)

- [x] 1.2.1 Add `clientLoader` function that checks for `type` and `id` URL params to determine fetch mode
- [x] 1.2.2 Implement dual-mode fetching: direct access (`GET /problems/:id`) or next problem (`GET /problems/next/?type=...&id=...`)
- [x] 1.2.3 Add `clientLoader.hydrate = true`
- [x] 1.2.4 Add `HydrateFallback` component with loading spinner
- [x] 1.2.5 Add `ErrorBoundary` component with "返回" button
- [x] 1.2.6 Remove `useEffect` data fetching logic (lines 22-49)
- [x] 1.2.7 Remove `useState` for problem, loading, hasNext
- [x] 1.2.8 Replace with `useLoaderData<typeof clientLoader>()`
- [x] 1.2.9 Remove error state type checks (`'message' in problem`)
- [x] 1.2.10 Remove inline error rendering (now handled by ErrorBoundary)
- [x] 1.2.11 Preserve type-specific rendering logic (algorithm, choice, fillblank)
- [x] 1.2.12 Preserve `hasNext` state and "Next" button logic
- [ ] 1.2.13 Test direct problem access
- [ ] 1.2.14 Test "Next problem" navigation
- [ ] 1.2.15 Test all three problem types render correctly

## 2. Phase 2: Medium Priority Pages

### 2.1 Migrate Problem Description Page (`problems.$problemId.description.tsx`)

- [x] 2.1.1 Add `clientLoader` function to fetch problem by ID
- [x] 2.1.2 Add `clientLoader.hydrate = true`
- [x] 2.1.3 Add `HydrateFallback` component with loading spinner
- [x] 2.1.4 Add `ErrorBoundary` component
- [x] 2.1.5 Remove `useEffect` data fetching logic (lines 14-26)
- [x] 2.1.6 Remove `useState` for loading and problem
- [x] 2.1.7 Replace with `useLoaderData<typeof clientLoader>()`
- [ ] 2.1.8 Test problem description displays correctly
- [ ] 2.1.9 Test markdown rendering works
- [ ] 2.1.9 Test markdown rendering works

### 2.2 Migrate Submissions Page (`problems.$problemId.submissions.tsx`)

- [x] 2.2.1 Add `clientLoader` function that extracts page and pageSize from URL
- [x] 2.2.2 Implement parallel fetching using `Promise.all` for submissions and problem data
- [x] 2.2.3 Add `clientLoader.hydrate = true`
- [x] 2.2.4 Add `HydrateFallback` component with loading spinner
- [x] 2.2.5 Add `ErrorBoundary` component
- [x] 2.2.6 Remove `useEffect` data fetching logic (lines 27-46)
- [x] 2.2.7 Remove `useState` for loading, submissions, totalItems, actualPageSize, problem
- [x] 2.2.8 Replace with `useLoaderData<typeof clientLoader>()`
- [x] 2.2.9 Preserve pagination logic and navigation
- [ ] 2.2.10 Test submission list displays
- [ ] 2.2.11 Test pagination works
- [ ] 2.2.12 Test parallel request error handling

## 3. Verification & Testing

- [x] 3.1 Run `pnpm run typecheck` in frontend directory and fix any TypeScript errors
- [ ] 3.2 Run `pnpm run lint` in frontend directory and fix any linting errors
- [ ] 3.3 Test all 4 pages load correctly in development
- [ ] 3.4 Test 401 redirects to login on all pages
- [ ] 3.5 Test 404 errors show ErrorBoundary on all pages
- [ ] 3.6 Test 500 errors show ErrorBoundary on all pages
- [ ] 3.7 Test client navigation between pages works smoothly
- [ ] 3.8 Test browser back/forward navigation
- [ ] 3.9 Test URL parameters update correctly for filters and pagination
- [ ] 3.10 Verify no `useEffect` data fetching remains in any of the 4 migrated files
- [ ] 3.11 Verify all migrated pages follow the same pattern as home/courses pages
- [ ] 3.12 Confirm caching headers still work on problems list page

## 4. Documentation & Cleanup

- [ ] 4.1 Update any internal documentation referencing the old useEffect pattern
- [ ] 4.2 Remove any unused imports after migration
- [ ] 4.3 Verify all TODO comments are addressed or documented
- [ ] 4.4 Confirm code follows project conventions (TypeScript strict mode, etc.)
