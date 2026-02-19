# frontend-theming Specification

## Purpose
TBD - created by archiving change fix-darkmode-problem-components. Update Purpose after archive.
## Requirements
### Requirement: Dark Mode Background Color Support for Problem Components
All problem display components SHALL use MUI semantic color tokens for background colors instead of hardcoded palette values to ensure proper visual appearance in both light and dark modes.

#### Scenario: Fill-blank problem displays correctly in dark mode
- **GIVEN** a user has dark mode enabled
- **AND** a fill-in-blank problem is displayed
- **WHEN** the problem input area is rendered
- **THEN** the background color adapts to the dark theme
- **AND** the background uses `background.paper` semantic token
- **AND** the input fields are clearly visible against the background
- **AND** no hardcoded gray background color (`grey.50`) is used

#### Scenario: Test case details display correctly in dark mode
- **GIVEN** a user has dark mode enabled
- **AND** a problem with test cases is displayed
- **WHEN** the CaseDetail component renders input/output areas
- **THEN** the background colors adapt to the dark theme
- **AND** the backgrounds use `background.paper` semantic token
- **AND** the text content remains clearly readable
- **AND** no hardcoded gray background color (`grey.100`) is used

#### Scenario: Components maintain proper appearance in light mode
- **GIVEN** a user has light mode enabled (default)
- **AND** problem components are displayed
- **WHEN** components using semantic tokens are rendered
- **THEN** the background colors match the original light theme appearance
- **AND** visual consistency with other components is maintained
- **AND** no regression in visual quality occurs

