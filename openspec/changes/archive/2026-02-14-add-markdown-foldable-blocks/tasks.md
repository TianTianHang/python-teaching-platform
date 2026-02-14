# Implementation Tasks

## 1. Install Dependencies

- [x] Add `remark-directive` to `frontend/web-student/package.json`
- [x] Add `unist-util-visit` to `frontend/web-student/package.json`
- [x] Run `pnpm install` to install dependencies

## 2. Create Attribute Parser Helper

- [x] Create `frontend/web-student/app/lib/parseDirectiveAttributes.ts`
- [x] Parse directive attributes object to extract `title` and `state`
- [x] Handle various attribute formats: `{title="Title"}`, `{title='Title'}`, `{title=Title}`
- [x] Handle state attributes: `{state=expanded}`, `{state=collapsed}`, `{.expanded}`, `{.collapsed}`
- [x] Handle mixed attribute styles: `{state=expanded .my-class title="Title"}`
- [x] Return parsed attributes with defaults

## 3. Create Custom Remark Plugin

- [x] Create `frontend/web-student/app/lib/remarkFoldableBlock.ts`
- [x] Implement AST visitor using `unist-util-visit`
- [x] Transform `containerDirective` nodes to `foldableBlock` nodes
- [x] Use `parseDirectiveAttributes` to extract title and state from directive attributes
- [x] Handle optional label parsing from directive node
- [x] Add proper TypeScript types for plugin
- [x] Support all four types: `fold`, `answer`, `warning`, `tip`

## 4. Create Type Definitions

- [x] Create `frontend/web-student/app/types/mdast.d.ts`
- [x] Extend MDAST ContentMap for `foldableBlock` type
- [x] Update `frontend/web-student/app/types/react-markdown.d.ts`
- [x] Add `foldableBlock` component handler type

## 5. Create FoldableBlock Component

- [x] Create `frontend/web-student/app/components/FoldableBlock.tsx`
- [x] Implement component with MUI Accordion/AccordionSummary/AccordionDetails
- [x] Add type-specific styling (icons, colors, default expanded state)
- [x] Support SSR (no browser-only APIs)
- [x] Add TypeScript types for props:
  - `type: 'fold' | 'answer' | 'warning' | 'tip'`
  - `title?: string`
  - `defaultExpanded?: boolean`
  - `children: React.ReactNode`
- [x] Apply type-specific defaults:
  - `fold`: ChevronRight icon, gray accent, collapsed by default
  - `answer`: VisibilityOff icon, blue accent, collapsed by default
  - `warning`: Warning icon, orange accent, expanded by default
  - `tip`: Lightbulb icon, green accent, expanded by default
- [x] Enhanced styling with modern design patterns

## 6. Integrate with MarkdownRenderer

- [x] Update `frontend/web-student/app/components/MarkdownRenderer.tsx`
- [x] Import and register `remarkFoldableBlock` plugin
- [x] Import and register `remarkDirective` plugin (must come before custom plugin)
- [x] Add `foldableBlock` component handler to render `FoldableBlock` component
- [x] Ensure existing `python-exec` code block functionality still works

## 7. Testing

- [x] Type check: `pnpm run type-check`
- [x] Dev server: `pnpm run dev`
- [x] Test basic foldable blocks without attributes: `:::tip`
- [x] Test foldable blocks with title attribute: `:::tip{title="Title"}`
- [x] Test foldable blocks with state attribute: `:::tip{state=collapsed}`
- [x] Test foldable blocks with both attributes: `:::tip{title="Title" state=expanded}`
- [x] Test class shortcut syntax: `:::fold{.expanded}`
- [x] Test label syntax: `:::answer[ref-id]{title="Answer"}`
- [x] Test all four block types (fold, answer, warning, tip)
- [x] Test nested markdown content inside foldable blocks
- [x] Test multiple attributes: `{state=expanded .my-class title="Title"}`
- [x] Verify SSR compatibility by checking server-rendered HTML
- [x] Test interaction (expand/collapse) works correctly
- [x] Verify no JavaScript errors in console
- [x] Confirm nested foldable blocks are NOT supported (explicitly test this limitation)

## 8. Style Optimization

- [x] Enhanced visual design with modern styling
- [x] Added gradient backgrounds for different block types
- [x] Improved icons with accent circles
- [x] Added hover effects and transitions
- [x] Better spacing and typography
- [x] Type-specific color schemes