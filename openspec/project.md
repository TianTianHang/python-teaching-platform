# Project Context

## Purpose
This is a **standard course content repository** (课程内容标准仓库) for storing Python programming course materials. It contains only documentation - course content authored in Markdown with YAML frontmatter format.

The repository serves as:
- A standalone, version-controlled course content library
- A content source that can be imported by any compatible learning platform
- A standardized format for authoring and sharing Python educational materials

The project aims to:
- Provide a structured, format-standardized way to author Python programming courses
- Support multiple problem types: algorithm problems, choice questions, and fill-in-the-blank questions
- Enable chapter-based learning progression with unlock conditions
- Maintain consistent formatting across all course materials
- Serve as a portable, platform-agnostic content distribution format

## Tech Stack
- **Content Format**: Markdown with YAML frontmatter
- **Version Control**: Git
- **Content Language**: Chinese (Simplified)
- **Platform**: Content-agnostic (can be imported by any compatible backend system)

### Platform Features
- **Executable Code Blocks**: Custom markdown syntax ```python-exec for marking executable Python code blocks
  - These code blocks are rendered with an interactive "Run" button on the platform
  - Allows students to execute code directly within the course content
  - Output is displayed inline below the code block

- **Jupyter Integration**: `/jupyter` url to opens an interactive code notebook for hands-on practice
  - Provides a full Jupyter environment for code experimentation
  - Supports running and testing code examples from the course
  - Enables students to practice without leaving the learning platform

### Key File Types
- `.md` - Course content files (chapters, problems)
- YAML frontmatter - Metadata for courses, chapters, and problems
- Templates - Located in `courses/_templates/`

## Project Conventions

### File Naming
- **Course folders**: `kebab-case` format (e.g., `python-basics`)
- **Chapter files**: `chapter-{order:02d}-{slug}.md` (e.g., `chapter-01-variables.md`)
- **Problem files**: `{slug}.md` (e.g., `two-sum.md`)
- **Course metadata**: Always `course.md` in each course folder
- **Sort order**: Numeric (01, 02, 03...)

### YAML Frontmatter Rules
- **All strings must be quoted**: Use `"value"` not `value`
- **Arrays must use brackets**: `["item1", "item2"]` not `[item1, item2]`
- **Required fields vary by type**:
  - Courses: `title`, `description`, `order`
  - Chapters: `title`, `order`
  - Problems: `title`, `type`, `difficulty`

### Problem Types
1. **algorithm** - Coding problems with function solutions
   - Fields: `time_limit`, `memory_limit`, `solution_name`, `test_cases`
   - Default time limit: 1000ms
   - Default memory limit: 256MB

2. **choice** - Multiple choice questions
   - Fields: `is_multiple_choice`, `options`, `correct_answer`
   - Options: A, B, C, D keys
   - Single answer: string `"A"`
   - Multiple answers: array `["A", "B"]`

3. **fill-blank** - Fill-in-the-blank questions
   - Fields: `content_with_blanks`, `blanks`, `blank_count`
   - Supports case sensitivity configuration
   - Supports multiple acceptable answers per blank

### Difficulty Levels
- `1` - Simple (direct application, <20 lines, 2000ms time limit)
- `2` - Medium (multiple steps, moderate complexity)
- `3` - Hard (complex logic, optimization required)

### Chapter Association
- `chapter` field in problems is optional
- References the `order` field of a chapter (not the title)
- If chapter doesn't exist, import fails with error
- If omitted, problem is not associated with any chapter

### Unlock Conditions
**Problems**:
- `none` - No restrictions (default)
- `prerequisite` - Must complete specified problems first
- `date` - Unlocks after specified date (ISO 8601 format)
- `both` - Combines prerequisite + date requirements
- Prerequisites referenced by filename (e.g., `problem-01.md`)
- Supports `minimum_percentage` field for partial completion

**Chapters**:
- `none` - No restrictions (default)
- `prerequisite` - Must complete specified chapters first
- `date` - Unlocks after specified date (ISO 8601 format)
- `all` - Combines prerequisite + date requirements
- Prerequisites referenced by chapter `order` (integer)
- No `minimum_percentage` field (all-or-nothing)

### Chapter Unlock Conditions
Chapters MAY include `unlock_conditions` in frontmatter to control student access:
- Prerequisites reference chapter `order` integers (e.g., `[1, 2]`)
- Date format: ISO 8601 (`"2025-03-01T00:00:00Z"`)
- Two-phase import: create chapters first, then unlock conditions
- Backward compatible: chapters without `unlock_conditions` remain unlocked

### Code Style
- **Python**: Follow PEP 8 for function naming (snake_case)
- **Solution functions**: Must match `solution_name.python` in YAML
- **Function documentation**: Use docstrings with Args/Returns sections

### Content Authoring Principles
- **Student-centered**: Consider prior knowledge and learning goals
- **Progressive**: Simple to complex, concrete to abstract
- **Practical**: Real-world applications and problem-solving focus
- **Chapter structure**: 1-3 hours per chapter, 4-6 topics, 2-4 exercises

### Content Organization
```
courses/
├── _templates/           # Do not edit directly
├── {course-slug}/        # Individual courses
│   ├── course.md         # Course metadata
│   ├── chapters/         # Chapter content
│   └── problems/         # Problem sets
docs/                     # Documentation and guides
```

## Domain Context

### Course Structure
- **Course** (课程): Top-level container with metadata
- **Chapter** (章节): Ordered sections within a course
- **Problem** (题目): Exercises associated with chapters or standalone

### Learning Progression
- **Prerequisites**: Courses can depend on other courses via `prerequisites` array
- **Difficulty**: Progressive from 1 (beginner) to 3 (advanced)
- **Unlock system**: Problems can be gated by completion of other problems or by date

### Import Workflow
This repository is designed to be imported by compatible learning platforms. The standard import process typically:

1. Platform's import system reads the repository structure
2. Parses all `course.md` files for course metadata
3. Creates/updates course, chapter, and problem records
4. Validates YAML syntax and required fields
5. Reports errors for missing chapters or invalid formats

**Note**: The actual import mechanism depends on the platform consuming this content. This repository defines the content format and structure only.

## Important Constraints

### Content Constraints
- **No execution**: Course content files are static - no code execution in this repo
- **YAML validation required**: Import fails on malformed YAML
- **Chapter references**: Must exist or import fails
- **File encoding**: UTF-8 (supports Chinese content)

### Format Constraints
- **Description length**: 50-200 characters for courses
- **Unique problem slugs**: Within each course
- **Chapter order**: Must be sequential integers starting from 1

### Language
- Primary content language: Chinese (Simplified)
- Technical terms: English where appropriate
- Code comments: Chinese preferred for student comprehension

## External Dependencies

### Platform Integration
- This is a **content-only** repository with no runtime dependencies
- Integration with learning platforms is handled by the platform's import system
- No backend code, database, or server requirements

### Template System
- Templates in `courses/_templates/` are authoritative
- Copy templates when creating new content - never edit originals
- Template types:
  - `course.md` - Course metadata
  - `chapter-00-template.md` - Chapter structure
  - `algorithm-problem-template.md` - Coding problems
  - `choice-problem-template.md` - Multiple choice
  - `fill-blank-problem-template.md` - Fill-in-the-blank

### Documentation References
- [Format Specification](../docs/format-specification.md) - Authoritative format rules
- [Course Authoring Guide](../docs/course-authoring-guide.md) - Writing best practices
- [Troubleshooting](../docs/troubleshooting.md) - Common issues and solutions
- [README](../README.md) - Quick start guide
  - `course.md` - Course metadata
  - `chapter-00-template.md` - Chapter structure
  - `algorithm-problem-template.md` - Coding problems
  - `choice-problem-template.md` - Multiple choice
  - `fill-blank-problem-template.md` - Fill-in-the-blank

### Documentation References
- [Format Specification](../docs/format-specification.md) - Authoritative format rules
- [Course Authoring Guide](../docs/course-authoring-guide.md) - Writing best practices
- [Troubleshooting](../docs/troubleshooting.md) - Common issues and solutions
