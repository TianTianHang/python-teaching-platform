# Tasks: Add Markdown Foldable Blocks

## Documentation Tasks

- [x] Update [docs/format-specification.md](../../docs/format-specification.md) with directive block syntax
  - [x] Add new section "可折叠块语法" under Markdown 规范
  - [x] Document the new directive syntax: `:::name[label]{attributes}`
  - [x] Include all four block types: `tip`, `warning`, `answer`, `fold`
  - [x] Document attribute syntax: `{title="Title"}`, `{state=expanded}`, `{.expanded}`, etc.
  - [x] Document label syntax: `[ref-id]` for references
  - [x] Provide syntax examples for each type and combination
  - [x] Document default states for each block type
  - [x] Attribute precedence rules

- [x] Update [docs/course-authoring-guide.md](../../docs/course-authoring-guide.md) with usage guidelines
  - [x] Add "可折叠块最佳实践" section
  - [x] Provide progressive hint pattern examples using new syntax
  - [x] Document when to use each block type
  - [x] Include examples for common use cases (hints, answers, warnings)
  - [x] Show attribute syntax best practices
  - [x] Document label usage for cross-references

## Content Migration (Optional)

- [ ] Review existing course content for opportunities to use directive blocks
  - Identify inline hints that could be in `:::tip{title="Hint" state="collapsed"}`
  - Identify answer sections that could be in `:::answer{title="Answer" state="collapsed"}`
  - Identify warning text that could be in `:::warning{title="Warning"}`
  - Document findings for future content updates

## Validation

- [x] Validate proposal with `openspec validate add-markdown-foldable-blocks --strict --no-interactive`
- [x] Verify all requirements have at least one scenario
- [x] Check that proposal.md, design.md, tasks.md, and spec deltas are complete
- [x] Ensure spec deltas use correct format (ADDED/MODIFIED/REMOVED Requirements)

## Post-Approval Tasks (Implementation Phase)

### Platform Implementation (Backend-dependent)

The following tasks are for the Django backend/platform team and are NOT part of this content repo change:

- [ ] Implement remark-directive plugin to parse `:::` directive blocks
- [ ] Create attribute parser for HTML-like syntax
- [ ] Create rehype component to render foldable blocks
- [ ] Add CSS styles for each block type
- [ ] Implement JavaScript expand/collapse interactions
- [ ] Add tests for directive block parsing
- [ ] Update platform documentation
- [ ] Handle fallback rendering for unsupported platforms

### Content Examples

- [ ] Create example course content using directive blocks
  - Add progressive hint example to a practice problem using new syntax
  - Add warning block to a chapter with potential pitfalls
  - Document the example for reference
