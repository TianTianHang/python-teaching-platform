# Design: Markdown Foldable Blocks

## Overview

This document describes the technical design for adding foldable markdown blocks to the course content format. The design follows the remark-directive specification with HTML-like attribute syntax.

## Syntax Specification

### Directive Format

Foldable blocks use the remark-directive container syntax:

```
:::name[label]{attributes}
content
:::
```

### Components

1. **Opening Delimiter**: `:::` (three colons)
2. **Directive Name**: One of `tip`, `warning`, `answer`, `fold`
3. **Label** (optional): `[label-content]` for references
4. **Attributes** (optional): `{key="value"}` configuration
5. **Content**: Any valid markdown content
6. **Closing Delimiter**: `:::`

### Grammar

```
foldable_block ::= OPENING LABEL? WHITESPACE? NEWLINE
                  content*
                  CLOSING NEWLINE?

OPENING     ::= ":::" NAME
NAME        ::= "tip" | "warning" | "answer" | "fold"
LABEL       ::= "[" any_text_except_bracket "]"
ATTRIBUTES  ::= "{" attribute_list "}"
attribute_list ::= attribute (WHITESPACE attribute)*
attribute    ::= key "=" value | class_shortcut
key         ::= "title" | "state" | "id" | "class"
value       ::= quoted_string | unquoted_string
class_shortcut ::= "." classname
WHITESPACE  ::= " " | "\t"
CONTENT     ::= any markdown content except ":::" at line start
CLOSING     ::= ":::"
```

### Attribute Syntax

The `{attributes}` part follows HTML-like attribute syntax:

| Syntax Pattern | Meaning | Example |
|----------------|----------|---------|
| `{title="Title"}` | Title with double quotes | `{title="My Title"}` |
| `{title='Title'}` | Title with single quotes | `{title='My Title'}` |
| `{state=expanded}` | State without quotes | `{state=expanded}` |
| `{state="expanded"}` | State with quotes | `{state="expanded"}` |
| `{.expanded}` | Class shortcut for state | `{.expanded}` |
| `{.collapsed}` | Class shortcut for collapsed | `{.collapsed}` |
| `{.my-class}` | Custom CSS class | `{.my-class}` |
| Multiple attributes | Space-separated | `{state="expanded" title="Title"}` |
| Mixed styles | Unquoted + class shortcut | `{state=expanded .my-class}` |

### Default States

| Type   | Default State | Rationale                            |
|--------|---------------|--------------------------------------|
| tip    | expanded      | Tips are helpful, show by default    |
| warning| expanded      | Warnings are important, show by default |
| answer | collapsed     | Answers are spoilers, hide by default |
| fold   | collapsed     | Generic foldable, hide by default    |

## Block Type Semantics

### tip

- **Purpose**: General hints, supplementary information, clarifications
- **Default State**: expanded
- **Default Title**: "提示" (Hint) or localized equivalent
- **Visual Style**: Info-blue or neutral color
- **Icon**: Lightbulb or info icon

### warning

- **Purpose**: Important warnings, caveats, common pitfalls
- **Default State**: expanded
- **Default Title**: "警告" (Warning) or localized equivalent
- **Visual Style**: Yellow or orange warning color
- **Icon**: Exclamation mark or warning triangle

### answer

- **Purpose**: Solutions, answers to problems, code solutions
- **Default State**: collapsed
- **Default Title**: "答案" (Answer) or localized equivalent
- **Visual Style**: Green or neutral color
- **Icon**: Checkmark or eye icon

### fold

- **Purpose**: Generic collapsible content, advanced details, optional reading
- **Default State**: collapsed
- **Default Title**: "展开" (Expand) or localized equivalent
- **Visual Style**: Neutral gray
- **Icon**: Chevron or arrow

## Attribute Behavior

### Title Attribute

- **Syntax**: `{title="Custom Title"}` or `{title='Custom Title'}`
- **Default**: Type-specific default (see above)
- **Required**: No
- **Behavior**: Overrides default title when provided

### State Attribute

- **Syntax**: `{state=expanded}` or `{state="expanded"}` or `{state=collapsed}`
- **Valid Values**: `expanded`, `collapsed`
- **Required**: No
- **Behavior**: Overrides type's default state
- **Class Shortcut**: `{.expanded}` is equivalent to `{class="expanded"}` which sets state to expanded

### Label

- **Syntax**: `[ref-id]` or `[any text]`
- **Purpose**: Cross-referencing, identification
- **Required**: No
- **Behavior**: Stored as metadata, not displayed in rendered output

## Parsing Rules

### Attribute Parsing Order

