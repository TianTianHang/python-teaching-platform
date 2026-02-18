# Capability: Python Introduction Course (Extended)

## Overview

This specification extends the existing Python 入门 (Introduction) course from 8 chapters to 17 chapters by adding essential Python topics that were missing from the original implementation and reorganizing the chapter order for better learning progression.

## MODIFIED Requirements

### Requirement: Chapter Structure

The course MUST contain 17 chapters covering fundamental Python topics in a logical progression.

#### Scenario: All chapters are created with proper metadata

**Given** the course folder structure exists
**When** creating all 17 chapters
**Then** each chapter file should:
- Use naming format `chapter-{order:02d}-{slug}.md`
- Have `title` field in Chinese
- Have sequential `order` field (1-17)
- Contain content in Markdown format

#### Scenario: Chapter topics cover complete introduction

**Given** the course structure
**When** listing all chapter topics
**Then** the following topics must be covered in order:
1. Python简介与环境搭建 (Introduction & Setup)
2. 变量与数据类型 (Variables & Data Types)
3. **数字(Number)** - Numeric types, math module, random module - NEW
4. 运算符 (Operators) - RENAMED from chapter 3
5. **字符串详解 (String Operations)** - String methods, formatting - NEW
6. 列表 (Lists)
7. **元组 (Tuples)** - Immutable sequences, unpacking - NEW
8. **集合 (Sets)** - Set operations, deduplication - NEW
9. 字典 (Dictionaries) - RENAMED from chapter 7
10. 控制流 - 条件语句 (Control Flow - Conditionals) - RENAMED from chapter 4
11. 控制流 - 循环 (Control Flow - Loops) - RENAMED from chapter 5
12. **列表推导式与生成器 (List Comprehensions & Generators)** - NEW
13. 函数基础 (Functions Basics) - RENAMED from chapter 8
14. **文件操作 (File Operations)** - Read/write files - NEW
15. **异常处理 (Exception Handling)** - try-except - NEW
16. **模块与包 (Modules and Packages)** - Import, standard library - NEW
17. **面向对象基础 (OOP Basics)** - Classes, objects - NEW

#### Scenario: Chapter order follows pedagogical best practices

**Given** the course structure
**When** examining the chapter progression
**Then**:
- Basic data types are covered before control flow (chapters 1-9 before 10-11)
- All data structures (lists, tuples, sets, dicts) are grouped together (chapters 6-9)
- Control flow comes after understanding data types
- Advanced topics (comprehensions, files, exceptions, modules, OOP) come last

#### Scenario: Course metadata is updated

**Given** the course has been extended to 17 chapters
**When** updating course.md
**Then** the file should:
- Include all 17 chapter links in the course outline
- Reflect the extended learning time (17-34 hours)
- Maintain all existing metadata fields

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

**Given** 17 chapters with 2-3 exercises each
**When** all exercises are created
**Then** the total count should be 34-51 exercises (including existing 27 exercises, adding 18-27 new exercises)

#### Scenario: Exercise difficulty is appropriate

**Given** the target audience is zero-experience beginners
**When** setting exercise difficulty
**Then**:
- Most exercises should be `difficulty: 1` (simple)
- Few to no exercises should be `difficulty: 2` or `3`

---

## ADDED Requirements

### Requirement: Chapter Reordering

Existing chapters MUST be renamed to reflect their new position in the course.

#### Scenario: Existing chapter files are renamed correctly

**Given** a chapter is being moved to a new position
**When** renaming the chapter file
**Then**:
- `chapter-03-operators.md` → `chapter-04-operators.md`
- `chapter-04-conditionals.md` → `chapter-10-conditionals.md`
- `chapter-05-loops.md` → `chapter-11-loops.md`
- `chapter-07-dictionaries.md` → `chapter-09-dictionaries.md`
- `chapter-08-functions.md` → `chapter-13-functions.md`
- `chapter-06-lists.md` remains unchanged

#### Scenario: Chapter order field is updated

**Given** a chapter file has been renamed
**When** updating the YAML frontmatter
**Then** the `order` field MUST match the new chapter number

#### Scenario: Problem chapter references are updated

