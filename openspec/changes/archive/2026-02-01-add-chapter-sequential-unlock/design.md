# Design: Add Sequential Chapter Unlock to Python Intro Course

## Overview
This design document outlines the technical approach for adding sequential chapter unlock conditions to the Python Intro course.

## Current State
The Python Intro course (`courses/python-intro/`) contains 8 chapters:
1. `chapter-01-python-intro.md` (order: 1)
2. `chapter-02-variables-types.md` (order: 2)
3. `chapter-03-operators.md` (order: 3)
4. `chapter-04-conditionals.md` (order: 4)
5. `chapter-05-loops.md` (order: 5)
6. `chapter-06-lists.md` (order: 6)
7. `chapter-07-dictionaries.md` (order: 7)
8. `chapter-08-functions.md` (order: 8)

Currently, none of these chapters have `unlock_conditions` in their frontmatter.

## Target State
Each chapter (2-8) will have an `unlock_conditions` block that requires completion of the immediately preceding chapter:

```yaml
---
title: "变量与数据类型"
order: 2
unlock_conditions:
  type: "prerequisite"
  prerequisites: [1]
---
```

## Technical Approach

### 1. Unlock Condition Format
According to [format-specification.md](../../../docs/format-specification.md), chapter unlock conditions use:
- `type`: `"prerequisite"` - requires completion of specified chapters
- `prerequisites`: array of chapter `order` integers (not filenames)
- No `minimum_percentage` field - all-or-nothing completion

### 2. Chapter Unlock Chain
```
Chapter 1 (unlocked)
      ↓
Chapter 2 (requires Ch 1)
      ↓
Chapter 3 (requires Ch 2)
      ↓
Chapter 4 (requires Ch 3)
      ↓
Chapter 5 (requires Ch 4)
      ↓
Chapter 6 (requires Ch 5)
      ↓
Chapter 7 (requires Ch 6)
      ↓
Chapter 8 (requires Ch 7)
```

### 3. Implementation Details
Each chapter file requires a single frontmatter addition:

| File | Order | Prerequisites |
|------|-------|---------------|
| `chapter-01-python-intro.md` | 1 | (none - entry point) |
| `chapter-02-variables-types.md` | 2 | `[1]` |
| `chapter-03-operators.md` | 3 | `[2]` |
| `chapter-04-conditionals.md` | 4 | `[3]` |
| `chapter-05-loops.md` | 5 | `[4]` |
| `chapter-06-lists.md` | 6 | `[5]` |
| `chapter-07-dictionaries.md` | 7 | `[6]` |
| `chapter-08-functions.md` | 8 | `[7]` |

### 4. YAML Structure
The YAML frontmatter for each chapter will follow this pattern:

**Chapter 1 (no change - already unlocked):**
```yaml
---
title: "Python简介与环境搭建"
order: 1
---
```

**Chapters 2-8 (with unlock conditions):**
```yaml
---
title: "章节标题"
order: N
unlock_conditions:
  type: "prerequisite"
  prerequisites: [N-1]
---
```

### 5. Validation Requirements
- All `prerequisites` values must reference valid chapter `order` numbers
- String values must be properly quoted in YAML
- Array format must use brackets `[1]` not `- 1`
- The existing import process should validate these conditions

## Backward Compatibility
- Chapters without `unlock_conditions` remain unlocked (default behavior)
- Chapter 1 will not have `unlock_conditions` - it's the course entry point
- Existing chapter content is not modified

## Future Considerations
- If new chapters are added, they should include appropriate `unlock_conditions`
- The pattern can be applied to other courses that want sequential chapter progression
- Time-based unlocks (`type: "date"` or `type: "all"`) could be added later if needed

## Normative Requirements

### General Course Standard
This change establishes a normative requirement that new courses SHOULD use sequential chapter unlocks by default. This is captured in a separate spec capability `course-chapter-unlock` that defines:

1. **Default Pattern**: New courses should use sequential unlocks (N requires N-1)
2. **Template Update**: The chapter template should include a commented example
3. **Documentation**: The course authoring guide should recommend this pattern
4. **Exceptions**: Non-linear patterns require pedagogical justification

### Template Changes
The chapter template at `courses/_templates/chapter-00-template.md` will be updated to include:

```yaml
# unlock_conditions:
#   type: "prerequisite"
#   prerequisites: [previous_chapter_order]
```

### Documentation Updates
The course authoring guide at `docs/course-authoring-guide.md` will be updated to:
- Recommend sequential chapter unlocks as the default
- Provide examples of the `unlock_conditions` format
- Explain when non-linear patterns might be appropriate
