# Tasks: Fix React Router Loader/Action JSON Serialization

This document outlines the step-by-step implementation tasks for fixing JSON serialization errors in React Router loaders and actions.

## Phase 1: Critical Fixes (Issue #1 - refresh.tsx)

### Task 1.1: Fix Missing Return in refresh.tsx Catch Block

**Description**: Add missing `return` statement to the catch block in refresh.tsx to prevent returning undefined.

**File**: `frontend/web-student/app/routes/refresh.tsx:26-31`

**Steps**:
1. Open `frontend/web-student/app/routes/refresh.tsx`
2. Locate the catch block at line 26
3. Add `return` before the `redirect()` call

**Current Code**:
```tsx
} catch {
    redirect("/auth/login", {
        headers: {
            'Set-Cookie': await destroySession(session),
        },
    });
}
```

**Expected Code**:
```tsx
} catch {
    return redirect("/auth/login", {
        headers: {
            'Set-Cookie': await destroySession(session),
        },
    });
}
```

**Validation**:
- Verify TypeScript compilation: `pnpm run typecheck`
- Test auth flow: logout, then attempt to access protected route
- Verify redirect to `/auth/login` works correctly

**Estimated Effort**: Small

**Dependencies**: None

---

## Phase 2: Type Definition Fixes (Issue #3, #4 - User Date Fields)

### Task 2.1: Update User Type to Use String for Date Fields

**Description**: Change `dateJoined` and `lastLogin` from `Date` to `string` in the User interface.

**File**: `frontend/web-student/app/types/user.ts:12-13`

**Steps**:
1. Open `frontend/web-student/app/types/user.ts`
2. Change `dateJoined: Date;` to `dateJoined: string;`
3. Change `lastLogin?: Date;` to `lastLogin?: string;`
4. Add JSDoc comment indicating ISO 8601 format

**Expected Code**:
```tsx
/**
 * ISO 8601 date string (e.g., "2024-01-15T10:30:00Z")
 */
dateJoined: string;

/**
 * ISO 8601 date string or undefined if user has never logged in
 */
lastLogin?: string;
```

**Validation**:
- Run `pnpm run typecheck` and verify no errors
- Search for usages of `dateJoined` and `lastLogin` that may need updates
- Verify display components properly format date strings

**Estimated Effort**: Small

**Dependencies**: None

---

## Phase 3: Loader Return Value Fixes (Issue #2 - threads.tsx)

### Task 3.1: Fix Undefined Return in threads.tsx Loader

**Description**: Change `return` to `return null` to prevent undefined return value.

**File**: `frontend/web-student/app/routes/threads.tsx:42-45`

**Steps**:
1. Open `frontend/web-student/app/routes/threads.tsx`
2. Locate the early return in the loader (line 44)
3. Change `return` to `return null;`

**Current Code**:
```tsx
const url = new URL(request.url);
if (url.pathname !== "/threads") {
    return
}
```

**Expected Code**:
```tsx
const url = new URL(request.url);
if (url.pathname !== "/threads") {
    return null;
}
```

**Validation**:
- Run `pnpm run typecheck`
- Test navigation to `/threads` route
- Verify component handles null return value correctly

**Estimated Effort**: Small

**Dependencies**: None

---

## Phase 4: Response.json() Removal (Issues #5, #6)

### Task 4.1: Remove Response.json() from threads.tsx Action

**Description**: Return data object directly instead of wrapping in Response.json().

**File**: `frontend/web-student/app/routes/threads.tsx:37`

**Steps**:
1. Open `frontend/web-student/app/routes/threads.tsx`
2. Locate the action return statement (line 37)
3. Check if it's a success response:
   ```tsx
   // Before:
   return Response.json(result);

   // After:
   return result;
   ```

**Note**: This appears to be a success response for thread creation, so it just needs a direct return.

**Expected Code**:
```tsx
const result = await http.post<Thread>("/threads/", body);
return result;
```

**Validation**:
- Test thread creation via form submission
- Verify response data is accessible in component

**Estimated Effort**: Small

**Dependencies**: None

---

### Task 4.2: Remove Response.json() from threads.tsx Loader

**Description**: Return data object directly instead of wrapping in Response.json().

**File**: `frontend/web-student/app/routes/threads.tsx:70`

**Steps**:
1. Open `frontend/web-student/app/routes/threads.tsx`
2. Locate the loader return statement (around line 70)
3. Check if it's paginated data:
   ```tsx
   // Before:
   return Response.json({
       data: data.results,
       currentPage: page,
       totalItems: data.count,
       actualPageSize: data.page_size || pageSize,
   });

   // After:
   return {
       data: data.results,
       currentPage: page,
       totalItems: data.count,
       actualPageSize: data.page_size || pageSize,
   };
   ```

**Note**: Loaders return paginated thread lists, so they just need direct return of the data object.

**Expected Code**:
```tsx
return {
    data: data.results,
    currentPage: page,
    totalItems: data.count,
    actualPageSize: data.page_size || pageSize,
};
```

**Validation**:
- Test pagination on threads page
- Verify data is accessible via `useLoaderData()`

**Estimated Effort**: Small

