## ADDED Requirements

### Requirement: Fill-in-Blank Problem Import
The course import service SHALL support importing fill-in-blank problems from markdown files with YAML frontmatter.

#### Scenario: Successful fill-in-blank problem import
- **GIVEN** a Git repository contains a `problems/fillblank-01.md` file with valid fill-in-blank frontmatter
- **WHEN** the import service processes the repository
- **THEN** a `Problem` record is created with `type='fillblank'`
- **AND** a `FillBlankProblem` record is created with the correct `content_with_blanks`, `blanks`, and `blank_count`

#### Scenario: Fill-in-blank problem with detailed blanks format
- **GIVEN** a problem file uses the detailed blanks format with per-blank configuration
- **WHEN** the problem is imported
- **THEN** each blank's `answers` list and `case_sensitive` setting are preserved
- **AND** the `blanks` field stores the complete configuration in JSON format

#### Scenario: Fill-in-blank problem with simple blanks format
- **GIVEN** a problem file uses the simple blanks format (uniform settings)
- **WHEN** the problem is imported
- **THEN** the `blanks` field stores the simple format with all answers and a single `case_sensitive` setting
- **AND** all blanks inherit the same case sensitivity setting

#### Scenario: Fill-in-blank problem with recommended list format
- **GIVEN** a problem file uses the recommended list format
- **WHEN** the problem is imported
- **THEN** the `blanks` field stores the list of per-blank configurations
- **AND** each blank can have independent `answers` and `case_sensitive` settings

#### Scenario: Auto-calculate blank count
- **GIVEN** a problem file does not specify `blank_count`
- **WHEN** the problem is imported
- **THEN** the system automatically calculates `blank_count` from the number of `[blankN]` markers in `content_with_blanks`

### Requirement: Fill-in-Blank Problem Validation
The import service SHALL validate fill-in-blank problem frontmatter before creating database records.

#### Scenario: Validate required fields
- **GIVEN** a fill-in-blank problem frontmatter is parsed
- **WHEN** validation runs
- **THEN** the system requires `type='fillblank'`, `title`, `difficulty`, `content_with_blanks`, and `blanks` fields
- **AND** raises `ValueError` if any required field is missing

#### Scenario: Validate blank marker format
- **GIVEN** a `content_with_blanks` field contains blank markers
- **WHEN** validation runs
- **THEN** the system requires markers to follow `[blankN]` format where N ≥ 1
- **AND** raises `ValueError` if markers use invalid format (e.g., `[blank]`, `[blank_1]`, `[Blank1]`)

#### Scenario: Validate blank definitions completeness
- **GIVEN** a `content_with_blanks` references `[blank1]`, `[blank2]`, and `[blank3]`
- **WHEN** validation runs
- **THEN** the system requires all three blanks to have definitions in the `blanks` field
- **AND** raises `ValueError` if any referenced blank is missing

#### Scenario: Validate blank count consistency
- **GIVEN** a problem specifies `blank_count=3`
- **WHEN** validation runs
- **THEN** the system counts actual `[blankN]` markers in `content_with_blanks`
- **AND** raises `ValueError` if the count doesn't match (e.g., 3 specified but 5 markers found)

#### Scenario: Validate blanks format
- **GIVEN** the `blanks` field is provided
- **WHEN** validation runs
- **THEN** the system accepts all three supported formats (detailed, simple, list)
- **AND** raises `ValueError` if the format doesn't match any of the three patterns

### Requirement: Fill-in-Blank Problem Update Support
The import service SHALL support updating existing fill-in-blank problems when `update_mode=True`.

#### Scenario: Update fill-in-blank problem content
- **GIVEN** a fill-in-blank problem already exists in the database
- **AND** the Git repository file has modified `content_with_blanks` or `blanks`
- **WHEN** the import service runs with `update_mode=True`
- **THEN** the existing `FillBlankProblem` record is updated with the new values
- **AND** the `updated_at` timestamp is set to the current time

#### Scenario: Skip update when update_mode=False
- **GIVEN** a fill-in-blank problem already exists in the database
- **WHEN** the import service runs with `update_mode=False`
- **THEN** the existing problem is not modified
- **AND** the import statistics show the problem as skipped

### Requirement: Fill-in-Blank Problem Chapter Association
The import service SHALL support associating fill-in-blank problems with chapters.

#### Scenario: Associate fill-in-blank problem with chapter
- **GIVEN** a fill-in-blank problem specifies `chapter: 2` in frontmatter
- **AND** a chapter with `order=2` exists in the course
- **WHEN** the problem is imported
- **THEN** the problem's `chapter` foreign key is set to the matching chapter
- **AND** the problem appears in that chapter's problem list

#### Scenario: Error on missing chapter
- **GIVEN** a fill-in-blank problem specifies `chapter: 5` in frontmatter
- **AND** no chapter with `order=5` exists in the course
- **WHEN** the import service attempts to import the problem
- **THEN** a `ValueError` is raised with message indicating chapter 5 not found
- **AND** the problem is not created
- **AND** the error is logged in the import statistics

### Requirement: Fill-in-Blank Problem Unlock Conditions
The import service SHALL support unlock conditions for fill-in-blank problems.

#### Scenario: Import prerequisite unlock conditions
- **GIVEN** a fill-in-blank problem specifies `unlock_conditions.type='prerequisite'`
- **AND** `prerequisites` lists other problem filenames
- **WHEN** the problem is imported (Phase 2 of two-phase import)
- **THEN** a `ProblemUnlockCondition` record is created
- **AND** the prerequisite problems are linked via `prerequisite_problems` M2M field

#### Scenario: Import date-based unlock conditions
- **GIVEN** a fill-in-blank problem specifies `unlock_conditions.type='date'`
- **AND** `unlock_date` is set to a valid ISO 8601 datetime
- **WHEN** the problem is imported
- **THEN** a `ProblemUnlockCondition` record is created with the unlock date
- **AND** the problem becomes accessible only after that date

#### Scenario: Import combined unlock conditions
- **GIVEN** a fill-in-blank problem specifies `unlock_conditions.type='both'`
- **AND** both `prerequisites` and `unlock_date` are provided
- **WHEN** the problem is imported
- **THEN** a `ProblemUnlockCondition` record is created with both conditions
- **AND** the problem becomes accessible only after both conditions are met
