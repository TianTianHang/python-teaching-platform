# Design: Markdown Foldable Blocks

## Overview

This feature adds custom markdown syntax for collapsible content blocks using remark-directive plugin with proper directive syntax.

## Syntax

### Directive Syntax Format

The foldable blocks use the remark-directive container syntax:
```
:::name[label]{attributes}
content
:::
```

Where:
- `name` is the directive type (fold, answer, warning, tip)
- `[label]` is optional and can contain text/markdown (used for references)
- `{attributes}` contains the block configuration (title, state, etc.)

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
- `{.expanded}` or `{.collapsed}` - Class shortcut for state (equivalent to `{class=expanded}`)
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

## Implementation Approach

### Chosen Approach: Custom Remark Plugin

Using `remark-directive` with a custom remark plugin that transforms directive nodes into custom node types.

**Rationale**:
- Follows unified/remark plugin development best practices
- Uses standard remark-directive syntax compatible with other tools
- Type-safe through MDAST type augmentation
- Clear separation of concerns (plugin transforms, component renders)
- Reusable plugin architecture
- No manual markdown string conversion needed
- Better performance (no redundant parsing)

**Dependencies**:
- `remark-directive` - parses generic directive syntax `:::name[label]{attributes}`
- `unist-util-visit` - AST traversal utilities

**Architecture**:
```
Markdown Source
       ↓
remark-directive (解析 :::name[label]{attributes} 语法为 containerDirective 节点)
       ↓
remarkFoldableBlock (自定义插件，转换为 foldableBlock 节点，解析 {attributes})
       ↓
ReactMarkdown components.foldableBlock (渲染 FoldableBlock 组件)
```

### Plugin Transformation Flow

1. `remark-directive` parses `:::name[label]{attributes}` into a containerDirective node with:
   - `name`: the directive name (fold, answer, warning, tip)
   - `attributes`: object containing parsed attributes (title, state, etc.)
   - `children`: the content inside the container

2. `remarkFoldableBlock` plugin visits containerDirective nodes and transforms them:
   - Extract `name` to determine block type
   - Parse `attributes` object to get title and state
   - Extract content from children
   - Transform into custom `foldableBlock` node with data attached

3. `FoldableBlock` component renders the transformed node with appropriate styling

### Attribute Parsing

```typescript
interface FoldableBlockAttributes {
  title?: string;
  state?: 'expanded' | 'collapsed';
  class?: string;  // For class shortcuts like {.expanded}
  // Other custom attributes...
}

function parseAttributes(attributes: Record<string, string | undefined>): {
  title?: string;
  defaultExpanded?: boolean;
} {
  const state = attributes.state || attributes.class;
  const defaultExpanded = state === 'expanded' || (!state && ['warning', 'tip'].includes(type));

  return {
    title: attributes.title,
    defaultExpanded,
  };
}
```

### Component Structure

```typescript
// FoldableBlock.tsx
interface FoldableBlockProps {
  type: 'fold' | 'answer' | 'warning' | 'tip';
  title?: string;
  defaultExpanded?: boolean;  // Explicit state from state attribute
  children: React.ReactNode;
}
```

### Type Defaults

| Type | Icon | Color | Default State (when not specified) |
|------|------|-------|---------------|
| fold | ChevronRight | Gray | Collapsed |
| answer | VisibilityOff | Blue | Collapsed |
| warning | Warning | Orange | Expanded |
| tip | Lightbulb | Green | Expanded |

### State Resolution Logic

```typescript
function getDefaultExpanded(
  type: string,
  attributes: Record<string, string | undefined>
): boolean {
  const state = attributes.state || attributes.class;

  // Explicit state attribute takes precedence
  if (state === 'expanded') return true;
  if (state === 'collapsed') return false;

  // Use type default when not specified
  return ['warning', 'tip'].includes(type);
}
```

## SSR Considerations

- Component must work with React Router v7 SSR
- No browser-only APIs
- MUI Accordion should work server-side

## Limitations

- **No nested foldable blocks**: Foldable blocks cannot contain other foldable blocks
  - This simplifies the parsing and rendering logic
  - If a user attempts to nest foldable blocks, the inner block will be rendered as plain markdown

## Migration Path

No migration needed - additive change.
