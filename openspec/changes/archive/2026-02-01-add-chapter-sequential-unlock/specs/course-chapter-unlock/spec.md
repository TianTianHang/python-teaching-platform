## ADDED Requirements

### Requirement: Default Sequential Chapter Unlock for New Courses

New courses MUST configure chapters with sequential `unlock_conditions` to enforce progressive learning, unless there is a specific pedagogical reason to allow non-linear access.

#### Scenario: Course author is creating a new course

**Given** a new course is being created
**When** designing the chapter structure
**Then** the course MUST use sequential chapter unlock conditions

#### Scenario: First chapter is always unlocked

**Given** a course with sequential chapter unlocks
**When** configuring Chapter 1 (order: 1)
**Then** the chapter MUST NOT have `unlock_conditions`
**And** the chapter serves as the course entry point

#### Scenario: Subsequent chapters require immediate predecessor

**Given** a chapter with order N (where N ≥ 2)
**When** the course uses sequential unlocks
**Then** the chapter MUST include `unlock_conditions` with:
- `type: "prerequisite"`
- `prerequisites: [N-1]`

#### Scenario: Sequential unlock is the default pattern

**Given** a course with multiple chapters
**When** no special pedagogical requirements exist
**Then** each chapter (N) MUST require completion of chapter (N-1)

#### Scenario: Non-linear unlocks require justification

**Given** a course with chapters
**When** using non-sequential unlock patterns
**Then** the course design document MUST explain:
- Why sequential progression is not appropriate
- What alternative pattern is used (e.g., branch selection, cumulative prerequisites)
- The pedagogical benefit of the alternative approach

#### Scenario: Frontmatter format for sequential unlocks

**Given** a chapter frontmatter with unlock conditions
**When** writing the YAML
**Then** the format should be:
```yaml
---
title: "章节标题"
order: N
unlock_conditions:
  type: "prerequisite"
  prerequisites: [N-1]
---
```

#### Scenario: Course template includes sequential unlock pattern

**Given** the chapter template at `courses/_templates/chapter-00-template.md`
**When** authors copy the template for new chapters
**Then** the template MUST include commented-out unlock conditions example:
```yaml
# For sequential unlocks (recommended), uncomment:
# unlock_conditions:
#   type: "prerequisite"
#   prerequisites: [previous_chapter_order]
```

#### Scenario: Documentation recommends sequential unlocks

**Given** the course authoring guide at `docs/course-authoring-guide.md`
**When** explaining chapter configuration
**Then** the guide MUST:
- State that sequential chapter unlocks are the recommended default
- Provide examples of the unlock_conditions format
- Explain when non-linear patterns might be appropriate
