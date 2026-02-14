# Change: Add Markdown Foldable Blocks Support

## Why

The platform currently lacks a way to present collapsible content in markdown. This is useful for:
- **Hints**: Showing optional hints without cluttering the main content
- **Warnings**: Displaying important warnings that can be dismissed
- **Answers**: Hiding exercise answers to prevent spoilers
- **Fold**: Generic collapsible content for space optimization

## What Changes

- Add `remark-directive` plugin to parse remark directive syntax `:::name[label]{attributes}` for foldable blocks
- Create custom `remarkFoldableBlock` plugin to transform directive nodes into custom node types
- Add `unist-util-visit` for AST traversal
- Support four directive names: `fold`, `answer`, `warning`, `tip`
- Use `{attributes}` syntax for title and state (e.g., `{title="My Title" state="expanded"}`)
- Support attribute shortcuts: `{state=expanded}`, `{state=collapsed}`, `{.expanded}`, `{.collapsed}`
- Default states when not specified: `fold` (collapsed), `answer` (collapsed), `warning` (expanded), `tip` (expanded)
- Render collapsible blocks with Material-UI Accordion component
- Apply distinct styling for each block type with appropriate icons
- Support nested markdown content (lists, code, links) inside foldable blocks
- Create proper TypeScript type definitions for MDAST and ReactMarkdown
- **Limitations**: Nested foldable blocks (foldable within foldable) are NOT supported
- **BREAKING**: None (additive change)

## Syntax Examples

```markdown
:::tip{title="Optional Title"}
Tip content here
:::

:::warning{title="Important Warning" state="expanded"}
Warning content here
:::

:::answer{title="Answer"}
The answer to the question
:::

:::fold{title="Optional Title" state="collapsed"}
Any content that should be collapsible
:::

:::tip[Reference Label]{title="Title with reference"}
Content with reference label
:::
```

## Impact

- Affected specs:
  - **NEW**: `markdown-foldable-blocks` - New capability for foldable markdown content
- Affected code:
  - `frontend/web-student/app/components/MarkdownRenderer.tsx` - Add foldable block support
  - `frontend/web-student/app/components/` - Create new `FoldableBlock` component
  - `frontend/web-student/app/lib/` - Create remark plugin and attribute parser
  - `frontend/web-student/package.json` - Add `remark-directive` and `unist-util-visit`
