# route-caching Specification

## Purpose
Define HTTP cache control header strategies for frontend routes to optimize SSR performance while maintaining data freshness.

## Requirements
### Requirement: Routes MUST export `headers()` function to set cache control

Routes that should be cached MUST export a `headers()` function that returns appropriate HTTP headers for caching.

#### Scenario: Public static page sets long cache duration

**Given** the membership page route (`_layout.membership.tsx`)
**When** the page is rendered via SSR
**Then** the response MUST include `Cache-Control: public, max-age=3600`
**And** the response MUST include `Cache-Control: s-maxage=3600`
**And** the response MAY include `stale-while-revalidate=86400`

#### Scenario: Public dynamic page sets short cache duration

**Given** the problems list page route (`_layout.problems.tsx`)
**When** the page is rendered via SSR
**Then** the response MUST include `Cache-Control: public, max-age=300`
**And** the response MUST include `Cache-Control: s-maxage=600`
**And** the response MUST include `Vary: Accept-Encoding`

#### Scenario: User-specific page uses private cache

**Given** the home dashboard route (`_layout.home.tsx`)
**When** an authenticated user requests the page
**Then** the response MUST include `Cache-Control: private, max-age=120`
**And** the response MUST NOT include `public` directive
**And** the response MUST include `must-revalidate`

---

### Requirement: Cache durations MUST match content update frequency

Cache durations MUST be configured based on how frequently the content changes and user tolerance for stale data.

#### Scenario: Static pricing content cached for 1 hour

**Given** the membership page displays pricing information
**When** pricing is updated (rarely, maybe monthly)
**Then** the cache duration MAY be up to 3600 seconds (1 hour)
**And** stale content MAY be served for up to 86400 seconds (24 hours) during revalidation

#### Scenario: Problems list cached for 5 minutes

**Given** the problems list displays available coding problems
**When** problems are added/removed (infrequently, maybe daily)
**Then** the cache duration MUST be 300 seconds (5 minutes) or less
**And** `stale-while-revalidate` MUST be set to 3600 seconds (1 hour)

#### Scenario: User dashboard cached for 2 minutes

**Given** the home page shows user-specific progress and enrollments
**When** user progress changes (frequently, after solving problems)
**Then** the cache duration MUST be 120 seconds (2 minutes) or less
**And** the cache directive MUST be `private` (not shared between users)

---

### Requirement: Authenticated routes MUST NOT leak private data in cache

Routes that display user-specific data MUST use appropriate cache directives to prevent one user's data from being shown to another.

#### Scenario: Private cache prevents cross-user data leakage

**Given** a user with ID=1 views their profile page
**When** the response is cached
**Then** the `Cache-Control` header MUST include `private` directive
**And** a shared cache (CDN) MUST NOT store the response
**And** user ID=2 MUST NOT see user ID=1's cached data

#### Scenario: Vary header prevents incorrect cache hits

**Given** an authenticated request includes a `Cookie` header
**When** caching the response
**Then** the `Vary` header MAY include `Cookie` if needed for correctness
**And** caches MUST NOT serve the response without matching the Cookie

---

### Requirement: Sensitive pages MUST NOT be cached

Routes that display sensitive or frequently-changing data MUST NOT be cached.

#### Scenario: Exam results page uses no-cache

**Given** the exam results page shows user's exam performance
**When** a user submits an exam and views results
**Then** the response MUST include `Cache-Control: no-cache`
**And** the response MUST include `no-store` directive
**And** the response MUST include `must-revalidate`

#### Scenario: Authentication pages use no-cache

**Given** the login or logout routes
**When** authentication state changes
**Then** the response MUST include `Cache-Control: no-store, no-cache, must-revalidate`
**And** the response MUST NOT be cached by any intermediate cache

---

### Requirement: Cache headers MUST support stale-while-revalidate

Cache headers SHALL include `stale-while-revalidate` directive to support serving stale data while background refresh occurs.

#### Scenario: API responses support stale data serving

**Given** a cached API response is served
**WHEN** the response is stale but `stale-while-revalidate` is set
**THEN** the system MAY serve stale data to the client
**AND** queue a background refresh task
**AND** subsequent requests SHOULD receive fresh data after refresh completes

#### Scenario: Frontend routes handle stale data gracefully

**Given** a stale response is received from the API
**WHEN** the frontend has `stale-while-revalidate` configured
**THEN** the frontend SHOULD display stale data with a loading indicator
**AND** update to fresh data when available

---

### Requirement: Backend cache control MUST be compatible with frontend cache control

Backend caching strategy MUST work in conjunction with frontend caching headers for optimal performance.

#### Scenario: Backend cache state determines frontend cache behavior

**WHEN** backend cache is hit
**THEN** backend SHOULD include appropriate cache headers
**AND** frontend SHOULD respect backend cache control

#### Scenario: Stale backend data is handled gracefully

**WHEN** backend serves stale data (with `stale-while-revalidate`)
**THEN** frontend SHOULD display appropriate UI for stale content
**AND** client SHOULD receive updated content when available

### Requirement: Cache warmup MUST prepare frontend-friendly data

Cache warming operations SHALL prepare data that works well with frontend SSR requirements.

#### Scenario: Pre-warmed cache supports SSR

**WHEN** frontend makes SSR request
**THEN** cache data SHOULD be properly serialized for SSR
**AND** include all required fields for component rendering

#### Scenario: Cache warming handles authentication context

**WHEN** warming user-specific data
**THEN** the system SHOULD prepare data for each user segment
**AND** anonymous vs authenticated data SHALL be separate