**Dependencies**: None

---

### Task 4.3: Remove Response.json() from submission.tsx Action

**Description**: Return data object directly instead of wrapping in Response.json().

**File**: `frontend/web-student/app/routes/submission.tsx:23`

**Steps**:
1. Open `frontend/web-student/app/routes/submission.tsx`
2. Locate the action return statement (line 23)
3. Check if it's a success response:
   ```tsx
   // Before:
   return Response.json(result);

   // After:
   return result;
   ```

**Note**: This appears to be a success response for code submission, so it just needs a direct return.

**Expected Code**:
```tsx
const result = await http.post<SubmissionFreelyRes | SubmissionRes>("/submissions/", { code, language, problem_id });
return result;
```

**Validation**:
- Test code submission
- Verify submission response is handled correctly

**Estimated Effort**: Small

**Dependencies**: None

---

### Task 4.4: Remove Response.json() from submission.tsx Loader

**Description**: Return data object directly instead of wrapping in Response.json().

**File**: `frontend/web-student/app/routes/submission.tsx:42`

**Steps**:
1. Open `frontend/web-student/app/routes/submission.tsx`
2. Locate the loader return statement (line 42)
3. Check if it's paginated data:
   ```tsx
   // Before:
   return Response.json({
       data: data.results,
       currentPage: page,
       totalItems: data.count,
       actualPageSize: data.page_size || pageSize,
   });

   // After:
   return {
       data: data.results,
       currentPage: page,
       totalItems: data.count,
       actualPageSize: data.page_size || pageSize,
   };
   ```

**Note**: Loaders return paginated submission lists, so they just need direct return of the data object.

**Expected Code**:
```tsx
return {
    data: data.results,
    currentPage: page,
    totalItems: data.count,
    actualPageSize: data.page_size || pageSize,
};
```

**Validation**:
- Test submissions list page
- Verify pagination works correctly

**Estimated Effort**: Small

**Dependencies**: None

---

### Task 4.5: Remove Response.json() from upload.$type.tsx

**Description**: Replace all Response.json() calls with appropriate return values in the upload route.

**File**: `frontend/web-student/app/routes/upload.$type.tsx`

**Instances**: 4 (lines 21, 47, 52, 56)

**Steps**:
1. Open `frontend/web-student/app/routes/upload.$type.tsx`
2. Add import at the top: `import { data } from "react-router";`
3. Replace error responses:
   ```tsx
   // Before:
   return Response.json({ error: "User ID missing" }, { status: 400 });

   // After:
   return data({ error: "User ID missing" }, { status: 400 });
   ```
4. Replace success responses:
   ```tsx
   // Before:
   return Response.json({ success: true, url });

   // After:
   return { success: true, url };
   ```

**Note**: This file uses error responses with status codes. Use the `data()` helper function instead of `Response.json()` for error responses. For success responses, return the data directly.

**Example patterns**:
```tsx
// Error response with status code
if (!userId) {
  return data({ error: "User ID missing" }, { status: 400 });
}

// Success response - direct return
return { success: true, url: uploadedUrl };
```

**Validation**:
- Test file upload functionality
- Verify error responses are handled correctly
- Ensure proper status codes are returned
- Verify success responses contain the expected data

**Estimated Effort**: Medium (4 instances to fix, import statement + error handling pattern)

**Dependencies**: None

---

### Task 4.6: Remove Response.json() from _layout.profile.tsx

**Description**: Replace Response.json() with appropriate return value.

**File**: `frontend/web-student/app/routes/_layout.profile.tsx:97`

**Steps**:
1. Open `frontend/web-student/app/routes/_layout.profile.tsx`
2. Add import at the top: `import { data } from "react-router";` if the Response.json() uses status codes
3. Locate the Response.json() call (line 97)
4. Check if it's an error response with status code:
   ```tsx
   // Before:
   return Response.json({ error: "message" }, { status: 400 });

   // After:
   return data({ error: "message" }, { status: 400 });
   ```
5. Or if it's a success response:
   ```tsx
   // Before:
   return Response.json({ success: true });

   // After:
   return { success: true };
   ```

**Validation**:
- Test profile update functionality
- Verify response data is accessible
- Ensure proper error status codes are returned if applicable

**Estimated Effort**: Small

**Dependencies**: None

---

### Task 4.7: Remove Response.json() from threads.$threadId.replies.tsx

**Description**: Return data objects directly instead of wrapping in Response.json().

**File**: `frontend/web-student/app/routes/threads.$threadId.replies.tsx`

**Instances**: 2 (lines 31, 55)

**Steps**:
1. Open `frontend/web-student/app/routes/threads.$threadId.replies.tsx`
2. Check if any Response.json() calls use status codes:
   ```tsx
   // If error response with status code:
   // Before:
   return Response.json({ error: "Not found" }, { status: 404 });

   // After:
   return data({ error: "Not found" }, { status: 404 });
   ```
3. For success responses, return directly:
   ```tsx
   // Before:
   return Response.json(result);

   // After:
   return result;
   ```

**Note**: Most of these are likely success responses, so they just need direct returns. Only use `data()` if there's an explicit status code in the Response.json() call.

