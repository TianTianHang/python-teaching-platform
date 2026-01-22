## Context

The Python Teaching Platform uses a declarative course management system where instructors maintain course content (courses, chapters, problems) in Git repositories as Markdown files with YAML frontmatter. The import service parses these files and populates the database.

Currently, the import system supports:
- **Algorithm problems**: Code execution with test cases
- **Choice problems**: Single/multiple choice questions

However, **fill-in-blank problems** are missing from the import pipeline despite having:
- A complete database model (`FillBlankProblem`) in `models.py:235-312`
- Frontend display and interaction components
- API endpoints for checking answers

This gap forces instructors to use the admin interface or API to create fill-in-blank problems manually, breaking the declarative workflow.

## Goals / Non-Goals

### Goals
- Enable instructors to define fill-in-blank problems in Markdown files with YAML frontmatter
- Support the three `blanks` field formats already defined in the model
- Validate fill-in-blank problem structure during import (fail fast with clear errors)
- Maintain consistency with existing algorithm and choice problem import patterns
- Support update mode for modifying existing fill-in-blank problems

### Non-Goals
- Modifying the `FillBlankProblem` database model (already complete)
- Frontend changes (already supports fill-in-blank display)
- API changes (already has check-fillblank endpoint)
- Excel import support (out of scope for this change)

## Decisions

### Decision 1: YAML Frontmatter Schema

**Choice**: Use the exact format provided in the user's template

**Rationale**:
- The template format is well-designed and supports three flexibility levels
- Matches the existing `FillBlankProblem.blanks` JSON field structure
- Aligns with the model's validation logic in `serializers.py`

**Required fields**:
```yaml
type: fillblank
title: string
difficulty: 1-3
content_with_blanks: string  # Text with [blank1], [blank2] markers
blanks: object  # 3 supported formats (see below)
```

**Optional fields**:
```yaml
chapter: int  # Chapter order number
blank_count: int  # Auto-calculated if not provided
unlock_conditions: object  # Same as other problem types
```

**Three supported formats for `blanks`**:

1. **Detailed format** - Maximum control per blank:
```yaml
blanks:
  blank1:
    answers: ["answer1", "alt1"]
    case_sensitive: false
  blank2:
    answers: ["answer2"]
    case_sensitive: true
```

2. **Simple format** - Uniform settings for all blanks:
```yaml
blanks:
  blanks: ["answer1", "answer2", "answer3"]
  case_sensitive: false
```

3. **Recommended format** - Per-blank settings in list:
```yaml
blanks:
  blanks:
    - answers: ["answer1", "alt1"]
      case_sensitive: false
    - answers: ["answer2"]
      case_sensitive: true
```

**Alternatives considered**:
- Require only one format → Rejected: Instructors should have flexibility for simple vs complex cases
- Create a new format → Rejected: Existing model already supports these three formats

### Decision 2: Validation Location

**Choice**: Add `_validate_fillblank_problem()` method to `MarkdownFrontmatterParser`

**Rationale**:
- Follows existing pattern (`_validate_algorithm_problem()`, `_validate_choice_problem()`)
- Validation happens early in the pipeline (fail fast)
- Separates validation logic from import logic
- Easy to test in isolation

**Validation rules**:
- `content_with_blanks` must be a non-empty string
- `content_with_blanks` must contain at least one `[blankN]` marker where N ≥ 1
- `blanks` must be present and valid (check all three formats)
- If provided, `blank_count` must match the actual number of blanks detected

**Alternatives considered**:
- Validate only in Django model clean() → Rejected: Would fail late in transaction, wasting work
- Validate only in serializers → Rejected: Import bypasses serializers for direct DB writes

### Decision 3: Import Method Location

**Choice**: Add `_import_fillblank_problem()` to `CourseImporter`

**Rationale**:
- Follows existing pattern (`_import_algorithm_problem()`, `_import_choice_problem()`)
- Called from `_import_problem_basic_info()` alongside other type handlers
- Uses `get_or_create()` with `update_mode` support
- Transaction is already wrapping the entire import

**Implementation approach**:
```python
def _import_fillblank_problem(self, problem: Problem, frontmatter: Dict) -> None:
    fillblank_info, created = FillBlankProblem.objects.get_or_create(
        problem=problem,
        defaults={
            'content_with_blanks': frontmatter['content_with_blanks'],
            'blanks': frontmatter['blanks'],
            'blank_count': frontmatter.get('blank_count', self._count_blanks(...))
        }
    )

    if not created and self.update_mode:
        # Update fields
        fillblank_info.save()
```

**Alternatives considered**:
- Generic problem importer → Rejected: Each type has unique fields, generic code would be complex
- Separate service class → Rejected: Over-engineering for ~20 lines of code

### Decision 4: Blank Marker Extraction

**Choice**: Use regex to extract blank markers from `content_with_blanks`

**Implementation**:
```python
BLANK_MARKER_PATTERN = re.compile(r'\[blank(\d+)\]')

def _extract_blank_markers(self, content: str) -> Set[int]:
    """Extract all blank marker numbers from content."""
    return set(int(m) for m in self.BLANK_MARKER_PATTERN.findall(content))
```

**Validation**:
- All referenced blanks (e.g., `[blank1]`, `[blank2]`) must have definitions
- No orphaned blank definitions (defined but not used in content)
- Numbering must be sequential starting from 1 (1, 2, 3, ...)

**Alternatives considered**:
- Allow any naming scheme → Rejected: Too complex, no clear use case
- Allow gaps in numbering → Rejected: Confusing, potential for errors

## Risks / Trade-offs

### Risk 1: Invalid `blanks` Format
- **Risk**: Instructors provide malformed `blanks` YAML
- **Impact**: Import fails with unclear error
- **Mitigation**: Comprehensive validation with specific error messages indicating which format was attempted and what's wrong

### Risk 2: Blank Count Mismatch
- **Risk**: `blank_count` field doesn't match actual blanks
- **Impact**: Frontend displays incorrect blank count
- **Mitigation**:
  - Auto-calculate `blank_count` if not provided
  - Validate that provided `blank_count` matches actual count
  - Log warning if mismatch detected

### Risk 3: Missing Blank Definitions
- **Risk**: Content references `[blank3]` but only `blank1` and `blank2` are defined
- **Impact**: Frontend error when rendering problem
- **Mitigation**: Validate that all referenced blanks have definitions during import

## Migration Plan

### No Database Migration Required
- `FillBlankProblem` model already exists
- This change only adds import capability

### Deployment Steps
1. Deploy code changes to production
2. Instructors can immediately start using fill-in-blank import
3. Existing manually-created fill-in-blank problems continue to work
4. Optionally backfill existing problems into Git repository (manual process)

### Rollback Plan
- Revert code changes
- System returns to previous state (manual fill-in-blank creation only)
- No database rollback needed (no schema changes)

## Open Questions

None. The requirements are clear and the implementation path is straightforward given the existing patterns for algorithm and choice problem imports.
