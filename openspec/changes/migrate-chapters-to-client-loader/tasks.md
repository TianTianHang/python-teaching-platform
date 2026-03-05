## 1. Preparation

- [ ] 1.1 Review existing clientLoader implementations (home.tsx, problems.tsx, courses.tsx)
- [ ] 1.2 Check current implementation of locked page (`_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx`)
- [ ] 1.3 Verify `clientHttp` token management implementation in `~/utils/http/client.ts`
- [ ] 1.4 Create `SkeletonChapterList` component in `~/components/skeleton/`
- [ ] 1.5 Create `SkeletonChapterDetail` component in `~/components/skeleton/`
- [ ] 1.6 Create `SidebarSkeleton` component if not exists (for chapter detail sidebar)

## 2. Migrate Chapter List Page

- [ ] 2.1 Remove `withAuth` wrapper from `export const loader` in `_layout.courses_.$courseId_.chapters/route.tsx`
- [ ] 2.2 Replace `loader` with `clientLoader` and add `hydrate = true`
- [ ] 2.3 Replace `createHttp(request)` with `clientHttp` for all API calls
- [ ] 2.4 Add 401 error handling with `redirect('/auth/login')` in clientLoader
- [ ] 2.5 Add `HydrateFallback` component using `SkeletonChapterList`
- [ ] 2.6 Add `ErrorBoundary` component with retry functionality
- [ ] 2.7 Update component to use `useLoaderData<typeof clientLoader>()`
- [ ] 2.8 Verify `useInfiniteScroll` hook still works with clientLoader data
- [ ] 2.9 Test chapter list page loading and navigation

## 3. Migrate Chapter Detail Page

- [ ] 3.1 Remove `withAuth` wrapper from `export const loader` in `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
- [ ] 3.2 Replace `loader` with `clientLoader` and add `hydrate = true`
- [ ] 3.3 Replace `createHttp(request)` with `clientHttp` for all API calls
- [ ] 3.4 Modify `unlock_status` check to return `{ isLocked: boolean }` instead of server-side redirect
- [ ] 3.5 Handle 403/404 errors from `unlock_status` API by returning `isLocked: true`
- [ ] 3.6 Add 401 error handling with `redirect('/auth/login')` in clientLoader
- [ ] 3.7 Keep side-effect logic (mark chapter as in-progress) as fire-and-forget
- [ ] 3.8 Add `HydrateFallback` component using `SkeletonChapterDetail`
- [ ] 3.9 Add `ErrorBoundary` component with retry functionality
- [ ] 3.10 Update component to use `useLoaderData<typeof clientLoader>()`
- [ ] 3.11 Add client-side redirect logic using `useNavigate()` when `isLocked === true`
- [ ] 3.12 Add early return to prevent rendering content when `isLocked === true`
- [ ] 3.13 Verify `clientAction` for marking completion still works
- [ ] 3.14 Test unlocked chapter access and rendering
- [ ] 3.15 Test locked chapter redirect to locked page

## 4. Migrate Locked Page (if applicable)

- [ ] 4.1 Check if locked page uses server-side loader
- [ ] 4.2 If yes, replace `loader` with `clientLoader` and add `hydrate = true`
- [ ] 4.3 Replace `createHttp(request)` with `clientHttp` for API calls
- [ ] 4.4 Add 401 error handling with `redirect('/auth/login')`
- [ ] 4.5 Add `HydrateFallback` component
- [ ] 4.6 Add `ErrorBoundary` component
- [ ] 4.7 Test locked page rendering

## 5. Testing and Validation

- [ ] 5.1 Manual test: Chapter list page loads correctly with valid authentication
- [ ] 5.2 Manual test: Chapter list page redirects to login on 401 error
- [ ] 5.3 Manual test: Infinite scroll works on chapter list page
- [ ] 5.4 Manual test: Unlocked chapter page renders correctly
- [ ] 5.5 Manual test: Locked chapter redirects to locked page (no content flash)
- [ ] 5.6 Manual test: Locked page displays correctly
- [ ] 5.7 Manual test: Client-side navigation between chapters is fast
- [ ] 5.8 Manual test: Error scenarios (403, 404, 500) display appropriate error messages
- [ ] 5.9 Manual test: Retry button in ErrorBoundary works correctly
- [ ] 5.10 Verify performance: Client-side navigation is faster than before
- [ ] 5.11 Check browser console for any errors or warnings
- [ ] 5.12 Update any related tests to work with clientLoader

## 6. Code Cleanup and Documentation

- [ ] 6.1 Remove commented-out server-side loader code
- [ ] 6.2 Update JSDoc comments if needed
- [ ] 6.3 Verify TypeScript types are correct
- [ ] 6.4 Run `pnpm run typecheck` to ensure no type errors
- [ ] 6.5 Run linting and fix any issues
- [ ] 6.6 Update any relevant documentation or comments

## 7. Deployment

- [ ] 7.1 Merge changes to main branch
- [ ] 7.2 Deploy to staging environment
- [ ] 7.3 Smoke test on staging environment
- [ ] 7.4 Monitor performance metrics on staging
- [ ] 7.5 Deploy to production environment
- [ ] 7.6 Monitor production metrics and error rates
- [ ] 7.7 Verify user feedback and behavior analytics
