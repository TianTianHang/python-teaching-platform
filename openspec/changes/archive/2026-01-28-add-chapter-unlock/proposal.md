# Change: Add Chapter Unlock Conditions

## Why

Problems currently support `unlock_conditions` for controlling student access, but chapters do not. This limits course authors' ability to create structured learning paths where chapters unlock based on prerequisite completion or scheduled dates. Adding chapter unlock conditions enables:

1. **Sequential Learning**: Ensure students complete prerequisite chapters before advancing
2. **Scheduled Content**: Release chapters on specific dates (e.g., weekly course releases)
3. **Flexible Progression**: Combine prerequisites with dates for hybrid unlocking strategies

## What Changes

- **Add chapter unlock conditions**: Extend chapter frontmatter to support `unlock_conditions` field
- **Four unlock types**: `none` (default), `prerequisite`, `date`, and `all`
- **Prerequisite chapters**: Reference by chapter `order` (integer) instead of filenames
- **Date-based unlocking**: ISO 8601 datetime format for scheduled access
- **Documentation updates**: Update format specification, templates, and guides

**Key differences from problem unlock conditions:**
- Prerequisites reference chapter `order` (integers) rather than problem filenames
- No `minimum_percentage` field (chapters are all-or-nothing)

## Impact

- Affected specs: `chapter-format` (new spec capability)
- Affected documentation:
  - [docs/format-specification.md](../../docs/format-specification.md) - Add chapter unlock section
  - [courses/_templates/chapters/chapter-00-template.md](../../courses/_templates/chapters/chapter-00-template.md) - Update template
  - [openspec/project.md](../project.md) - Update conventions
- Backward compatible: Chapters without `unlock_conditions` remain unlocked (default behavior)
