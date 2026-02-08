# Proposal: Skip Underscore-Prefixed Courses

## Summary
Add filtering logic to the course import service to skip courses whose directory names start with an underscore (`_`). This allows instructors to maintain draft, template, or experimental courses in the same repository without importing them to the production database.

## Problem Statement
The course import service currently imports all courses found in the `courses/` directory of the repository, without any filtering mechanism. This creates several issues:

1. **Draft courses**: Instructors may want to keep work-in-progress courses in the repository without importing them
2. **Template courses**: Repository maintainers may include template courses as examples that shouldn't be imported
3. **Experimental content**: Test or experimental courses may exist alongside production content

Using the underscore prefix convention (`_`) is a common pattern in many systems (like Jekyll, Hugo, etc.) to exclude files/directories from processing.

## Proposed Solution
Add a simple filter in `CourseImporter.import_all()` to skip course directories whose names start with `_`.

### Implementation Location
The filter will be added in [`backend/courses/course_import_services/course_importer.py`](../../../../backend/courses/course_import_services/course_importer.py) at line 77-78, where course directories are iterated.

### Key Design Decisions

1. **Simple prefix check**: Use `course_dir.name.startswith('_')` for filtering - straightforward and efficient
2. **Silent skipping**: Skipped courses are not logged as errors, only as info-level logs, since this is expected behavior
3. **No configuration needed**: The underscore convention is self-documenting and requires no additional configuration

## Affected Components

### Backend
- **[course_importer.py](../../../../backend/courses/course_import_services/course_importer.py)**:
  - Add filter condition in `import_all()` method to skip underscore-prefixed directories
  - Add info-level logging for skipped courses

## Alternatives Considered

### Alternative 1: Configuration-based filtering
Add a command-line option or configuration file to specify which courses to skip.
- **Rejected**: Over-engineering for a simple use case; underscore convention is widely understood

### Alternative 2: Frontmatter-based filtering
Add a field in `course.md` like `import: false`.
- **Rejected**: Requires parsing each file before deciding to skip, less efficient

### Alternative 3: Separate repository
Keep draft courses in a separate repository.
- **Rejected**: Inconvenient for instructors; having everything in one repo with simple exclusion is easier

## Dependencies
- None - this is a standalone enhancement to the existing import service

## Success Criteria
1. Course directories starting with `_` are silently skipped during import
2. Other courses are imported normally
3. Import statistics reflect only non-skipped courses
4. Info-level logging indicates which courses were skipped

## Related Specs
- [course-import](../../../../specs/course-import/spec.md) - Course import service specification

## Implementation Approach
1. Add filter condition in `CourseImporter.import_all()` method
2. Add logging for skipped courses
3. Add unit tests to verify filtering behavior
4. Add integration test with sample repository structure
