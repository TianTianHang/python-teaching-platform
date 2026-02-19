# python-practice-course Spec Delta

## MODIFIED Requirements

### Requirement: Problem Description Format

All problem descriptions MUST follow a consistent, beginner-friendly format. Hint sections MUST use collapsible directive blocks to hide hints by default.

#### Scenario: Problem description is concise

**Given** any problem in the course
**When** reading the problem description
**Then** it should:
- Be 1-2 sentences maximum
- Use simple language
- Clearly state the required operation
- Avoid technical jargon

#### Scenario: Problem includes collapsible hint section

**Given** any problem in the course
**When** reviewing the problem structure
**Then** it MUST include:
- A "### 提示" section
- A `:::tip{title="提示" state="collapsed"}` directive block wrapping the hint content
- Guidance on which data structure/operation to use
- Example syntax or method name (inside the collapsible block)
- Edge case considerations (inside the collapsible block)

#### Scenario: Simple hint uses single collapsible block with title

**Given** a problem with a simple hint
**When** writing the hint section
**Then** the hint MUST be formatted as:
```markdown
### 提示

:::tip{title="提示" state="collapsed"}
Hint content here
:::
```

#### Scenario: Multi-approach hint uses multiple collapsible blocks

**Given** a problem with multiple solution approaches
**When** writing the hint section
**Then** the hint SHOULD be formatted as multiple blocks:
```markdown
### 提示

:::tip{title="方法一" state="collapsed"}
First approach hint
:::

:::tip{title="方法二" state="collapsed"}
Second approach hint
:::
```

#### Scenario: Problem has appropriate test cases

**Given** an algorithm problem
**When** reviewing test_cases in frontmatter
**Then** it MUST include:
- At least one `is_sample: true` test case
- 3-5 total test cases covering:
  - Normal case
  - Edge case (empty input, single element)
  - Boundary case