1. Parse opening delimiter and directive name
2. Parse optional label: `[` ... `]`
3. Parse optional attributes: `{` key=value* `}`
4. Parse newline (content separator)
5. Parse content until closing delimiter

### State Resolution

1. If `state` attribute is present, use it
2. Else if `class` attribute contains `expanded` or `collapsed`, use it
3. Else if class shortcut `.expanded` or `.collapsed` is present, use it
4. Else use type's default state

### Title Resolution

1. If `title` attribute is present, use it
2. Else use type-specific default title
3. Else use empty string

## Content Parsing Rules

### Nested Blocks

**Decision**: Nested foldable blocks are NOT supported in initial version.

**Rationale**:
- Simpler parsing implementation
- Better UX (deep nesting is confusing)
- Can be added later if needed

**Behavior**: If `:::` is detected inside a foldable block, treat it as literal text, not a nested block.

### Code Blocks Inside Foldable

Standard markdown code blocks ARE supported inside foldable blocks:

```markdown
:::tip{title="Python Example"}
Here's how to use list comprehension:

```python
squares = [x**2 for x in range(5)]
```
:::
```

### Other Markdown Inside Foldable

All standard markdown is supported:
- Headers (H1-H6)
- Lists (ordered/unordered)
- Links and images
- Inline code
- Other custom blocks (like `python-exec`)

## Error Handling

### Malformed Blocks

The following cases should be handled gracefully:

1. **Unclosed block**: Missing closing `:::`
   - Behavior: Close at end of file or next block opening

2. **Unknown directive name**: `:::unknown Type`
   - Behavior: Render as plain text or generic block

3. **Invalid state**: `{state=invalid}`
   - Behavior: Use default state, log warning

4. **Empty content**: `:::tip\n:::`
   - Behavior: Render empty block with title only

5. **Malformed attributes**: `{title=unclosed`
   - Behavior: Attempt to parse, fall back to defaults if invalid

6. **Mismatched quotes**: `{title="mixed'}`
   - Behavior: Use proper quote escaping or fall back to defaults

## Examples

### Basic Examples

```markdown
:::tip{title="提示"}
This is a tip with custom title
:::

:::warning
This uses default title
:::

:::answer{state="expanded"}
Answer shown by default
:::

:::fold{title="Advanced" state="collapsed"}
Advanced content hidden by default
:::
```

### With All Components

```markdown
:::tip[ref-1]{title="Custom Title" state="expanded" .highlight}
Content that can be referenced with ref-1
:::
```

### Class Shortcuts

```markdown
:::tip{.expanded}
Equivalent to {state="expanded"}
:::

:::fold{.collapsed .advanced}
Collapsed with custom class
:::
```

## Platform Implementation Notes

### Markdown Parser

This spec defines the CONTENT format. Platform implementation requires:

1. **Remark Directive Plugin**: Parse `:::` directive blocks into custom AST nodes
2. **Attribute Parser**: Parse HTML-like attributes (key=value pairs)
3. **Rehype Component**: Convert AST nodes to HTML with collapsible behavior
4. **CSS Styling**: Style different block types appropriately
5. **JavaScript**: Handle expand/collapse interactions

### AST Structure Example

```javascript
{
  type: 'foldableDirective',
  name: 'tip',
  label: 'ref-1',
  attributes: {
    title: 'Custom Title',
    state: 'expanded',
    class: ['highlight']
  },
  content: [...children]
}
```

### Fallback Rendering

For platforms that don't support this syntax yet:

1. **Option A**: Render as blockquotes with type annotation
   ```html
   <blockquote class="foldable-tip" data-type="tip" data-state="expanded">
     <strong>Tip:</strong> Content
   </blockquote>
   ```

2. **Option B**: Render as plain text with visible delimiters

### Migration Path

1. **Phase 1**: Define spec (this proposal)
2. **Phase 2**: Update documentation
3. **Phase 3**: Platform implements rendering
4. **Phase 4**: Authors start using new syntax

## Compatibility

### Backward Compatibility

- Existing markdown content remains valid
- No changes to existing syntax
- New syntax is additive only

### Forward Compatibility

- New directive names can be added without breaking existing content
- New attributes can be added in future
- Unknown attributes should have graceful fallback

## Complete Example

```markdown
---
title: "List Operations Practice"
order: 1
---

## Find the Maximum Value

Write a function to find the maximum value in a list.

:::tip{title="Hint 1" state="collapsed"}
Python provides a built-in function for this.
:::

:::tip{title="Hint 2" state="collapsed"}
The function is three letters: max
:::

:::answer{title="Answer" state="collapsed"}
```python
def find_max(numbers):
    return max(numbers)
```
:::

:::warning{title="Important"}
Make sure the list is not empty, otherwise it will raise an exception.
:::
```
