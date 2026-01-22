# Change: Add Fill-in-Blank Problem Import Support

## Why

The system currently supports `fillblank` as a problem type in the database model (`FillBlankProblem`), and the frontend can display and interact with fill-in-blank problems. However, the course import service (`course_importer.py`) and markdown parser (`markdown_parser.py`) do not support importing fill-in-blank problems from Git repositories. This creates a gap where instructors must manually create fill-in-blank problems through the admin interface or API, rather than managing them declaratively through the course repository alongside algorithm and choice problems.

## What Changes

- Add `_validate_fillblank_problem()` method to `MarkdownFrontmatterParser` in `markdown_parser.py` to validate fill-in-blank problem frontmatter
- Add `_import_fillblank_problem()` method to `CourseImporter` in `course_importer.py` to import fill-in-blank problem data
- Update `validate_problem_frontmatter()` to accept `'fillblank'` as a valid problem type
- Support three YAML frontmatter formats for the `blanks` field (detailed, simple, and recommended list format)
- Validate required fields: `content_with_blanks`, `blanks`, and optional `blank_count`
- Ensure backward compatibility with existing algorithm and choice problem imports

## Impact

- **Affected specs**: `course-import` capability (new spec)
- **Affected code**:
  - `backend/courses/course_import_services/markdown_parser.py` (~50 lines added)
  - `backend/courses/course_import_services/course_importer.py` (~30 lines added)
- **Backward compatibility**: ✅ Fully backward compatible - existing imports continue to work unchanged
- **User impact**: Instructors can now manage fill-in-blank problems through Git repositories, enabling version control and bulk imports
