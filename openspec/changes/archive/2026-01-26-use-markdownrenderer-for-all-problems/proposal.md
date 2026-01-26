# Proposal: Use MarkdownRenderer for All Problem Content

## Summary

Update `ChoiceProblemCmp.tsx` and `FillBlankProblemCmp.tsx` components to use the existing `MarkdownRenderer` component for rendering `problem.content`, ensuring consistent markdown rendering across all problem types.

## Current State

The platform has inconsistent markdown rendering for problem content:

| Component | Current Implementation |
|-----------|----------------------|
| `Problem/index.tsx` | Uses `MarkdownRenderer` for `problem.content` |
| `ChoiceProblemCmp.tsx` | Renders `problem.content` as plain Typography (line 92) |
| `FillBlankProblemCmp.tsx` | Renders `problem.content` as plain Typography (line 141) |
| Algorithm Problem pages | Uses `MarkdownRenderer` |

This inconsistency means:
- Choice and fill-in-blank problems cannot use markdown formatting (headers, code blocks, links, tables, etc.)
- Authors must write different content formats for different problem types
- The JupyterLite interactive Python blocks (`python-exec`) are unavailable in choice/fill-blank problems

## Proposed Change

### Components to Modify

1. **`frontend/web-student/app/components/Problem/ChoiceProblemCmp.tsx`**
   - Replace `<Typography variant="h5">{problem.content}</Typography>` (line 91-93)
   - With `<MarkdownRenderer markdownContent={problem.content} />`
   - Keep the surrounding `Card`, `CardContent`, and metadata chips unchanged

2. **`frontend/web-student/app/components/Problem/FillBlankProblemCmp.tsx`**
   - Replace `<Typography variant="h5">{problem.content}</Typography>` (line 140-142)
   - With `<MarkdownRenderer markdownContent={problem.content} />`
   - Keep the `content_with_blanks` logic for interactive blank inputs unchanged
   - Keep the surrounding `Card`, `CardContent`, and metadata chips unchanged

### Expected Benefits

1. **Content Consistency**: All problem types support the same markdown formatting
2. **Rich Content**: Choice and fill-blank problems can now include:
   - Code blocks with syntax highlighting
   - Interactive JupyterLite notebooks (`python-exec` blocks)
   - Tables, lists, links, images
   - Styled text (bold, italic, headers)
3. **Maintainability**: Single source of truth for markdown rendering logic
4. **Author Experience**: Content authors can use markdown across all problem types

### Technical Details

**No API or backend changes required** - the backend already stores `content` as raw markdown.

**No breaking changes** - existing plain text content will render correctly through MarkdownRenderer (it handles plain text as-is).

**Dependencies**:
- `MarkdownRenderer` component already exists and is stable
- `JupyterLiteCodeBlock` component for `python-exec` blocks
- MUI theme integration already in place

## Affected Capabilities

This change spans the problem display capability but does not introduce new functionality - it aligns existing implementations with the established markdown rendering pattern.

## Alternatives Considered

1. **Create separate markdown components for each problem type**
   - Rejected: Duplicates logic, creates maintenance burden

2. **Keep current plain text rendering**
   - Rejected: Limits content quality, inconsistent with other problem types

3. **Create a unified problem content wrapper component**
   - Not pursued: Unnecessary abstraction - MarkdownRenderer is already the appropriate wrapper

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Styling conflicts between Typography and MarkdownRenderer | Low | Low | MarkdownRenderer uses MUI theme, should integrate seamlessly |
| Performance regression from markdown parsing | Low | Low | react-markdown is fast; choice/fill-blank problems typically have shorter content |
| Existing content relies on plain text formatting | Low | Low | MarkdownRenderer handles plain text correctly |

## Success Criteria

- [x] Choice problems render markdown-formatted content correctly
- [x] Fill-blank problems render markdown-formatted content correctly
- [x] No regressions in problem list display
- [x] `python-exec` blocks work in choice/fill-blank problems
- [x] Type checking passes (`pnpm run typecheck`)
