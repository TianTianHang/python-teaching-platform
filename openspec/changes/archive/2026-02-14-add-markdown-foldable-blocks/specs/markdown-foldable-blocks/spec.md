# markdown-foldable-blocks Specification

## Purpose

Defines the specification for foldable/collapsible content blocks in course content markdown using remark-directive syntax with `:::name[label]{attributes}` delimiters. This includes four block types (tip, warning, answer, fold) with configurable default states and HTML-like attributes.

## ADDED Requirements

### Requirement: Directive Block Syntax

Course content markdown MUST support custom foldable block syntax using remark-directive container format with `:::` delimiters, optional label, and HTML-like attributes.

#### Scenario: Basic tip block with title attribute

**Given** a markdown content file
**When** author writes a basic tip block with title attribute:
```markdown
:::tip{title="Optional Title"}
Tip content here
:::
```
**Then** the block MUST be parsed as:
- Type: `tip`
- State: `expanded` (default for tip)
- Title: "Optional Title"
- Content: "Tip content here"

#### Scenario: Answer block with explicit collapsed state

**Given** a markdown content file
**When** author writes an answer block with explicit state attribute:
```markdown
:::answer{title="答案" state="collapsed"}
The answer content
:::
```
**Then** the block MUST be parsed as:
- Type: `answer`
- State: `collapsed`
- Title: "答案"
- Content: "The answer content"

#### Scenario: Fold block without title

**Given** a markdown content file
**When** author writes a fold block without title:
```markdown
:::fold{state="expanded"}
Content that is shown by default
:::
```
**Then** the block MUST be parsed as:
- Type: `fold`
- State: `expanded`
- Title: (empty or type default)
- Content: "Content that is shown by default"

#### Scenario: Block with label and attributes

**Given** a markdown content file
**When** author writes a block with label and attributes:
```markdown
:::tip[ref-id]{title="Custom Title" state="expanded"}
Content that can be referenced
:::
```
**Then** the block MUST be parsed as:
- Type: `tip`
- Label: `ref-id`
- Title: "Custom Title"
- State: `expanded`
- Content: "Content that can be referenced"

---

### Requirement: Block Type Definitions

The specification MUST define four directive block types with specific default states and purposes.

#### Scenario: Tip block defaults to expanded

**Given** a `tip` block without state attribute
**When** the block is rendered
**Then** it MUST default to `expanded` state
**And** it SHOULD be used for general hints and supplementary information

#### Scenario: Warning block defaults to expanded

**Given** a `warning` block without state attribute
**When** the block is rendered
**Then** it MUST default to `expanded` state
**And** it SHOULD be used for important warnings and caveats

#### Scenario: Answer block defaults to collapsed

**Given** an `answer` block without state attribute
**When** the block is rendered
**Then** it MUST default to `collapsed` state
**And** it SHOULD be used for solutions and answers

#### Scenario: Fold block defaults to collapsed

**Given** a `fold` block without state attribute
**When** the block is rendered
**Then** it MUST default to `collapsed` state
**And** it SHOULD be used for generic collapsible content

---

### Requirement: Attribute Syntax

Attributes MUST be specified using HTML-like syntax with curly braces: `{key="value"}` or `{key='value'}` or `{key=value}`.

#### Scenario: Title attribute with double quotes

**Given** a block with title attribute
**When** author writes `{title="My Title"}`
**Then** the title MUST be parsed as "My Title"

#### Scenario: Title attribute with single quotes

**Given** a block with title attribute
**When** author writes `{title='My Title'}`
**Then** the title MUST be parsed as "My Title"

#### Scenario: State attribute without quotes

**Given** a block with state attribute
**When** author writes `{state=expanded}`
**Then** the state MUST be parsed as "expanded"

#### Scenario: Multiple attributes

**Given** a block with multiple attributes
**When** author writes `{title="My Title" state="collapsed"}`
**Then** both attributes MUST be parsed correctly

#### Scenario: Class shortcut for state

**Given** a block with class shortcut
**When** author writes `{.expanded}` or `{.collapsed}`
**Then** the state MUST be set based on the class value
**And** this MUST be equivalent to `{state="expanded"}` or `{state="collapsed"}`

---

### Requirement: Attribute Behavior

Attributes MUST follow specific precedence rules and behaviors.

#### Scenario: State attribute overrides default

