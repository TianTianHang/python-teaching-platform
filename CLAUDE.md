# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **course content repository** for a Python teaching platform. Courses are authored as Markdown files with YAML frontmatter, then imported into a Django backend via a management command.

**Key Design Principle:** Content is stored separately from the application code. Course authors work with Markdown files in this repository; the Django backend imports and parses them.

## Repository Structure

```
course-content/
├── courses/
│   ├── _templates/           # Reference templates - do NOT edit directly
│   │   ├── course.md
│   │   ├── chapters/chapter-00-template.md
│   │   └── problems/{algorithm,choice}-problem-template.md
│   └── {course-slug}/        # Individual course directories
│       ├── course.md         # Course metadata + overview
│       ├── chapters/         # Chapter content files
│       └── problems/         # Algorithm/choice problems
└── docs/                     # Detailed format documentation
```

## File Naming Conventions

- **Course directories**: `kebab-case` (e.g., `python-basics`)
- **Chapter files**: `chapter-{order:02d}-{slug}.md` (e.g., `chapter-01-variables.md`)
- **Problem files**: `{slug}.md` (e.g., `two-sum.md`)

## Importing Content

The Django backend has a management command that imports course content:

```bash
# From the backend directory, run:
uv run python manage.py import_course_from_repo /path/to/course-content --update

# View all options:
uv run python manage.py import_course_from_repo --help
```

The `--update` flag updates existing courses instead of failing.

## Content Format

All content files use **YAML frontmatter** followed by Markdown body.

### Course Metadata (`course.md`)

Required frontmatter fields:
```yaml
---
title: "Course Title"
description: "50-200 character description"
order: 1           # Display order integer
difficulty: 1      # Optional: 1=easy, 2=medium, 3=hard
prerequisites: []  # Optional: list of prerequisite course slugs
tags: []           # Optional: list of tag strings
---
```

### Chapter Files

Required frontmatter:
```yaml
---
title: "Chapter Title"
order: 1
---
```

Chapter body should follow the template structure with **知识点** (knowledge point) sections containing:
- **描述** (Description)
- **示例代码** (Example code)
- **解释** (Explanation)

### Problem Files

Problems can be `algorithm` or `choice` type. Required frontmatter:

```yaml
---
title: "Problem Title"
type: "algorithm"  # or "choice"
difficulty: 1
chapter: 1         # Optional: links to chapter by order number
---
```

**Algorithm problems** also require:
```yaml
time_limit: 1000         # milliseconds
memory_limit: 256        # MB
solution_name:
  python: "functionName"
code_template:
  python: |
    def functionName(args):
        # student code here
        pass
test_cases:
  - input: "[[2,7,11,15],9]"  # JSON string
    output: "[0,1]"            # JSON string
    is_sample: true
```

**Choice problems** also require:
```yaml
is_multiple_choice: false
options:
  A: "Option text"
  B: "Option text"
  C: "Option text"
  D: "Option text"
correct_answer: "C"  # or ["A","C"] for multiple choice
```

### Unlock Conditions

Problems can have optional `unlock_conditions` frontmatter:

```yaml
unlock_conditions:
  type: "prerequisite"  # or "date", "both", "none"
  prerequisites: ["previous-problem.md"]
  minimum_percentage: 100  # 0-100, optional
  unlock_date: "2024-12-31T23:59:59"  # ISO 8601, for "date"/"both" types
```

The `chapter` field in problems references the chapter's `order` number, not the title. If the specified chapter order doesn't exist, import fails.

## Creating New Courses

1. Create directory structure: `mkdir -p courses/{course-slug}/{chapters,problems}`
2. Copy templates from `courses/_templates/` and modify
3. Edit YAML frontmatter with appropriate metadata
4. Write chapter content following the template structure
5. Create problems with appropriate test cases
6. Import using the management command

## Important Notes

- **Do not edit templates** in `courses/_templates/` - copy them instead
- **Test case I/O must be valid JSON strings** in YAML
- **All files must be UTF-8 encoded**
- **Chapter `order` field is used for problem `chapter` reference**
- **At least one test case must have `is_sample: true`**
- **Unlock condition prerequisites reference problem filenames** (with `.md` extension)

## Documentation

- [README.md](README.md) - Quick start and contribution guide
- [docs/format-specification.md](docs/format-specification.md) - Complete format reference
- [docs/course-authoring-guide.md](docs/course-authoring-guide.md) - Step-by-step authoring tutorial
- [docs/troubleshooting.md](docs/troubleshooting.md) - Common issues and solutions
