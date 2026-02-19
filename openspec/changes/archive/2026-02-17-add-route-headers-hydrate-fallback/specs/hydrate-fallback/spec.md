# hydrate-fallback Specification

## Purpose

Define requirements for implementing HydrateFallback components in React Router routes to provide loading states during client-side hydration, improving perceived performance and user experience.

## ADDED Requirements

### Requirement: Routes with slow loaders MUST export `HydrateFallback` component

Routes that take more than 500ms to load data MUST export a `HydrateFallback` component that displays while `clientLoader` completes.

#### Scenario: Home page shows skeleton during hydration

**Given** the home page route (`_layout.home.tsx`) with multiple parallel API calls
**When** a user first visits the page
**Then** the `HydrateFallback` component MUST be rendered immediately
**And** the skeleton MUST match the page's visual structure
**And** the actual page content MUST render after loader completes

#### Scenario: Problems list shows skeleton during hydration

**Given** the problems list route (`_layout.problems.tsx`) with paginated data
**When** a user navigates to the problems page
**Then** the `HydrateFallback` component MUST display skeleton list items
**And** the skeleton MUST match the table/filter layout
**And** the actual problems MUST render after data loads

#### Scenario: Profile page shows skeleton during hydration

**Given** the profile page route (`_layout.profile.tsx`) with user data
**When** a user navigates to their profile
**Then** the `HydrateFallback` component MUST display a profile skeleton
**And** the skeleton MUST match the profile header and progress cards layout
**And** the actual profile MUST render after loader completes

---

### Requirement: `clientLoader` MUST enable hydration for fallback to work

Routes using `HydrateFallback` MUST implement `clientLoader` with `hydrate = true` to enable the fallback during initial page load.

#### Scenario: clientLoader enables hydration

**Given** a route with `HydrateFallback` exported
**When** implementing the loader pattern
**Then** `clientLoader` MUST be defined
**And** `clientLoader.hydrate` MUST be set to `true` (as const)
**And** `clientLoader` MUST call `serverLoader()` to get SSR data

Example:
```tsx
export async function clientLoader({ serverLoader }: Route.ClientLoaderArgs) {
  return await serverLoader();
}
clientLoader.hydrate = true as const;

export function HydrateFallback() {
  return <SkeletonComponent />;
}
```

#### Scenario: Routes without clientLoader skip hydration fallback

**Given** a route without `clientLoader` defined
**When** the page loads
**Then** `HydrateFallback` MUST NOT be used
**And** the page MUST use standard SSR rendering without client hydration delay

---

### Requirement: Skeleton components MUST match actual page structure

`HydrateFallback` skeleton components MUST visually match the structure and layout of the actual page content to avoid layout shifts.

#### Scenario: Home skeleton matches course cards layout

**Given** the home page displays enrolled courses in a grid
**When** rendering the `SkeletonHome` component
**Then** the skeleton MUST render the same number of card placeholders
**And** the skeleton MUST use the same spacing (gap, padding) as actual cards
**And** the skeleton MUST match the card aspect ratio

#### Scenario: Problems skeleton matches table structure

**Given** the problems page displays a table of problems
**When** rendering the `SkeletonProblems` component
**Then** the skeleton MUST render the same table headers
**And** the skeleton MUST render the same number of row placeholders
**And** the skeleton MUST match the column widths of the actual table

#### Scenario: Skeleton uses MUI Skeleton variants

**Given** the project uses Material-UI components
**When** creating skeleton components
**Then** `Skeleton` components MUST be imported from `@mui/material`
**And** `variant` prop MUST match the content type (text, rect, circular, etc.)
**And** `animation` prop MAY be "wave" or "pulse" for visual feedback

---

### Requirement: HydrateFallback MUST not block navigation

The `HydrateFallback` component MUST only appear during initial page load, NOT during client-side navigation between routes.

#### Scenario: Client navigation uses standard loading state

**Given** a user is already on the home page
**When** they click a link to navigate to problems
**Then** `HydrateFallback` MUST NOT be shown
**And** the existing navigation loading indicator MUST be used instead

#### Scenario: Only first page load shows hydration fallback

**Given** a user directly visits `/problems` (not via SPA navigation)
**When** the page initially loads
**Then** `HydrateFallback` MUST be rendered
**And** the fallback MUST be replaced by actual content once loader completes
**And** subsequent navigation MUST NOT trigger the fallback

---

### Requirement: Routes with fast loaders MUST support optional HydrateFallback

Routes that load data quickly (under 500ms) MAY omit `HydrateFallback` if the loading delay is not perceptible to users. Implementation MUST NOT require HydrateFallback for all routes.

#### Scenario: Fast-loading route skips fallback

**Given** a route with a simple loader that completes in <500ms
**When** implementing the route
**Then** `HydrateFallback` MAY be omitted
**And** the route MUST still load correctly without hydration delay
**And** users SHOULD NOT perceive a blank/loading state

#### Scenario: Static content routes skip fallback

**Given** the membership page displays static pricing content
**When** implementing the route
**Then** `HydrateFallback` MAY be omitted
**And** the page MAY use cache headers instead for instant loads
