# Design: Chapter Unlock Condition Markdown Specification

## Overview
This document specifies the markdown frontmatter format for chapter unlock conditions, following the pattern established for problem unlock conditions.

## Markdown Field Specification

### Chapter Frontmatter with Unlock Conditions

```yaml
---
title: "Advanced Loops"
order: 2
unlock_conditions:
  type: prerequisite          # Required: unlock condition type
  prerequisites:              # Optional: list of prerequisite chapter orders
    - 1
    - 3
  unlock_date: "2025-03-01T00:00:00Z"  # Optional: ISO 8601 datetime
---

Chapter content here...
```

## Field Definitions

### unlock_conditions (optional)
Parent object containing all unlock condition settings. If omitted, chapter has no unlock conditions (default: unlocked).

#### unlock_conditions.type (required if unlock_conditions exists)
The unlock condition type. Maps to `ChapterUnlockCondition.unlock_condition_type`.

| Value | Description | Required Fields |
|-------|-------------|-----------------|
| `prerequisite` | Only check prerequisite chapters | `prerequisites` |
| `date` | Only check unlock date | `unlock_date` |
| `all` | Check both prerequisites and date | `prerequisites`, `unlock_date` |
| `none` | No conditions (unlocked) | None |

**Validation**: Must be one of the four values above. Default is `none`.

#### unlock_conditions.prerequisites (conditional)
List of chapter order numbers that must be completed before this chapter unlocks. Maps to `ChapterUnlockCondition.prerequisite_chapters` ManyToManyField.

**Type**: List of integers
**Required when**: `type` is `prerequisite` or `all`
**Validation rules**:
- Each value must be a positive integer
- Referenced chapters must exist in the same course (validated during import)
- Chapter cannot reference itself (validated during import)
- Circular dependencies are detected and rejected (validated at model level)

**Example**:
```yaml
prerequisites:
  - 1    # Chapter with order=1
  - 2    # Chapter with order=2
```

#### unlock_conditions.unlock_date (conditional)
ISO 8601 datetime string before which the chapter remains locked. Maps to `ChapterUnlockCondition.unlock_date`.

**Type**: String (ISO 8601 datetime)
**Required when**: `type` is `date` or `all`
**Format examples**:
- `"2025-03-01T00:00:00Z"` (UTC timezone)
- `"2025-03-01T08:00:00+08:00"` (With timezone offset)
- `"2025-03-01 00:00:00"` (Simple format, parsed as UTC)

**Validation**: Must be a valid datetime string parseable by `dateutil.parser.isoparse`.

## Examples

### Example 1: Single Prerequisite
```yaml
---
title: "Functions"
order: 2
unlock_conditions:
  type: prerequisite
  prerequisites:
    - 1
---
```
**Behavior**: Chapter unlocks only after completing Chapter 1.

### Example 2: Multiple Prerequisites
```yaml
---
title: "Object-Oriented Programming"
order: 4
unlock_conditions:
  type: all
  prerequisites:
    - 1
    - 2
    - 3
---
```
**Behavior**: Chapter unlocks only after completing Chapters 1, 2, AND 3.

### Example 3: Date-Based Unlock
```yaml
---
title: "Spring Semester Content"
order: 5
unlock_conditions:
  type: date
  unlock_date: "2025-03-01T00:00:00Z"
---
```
**Behavior**: Chapter unlocks on March 1, 2025, regardless of prerequisite completion.

### Example 4: Combined Prerequisites and Date
```yaml
---
title: "Advanced Topics"
order: 6
unlock_conditions:
  type: all
  prerequisites:
    - 5
  unlock_date: "2025-03-01T00:00:00Z"
---
```
**Behavior**: Chapter unlocks only after BOTH completing Chapter 5 AND reaching March 1, 2025.

### Example 5: No Unlock Conditions (Default)
```yaml
---
title: "Introduction"
order: 0
---
```
**Behavior**: Chapter is immediately accessible to all enrolled students (no `ChapterUnlockCondition` record created).

## Comparison with Problem Unlock Conditions

| Aspect | Problem Unlock | Chapter Unlock |
|--------|---------------|----------------|
| Prerequisite reference | Filenames (e.g., `problem-01.md`) | Chapter orders (integers) |
| Validation | File existence check | Chapter order existence check |
| Self-reference prevention | Title comparison | Order number comparison |

## Implementation Notes

### Parser Validation
The `MarkdownFrontmatterParser.validate_chapter_unlock_conditions()` method will validate:
1. `unlock_conditions` is a dictionary if present
2. `type` is one of the four valid values
3. Required fields are present based on `type`
4. `prerequisites` is a list of integers (if present)
5. `unlock_date` is a valid ISO 8601 datetime string (if present)

### Importer Logic
The `CourseImporter` will handle chapter unlock conditions in two phases:
1. **Phase 1**: Import all chapters (basic info only, skip unlock_conditions)
2. **Phase 2**: Import all chapter unlock conditions (after all chapters exist)

This mirrors the existing problem unlock condition import pattern.

### Error Handling
- **Invalid prerequisite order**: Log warning, skip that prerequisite, continue with others
- **Non-existent chapter order**: Log warning, skip that prerequisite
- **Self-reference**: Log error, skip unlock condition creation
- **Invalid datetime**: Raise `ValueError`, fail chapter import

## Backward Compatibility
Chapter files without `unlock_conditions` field remain unlocked (no `ChapterUnlockCondition` record created). This ensures existing course repositories continue to work without modification.
