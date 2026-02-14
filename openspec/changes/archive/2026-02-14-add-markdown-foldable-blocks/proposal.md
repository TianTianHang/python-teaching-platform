# Proposal: Add Markdown Foldable Blocks

## Summary

Add custom Markdown foldable block syntax specification to support creating collapsible hints, warnings, answers, and other blocks in course content. The syntax uses remark-directive container format with `:::name[label]{attributes}` delimiters. Authors can wrap auxiliary content (hints, answers, warnings) in collapsible blocks with configurable default states and titles.

## Syntax Overview

### Directive Syntax Format

The foldable blocks use remark-directive container syntax:

```
:::name[label]{attributes}
content
:::
```

Where:
- `name` is the directive type (`fold`, `answer`, `warning`, `tip`)
- `[label]` is optional and can contain text/markdown (used for references)
- `{attributes}` contains the block configuration (`title`, `state`, etc.)

### Basic Syntax (uses default state)

```markdown
:::tip{title="Optional Title"}
Tip content here
:::

:::warning{title="Important Warning"}
Warning content here
:::

:::answer{title="Answer"}
The answer to the question
:::

:::fold{title="Optional Title"}
Any content that should be collapsible
:::
```

### With Explicit State Attribute

```markdown
:::tip{title="Optional Title" state="expanded"}
This tip is explicitly set to expanded (same as default)
:::

:::tip{title="Optional Title" state="collapsed"}
This tip is explicitly set to collapsed (overrides default)
:::

:::answer{title="Answer" state="expanded"}
This answer is explicitly shown by default
:::

:::fold{title="Optional Title" state="expanded"}
This foldable is explicitly expanded by default
:::
```

### Attribute Syntax Rules

The `{attributes}` part follows HTML-like attribute syntax:
- `{title="Title"}` or `{title='Title'}` - Title with double or single quotes
- `{state=expanded}` or `{state="expanded"}` - State attribute (quotes optional)
- `{.expanded}` or `{.collapsed}` - Class shortcut for state (equivalent to `{class="expanded"}`)
- `{state="expanded" title="My Title"}` - Multiple attributes
- `{state=expanded .my-class}` - Mixed attribute styles

### Block Without Title (uses default)

```markdown
:::tip
Tip content here (uses default title)
:::

:::fold{state=expanded}
Content expanded by default with default title
:::
```

### With Optional Label (for references)

```markdown
:::tip[ref-id]{title="Title with reference"}
Content that can be referenced elsewhere
:::
```

## Motivation

Current course content displays hints, answers, and warnings directly in the main text, which causes:

1. **Spoiler problem**: Answers are directly visible before students have time to think
2. **Content clutter**: Detailed hints take up significant space, affecting reading experience
3. **Lack of progressive guidance**: Cannot achieve "small hint → detailed hint → answer" progressive hints
4. **Warnings ignored**: Important warning information gets lost in main content

By introducing foldable blocks:
- **Answers hidden by default**: Students think first, then view answers when needed
- **Progressive hints**: Multiple levels of hints that students expand on demand
- **Highlight important info**: Warnings and notes display independently, more attention-grabbing
- **Keep content clean**: Auxiliary content doesn't occupy primary reading space

## Why Directive Syntax

The new directive-based syntax (`:::name[label]{attributes}`) was chosen because:

1. **Standards-compliant**: Follows remark-directive specification, a widely-adopted standard
2. **Extensible**: Attribute-based approach allows future extensions without breaking changes
3. **Familiar**: HTML-like attribute syntax is familiar to most authors
4. **Flexible**: Labels enable cross-referencing, attributes enable rich configuration
5. **Tooling support**: Better parser ecosystem support for remark-directive format

## What Changes

- **NEW**: Four directive block types: `tip`, `warning`, `answer`, `fold`
- **NEW**: HTML-like attribute syntax in `{attributes}` section
- **NEW**: Optional `[label]` for references
- **NEW**: State attributes: `state="expanded"`, `state="collapsed"`, or class shortcuts `.expanded`, `.collapsed`
- **NEW**: Title attribute: `title="Custom Title"`
- **COMPATIBLE**: Existing markdown content remains valid

