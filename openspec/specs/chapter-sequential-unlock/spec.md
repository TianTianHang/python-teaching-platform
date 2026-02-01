# chapter-sequential-unlock Specification

## Purpose
TBD - created by archiving change add-chapter-sequential-unlock. Update Purpose after archive.
## Requirements
### Requirement: Sequential Chapter Unlock

Chapters in the Python Intro course MUST have sequential `unlock_conditions` to enforce progressive learning.

#### Scenario: Chapter 1 is the entry point with no unlock conditions

**Given** the course has 8 chapters
**When** configuring Chapter 1 (Python简介与环境搭建)
**Then** the chapter frontmatter should NOT include `unlock_conditions`
**And** the chapter should be accessible to all students by default

#### Scenario: Each subsequent chapter requires the previous chapter

**Given** a chapter with order N (where 2 ≤ N ≤ 8)
**When** configuring the chapter frontmatter
**Then** the chapter MUST include `unlock_conditions` with:
- `type: "prerequisite"`
- `prerequisites: [N-1]` (array containing the previous chapter's order)

#### Scenario: Chapter 2 requires Chapter 1 completion

**Given** Chapter 2 (变量与数据类型) has order 2
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [1]
```

#### Scenario: Chapter 3 requires Chapter 2 completion

**Given** Chapter 3 (运算符) has order 3
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [2]
```

#### Scenario: Chapter 4 requires Chapter 3 completion

**Given** Chapter 4 (控制流 - 条件语句) has order 4
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [3]
```

#### Scenario: Chapter 5 requires Chapter 4 completion

**Given** Chapter 5 (控制流 - 循环) has order 5
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [4]
```

#### Scenario: Chapter 6 requires Chapter 5 completion

**Given** Chapter 6 (列表) has order 6
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [5]
```

#### Scenario: Chapter 7 requires Chapter 6 completion

**Given** Chapter 7 (字典) has order 7
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [6]
```

#### Scenario: Chapter 8 requires Chapter 7 completion

**Given** Chapter 8 (函数基础) has order 8
**When** setting unlock conditions
**Then** the frontmatter should include:
```yaml
unlock_conditions:
  type: "prerequisite"
  prerequisites: [7]
```

#### Scenario: YAML format is correct for unlock conditions

**Given** a chapter frontmatter with unlock conditions
**When** writing the YAML
**Then**:
- `type` value must be quoted: `"prerequisite"`
- `prerequisites` must be an array with brackets: `[1]`
- The structure must follow proper YAML indentation

#### Scenario: Chapter unlock chain is complete

**Given** all 8 chapters are configured
**When** reviewing the unlock structure
**Then** the complete chain should be:
- Ch 1 (no unlock) → Ch 2 (requires 1) → Ch 3 (requires 2) → Ch 4 (requires 3) → Ch 5 (requires 4) → Ch 6 (requires 5) → Ch 7 (requires 6) → Ch 8 (requires 7)