**Given** existing problems reference old chapter numbers
**When** the chapters are reordered
**Then** the `chapter` field in problems MUST be updated:
- Chapter 3 → 4 (运算符 problems)
- Chapter 4 → 10 (条件语句 problems)
- Chapter 5 → 11 (循环 problems)
- Chapter 7 → 9 (字典 problems)
- Chapter 8 → 13 (函数 problems)

---

### Requirement: New Chapter Content Quality

Each new chapter (3, 5, 7, 8, 12, 14, 15, 16, 17) MUST maintain the same quality and pedagogical standards as existing chapters.

#### Scenario: New chapter follows existing structure

**Given** a new chapter is being authored
**When** writing chapter content
**Then** each chapter should include:
- Clear learning objectives
- Conceptual explanations with examples
- Code examples with `python` or `python-exec` syntax highlighting
- Key takeaways or summary points
- 2-3 associated exercises

#### Scenario: Code examples are appropriate for beginners

**Given** a new chapter contains code examples
**When** writing the code
**Then**:
- Code should be simple and well-commented
- Examples should demonstrate one concept at a time
- Output should be shown when applicable

#### Scenario: New chapter topics are appropriately scoped

**Given** a new chapter is planned
**When** defining the chapter scope
**Then**:
- Topics should be fundamental, not advanced
- Complex topics should be broken down into digestible parts
- Practical examples should be relatable to beginners

#### Scenario: Number chapter (Chapter 3) covers essential numeric concepts

**Given** chapter 3 is about numbers
**When** writing the content
**Then** it should cover:
- Numeric types: int, float, complex
- Type conversion between numeric types
- Mathematical operations and the `math` module
- Random numbers with `random` module
- Number system basics (binary, octal, hex) - briefly

---

### Requirement: Chapter Association for New Problems

New problems MUST reference the correct chapter order number.

#### Scenario: Problem chapter reference is valid

**Given** a new problem is being created
**When** setting the `chapter` field
**Then**:
- `chapter: 3` for 数字 problems
- `chapter: 5` for 字符串详解 problems
- `chapter: 7` for 元组 problems
- `chapter: 8` for 集合 problems
- `chapter: 12` for 列表推导式与生成器 problems
- `chapter: 14` for 文件操作 problems
- `chapter: 15` for 异常处理 problems
- `chapter: 16` for 模块与包 problems
- `chapter: 17` for 面向对象基础 problems

---

### Requirement: Algorithm Problem Complexity

New algorithm problems MUST remain simple and appropriate for beginners.

#### Scenario: Algorithm problem uses new concepts appropriately

**Given** an algorithm problem is created for new chapters
**When** designing the problem
**Then**:
- Solution should be under 30 lines of code
- Should use concepts taught in the corresponding chapter
- Include helpful hints for beginners
- Sample test case with explanation

#### Scenario: File operation problems are handled appropriately

**Given** an algorithm problem involves file operations (chapter 14)
**When** creating test cases
**Then**:
- Files should be created/mocked in the test environment
- Test cases should not rely on external files
- File paths should use relative paths or temp directories

#### Scenario: OOP problems are simple

**Given** an algorithm problem involves OOP (chapter 17)
**When** designing the problem
**Then**:
- Class should be simple with few methods
- Avoid complex inheritance patterns
- Focus on basic class definition and instantiation

---

## MODIFIED Requirements

### Requirement: Content Localization

All new course content MUST be in Chinese (Simplified) with appropriate English technical terms.

#### Scenario: Content language is consistent

**Given** new course content is being created
**When** writing text content
**Then**:
- Main text in Chinese (Simplified)
- Technical terms in English where appropriate
- Code comments in Chinese for clarity
- Consistency with existing chapters terminology

---

## ADDED Requirements

### Requirement: Chapter Numbering Consistency

All chapter numbers MUST be consistent across filenames, frontmatter, and problem references.

#### Scenario: No gaps in chapter numbering

**Given** the course has 17 chapters
**When** listing all chapters
**Then** the `order` field must be 1-17 with no missing numbers

#### Scenario: Filename matches order field

**Given** a chapter file exists
**When** comparing filename to frontmatter
**Then** the number in `chapter-XX-slug.md` MUST match the `order` field in YAML

#### Scenario: Problem references point to valid chapters

**Given** a problem has a `chapter` field
**When** checking the reference
**Then** a chapter with that `order` MUST exist in the course
