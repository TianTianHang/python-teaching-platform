# Chapter Format Specification

## ADDED Requirements

### Requirement: Chapter Unlock Conditions

The chapter format SHALL support an optional `unlock_conditions` field in YAML frontmatter to control when students can access chapter content. When present, the system MUST enforce the specified unlock conditions which support prerequisite-based, date-based, or combined unlocking strategies.

#### Scenario: Prerequisite-only unlock

- **GIVEN** a chapter file with `unlock_conditions.type: prerequisite`
- **AND** `unlock_conditions.prerequisites: [1, 2]`
- **WHEN** the chapter is imported
- **THEN** the chapter should be locked until the student completes both chapters with `order=1` and `order=2`

#### Scenario: Date-only unlock

- **GIVEN** a chapter file with `unlock_conditions.type: date`
- **AND** `unlock_conditions.unlock_date: "2025-03-01T00:00:00Z"`
- **WHEN** the chapter is imported
- **THEN** the chapter should be locked until the specified date/time is reached

#### Scenario: Combined prerequisite and date unlock

- **GIVEN** a chapter file with `unlock_conditions.type: all`
- **AND** `unlock_conditions.prerequisites: [1]`
- **AND** `unlock_conditions.unlock_date: "2025-03-01T00:00:00Z"`
- **WHEN** the chapter is imported
- **THEN** the chapter should be locked until BOTH the prerequisite is completed AND the date is reached

#### Scenario: No unlock conditions (default)

- **GIVEN** a chapter file without `unlock_conditions` field
- **WHEN** the chapter is imported
- **THEN** the chapter should be immediately accessible to all enrolled students

#### Scenario: Explicit none type

- **GIVEN** a chapter file with `unlock_conditions.type: none`
- **WHEN** the chapter is imported
- **THEN** the chapter should be immediately accessible to all enrolled students

### Requirement: Chapter Unlock Validation

Platforms importing chapter content MUST validate the `unlock_conditions` field according to the format specification.

#### Scenario: Invalid type value

- **GIVEN** a chapter with `unlock_conditions.type: invalid_type`
- **WHEN** the chapter is validated
- **THEN** a validation error should be raised indicating the invalid type value

#### Scenario: Missing required field

- **GIVEN** a chapter with `unlock_conditions.type: prerequisite`
- **AND** no `prerequisites` field
- **WHEN** the chapter is validated
- **THEN** a validation error should be raised indicating the missing required field

#### Scenario: Invalid datetime format

- **GIVEN** a chapter with `unlock_conditions.unlock_date: "not-a-date"`
- **WHEN** the chapter is validated
- **THEN** a validation error should be raised indicating the invalid datetime format

#### Scenario: Non-existent prerequisite chapter

- **GIVEN** a chapter with `unlock_conditions.prerequisites: [99]`
- **AND** no chapter with `order=99` exists in the course
- **WHEN** the chapter is imported
- **THEN** a warning should be logged and the invalid prerequisite should be skipped

#### Scenario: Self-reference prevention

- **GIVEN** a chapter with `order: 5`
- **AND** `unlock_conditions.prerequisites: [5]`
- **WHEN** the chapter is validated
- **THEN** a validation error should be raised indicating self-reference is not allowed

### Requirement: Prerequisites Reference Format

Chapter prerequisites MUST reference chapters by their `order` field (integer), not by filename or title.

#### Scenario: Valid integer prerequisite

- **GIVEN** a chapter with `unlock_conditions.prerequisites: [1, 2, 3]`
- **WHEN** the chapter is validated
- **THEN** each prerequisite should be validated as an integer
- **AND** the corresponding chapter with that `order` should exist

#### Scenario: Invalid prerequisite type

- **GIVEN** a chapter with `unlock_conditions.prerequisites: ["chapter-01"]`
- **WHEN** the chapter is validated
- **THEN** a validation error should be raised indicating prerequisites must be integers

### Requirement: ISO 8601 Datetime Format

The `unlock_date` field MUST be a valid ISO 8601 datetime string.

#### Scenario: UTC datetime format

- **GIVEN** a chapter with `unlock_conditions.unlock_date: "2025-03-01T00:00:00Z"`
- **WHEN** the chapter is validated
- **THEN** the datetime should be parsed successfully

#### Scenario: Timezone offset format

- **GIVEN** a chapter with `unlock_conditions.unlock_date: "2025-03-01T08:00:00+08:00"`
- **WHEN** the chapter is validated
- **THEN** the datetime should be parsed successfully

#### Scenario: Simple datetime format

- **GIVEN** a chapter with `unlock_conditions.unlock_date: "2025-03-01 00:00:00"`
- **WHEN** the chapter is validated
- **THEN** the datetime should be parsed successfully as UTC
