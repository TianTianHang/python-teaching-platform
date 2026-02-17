# JupyterLite Code Block Rendering Specification (Delta - Revised)

## ADDED Requirements

### Requirement: Render JupyterLite Code Blocks Without White Flash During Theme Switching

The system SHALL render JupyterLite iframe-based code blocks with immediate theme switching and loading indicators to prevent visual flashes of white background when changing themes.

#### Scenario: Theme switch from light to dark with no white flash

- **GIVEN** user is on light theme with visible JupyterLite code blocks
- **WHEN** user switches to dark mode
- **THEN** loading mask appears immediately
- **AND** old iframe is removed instantly (no fade animation)
- **AND** loading mask covers entire container area
- **AND** new iframe loads behind the mask
- **AND** loading mask hides when JupyterLite is ready
- **AND** user sees dark theme without any white flash

#### Scenario: Theme switch from dark to light with no white flash

- **GIVEN** user is on dark theme with visible JupyterLite code blocks
- **WHEN** user switches to light mode
- **THEN** loading mask appears immediately
- **AND** old iframe is removed instantly
- **AND** loading mask covers white background of new iframe
- **AND** loading mask hides when JupyterLite is ready
- **AND** user sees light theme without any white flash

#### Scenario: Initial load in dark mode

- **GIVEN** user loads a page with JupyterLite blocks in dark mode
- **WHEN** the page loads
- **THEN** loading mask is visible from the start
- **AND** mask covers the container while iframe loads
- **AND** mask hides when JupyterLite is ready
- **AND** no white background is visible during loading

#### Scenario: Multiple JupyterLite blocks during theme switch

- **GIVEN** a page contains multiple JupyterLite code blocks
- **WHEN** user switches themes
- **THEN** all blocks show loading mask simultaneously
- **AND** all masks hide when content is ready
- **AND** no block shows white flash during transition

#### Scenario: Slow network connection

- **GIVEN** user is on slow network (3G or slower)
- **WHEN** a page with JupyterLite blocks loads
- **THEN** loading mask remains visible until content is ready
- **AND** mask provides clear feedback that content is loading
- **AND** no white background is exposed during slow loading

#### Scenario: Fast theme switching

- **GIVEN** user switches themes rapidly
- **WHEN** new theme switch occurs before previous loading completes
- **THEN** loading mask remains visible
- **AND** new iframe loading begins
- **AND** mask hides only when final content is ready
- **AND** system handles multiple loading states correctly
