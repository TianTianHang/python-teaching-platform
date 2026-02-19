# markdown-lazy-render Specification

## Purpose
TBD - created by archiving change add-markdown-lazy-render. Update Purpose after archive.
## Requirements
### Requirement: LazyRender Component

The system SHALL provide a LazyRender component that defers rendering children until the element enters the viewport.

#### Scenario: Component renders fallback initially

- **GIVEN** a LazyRender component with children and fallback content
- **WHEN** the component is first rendered
- **THEN** the fallback content is displayed
- **AND** the children are not rendered

#### Scenario: Component renders children when in viewport

- **GIVEN** a LazyRender component that is displaying fallback
- **WHEN** the component enters the viewport
- **THEN** the children are rendered
- **AND** the fallback is removed
- **AND** the observer is disconnected

#### Scenario: Component supports custom root margin

- **GIVEN** a LazyRender component with `rootMargin="200px"`
- **WHEN** the component is within 200px of the viewport
- **THEN** the children are rendered (pre-loading)

#### Scenario: Component is SSR compatible

- **GIVEN** a LazyRender component rendered on the server
- **WHEN** the HTML is generated
- **THEN** only the fallback content is included
- **AND** no hydration mismatch occurs

#### Scenario: Component handles missing Intersection Observer

- **GIVEN** a browser without Intersection Observer support
- **WHEN** the component mounts
- **THEN** children render immediately (fallback to eager loading)

### Requirement: Lazy Load JupyterLite Code Blocks

The system SHALL lazy load JupyterLite iframe code blocks.

#### Scenario: Code block below fold uses skeleton

- **GIVEN** a markdown document with a python-exec code block below the viewport
- **WHEN** the page is loaded
- **THEN** a skeleton placeholder is displayed
- **AND** the iframe is not initialized

#### Scenario: Code block loads when scrolled into view

- **GIVEN** a markdown document with a lazy-loaded code block
- **WHEN** the user scrolls to the code block
- **THEN** the iframe is initialized
- **AND** the skeleton is replaced with the actual code block

#### Scenario: Multiple code blocks load progressively

- **GIVEN** a markdown document with 5 code blocks spread across the page
- **WHEN** the user scrolls through the page
- **THEN** each code block loads as it enters the viewport
- **AND** only visible code blocks are initialized

### Requirement: Lazy Load Collapsed Foldable Blocks

The system SHALL lazy load foldable block content when in collapsed state.

#### Scenario: Expanded foldable block loads immediately

- **GIVEN** a foldable block with `defaultExpanded=true`
- **WHEN** the page is loaded
- **THEN** the content renders immediately (no lazy loading)

#### Scenario: Collapsed foldable block defers content rendering

- **GIVEN** a foldable block with `defaultExpanded=false`
- **WHEN** the page is loaded
- **AND** the block is below the viewport
- **THEN** only the header is rendered
- **AND** the content is not rendered

#### Scenario: Collapsed block renders content when expanded

- **GIVEN** a collapsed foldable block
- **WHEN** the user clicks to expand it
- **THEN** the content is rendered
- **AND** the expansion is smooth

### Requirement: Prevent Layout Shift

The system SHALL prevent cumulative layout shift during lazy loading.

#### Scenario: Skeleton reserves correct space

- **GIVEN** a lazy-loaded code block with height=400px
- **WHEN** the skeleton is displayed
- **THEN** the skeleton reserves 400px of space
- **AND** no layout shift occurs when content loads

#### Scenario: Foldable block header reserves space

- **GIVEN** a lazy-loaded collapsed foldable block
- **WHEN** the page is loaded
- **THEN** the foldable block header is visible
- **AND** clicking expand doesn't cause layout shift

### Requirement: Maintain Markdown Functionality

The system SHALL not break existing markdown rendering features.

#### Scenario: Code execution still works

- **GIVEN** a lazy-loaded python-exec code block
- **WHEN** the code block is loaded and user executes code
- **THEN** the code executes correctly
- **AND** output is displayed

#### Scenario: Foldable block toggle still works

- **GIVEN** a lazy-loaded foldable block
- **WHEN** the user clicks to expand/collapse
- **THEN** the toggle works smoothly
- **AND** state is preserved

#### Scenario: Nested markdown in lazy components

- **GIVEN** a lazy-loaded foldable block with nested markdown
- **WHEN** the content is rendered
- **THEN** all nested markdown is correctly formatted

### Requirement: Theme Support

The system SHALL support dark/light mode for lazy-loaded components.

#### Scenario: Skeleton matches theme

- **GIVEN** a lazy-loaded code block skeleton
- **WHEN** the theme is dark
- **THEN** the skeleton uses dark mode colors
- **AND** when the theme is light
- **THEN** the skeleton uses light mode colors

#### Scenario: Loaded component matches theme

- **GIVEN** a lazy-loaded JupyterLite code block
- **WHEN** the component loads
- **THEN** the iframe uses the correct theme

### Requirement: Performance Targets

The system SHALL meet specified performance targets.

#### Scenario: First Content Paint improvement

- **GIVEN** a page with 3+ code blocks
- **WHEN** lazy loading is enabled
- **THEN** FCP is reduced by at least 30% compared to eager loading

#### Scenario: No regression for simple content

- **GIVEN** a page with only text markdown (no heavy components)
- **WHEN** the page is loaded
- **THEN** rendering time is similar to eager loading (no overhead)