**Validation**:
- Test reply creation
- Test reply list pagination
- Verify data is accessible via `useLoaderData()` and `useActionData()`
- Verify error responses with status codes work correctly

**Estimated Effort**: Small

**Dependencies**: None

---

## Phase 5: Verification and Testing

### Task 5.1: Full Type Check

**Description**: Run full TypeScript type check to ensure no new errors.

**Steps**:
1. Run `pnpm run typecheck`
2. Fix any remaining type errors
3. Verify all loader/action return types are compatible

**Validation**:
- `pnpm run typecheck` completes with no errors

**Estimated Effort**: Small

**Dependencies**: Tasks 1.1, 2.1, 3.1, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7

---

### Task 5.2: Manual Testing - Auth Flow

**Description**: Test authentication flows that trigger the refresh loader.

**Test Cases**:
1. Log out, then navigate to protected route
2. Wait for access token to expire (if applicable)
3. Verify redirect to login works without serialization errors

**Validation**:
- No "Value is not JSON serializable" errors in console
- Login redirect works correctly

**Estimated Effort**: Small

**Dependencies**: Tasks 1.1, 5.1

---

### Task 5.3: Manual Testing - Thread Operations

**Description**: Test thread creation, listing, and replies.

**Test Cases**:
1. Navigate to `/threads` page
2. Create a new thread via form
3. Verify thread appears in list
4. Test pagination
5. Navigate to a thread detail page
6. Create a reply
7. Verify reply appears in the thread

**Validation**:
- No serialization errors
- Thread data displays correctly
- Reply functionality works

**Estimated Effort**: Small

**Dependencies**: Tasks 3.1, 4.1, 4.2, 4.7, 5.1

---

### Task 5.4: Manual Testing - Submission Flow

**Description**: Test code submission and submissions list.

**Test Cases**:
1. Submit code for a problem
2. Navigate to submissions list
3. Test pagination

**Validation**:
- No serialization errors
- Submission data displays correctly

**Estimated Effort**: Small

**Dependencies**: Tasks 4.3, 4.4, 5.1

---

### Task 5.5: Manual Testing - Upload and Profile

**Description**: Test file upload and profile update functionality.

**Test Cases**:
1. Navigate to profile page
2. Upload a new avatar image
3. Verify upload succeeds and image displays
4. Update profile information
5. Verify profile update succeeds
6. Test error handling (missing file, invalid file type)

**Validation**:
- No serialization errors
- File upload works correctly
- Profile update works correctly
- Error responses are handled properly

**Estimated Effort**: Small

**Dependencies**: Tasks 4.5, 4.6, 5.1

---

## Task Summary

| Task | Description | Phase | Effort |
|------|-------------|-------|--------|
| 1.1 | Fix refresh.tsx missing return | 1 | Small |
| 2.1 | Update User type Date fields | 2 | Small |
| 3.1 | Fix threads.tsx undefined return | 3 | Small |
| 4.1 | Remove Response.json() from threads.tsx action | 4 | Small |
| 4.2 | Remove Response.json() from threads.tsx loader | 4 | Small |
| 4.3 | Remove Response.json() from submission.tsx action | 4 | Small |
| 4.4 | Remove Response.json() from submission.tsx loader | 4 | Small |
| 4.5 | Remove Response.json() from upload.$type.tsx (4 instances) | 4 | Medium |
| 4.6 | Remove Response.json() from _layout.profile.tsx | 4 | Small |
| 4.7 | Remove Response.json() from threads.$threadId.replies.tsx (2 instances) | 4 | Small |
| 5.1 | Full type check | 5 | Small |
| 5.2 | Manual auth flow testing | 5 | Small |
| 5.3 | Manual thread operations testing | 5 | Small |
| 5.4 | Manual submission flow testing | 5 | Small |
| 5.5 | Manual upload and profile testing | 5 | Small |

**Total Estimated Effort**: 15 tasks - 13 small, 2 medium.

**Parallelization Opportunities**:
- Tasks 1.1-4.7 can be done in parallel (no dependencies)
- Phase 5 tasks depend on all fix tasks being complete

---

## Completion Checklist

- [x] Task 1.1: Fix refresh.tsx missing return
- [x] Task 2.1: Update User type Date fields
- [x] Task 3.1: Fix threads.tsx undefined return
- [x] Task 4.1: Remove Response.json() from threads.tsx action
- [x] Task 4.2: Remove Response.json() from threads.tsx loader
- [x] Task 4.3: Remove Response.json() from submission.tsx action
- [x] Task 4.4: Remove Response.json() from submission.tsx loader
- [x] Task 4.5: Remove Response.json() from upload.$type.tsx (4 instances)
- [x] Task 4.6: Remove Response.json() from _layout.profile.tsx
- [x] Task 4.7: Remove Response.json() from threads.$threadId.replies.tsx (2 instances)
- [x] Task 5.1: Full type check (passed)

**Status**: All implementation tasks completed. Type check passed successfully.

**Remaining**: Manual testing tasks (5.2, 5.3, 5.4, 5.5) should be performed by the user to verify the fixes work correctly in the running application.
