# Tasks: Use MarkdownRenderer for All Problem Content

## Implementation Tasks

### 1. Update ChoiceProblemCmp.tsx
**File**: `frontend/web-student/app/components/Problem/ChoiceProblemCmp.tsx`

- [x] Import `MarkdownRenderer` component
- [x] Replace `<Typography variant="h5">{problem.content}</Typography>` with `<MarkdownRenderer markdownContent={problem.content} />`
- [x] Verify no duplicate headers (`problem.content` already rendered by MarkdownRenderer's h1 styling)
- [x] Test that multiple choice options still display correctly below content

### 2. Update FillBlankProblemCmp.tsx
**File**: `frontend/web-student/app/components/Problem/FillBlankProblemCmp.tsx`

- [x] Import `MarkdownRenderer` component
- [x] Replace `<Typography variant="h5">{problem.content}</Typography>` with `<MarkdownRenderer markdownContent={problem.content} />`
- [x] Verify that `content_with_blanks` logic remains unchanged
- [x] Test that interactive blank inputs still render correctly

### 3. Type Checking
**File**: `frontend/web-student/app/components/Problem/`

- [x] Run `pnpm run typecheck` to verify no TypeScript errors
- [x] Ensure `MarkdownRenderer` props are correctly typed (`markdownContent: string`)

### 4. Visual Testing
**Validation**: Manual testing in browser

- [x] Test choice problem with markdown content (headers, code blocks, tables)
- [x] Test fill-blank problem with markdown content
- [x] Test `python-exec` blocks render JupyterLite notebooks in both problem types
- [x] Verify plain text content still renders correctly (backward compatibility)
- [x] Check dark/light theme styling consistency

### 5. Regression Testing
**Validation**: Ensure no breaks to existing functionality

- [x] Verify problem list page still displays all problem types correctly
- [x] Verify algorithm problem pages (already using MarkdownRenderer) are unaffected
- [x] Verify chapter content pages (already using MarkdownRenderer) are unaffected
- [x] Test problem navigation and routing

## Task Dependencies

```
1. Update ChoiceProblemCmp.tsx ──┐
                                 ├──> 3. Type Checking ──> 4. Visual Testing
2. Update FillBlankProblemCmp.tsx ─┘
                                 └──────────────────────────────> 5. Regression Testing
```

- Tasks 1 and 2 can be done in parallel
- Task 3 blocks task 4
- Task 5 runs after task 4

## Parallelizable Work

- **Task 1** (ChoiceProblemCmp.tsx) and **Task 2** (FillBlankProblemCmp.tsx) are independent and can be done simultaneously
