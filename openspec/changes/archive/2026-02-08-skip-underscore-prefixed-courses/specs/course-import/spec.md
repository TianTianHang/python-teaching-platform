# course-import Specification Delta

## ADDED Requirements

### Requirement: Course Directory Filtering
The course import service SHALL skip course directories whose names start with an underscore (`_`).

#### Scenario: Skip underscore-prefixed course directory
- **GIVEN** a Git repository contains a `courses/_draft-python/` directory
- **WHEN** the import service processes the repository
- **THEN** the `_draft-python` course is NOT imported
- **AND** no error is raised
- **AND** an info-level log message indicates the course was skipped

#### Scenario: Import regular course alongside underscore-prefixed course
- **GIVEN** a Git repository contains `courses/_template/` and `courses/python-basics/` directories
- **WHEN** the import service processes the repository
- **THEN** only `python-basics` course is imported
- **AND** `_template` course is skipped
- **AND** import statistics show `courses_created=1` and `courses_filtered=1`

#### Scenario: Course with underscore in middle of name is imported
- **GIVEN** a Git repository contains a `courses/python_advanced_part1/` directory
- **WHEN** the import service processes the repository
- **THEN** the course is imported normally
- **AND** the underscore in the middle of the name does NOT cause it to be skipped

#### Scenario: Repository with no underscore-prefixed courses
- **GIVEN** a Git repository contains only regular course directories (no `_` prefix)
- **WHEN** the import service processes the repository
- **THEN** all courses are imported normally
- **AND** `courses_filtered=0` in the statistics
