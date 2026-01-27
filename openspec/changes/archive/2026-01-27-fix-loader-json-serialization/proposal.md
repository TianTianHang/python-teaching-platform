# Fix React Router Loader/Action JSON Serialization

## Summary

Fix critical `TypeError: Value is not JSON serializable` errors in React Router v7 loaders and actions by ensuring all return values are properly JSON-serializable.

## Motivation

### Current State

The application experiences runtime errors when navigating between routes, particularly after `/problems/1` returns a 302 redirect. The error trace shows:

```
TypeError: Value is not JSON serializable
    at /home/tiantian/project/python-teaching-platform/frontend/web-student/node_modules/react-router/dist/index.js:2689:46
    at Object.json (native)
    at Object.call (node_modules/react-router/dist/index.js:2689:46)
```

### Root Causes Identified

1. **refresh.tsx:27** - catch block missing `return`, causing function to return `undefined`
2. **threads.tsx:44** - loader may return `undefined` when pathname doesn't match
3. **threads.tsx:28** - User object from session contains `Date` objects (dateJoined, lastLogin)
4. **user.ts:12-13** - Type definitions use `Date` which is not JSON-serializable
5. **submission.tsx:24/43** - Using `Response.json()` instead of returning plain objects
6. **threads.tsx:38/70** - Same `Response.json()` issue

### Why This Matters

React Router v7 requires loaders and actions to return JSON-serializable data because:
- Response data is serialized to JSON during SSR
- Client-side hydration expects plain JSON objects
- Non-serializable types (Date, undefined, Response objects, Map/Set) cause runtime errors

## Proposed Changes

### 1. Fix refresh.tsx Missing Return (Critical)

**File**: `frontend/web-student/app/routes/refresh.tsx:26-31`

**Current**:
```tsx
} catch {
    redirect("/auth/login", {
        headers: {
            'Set-Cookie': await destroySession(session),
        },
    });
}
```

**Fix**:
```tsx
} catch {
    return redirect("/auth/login", {
        headers: {
            'Set-Cookie': await destroySession(session),
        },
    });
}
```

**Impact**: Critical - this is likely the primary cause of the error after 302 redirects.

### 2. Fix threads.tsx Undefined Return

**File**: `frontend/web-student/app/routes/threads.tsx:42-45`

**Current**:
```tsx
const url = new URL(request.url);
if (url.pathname !== "/threads") {
    return  // Returns undefined
}
```

**Fix**:
```tsx
const url = new URL(request.url);
if (url.pathname !== "/threads") {
    return null;  // Return null instead of undefined
}
```

### 3. Fix User Type Date Fields

**File**: `frontend/web-student/app/types/user.ts:12-13`

**Current**:
```tsx
dateJoined: Date;
lastLogin?: Date;
```

**Fix**:
```tsx
dateJoined: string;  // ISO 8601 date string
lastLogin?: string;  // ISO 8601 date string or undefined
```

**Rationale**: Date objects are not JSON-serializable. Use ISO 8601 strings instead.

### 4. Remove Response.json() Wrappers

**Files affected**:
- `frontend/web-student/app/routes/threads.tsx:37, 70`
- `frontend/web-student/app/routes/submission.tsx:23, 42`
- `frontend/web-student/app/routes/upload.$type.tsx:21, 47, 52, 56` (4 instances)
- `frontend/web-student/app/routes/_layout.profile.tsx:97`
- `frontend/web-student/app/routes/threads.$threadId.replies.tsx:31, 55`

**Total**: 13 instances of `Response.json()` across 5 files

## Response.json() Replacement Strategy

React Router v7 provides a `data()` helper function to create responses with status codes and headers while maintaining JSON-serializability.

### 4.1 Import the data() Helper

```tsx
import { data } from "react-router";
```

### 4.2 Replacement Patterns

#### Pattern 1: Success Response - Direct Return
```tsx
// ❌ Current - wraps data in Response object
return Response.json(result);

// ✅ Fixed - return data directly
return result;
```

#### Pattern 2: Error Response with Status Code
```tsx
// ❌ Current - Response object not serializable
return Response.json({ error: "User ID missing" }, { status: 400 });

// ✅ Fixed - use data() helper
return data({ error: "User ID missing" }, { status: 400 });
```

#### Pattern 3: Success Response with Custom Status/Headers
```tsx
// ✅ Fixed - use data() for custom responses
return data(result, {
  status: 201,  // Created
  headers: { "X-Custom-Header": "value" }
});
```

### 4.3 data() Function Signature

```tsx
function data<D>(data: D, init?: number | ResponseInit)
```

- **data**: The data to include in the response (any JSON-serializable type)
- **init**: Optional status code or ResponseInit object with status and headers

### 4.4 Key Points

- For normal success responses, return the data directly
- For error responses, use `data({ error: "message" }, { status: 400 })`
- For success responses with custom status codes (e.g., 201), use `data()`
- React Router handles the JSON serialization automatically
- The `data()` helper creates a special object that React Router understands but remains JSON-serializable

### 5. Update Session User Serialization

**File**: `frontend/web-student/app/routes/threads.tsx:27`

When storing user in session, ensure Date fields are converted to strings:

**Current**:
```tsx
author: session.get("user"),
```

**Note**: The user object in session should already have Date fields as strings from the login flow. Verify the login loader properly serializes the user object.

## Affected Components

| File | Line(s) | Issue | Severity |
|------|---------|-------|----------|
| refresh.tsx | 26-31 | Missing return in catch | Critical |
| threads.tsx | 42-45 | Returns undefined | High |
| user.ts | 12-13 | Date type definitions | High |
| threads.tsx | 37, 70 | Response.json() usage | Medium |
| submission.tsx | 23, 42 | Response.json() usage | Medium |
| upload.$type.tsx | 21, 47, 52, 56 | Response.json() usage (4 instances) | Medium |
| _layout.profile.tsx | 97 | Response.json() usage | Medium |
| threads.$threadId.replies.tsx | 31, 55 | Response.json() usage | Medium |

**Total**: 3 files with critical/high issues, 5 files with Response.json() issues (13 instances total)
| threads.tsx | 42-45 | Returns undefined | High |
| user.ts | 12-13 | Date type definitions | High |
| threads.tsx | 37, 70 | Response.json() usage | Medium |
| submission.tsx | 23, 42 | Response.json() usage | Medium |

## Testing Strategy

1. **Unit Tests**: Add tests verifying loader/action return values are JSON-serializable
2. **Integration Tests**: Test navigation flows that trigger these loaders
3. **Manual Testing**: Navigate through auth flows, thread creation, and problem submission

## Rollout Plan

1. Fix critical `refresh.tsx` issue first (likely root cause)
2. Fix `user.ts` type definitions
3. Fix `threads.tsx` and `submission.tsx` Response.json() issues
4. Add validation tests to prevent future regressions

## Alternatives Considered

### Alternative 1: Use Custom Serializers
Add custom serialization logic for Date objects in React Router middleware.
**Rejected**: More complex than needed; string types are simpler and sufficient.

### Alternative 2: Keep Response.json() with Body Extraction
Extract Response.json().body before returning.
**Rejected**: Adds unnecessary wrapper; React Router expects plain objects.

### Alternative 3: Ignore the Issue
Use `@ts-expect-error` comments and hope for the best.
**Rejected**: Runtime errors will persist; this is a correctness issue, not a type issue.
