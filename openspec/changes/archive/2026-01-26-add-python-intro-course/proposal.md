# Proposal: Add Python 入门 Course

## Summary

Create a comprehensive Python 入门 (Python Introduction) course designed for complete beginners with zero programming experience. The course will cover fundamental Python concepts including basic syntax, data structures, and functions, with a focus on conceptual understanding through choice and fill-in-the-blank exercises.

## Motivation

Python is one of the most beginner-friendly programming languages, and a structured introductory course is essential for:
- Complete beginners to start their programming journey
- Establishing solid foundations in Python programming concepts
- Preparing learners for more advanced Python topics

## Proposed Solution

### Course Structure

Create a new course `python-intro` with the following chapters:

1. **Python简介与环境搭建** (Introduction & Setup)
   - What is Python, history, features
   - Platform's built-in Jupyter notebook (`/jupyter`)
   - Installation and local environment setup (optional)
   - First Python program (Hello World)

2. **变量与数据类型** (Variables & Data Types)
   - Variables and naming rules
   - Basic data types: int, float, str, bool
   - Type conversion
   - Input and output

3. **运算符** (Operators)
   - Arithmetic operators
   - Comparison operators
   - Logical operators
   - Operator precedence

4. **控制流 - 条件语句** (Control Flow - Conditionals)
   - if statements
   - if-else statements
   - if-elif-else statements
   - Nested conditionals

5. **控制流 - 循环** (Control Flow - Loops)
   - while loops
   - for loops
   - Loop control (break, continue)
   - Nested loops

6. **列表** (Lists)
   - List creation and indexing
   - List operations and methods
   - List slicing
   - List traversal

7. **字典** (Dictionaries)
   - Dictionary creation and access
   - Dictionary operations and methods
   - Dictionary traversal
   - Common use cases

8. **函数基础** (Functions Basics)
   - Function definition and calls
   - Parameters and arguments
   - Return values
   - Scope and lifetime

### Exercise Distribution

Each chapter will include 2-3 exercises, totaling approximately 18-24 exercises:

- **60% Choice Questions** (~12-15 questions) - Test conceptual understanding
- **30% Fill-blank Questions** (~6-8 questions) - Reinforce syntax and key concepts
- **10% Algorithm Problems** (~2-3 simple problems) - Basic coding practice

### Target Audience

- Complete beginners with zero programming experience
- Students who prefer conceptual learning before heavy coding
- Learners who want a structured introduction to Python

### Code Examples Strategy

- Use standard ` ```python ` blocks for code that is meant to be read
- Use ` ```python-exec ` blocks for interactive examples that students can run directly in the course content
- Prioritize `python-exec` for:
  - First program examples (Hello World)
  - Concept demonstrations (variables, operators, control flow)
  - Data structure operations
  - Function examples
- Use standard ` ```python ` for:
  - Longer code snippets that are reference material
  - Solution implementations for algorithm problems

## Alternatives Considered

### Alternative 1: Project-based Course
Focus on building small projects from the start.
- **Pros**: Practical, engaging results
- **Cons**: Too advanced for zero-experience beginners

### Alternative 2: Video-first Course
Use video lectures as primary content.
- **Pros**: Visual learning
- **Cons**: Not supported by current platform format

### Alternative 3: Heavy Programming Focus
Emphasize coding exercises over concepts.
- **Pros**: More programming practice
- **Cons**: May overwhelm beginners; selected approach balances concepts first

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Content too simple for some learners | Low | Include optional challenge problems |
| Progression too slow | Low | Clear chapter structure allows self-paced learning |
| Exercise quality issues | Medium | Use peer review and validation process |

## Dependencies

None - this is a standalone course with no prerequisites.

## Success Criteria

- [ ] Course metadata created in `courses/python-intro/course.md`
- [ ] All 8 chapters created with proper YAML frontmatter
- [ ] 18-24 exercises created (choice, fill-blank, algorithm)
- [ ] All content follows project format conventions
- [ ] Code examples are tested and verified
- [ ] YAML validation passes without errors

## Open Questions

1. Should we include error handling (exceptions) as a chapter?
   - **Decision**: Deferred to a future intermediate course

2. Should we include file operations?
   - **Decision**: Deferred to a future intermediate course

## Related Changes

- None - this is the first course in the repository

## References

- [Project Context](../project.md)
- [Format Specification](../../docs/format-specification.md)
- [Course Authoring Guide](../../docs/course-authoring-guide.md)
- [菜鸟教程 Python3 教程](https://www.runoob.com/python3/python3-tutorial.html) - Reference for course content structure and examples
