# Capability: Python Introduction Course

## Overview

This specification defines the Python 入门 (Introduction) course - a comprehensive beginner-level course covering fundamental Python programming concepts for learners with zero programming experience.

## ADDED Requirements

### Requirement: Course Metadata

The course MUST have properly configured metadata in `courses/python-intro/course.md`.

#### Scenario: Course metadata is created

**Given** the project follows the standard course format
**When** creating the Python Introduction course
**Then** the course.md file should contain:
- `title`: "Python 入门"
- `description`: A 50-200 character description in Chinese
- `order`: A unique numeric order for course display
- Properly quoted YAML strings

#### Scenario: Course folder structure exists

**Given** the course is being created
**When** setting up the course structure
**Then** the following directories should exist:
- `courses/python-intro/`
- `courses/python-intro/chapters/`
- `courses/python-intro/problems/`

---

### Requirement: Chapter Structure

The course MUST contain 8 chapters covering fundamental Python topics in a logical progression.

#### Scenario: All chapters are created with proper metadata

**Given** the course folder structure exists
**When** creating all 8 chapters
**Then** each chapter file should:
- Use naming format `chapter-{order:02d}-{slug}.md`
- Have `title` field in Chinese
- Have sequential `order` field (1-8)
- Contain content in Markdown format

#### Scenario: Chapter content follows pedagogical principles

**Given** a chapter is being authored
**When** writing chapter content
**Then** each chapter should include:
- Clear learning objectives
- Conceptual explanations with examples
- Code examples with `python` or `python-exec` syntax highlighting
- Key takeaways or summary points

#### Scenario: Chapter topics cover complete introduction

**Given** the course structure
**When** listing all chapter topics
**Then** the following topics must be covered:
1. Python简介与环境搭建 (Introduction & Setup)
2. 变量与数据类型 (Variables & Data Types)
3. 运算符 (Operators)
4. 控制流 - 条件语句 (Control Flow - Conditionals)
5. 控制流 - 循环 (Control Flow - Loops)
6. 列表 (Lists)
7. 字典 (Dictionaries)
8. 函数基础 (Functions Basics)

#### Scenario: Chapter 1 introduces platform features

**Given** the first chapter covers environment setup
**When** writing the chapter content
**Then** Chapter 1 MUST include:
- Introduction to the platform's built-in Jupyter notebook (`/jupyter`)
- Instructions on how to access and use the Jupyter environment
- Guidance that local Python installation is optional since the platform provides an interactive coding environment

---

### Requirement: Platform Feature Integration

The course MUST leverage platform features to enhance the learning experience.

#### Scenario: Jupyter notebook is highlighted as primary coding environment

**Given** the platform has Jupyter integration
**When** learners need to practice coding
**Then** the course should:
- Promote `/jupyter` as the primary environment for running code
- Explain that no local setup is required to start learning
- Provide links to Jupyter where appropriate

#### Scenario: python-exec blocks are used for interactive examples

