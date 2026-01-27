# problem-display Specification

## Purpose
Defines requirements for rendering problem content across all problem types with consistent markdown formatting and interactive elements.

## ADDED Requirements

### Requirement: Unified Markdown Rendering for Problem Content
All problem types SHALL render the `content` field using the `MarkdownRenderer` component to ensure consistent formatting and feature support.

#### Scenario: Display choice problem with markdown content
- **GIVEN** a choice problem exists with markdown-formatted content
- **WHEN** the problem is displayed in the student interface
- **THEN** the content renders with full markdown support
- **AND** headers, code blocks, lists, and tables display correctly
- **AND** the multiple choice options render below the content

#### Scenario: Display fill-blank problem with markdown content
- **GIVEN** a fill-in-blank problem exists with markdown-formatted content
- **AND** the content includes `[blank1]`, `[blank2]` placeholders in `content_with_blanks`
- **WHEN** the problem is displayed in the student interface
- **THEN** the static `content` field renders with full markdown support
- **AND** interactive input fields replace `[blankN]` placeholders correctly
- **AND** markdown formatting in the content displays properly

#### Scenario: Display algorithm problem with markdown content
- **GIVEN** an algorithm problem exists with markdown-formatted content
- **WHEN** the problem is displayed in the student interface
- **THEN** the content renders with full markdown support via MarkdownRenderer
- **AND** the code editor displays below the content
- **AND** test cases display correctly

#### Scenario: Backward compatibility with plain text content
- **GIVEN** a problem exists with plain text content (no markdown formatting)
- **WHEN** the problem is displayed
- **THEN** the content renders correctly as plain text
- **AND** no markdown parsing errors occur
- **AND** the display is visually consistent with other problems

### Requirement: JupyterLite Integration for Interactive Python
Problem content SHALL support interactive Python code blocks using the `python-exec` language identifier.

#### Scenario: Render python-exec block in choice problem
- **GIVEN** a choice problem content contains a code block marked as `python-exec`
- **WHEN** the problem is displayed
- **THEN** the code block renders as an interactive JupyterLite notebook
- **AND** users can execute Python code directly in the problem view

#### Scenario: Render python-exec block in fill-blank problem
- **GIVEN** a fill-blank problem content contains a code block marked as `python-exec`
- **WHEN** the problem is displayed
- **THEN** the code block renders as an interactive JupyterLite notebook
- **AND** users can execute Python code without leaving the problem page

#### Scenario: Render python-exec block in algorithm problem
- **GIVEN** an algorithm problem content contains a code block marked as `python-exec`
- **WHEN** the problem is displayed
- **THEN** the code block renders as an interactive JupyterLite notebook
- **AND** users can experiment with example code before attempting the problem

### Requirement: Styled Markdown Elements
The MarkdownRenderer SHALL apply MUI theme-consistent styling to all markdown elements.

#### Scenario: Heading styling
- **GIVEN** problem content contains markdown headings (h1-h6)
- **WHEN** the content is rendered
- **THEN** each heading level uses the appropriate MUI typography variant
- **AND** h1 and h2 include bottom borders for visual separation

#### Scenario: Code block styling
- **GIVEN** problem content contains a fenced code block
- **WHEN** the content is rendered
- **THEN** the code block has a contrasting background color
- **AND** the background adapts to dark/light theme
- **AND** the code block is horizontally scrollable when needed

#### Scenario: Inline code styling
- **GIVEN** problem content contains inline code (backticks)
- **WHEN** the content is rendered
- **THEN** the inline code has a distinct background color
- **AND** monospace font is applied
- **AND** the styling adapts to the current theme

#### Scenario: Table styling
- **GIVEN** problem content contains a markdown table
- **WHEN** the content is rendered
- **THEN** the table uses MUI-styled borders and spacing
- **AND** table headers have a distinct background color
- **AND** cells have proper padding

### Requirement: Component Integration
Problem components SHALL import and use the MarkdownRenderer component consistently.

#### Scenario: Import MarkdownRenderer in ChoiceProblemCmp
- **GIVEN** the ChoiceProblemCmp component needs to render problem content
- **WHEN** the component file is written
- **THEN** MarkdownRenderer is imported from the components directory
- **AND** the component passes `problem.content` as `markdownContent` prop

#### Scenario: Import MarkdownRenderer in FillBlankProblemCmp
- **GIVEN** the FillBlankProblemCmp component needs to render problem content
- **WHEN** the component file is written
- **THEN** MarkdownRenderer is imported from the components directory
- **AND** the component passes `problem.content` as `markdownContent` prop
- **AND** the `content_with_blanks` logic for interactive inputs remains separate

### Requirement: Type Safety
The MarkdownRenderer integration SHALL maintain TypeScript type safety.

#### Scenario: Prop typing for markdownContent
- **GIVEN** a component uses MarkdownRenderer
- **WHEN** TypeScript compiles the code
- **THEN** `markdownContent` prop is typed as `string`
- **AND** passing `problem.content` (which is `string`) produces no type errors

#### Scenario: No type errors after modification
- **GIVEN** ChoiceProblemCmp and FillBlankProblemCmp are updated to use MarkdownRenderer
- **WHEN** `pnpm run typecheck` is executed
- **THEN** no TypeScript errors are reported
- **AND** all component props are correctly typed
