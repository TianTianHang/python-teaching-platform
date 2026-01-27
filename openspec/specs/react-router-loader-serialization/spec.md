# react-router-loader-serialization Specification

## Purpose
TBD - created by archiving change fix-loader-json-serialization. Update Purpose after archive.
## Requirements
### Requirement: Loaders MUST return JSON-serializable data

All React Router loader functions MUST return values that can be serialized to JSON. This includes primitive types (string, number, boolean, null), plain objects, and arrays containing these types.

#### Scenario: Loader returns plain object

**Given** a loader function in a route file
**When** the loader fetches data from an API
**Then** the loader MUST return a plain JavaScript object with JSON-serializable properties
**And** the return value MUST NOT contain Date objects, Map, Set, or custom class instances

**Example**:
```tsx
// ✅ Correct
export async function loader({ request }: Route.LoaderArgs) {
    const data = await fetchData();
    return { items: data.results, count: data.count };
}

// ❌ Incorrect
export async function loader({ request }: Route.LoaderArgs) {
    const data = await fetchData();
    return { createdAt: new Date(), items: new Map(...) };
}
```

#### Scenario: Action returns primitive values

**Given** an action function that processes a form submission
**When** the action completes successfully
**Then** the action MAY return primitive values (string, number, boolean, null)
**And** the action MUST NOT return undefined

**Example**:
```tsx
// ✅ Correct
export async function action({ request }: Route.ActionArgs) {
    await processForm(formData);
    return { success: true };
}

// ❌ Incorrect - returns undefined
export async function action({ request }: Route.ActionArgs) {
    await processForm(formData);
    return; // No value returned
}
```

---

### Requirement: Date fields MUST be stored as ISO 8601 strings

TypeScript interfaces for data models MUST use `string` type for date fields instead of `Date`. Date values MUST be stored and transmitted as ISO 8601 formatted strings.

#### Scenario: User interface uses string dates

**Given** a User interface with dateJoined and lastLogin fields
**When** the interface is defined
**Then** dateJoined MUST be typed as `string`
**And** lastLogin MUST be typed as `string | undefined`
**And** both fields MUST contain ISO 8601 formatted date strings (e.g., "2024-01-15T10:30:00Z")

**Example**:
```tsx
// ✅ Correct
export interface User {
    id: number;
    username: string;
    dateJoined: string;  // ISO 8601 string
    lastLogin?: string;  // ISO 8601 string or undefined
}

// ❌ Incorrect
export interface User {
    id: number;
    username: string;
    dateJoined: Date;      // Not JSON-serializable
    lastLogin?: Date;      // Not JSON-serializable
}
```

#### Scenario: Converting Date to string before storage

**Given** a loader that receives user data with Date objects from an API
**When** storing the user data in session or returning from loader
**Then** all Date fields MUST be converted to ISO 8601 strings
**And** conversion MUST use `date.toISOString()` method

**Example**:
```tsx
// ✅ Correct
const userData = await api.getUser();
const serializableUser = {
    ...userData,
    dateJoined: userData.dateJoined.toISOString(),
    lastLogin: userData.lastLogin?.toISOString(),
};
session.set("user", serializableUser);

// ❌ Incorrect
const userData = await api.getUser();
session.set("user", userData);  // Contains Date objects
```

---

### Requirement: Loaders and actions MUST NOT return Response.json() wrappers

React Router automatically serializes loader/action return values. Loaders and actions MUST return plain data objects and MUST NOT wrap return values in `Response.json()` which creates Response objects that cannot be serialized.

#### Scenario: Loader returns data object directly

**Given** a loader that fetches paginated data
**When** returning the data to the component
**Then** the loader MUST return the data object directly
**And** the loader MUST NOT wrap the data in `Response.json()`

**Example**:
```tsx
// ✅ Correct
export async function loader({ request }: Route.LoaderArgs) {
    const data = await http.get<Page<Thread>>("/threads/");
    return {
        data: data.results,
        currentPage: 1,
        totalItems: data.count,
    };
}

// ❌ Incorrect
export async function loader({ request }: Route.LoaderArgs) {
    const data = await http.get<Page<Thread>>("/threads/");
    return Response.json({
        data: data.results,
        currentPage: 1,
        totalItems: data.count,
    });
}
```

#### Scenario: Action returns API response directly

**Given** an action that creates a resource via POST
**When** the API returns the created resource
**Then** the action MUST return the resource object directly
**And** the action MUST NOT wrap in `Response.json()`

**Example**:
```tsx
// ✅ Correct
export async function action({ request }: Route.ActionArgs) {
    const result = await http.post<Thread>("/threads/", body);
    return result;
}

// ❌ Incorrect
export async function action({ request }: Route.ActionArgs) {
    const result = await http.post<Thread>("/threads/", body);
    return Response.json(result);
}
```

---

### Requirement: All code paths in loaders/actions MUST return valid values

Loader and action functions MUST have return statements on all code paths, including error handlers. Early returns MUST return a valid JSON-serializable value, not undefined.

#### Scenario: Catch block returns redirect

**Given** a loader with a try-catch block for error handling
**When** an error is caught in the catch block
**Then** the catch block MUST include a `return` statement before `redirect()`
**And** the return value MUST be a valid redirect response or data

**Example**:
```tsx
// ✅ Correct
export async function loader({ request }: Route.LoaderArgs) {
    try {
        const data = await fetchData();
        return data;
    } catch {
        return redirect("/error", {
            headers: { "Set-Cookie": await destroySession(session) }
        });
    }
}

// ❌ Incorrect - missing return
export async function loader({ request }: Route.LoaderArgs) {
    try {
        const data = await fetchData();
        return data;
    } catch {
        redirect("/error", {  // Function returns undefined
            headers: { "Set-Cookie": await destroySession(session) }
        });
    }
}
```

#### Scenario: Early return with null

**Given** a loader that may exit early based on a condition
**When** the early return condition is met
**Then** the return statement MUST explicitly return `null` or a valid data object
**And** the return MUST NOT be a bare `return` (which returns undefined)

**Example**:
```tsx
// ✅ Correct
export async function loader({ request }: Route.LoaderArgs) {
    const url = new URL(request.url);
    if (url.pathname !== "/expected-path") {
        return null;  // Explicitly return null
    }
    return await fetchData();
}

// ❌ Incorrect - returns undefined
export async function loader({ request }: Route.LoaderArgs) {
    const url = new URL(request.url);
    if (url.pathname !== "/expected-path") {
        return;  // Returns undefined
    }
    return await fetchData();
}
```

---

### Requirement: Type definitions must reflect JSON-serializable types

TypeScript interfaces used for loader/action return types MUST only use JSON-serializable types. Custom interfaces should not reference non-serializable types.

#### Scenario: Page interface uses serializable types

**Given** a Page interface for paginated responses
**When** the interface is defined
**Then** all generic type parameters MUST be constrained to JSON-serializable types
**And** date fields within the interface MUST be typed as `string`

**Example**:
```tsx
// ✅ Correct
export interface Page<T> {
    count: number;
    next: string | null;
    previous: string | null;
    page_size: number;
    results: T[];
}

// ❌ Incorrect - Date is not serializable
export interface Page<T> {
    count: number;
    timestamp: Date;  // Not allowed
    results: T[];
}
```

---

