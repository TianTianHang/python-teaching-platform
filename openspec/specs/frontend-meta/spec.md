# frontend-meta Specification

## Purpose
TBD - created by archiving change add-react19-meta-tags. Update Purpose after archive.
## Requirements
### Requirement: React 19 Native Meta Elements

The frontend SHALL use React 19's native `<title>` and `<meta>` elements instead of React Router's deprecated `meta()` export pattern.

#### Scenario: Route with static meta tags
- **GIVEN** a route with static content (e.g., login page)
- **WHEN** the component is rendered
- **THEN** `<title>` and `<meta>` elements are rendered at the component root
- **AND** these elements appear in the HTML `<head>` during SSR

#### Scenario: Route with dynamic meta tags
- **GIVEN** a route with dynamic content (e.g., course detail page)
- **WHEN** the loader provides data including title/description
- **THEN** the component uses loader data to populate meta element attributes
- **AND** fallback values are provided if data is undefined

### Requirement: SEO-Optimized Meta Tags

All public-facing pages SHALL include SEO-optimized meta tags including title, description, and Open Graph tags.

#### Scenario: Title tag format
- **GIVEN** any route in the application
- **WHEN** rendering the page
- **THEN** the `<title>` element follows the pattern: `[Page Content] - Python教学平台`
- **AND** the title length is between 30 and 60 characters
- **AND** the title accurately describes the page content

#### Scenario: Description meta tag
- **GIVEN** any route in the application
- **WHEN** rendering the page
- **THEN** a `<meta name="description">` element is present
- **AND** the description length is between 120 and 160 characters
- **AND** the description accurately summarizes the page content

#### Scenario: Open Graph tags
- **GIVEN** any route in the application
- **WHEN** rendering the page
- **THEN** `<meta property="og:title">` is present and matches the page title
- **AND** `<meta property="og:description">` is present and matches the description
- **AND** `<meta property="og:type">` is present with appropriate value (website, profile, etc.)

### Requirement: SSR Meta Tag Rendering

Meta tags SHALL be rendered correctly during server-side rendering to ensure SEO and social sharing work without JavaScript.

#### Scenario: View-source meta tag verification
- **GIVEN** any route in the application
- **WHEN** viewing the page source (view-source: URL)
- **THEN** all meta tags are present in the initial HTML
- **AND** meta tags are not missing or empty
- **AND** dynamic meta tags contain the correct values from the loader

#### Scenario: Social media sharing preview
- **GIVEN** a URL to any public page on the platform
- **WHEN** shared on social media (Facebook, LinkedIn, etc.)
- **THEN** the link preview displays the correct title
- **AND** the link preview displays the correct description
- **AND** the preview type is appropriate for the content

### Requirement: Dynamic Meta Tag Pattern

Routes with dynamic content (courses, problems, threads) SHALL use loader data to populate meta tags with appropriate fallbacks.

#### Scenario: Course detail page meta
- **GIVEN** a course detail route with loader returning course data
- **WHEN** the course data includes a title
- **THEN** the page title is `[Course Title] - Python教学平台`
- **WHEN** the course data includes a description
- **THEN** the meta description is the course description (truncated to 160 chars if needed)
- **WHEN** the course data is loading or fails to load
- **THEN** fallback title "课程详情 - Python教学平台" is used
- **AND** fallback description describes the course page

#### Scenario: Problem detail page meta
- **GIVEN** a problem detail route with loader returning problem data
- **WHEN** the problem data includes a title
- **THEN** the page title is `[Problem Title] - 题目详情 - Python教学平台`
- **AND** the problem type/level is included in the description if available

### Requirement: User-Specific Meta Tags

Pages with user-specific content (profile, home dashboard) SHALL include relevant user context in meta tags.

#### Scenario: Profile page meta
- **GIVEN** a profile route with loader returning user data
- **WHEN** the user data includes a username
- **THEN** the page title is `[Username] - 个人中心 - Python教学平台`
- **AND** the description mentions the user's profile

#### Scenario: Home dashboard meta
- **GIVEN** a home route with loader returning user data
- **WHEN** the user data includes a username
- **THEN** the page title includes the username
- **AND** the description mentions personalized learning dashboard

### Requirement: Protected Route Meta Tags

Protected routes (requiring authentication) SHALL still include proper meta tags for SEO and browser display.

#### Scenario: Authenticated page meta tags
- **GIVEN** a protected route (requires login)
- **WHEN** the page is rendered (after authentication)
- **THEN** appropriate title and meta tags are present
- **AND** the page displays correctly in browser history
- **AND** social sharing works if the user shares the URL (would prompt login)

### Requirement: Meta Tag Configuration

The application SHALL provide shared configuration for default meta tag values to ensure consistency across routes.

#### Scenario: Default meta values
- **GIVEN** any route component
- **WHEN** implementing meta tags
- **THEN** default values are available from `~/config/meta.ts`
- **AND** defaults include site name, base description, and OG type
- **AND** routes can override defaults as needed

### Requirement: Fallback and Error Handling

Meta tag implementation SHALL handle edge cases including loading states, errors, and missing data.

#### Scenario: Loading state meta
- **GIVEN** a route with async data loading
- **WHEN** data is still loading
- **THEN** meta tags use fallback values instead of undefined
- **AND** the page shows a loading-appropriate title

#### Scenario: Error state meta
- **GIVEN** a route where data loading failed
- **WHEN** an error is returned from the loader
- **THEN** meta tags use error-appropriate fallback values
- **AND** the title indicates an error occurred