**Given** the platform supports executable code blocks
**When** creating code examples in chapters
**Then** appropriate code blocks should use ` ```python-exec ` syntax to enable the "Run" button feature

---

### Requirement: Exercise Distribution

Each chapter MUST include 2-3 exercises with a focus on conceptual understanding.

#### Scenario: Exercise types are balanced per chapter

**Given** a chapter needs exercises
**When** creating exercises for a chapter
**Then** the distribution should be approximately:
- 60% Choice Questions (conceptual understanding)
- 30% Fill-blank Questions (syntax and key concepts)
- 10% Algorithm Problems (basic coding)

#### Scenario: Total exercise count meets target

**Given** 8 chapters with 2-3 exercises each
**When** all exercises are created
**Then** the total count should be 18-24 exercises

#### Scenario: Exercise difficulty is appropriate

**Given** the target audience is zero-experience beginners
**When** setting exercise difficulty
**Then**:
- Most exercises should be `difficulty: 1` (simple)
- Few to no exercises should be `difficulty: 2` or `3`

---

### Requirement: Choice Questions

Choice questions MUST test conceptual understanding of Python concepts.

#### Scenario: Choice question has proper structure

**Given** a choice question is being created
**When** writing the YAML frontmatter
**Then** the file should include:
- `type: "choice"`
- `difficulty: 1` (typically)
- `chapter: <chapter_order>` (associated chapter)
- `is_multiple_choice: false` or `true`
- `options` object with A, B, C, D keys
- `correct_answer` as string or array

#### Scenario: Choice question tests conceptual knowledge

**Given** a choice question
**When** reading the question content
**Then** it should:
- Test understanding of concepts rather than memorization
- Have clearly distinguishable options
- Include explanations in the content body

---

### Requirement: Fill-blank Questions

Fill-blank questions MUST reinforce Python syntax and key terminology.

#### Scenario: Fill-blank question has proper structure

**Given** a fill-blank question is being created
**When** writing the YAML frontmatter
**Then** the file should include:
- `type: "fillblank"`
- `difficulty: 1`
- `chapter: <chapter_order>` (associated chapter)
- `content_with_blanks` with `[blankN]` placeholders
- `blanks` object with answers for each blank
- `blank_count` matching the number of blanks

#### Scenario: Fill-blank question allows for multiple valid answers

**Given** a fill-blank question
**When** configuring blank answers
**Then**:
- Each blank can have multiple acceptable answers
- `case_sensitive: false` for flexibility
- Answers cover common variations

---

### Requirement: Algorithm Problems

Algorithm problems MUST provide simple coding practice for beginners.

#### Scenario: Algorithm problem has proper structure

**Given** an algorithm problem is being created
**When** writing the YAML frontmatter
**Then** the file should include:
- `type: "algorithm"`
- `difficulty: 1` (simple, <20 lines)
- `chapter: <chapter_order>` (associated chapter)
- `time_limit: 1000` or higher for beginners
- `memory_limit: 256`
- `solution_name.python` with function name
- `code_template.python` with starter code
- `test_cases` with at least one sample

#### Scenario: Algorithm problem is beginner-appropriate

**Given** an algorithm problem for beginners
**When** designing the problem
**Then**:
- Solution should be under 20 lines of code
- Clear input/output format
- Include helpful hints
- Sample test case with explanation

---

### Requirement: Code Examples

All code examples in chapters MUST be accurate and tested.

#### Scenario: Code examples use proper syntax highlighting

**Given** a chapter contains code examples
**When** writing the Markdown
**Then** code blocks should use:
- ` ```python ` for standard code blocks
- ` ```python-exec ` for executable code blocks (platform feature)

#### Scenario: Code examples are verified

**Given** code examples are written
**When** validating the course content
**Then**:
- All code examples should be syntactically correct
- Code should run without errors when tested
- Output examples match actual execution

---

### Requirement: Content Localization

All course content MUST be in Chinese (Simplified) with appropriate English technical terms.

#### Scenario: Content language is consistent

**Given** course content is being created
**When** writing text content
**Then**:
- Main text in Chinese (Simplified)
- Technical terms in English where appropriate
- Code comments in Chinese for clarity

#### Scenario: File encoding is correct

**Given** course files are created
**When** saving files
**Then** all files should use UTF-8 encoding

---

### Requirement: YAML Format Compliance

All YAML frontmatter MUST follow project formatting rules.

#### Scenario: YAML strings are properly quoted

**Given** a YAML frontmatter is being written
**When** setting string values
**Then** all strings must be quoted: `"value"` not `value`

#### Scenario: YAML arrays use proper format

**Given** a YAML array field
**When** writing the array
**Then** arrays must use brackets: `["item1", "item2"]`

#### Scenario: Required fields are present

**Given** a content file is being created
**When** writing the YAML frontmatter
**Then** required fields must be present:
- Course: `title`, `description`, `order`
- Chapter: `title`, `order`
- Problem: `title`, `type`, `difficulty`

---

## Cross-References

- Related to: [Format Specification](../../../docs/format-specification.md)
- Related to: [Course Authoring Guide](../../../docs/course-authoring-guide.md)
- Follows: [Project Conventions](../project.md)
