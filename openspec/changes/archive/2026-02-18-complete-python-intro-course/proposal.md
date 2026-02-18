# Proposal: Complete Python 入门 Course

## Summary

Extend the existing Python 入门 course from 8 chapters to 17 chapters by adding essential Python topics that are currently missing and reorganizing the chapter order for better learning progression. This will create a comprehensive introductory course that covers all fundamental Python concepts needed for beginners to progress to intermediate levels.

## Motivation

The current Python 入门 course (8 chapters) covers core concepts but has several issues:

1. **Missing essential topics**:
   - **数字(Number)** - Detailed coverage of numeric types and operations
   - **元组 (Tuples)** - A core built-in sequence type
   - **集合 (Sets)** - Essential for data deduplication and set operations
   - **字符串详解 (String Operations)** - Detailed string methods and formatting
   - **文件操作 (File Operations)** - Reading and writing files is a basic programming skill
   - **异常处理 (Exception Handling)** - Essential for writing robust code
   - **模块与包 (Modules and Packages)** - Understanding Python's import system
   - **面向对象基础 (OOP Basics)** - Classes and objects are fundamental to Python
   - **列表推导式 (List Comprehensions)** - Pythonic way of creating lists

2. **Suboptimal chapter order**: The current order mixes control flow before covering all data types, which can be confusing for beginners.

## Proposed Solution

### Reorganized 17-Chapter Structure

**Rationale for the new order**: Topics progress from simple to complex, covering all basic data types first, then control flow, then advanced features.

| 章节 | 标题 | 状态 | 说明 |
|------|------|------|------|
| 第1章 | Python简介与环境搭建 | 现有 | Introduction & Setup |
| 第2章 | 变量与数据类型 | 现有 | Variables & Data Types (basic types) |
| 第3章 | **数字(Number)** | **新增** | 整数、浮点数、复数、math模块 |
| 第4章 | 运算符 | 现有 | Arithmetic, comparison, logical |
| 第5章 | **字符串详解** | **新增** | String methods, formatting, slicing |
| 第6章 | 列表 | 现有 | List creation, operations, slicing |
| 第7章 | **元组** | **新增** | Immutable sequences, unpacking |
| 第8章 | **集合** | **新增** | Set operations, deduplication |
| 第9章 | 字典 | 现有 | Dictionary creation, access, operations |
| 第10章 | 控制流 - 条件语句 | 现有 | if, if-else, if-elif-else |
| 第11章 | 控制流 - 循环 | 现有 | while, for, break, continue |
| 第12章 | **列表推导式与生成器** | **新增** | List comprehensions, generators |
| 第13章 | 函数基础 | 现有 | Function definition, parameters, return |
| 第14章 | **文件操作** | **新增** | Read/write files, context managers |
| 第15章 | **异常处理** | **新增** | try-except, raising exceptions |
| 第16章 | **模块与包** | **新增** | Import, standard library, custom modules |
| 第17章 | **面向对象基础** | **新增** | Classes, objects, inheritance |

### New Chapter Details

#### 第3章: 数字(Number)
- Numeric types: int, float, complex
- Type conversion between numeric types
- Mathematical operations
- The `math` module introduction
- Random numbers with `random` module
- Number system basics (binary, octal, hex)

#### 第5章: 字符串详解
- String creation and basic operations
- String methods (find, replace, split, join, strip, etc.)
- String formatting (f-strings, format(), %)
- String slicing and indexing
- Escape characters

#### 第7章: 元组
- Tuple creation and immutability
- Tuple operations and methods
- Tuple unpacking and packing
- Named tuples (brief introduction)
- When to use tuples vs lists

#### 第8章: 集合
- Set creation and properties
- Set operations (union, intersection, difference)
- Set methods (add, remove, update)
- Frozen sets
- Use cases for sets (deduplication, membership testing)

#### 第12章: 列表推导式与生成器
- List comprehension syntax
- Generator expressions
- Generator functions with yield
- Performance considerations
- When to use comprehensions vs loops