## Block Types and Defaults

| Type   | Default State | Purpose                      |
|--------|---------------|------------------------------|
| `tip`    | `expanded`      | General hints and supplementary information |
| `warning` | `expanded`      | Important warnings and caveats |
| `answer` | `collapsed`     | Solutions and answers to problems |
| `fold`   | `collapsed`     | Generic collapsible content |

## Usage Examples

### 1. Progressive Hints

```markdown
## Problem: Find the maximum value in a list

:::tip{title="Hint 1" state="collapsed"}
Python provides a built-in function to quickly find the maximum value.
:::

:::tip{title="Hint 2" state="collapsed"}
The function name is three letters starting with 'm'.
:::

:::answer{title="Answer" state="collapsed"}
Use the `max()` function: `max(numbers)`
:::
```

### 2. Code Warnings

```markdown
## Floating Point Comparison

```python
# Not recommended
if 0.1 + 0.2 == 0.3:
    print("equal")
```

:::warning{title="Floating Point Precision Issue"}
Due to floating point precision limits, `0.1 + 0.2` actually equals `0.30000000000000004`, not `0.3`. Direct comparison of floating point numbers may give incorrect results.
:::
```

### 3. Supplementary Knowledge

```markdown
## List Comprehensions

```python
squares = [x**2 for x in range(5)]
```

:::fold{title="Advanced Usage"}
List comprehensions can also include conditions:

```python
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

This generates a list of squares for even numbers from 0-10.
:::
```

## Impact

### Content Format Changes

- New directive-based block syntax: `:::name[label]{attributes}`
- Four block types with configurable attributes
- HTML-like attribute syntax for configuration
- Compatible with existing Markdown

### Rendering Platform Changes

- Need to implement remark-directive plugin for parsing
- Need to implement frontend collapsible components
- Need to handle attribute parsing (title, state, class)

### Documentation Updates

Required updates:
- [format-specification.md](../../docs/format-specification.md) - Add foldable block syntax
- [course-authoring-guide.md](../../docs/course-authoring-guide.md) - Add usage examples and best practices

## Alternatives Considered

### HTML Details/Summary

```markdown
<details>
<summary>Click to view hint</summary>
Hint content
</details>
```

**Pros**: Standard HTML, no custom parsing needed

**Cons**:
- Verbose syntax
- No default state control
- Requires manual HTML writing
- Limited style control

### Custom YAML Frontmatter

```yaml
---
hints:
  - level: 1
    content: "Hint 1"
  - level: 2
    content: "Hint 2"
---
```

**Cons**:
- Mixes content with metadata
- Not intuitive
- Hard to preview in context

### Previous Bracket Syntax

```markdown
:::tip[collapsed] Optional Title
Content
:::
```

**Cons**:
- Non-standard syntax
- Less extensible
- No support for additional attributes
- Harder to parse correctly

### Conclusion

Adopting directive syntax (`:::name[label]{attributes}`):
- Standards-compliant (remark-directive)
- More extensible for future enhancements
- HTML-like attributes familiar to authors
- Better tooling ecosystem support
- Clear separation of type, label, and attributes

## Open Questions

1. **Should nested blocks be supported?**
   - Example: `:::fold` containing another `:::tip`
   - Recommendation: Not supported in initial version, evaluate later based on demand

2. **Should more block types be added?**
   - Example: `info`, `error`, `success`, etc.
   - Recommendation: Initial version supports 4 base types only, extensible later

3. **What additional attributes should be supported?**
   - Example: `id`, `class`, `data-*` attributes
   - Recommendation: Start with `title` and `state`, extend as needed

4. **Platform implementation timeline?**
   - This spec defines content format only, actual rendering requires platform support
   - Recommendation: Spec first, platform implements progressively