**Given** a `tip` block with `{state="collapsed"}`
**When** the block is parsed
**Then** the state MUST be `collapsed` (overriding tip's default of `expanded`)

#### Scenario: Title attribute overrides default title

**Given** a block with `{title="Custom Title"}`
**When** the block is rendered
**Then** the title MUST be "Custom Title" instead of the type default

#### Scenario: Missing title uses type default

**Given** a block without title attribute
**When** the block is rendered
**Then** the title MUST use the type-specific default

#### Scenario: Invalid state value handling

**Given** a block with `{state=invalid}`
**When** the block is parsed
**Then** the parser SHOULD fall back to the type's default state
**And** a warning SHOULD be logged

---

### Requirement: Label Syntax

Labels MUST be specified using square brackets immediately after the directive name and before attributes: `[label-content]`.

#### Scenario: Block with label

**Given** a block with label
**When** author writes `:::tip[ref-id]{title="Title"}`
**Then** the label MUST be parsed as "ref-id"
**And** the label MUST be stored as metadata
**And** the label MUST NOT be displayed in rendered output

#### Scenario: Block without label

**Given** a block without label
**When** author writes `:::tip{title="Title"}`
**Then** the label MUST be null or empty

#### Scenario: Label with markdown content

**Given** a block with markdown in label
**When** author writes `:::tip[**Bold**]{title="Title"}`
**Then** the label MAY contain markdown formatting
**And** it MUST be stored appropriately

---

### Requirement: Content Parsing

Foldable blocks MUST support all standard markdown content within the block body.

#### Scenario: Code blocks inside foldable

**Given** a foldable block
**When** it contains a code block:
```markdown
:::tip{title="Example"}
```python
print("Hello")
```
:::
```
**Then** the code block MUST be rendered correctly within the foldable

#### Scenario: Nested markdown content

**Given** a foldable block
**When** it contains lists, links, or other markdown elements
**Then** these elements MUST be rendered correctly

#### Scenario: Python-exec blocks inside foldable

**Given** a foldable block
**When** it contains a `python-exec` code block:
```markdown
:::tip{title="Try this"}
```python-exec
print(1 + 1)
```
:::
```
**Then** the `python-exec` block MUST be handled correctly by the platform

---

### Requirement: Delimiter Rules

Block opening and closing MUST follow specific delimiter rules based on remark-directive format.

#### Scenario: Opening delimiter format

**Given** a foldable block opening
**When** written as `:::name`, `:::name{attributes}`, or `:::name[label]{attributes}`
**Then** it MUST be recognized as a valid opening delimiter

#### Scenario: Closing delimiter format

**Given** a foldable block
**When** a line contains only `:::` (optionally preceded by whitespace)
**Then** it MUST be recognized as the closing delimiter
**And** the block MUST end at that line

#### Scenario: Unclosed block handling

**Given** a foldable block without a closing delimiter
**When** the file ends or another block starts
**Then** the block MUST be implicitly closed at that point

---

### Requirement: Error Handling

The markdown parser MUST handle malformed foldable blocks gracefully.

#### Scenario: Unknown directive name

**Given** a block with unknown type: `:::unknown Content :::`
**When** the block is parsed
**Then** it SHOULD either:
  - Render as a generic foldable block, OR
  - Render as plain text with delimiters visible

#### Scenario: Empty block content

**Given** a foldable block with no content: `:::tip\n:::`
**When** the block is rendered
**Then** it MUST render an empty block with the title (if provided)

#### Scenario: Malformed attributes

**Given** a block with malformed attributes: `{title=unclosed`
**When** the block is parsed
**Then** it SHOULD treat the text as part of the title or fall back to defaults

#### Scenario: Mismatched quotes in attributes

**Given** a block with mismatched quotes: `{title="mixed'}`
**When** the block is parsed
**Then** it SHOULD fall back to defaults or use proper escaping

---

### Requirement: Backward Compatibility

The new directive block syntax MUST NOT break existing markdown content.

#### Scenario: Existing markdown remains valid

**Given** any existing course content file
**When** it does not contain `:::` foldable blocks
**Then** it MUST render exactly as before
**And** no changes to existing content are required

#### Scenario: Plain triple colons are not blocks

**Given** markdown content with `:::` used as a horizontal rule or separator
**When** it's not followed by a valid directive name
**Then** it SHOULD NOT be parsed as a foldable block

---

### Requirement: Progressive Hint Support

The specification MUST support creating multiple levels of progressive hints.

#### Scenario: Multiple hint blocks in sequence

**Given** a problem description
**When** author writes multiple hint blocks:
```markdown
:::tip{title="Hint 1" state="collapsed"}
First hint
:::

:::tip{title="Hint 2" state="collapsed"}
Second hint
:::

:::answer{title="Answer" state="collapsed"}
The solution
:::
```
**Then** each block MUST be rendered independently
**And** students can expand each hint progressively

---

### Requirement: Documentation Updates

The project documentation MUST be updated to include directive block syntax.

#### Scenario: Format specification updated

**Given** the [format-specification.md](../../../docs/format-specification.md) file
**When** the spec is adopted
**Then** it MUST include:
  - Directive block syntax description
  - All four block types and their defaults
  - Attribute syntax (title, state, class shortcuts)
  - Label syntax
  - Usage examples

#### Scenario: Authoring guide updated

**Given** the [course-authoring-guide.md](../../../docs/course-authoring-guide.md) file
**When** the spec is adopted
**Then** it MUST include:
  - When to use each block type
  - Progressive hint patterns
  - Best practices for hiding spoilers
  - Examples of good usage

---

### Requirement: Platform Rendering Support

Platforms rendering course content MUST support directive block rendering.

#### Scenario: Fallback for unsupported platforms

**Given** a platform that doesn't support directive blocks
**When** content contains `:::` blocks
**Then** the platform SHOULD:
  - Render as styled blockquotes with data attributes, OR
  - Render as plain text with visible delimiters
**And** the content MUST remain readable

#### Scenario: Interactive expand/collapse

**Given** a platform with full support
**When** a foldable block is rendered
**Then** it MUST provide:
  - Visual indication of collapsed/expanded state
  - Click or tap interaction to toggle state
  - Smooth animation for state transitions (optional)

---

### Requirement: Attribute Precedence

When multiple sources specify state or title, a clear precedence MUST be followed.

#### Scenario: State attribute takes precedence over class

**Given** a block with both `{state="collapsed"}` and `{.expanded}`
**When** the block is parsed
**Then** the `state` attribute MUST take precedence

#### Scenario: Class shortcut for state

**Given** a block with `{.expanded}` and no state attribute
**When** the block is parsed
**Then** the state MUST be `expanded`

#### Scenario: Title attribute takes precedence

**Given** a block with `{title="Custom"}`
**When** the block is rendered
**Then** "Custom" MUST be used instead of type default
