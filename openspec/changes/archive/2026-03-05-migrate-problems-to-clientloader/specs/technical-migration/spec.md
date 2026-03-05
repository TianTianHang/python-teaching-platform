# Technical Migration Note: Problem Pages to clientLoader

## Overview

This is a technical migration that moves 4 problem-related pages from `useEffect` data fetching to React Router v7's `clientLoader` pattern.

**Scope**: Pure implementation change. No functional requirements or user-facing behavior changes.

## Background

These pages currently use the `useEffect` pattern for data fetching:

```tsx
// Current pattern
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchData = async () => {
    try {
      const result = await clientHttp.get('/api/endpoint');
      setData(result);
    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [dependencies]);
```

This pattern has several limitations:
- Data fetching happens after component render
- No SSR/Hydration support
- Requires manual loading/error state management
- Inconsistent with already-migrated pages (home, courses)

## Migration Target Pattern

All pages will be migrated to the `clientLoader` pattern:

```tsx
// New pattern
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  try {
    const url = new URL(request.url);
    const param1 = url.searchParams.get('param1');
    const data = await clientHttp.get('/api/endpoint', { param1 });
    return data;
  } catch (error: any) {
    if (error?.response?.status === 401) {
      throw redirect('/auth/login');
    }
    throw new Response('Error', { status: error?.response?.status || 500 });
  }
}

clientLoader.hydrate = true;

export function HydrateFallback() {
  return <SkeletonComponent />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <ErrorUI error={error} />;
}

// In component
const data = useLoaderData<typeof clientLoader>();
```

## Pages Being Migrated

### 1. `_layout.problems.tsx` (Problem List Page)

**Current Implementation**:
- Uses `useEffect` to fetch problems with filters (type, difficulty, ordering) and pagination
- Has manual loading state and error handling with `ResolveError` component
- Exports `headers()` for HTTP caching

**Migration Approach**:
- Extract query parameters from `request.url` in clientLoader
- Move `clientHttp.get('/problems/')` to clientLoader
- Add `HydrateFallback` using existing `SkeletonProblems` component
- Add `ErrorBoundary` to handle errors
- Remove `useEffect`, `useState` for data/loading/error
- Keep `headers()` export for caching (Cache-Control: public, max-age=300)

**Key Considerations**:
- Complex filtering logic must be preserved
- URL parameters must be correctly extracted and passed to API
- Caching headers must remain in place

### 2. `problems.$problemId/route.tsx` (Problem Detail Page)

**Current Implementation**:
- Uses `useEffect` to fetch problem data
- Supports two modes:
  - Direct access: `GET /problems/:id`
  - Next problem navigation: `GET /problems/next/?type=...&id=...`
- Renders different components based on problem type (algorithm, choice, fillblank)

**Migration Approach**:
- Check URL parameters (`type`, `id`) to determine fetch mode
- Move API calls to clientLoader
- Add `HydrateFallback` and `ErrorBoundary`
- Remove `useEffect` data fetching
- Preserve conditional routing logic

**Key Considerations**:
- Must preserve dual-mode fetching logic
- `has_next` state must be correctly passed to components
- Type-specific rendering must remain unchanged

### 3. `problems.$problemId.description.tsx` (Problem Description)

**Current Implementation**:
- Simple `useEffect` fetching single problem by ID
- Basic loading state with spinner

**Migration Approach**:
- Straightforward migration to clientLoader
- Add `HydrateFallback` (can use simple spinner)
- Add `ErrorBoundary`

**Key Considerations**:
- Simplest of the four migrations
- Good starting point to validate pattern

### 4. `problems.$problemId.submissions.tsx` (Submission History)

**Current Implementation**:
- Uses `Promise.all` to parallel fetch:
  - Submission list (paginated)
  - Problem details
- Complex pagination logic

**Migration Approach**:
- Move `Promise.all` logic to clientLoader
- Extract pagination params from URL
- Add `HydrateFallback` and `ErrorBoundary`
- Remove `useEffect` data fetching

**Key Considerations**:
- Parallel request pattern must be preserved
- Error handling for `Promise.all` (one failure = all fail)
- Pagination navigation uses `useSearchParams` - must preserve this

## Error Handling Strategy

### Current Pattern
Each component manages its own error state:
```tsx
const [error, setError] = useState(null);
// In useEffect catch block
setError(error.response?.data || 'Error message');
// In render
{error && <ResolveError status={error.status} message={error.message} />}
```

### New Pattern
Unified error handling via `ErrorBoundary`:

```tsx
// In clientLoader
try {
  const data = await clientHttp.get('/endpoint');
  return data;
} catch (error: any) {
  if (error?.response?.status === 401) {
    throw redirect('/auth/login');
  }
  throw new Response('Error', { status: error?.response?.status || 500 });
}

// ErrorBoundary component
export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return (
    <Box p={4}>
      <Typography variant="h6" color="error">
        加载失败
      </Typography>
      <Button onClick={() => navigate(-1)}>返回</Button>
    </Box>
  );
}
```

**Benefits**:
- Consistent error UX across all pages
- Cleaner component code (no error state management)
- Leverages React Router's built-in error handling

## Data Access Pattern

### Before
```tsx
const [problems, setProblems] = useState(null);
const [loading, setLoading] = useState(true);
// In useEffect
const data = await clientHttp.get('/problems/');
setProblems(data);
// In render
{problems?.map(...)}
```

### After
```tsx
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  const data = await clientHttp.get('/problems/');
  return data;
}

// In component
const problems = useLoaderData<typeof clientLoader>();
// In render
{problems?.map(...)}
```

**Type Safety**: `useLoaderData<typeof clientLoader>()` provides full type inference.

## Testing Strategy

### Manual Testing Checklist

Each migrated page must be tested for:

1. **Happy Path**
   - [ ] Page loads correctly
   - [ ] Data displays properly
   - [ ] Loading state shows (HydrateFallback)
   - [ ] Filters/pagination work (if applicable)

2. **Error Scenarios**
   - [ ] 401 redirects to login
   - [ ] 404 shows error boundary
   - [ ] 500 shows error boundary
   - [ ] Network errors handled

3. **Navigation**
   - [ ] Client navigation works (clicking links)
   - [ ] Browser back/forward works
   - [ ] URL parameters update correctly

4. **Type Safety**
   - [ ] Run `pnpm run typecheck`
   - [ ] No TypeScript errors

### Page-Specific Tests

**Problems List**:
- [ ] Filter by type (algorithm, choice, fillblank)
- [ ] Filter by difficulty
- [ ] Change ordering
- [ ] Pagination works
- [ ] Locked problems show lock icon
- [ ] Click on unlocked problem navigates to detail

**Problem Detail**:
- [ ] Direct access loads correct problem
- [ ] "Next problem" navigation works
- [ ] All problem types render correctly
- [ ] `has_next` controls "Next" button visibility

**Problem Description**:
- [ ] Markdown renders correctly
- [ ] Title displays

**Submissions**:
- [ ] Submission list loads
- [ ] Pagination works
- [ ] Problem info displays

## Rollback Plan

If issues arise:
1. Git revert to pre-migration commit
2. No database or backend changes needed
3. Zero data migration risk

## Success Criteria

- [ ] All 4 pages use `clientLoader` pattern
- [ ] No `useEffect` data fetching remains in these pages
- [ ] Typecheck passes (`pnpm run typecheck`)
- [ ] Manual testing passes for all scenarios
- [ ] Consistent with home/courses page patterns
- [ ] No functional regressions