#### 第14章: 文件操作
- Opening and closing files
- Reading files (read, readline, readlines)
- Writing files (write, writelines)
- Context managers (with statement)
- File modes and encoding
- Working with file paths

#### 第15章: 异常处理
- What are exceptions
- try-except blocks
- Catching specific exceptions
- else and finally clauses
- Raising exceptions
- Common exception types

#### 第16章: 模块与包
- Import statements and variations
- Standard library modules overview
- Creating custom modules
- Package structure
- `__name__ == "__main__"`
- pip and third-party packages (brief)

#### 第17章: 面向对象基础
- Classes and objects
- Attributes and methods
- `__init__` constructor
- Inheritance basics
- Encapsulation concept
- Class vs instance attributes

### Update Course Metadata

Update `courses/python-intro/course.md` to:
- Reflect the new 17-chapter structure with reorganized order
- Update chapter links in the course outline
- Adjust estimated learning time (from 8-16 hours to 17-34 hours)
- Note the reorganized learning progression

### Exercise Distribution

Add 2-3 exercises per new chapter (~18-27 new exercises):
- **60% Choice Questions** (~11-16 questions)
- **30% Fill-blank Questions** (~6-8 questions)
- **10% Algorithm Problems** (~2-3 problems)

### Target Audience

The same as the existing course:
- Complete beginners with zero programming experience
- Students who have completed chapters 1-8
- Learners preparing for intermediate Python topics

## Alternatives Considered

### Alternative 1: Create a Separate Intermediate Course
Put these topics in a new "Python Intermediate" course.
- **Pros**: Clear separation of difficulty levels
- **Cons**: These topics are fundamental and should be in the intro course; learners would have to navigate between courses

### Alternative 2: Keep Course at 8 Chapters
Accept the current course as complete enough.
- **Pros**: No additional work needed
- **Cons**: Learners miss essential topics; course feels incomplete compared to other intro courses

### Alternative 3: Add Selected Topics Only
Add only 3-4 most critical topics.
- **Pros**: Faster to implement
- **Cons**: Still leaves gaps; inconsistent approach to topic coverage

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Course becomes too long | Medium | Clear chapter structure allows learners to pace themselves |
| Some topics may be too advanced | Low | Keep explanations simple and beginner-friendly |
| Exercise quality may vary | Medium | Follow existing exercise patterns and templates |
| Duplicate content with existing chapters | Low | Review existing content before writing new chapters |

## Dependencies

- Existing `python-intro` course (chapters 1-8) must remain unchanged
- Exercise templates in `courses/_templates/` must be followed
- The `python-intro-course` spec will need to be updated

## Success Criteria

- [ ] 9 new chapters created (chapter-03, chapter-05, chapter-07, chapter-08, chapter-12, chapter-14, chapter-15, chapter-16, chapter-17)
- [ ] Existing chapters reordered (1→1, 2→2, 3→4, 4→10, 5→11, 6→6, 7→9, 8→13)
- [ ] 18-27 new exercises created
- [ ] Course metadata updated to reflect 17 chapters with new order
- [ ] All content follows project format conventions
- [ ] Code examples are tested and verified
- [ ] YAML validation passes without errors
- [ ] All chapter orders are sequential (1-17)

## Open Questions

1. Should file operations include JSON handling?
   - **Recommendation**: Keep it simple - basic text file operations only, defer JSON to a data handling course

2. Should OOP include more advanced topics like polymorphism?
   - **Recommendation**: No - keep it to basic classes, instances, and simple inheritance only

3. Should we add a final capstone project chapter?
   - **Recommendation**: Defer to a separate project-based course; keep this course focused on concepts

## Related Changes

- Original course: [add-python-intro-course](archive/2026-01-26-add-python-intro-course/)
- Spec to modify: `python-intro-course`

## References

- [Project Context](../project.md)
- [python-intro-course Spec](../specs/python-intro-course/spec.md)
- [菜鸟教程 Python3 教程](https://www.runoob.com/python3/python3-tutorial.html)
- [Python 官方文档](https://docs.python.org/3/)
