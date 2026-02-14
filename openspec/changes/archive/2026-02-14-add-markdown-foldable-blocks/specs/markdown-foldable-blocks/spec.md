# Markdown Foldable Blocks Specification

## ADDED Requirements

### Requirement: Parse Remark Directive Container Syntax

The system SHALL parse custom container syntax using remark-directive format `:::name[label]{attributes}` and `:::` delimiters in markdown content.

#### Scenario: Valid foldable block syntax without attributes

- **GIVEN** markdown content with `:::tip` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block node is created with type `tip` and uses type's default state

#### Scenario: Valid foldable block syntax with title attribute

- **GIVEN** markdown content with `:::tip{title="Title"}` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block node is created with type `tip`, title `Title`, and uses type's default state

#### Scenario: Valid foldable block syntax with expanded state attribute

- **GIVEN** markdown content with `:::tip{title="Title" state="expanded"}` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block node is created with type `tip`, title `Title`, and `defaultExpanded=true`

#### Scenario: Valid foldable block syntax with collapsed state attribute

- **GIVEN** markdown content with `:::answer{title="Title" state="collapsed"}` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block node is created with type `answer`, title `Title`, and `defaultExpanded=false`

#### Scenario: Valid foldable block syntax with class shortcut for state

- **GIVEN** markdown content with `:::fold{title="Title" .expanded}` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block node is created with type `fold`, title `Title`, and `defaultExpanded=true`

#### Scenario: Valid foldable block syntax with state attribute without quotes

- **GIVEN** markdown content with `:::tip{state=expanded}` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block node is created with type `tip` and `defaultExpanded=true`

#### Scenario: Multiple foldable blocks

- **GIVEN** markdown content with multiple foldable blocks of different types
- **WHEN** the markdown is parsed
- **THEN** each block is parsed independently

#### Scenario: Block with no title attribute

- **GIVEN** markdown content with `:::fold` (no title attribute)
- **WHEN** the markdown is parsed
- **THEN** a foldable block is created with a default title

#### Scenario: Block with label but no attributes

- **GIVEN** markdown content with `:::tip[Reference]` followed by content and ending with `:::`
- **WHEN** the markdown is parsed
- **THEN** a foldable block is created with type `tip` and the label is stored for reference

#### Scenario: Block with label and attributes

- **GIVEN** markdown content with `:::answer[ref-id]{title="Answer"}`
- **WHEN** the markdown is parsed
- **THEN** a foldable block is created with type `answer`, title `Answer`, and reference id `ref-id`

### Requirement: Render Foldable Blocks

The system SHALL render foldable blocks as collapsible UI components with appropriate styling based on type and state.

#### Scenario: Render tip block with default state

- **GIVEN** a parsed foldable block with type `tip` and no explicit state attribute
- **WHEN** rendered
- **THEN** display with tip icon, green accent, and expanded state

#### Scenario: Render tip block with collapsed state

- **GIVEN** a parsed foldable block with type `tip{state=collapsed}`
- **WHEN** rendered
- **THEN** display with tip icon, green accent, and collapsed state (overrides default)

#### Scenario: Render answer block with default state

- **GIVEN** a parsed foldable block with type `answer` and no explicit state attribute
- **WHEN** rendered
- **THEN** display with answer icon, blue accent, and collapsed state

#### Scenario: Render answer block with expanded state

- **GIVEN** a parsed foldable block with type `answer{state=expanded}`
- **WHEN** rendered
- **THEN** display with answer icon, blue accent, and expanded state (overrides default)

#### Scenario: Render warning block

- **GIVEN** a parsed foldable block with type `warning`
- **WHEN** rendered
- **THEN** display with warning icon, orange accent, and expanded state (default or explicit)

#### Scenario: Render generic fold block

- **GIVEN** a parsed foldable block with type `fold`
- **WHEN** rendered
- **THEN** display with chevron icon, gray accent, and collapsed state (default or explicit)

#### Scenario: Render with custom title from attribute

- **GIVEN** a parsed foldable block with `title="Custom Title"` attribute
- **WHEN** rendered
- **THEN** display `Custom Title` in the block header

### Requirement: Support Nested Markdown Content

The system SHALL parse and render markdown content inside foldable blocks.

#### Scenario: Nested formatting

- **GIVEN** a foldable block containing bold text, links, and code
- **WHEN** rendered
- **THEN** all markdown formatting is correctly displayed

#### Scenario: Nested code blocks

- **GIVEN** a foldable block containing code fences
- **WHEN** rendered
- **THEN** code blocks are properly syntax highlighted

### Requirement: Toggle Expand/Collapse State

The system SHALL allow users to toggle the expanded/collapsed state of foldable blocks.

#### Scenario: Click to expand

- **GIVEN** a collapsed foldable block
- **WHEN** user clicks the header
- **THEN** the block expands to show content

#### Scenario: Click to collapse

- **GIVEN** an expanded foldable block
- **WHEN** user clicks the header
- **THEN** the block collapses to hide content

### Requirement: SSR Compatibility

The foldable block component SHALL work with React Router v7 server-side rendering.

#### Scenario: Server render

- **GIVEN** markdown content with foldable blocks
- **WHEN** rendered on the server
- **THEN** no JavaScript errors occur and markup is generated correctly

### Requirement: Attribute Parsing

The system SHALL correctly parse directive attributes in various formats.

#### Scenario: Parse double-quoted attributes

- **GIVEN** attribute `title="My Title"` in `{attributes}`
- **WHEN** parsed
- **THEN** the title value is extracted as `My Title`

#### Scenario: Parse single-quoted attributes

- **GIVEN** attribute `title='My Title'` in `{attributes}`
- **WHEN** parsed
- **THEN** the title value is extracted as `My Title`

#### Scenario: Parse unquoted attributes

- **GIVEN** attribute `state=expanded` in `{attributes}`
- **WHEN** parsed
- **THEN** the state value is extracted as `expanded`

#### Scenario: Parse class shortcut

- **GIVEN** attribute `.expanded` in `{attributes}`
- **WHEN** parsed
- **THEN** the state is set to expanded based on the class

#### Scenario: Parse mixed attribute styles

- **GIVEN** attributes `{state=expanded .my-class title="Title"}`
- **WHEN** parsed
- **THEN** all attributes are correctly extracted and applied

#### Scenario: Parse ID shortcut

- **GIVEN** attribute `{#my-id}` in `{attributes}`
- **WHEN** parsed
- **THEN** the id is set to `my-id` (equivalent to `{id=my-id}`)
