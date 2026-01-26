# Tasks: Add Python 入门 Course

## Prerequisites

- Read [project.md](../project.md) for format conventions
- Read [course authoring guide](../../docs/course-authoring-guide.md)
- Review [format specification](../../docs/format-specification.md)
- Review templates in `courses/_templates/`

## Content References

When authoring course content, you may reference:
- [菜鸟教程 Python3 教程](https://www.runoob.com/python3/python3-tutorial.html) - For structure and example ideas
- [Python 官方文档](https://docs.python.org/3/) - For authoritative technical details

## Implementation Tasks

### Phase 1: Course Setup

- [x] Create course folder structure: `courses/python-intro/`, `chapters/`, `problems/`
- [x] Create `courses/python-intro/course.md` with proper metadata
  - Set `title: "Python 入门"`
  - Write `description` (50-200 characters)
  - Set `order` value
- [x] Verify YAML syntax is correct (all strings quoted, arrays with brackets)

### Phase 2: Chapter Content Creation

- [x] Create `chapters/chapter-01-python-intro.md` - Python简介与环境搭建
  - Include: What is Python, history, features, installation, Hello World
  - Add 2-3 exercises (choice + fill-blank)

- [x] Create `chapters/chapter-02-variables-types.md` - 变量与数据类型
  - Include: Variables, naming, int/float/str/bool, type conversion, input/output
  - Add 2-3 exercises (choice + fill-blank)

- [x] Create `chapters/chapter-03-operators.md` - 运算符
  - Include: Arithmetic, comparison, logical operators, precedence
  - Add 2-3 exercises (choice + fill-blank)

- [x] Create `chapters/chapter-04-conditionals.md` - 控制流 - 条件语句
  - Include: if, if-else, if-elif-else, nested conditionals
  - Add 2-3 exercises (choice + fill-blank)

- [x] Create `chapters/chapter-05-loops.md` - 控制流 - 循环
  - Include: while, for, break/continue, nested loops
  - Add 2-3 exercises (choice + fill-blank)

- [x] Create `chapters/chapter-06-lists.md` - 列表
  - Include: List creation, indexing, operations, slicing, traversal
  - Add 2-3 exercises (choice + fill-blank + 1 algorithm)

- [x] Create `chapters/chapter-07-dictionaries.md` - 字典
  - Include: Dictionary creation, access, operations, traversal
  - Add 2-3 exercises (choice + fill-blank + 1 algorithm)

- [x] Create `chapters/chapter-08-functions.md` - 函数基础
  - Include: Function definition, parameters, return values, scope
  - Add 2-3 exercises (choice + fill-blank + 1 algorithm)

### Phase 3: Exercise Creation

#### Choice Questions (~12-15 total)

- [x] Create choice questions for Chapter 1: Python简介与环境搭建
  - [x] `problems/python-history-choice.md`
  - [x] `problems/python-features-choice.md`

- [x] Create choice questions for Chapter 2: 变量与数据类型
  - [x] `problems/variable-naming-choice.md`
  - [x] `problems/data-types-choice.md`

- [x] Create choice questions for Chapter 3: 运算符
  - [x] `problems/arithmetic-operators-choice.md`
  - [x] `problems/logical-operators-choice.md`

- [x] Create choice questions for Chapter 4: 控制流 - 条件语句
  - [x] `problems/if-structure-choice.md`
  - [x] `problems/conditional-logic-choice.md`

- [x] Create choice questions for Chapter 5: 控制流 - 循环
  - [x] `problems/while-vs-for-choice.md`
  - [x] `problems/loop-control-choice.md`

- [x] Create choice questions for Chapter 6: 列表
  - [x] `problems/list-indexing-choice.md`
  - [x] `problems/list-methods-choice.md`

- [x] Create choice questions for Chapter 7: 字典
  - [x] `problems/dictionary-basics-choice.md`
  - [x] `problems/dictionary-operations-choice.md`

- [x] Create choice questions for Chapter 8: 函数基础
  - [x] `problems/function-definition-choice.md`
  - [x] `problems/function-parameters-choice.md`

#### Fill-blank Questions (~6-8 total)

- [x] Create fill-blank questions for Chapter 1: Python简介与环境搭建
  - [x] `problems/python-basics-fillblank.md`

- [x] Create fill-blank questions for Chapter 2: 变量与数据类型
  - [x] `problems/type-conversion-fillblank.md`

- [x] Create fill-blank questions for Chapter 3: 运算符
  - [x] `problems/operator-precedence-fillblank.md`

- [x] Create fill-blank questions for Chapter 4: 控制流 - 条件语句
  - [x] `problems/conditional-syntax-fillblank.md`

- [x] Create fill-blank questions for Chapter 5: 控制流 - 循环
  - [x] `problems/loop-syntax-fillblank.md`

- [x] Create fill-blank questions for Chapter 6: 列表
  - [x] `problems/list-operations-fillblank.md`

- [x] Create fill-blank questions for Chapter 7: 字典
  - [x] `problems/dictionary-access-fillblank.md`

- [x] Create fill-blank questions for Chapter 8: 函数基础
  - [x] `problems/function-syntax-fillblank.md`

#### Algorithm Problems (~2-3 simple problems)

- [x] Create algorithm problem for Chapter 6: 列表
  - [x] `problems/list-sum-algorithm.md` - Calculate sum of list elements

- [x] Create algorithm problem for Chapter 7: 字典
  - [x] `problems/dictionary-count-algorithm.md` - Count occurrences using dict

- [x] Create algorithm problem for Chapter 8: 函数基础
  - [x] `problems/simple-function-algorithm.md` - Implement a simple calculation function

### Phase 4: Validation and Testing

- [x] Run YAML syntax validation on all files
- [x] Verify all code examples are syntactically correct
- [x] Test all algorithm problem solutions
- [x] Check all chapter references in problems exist
- [x] Verify all required fields are present
- [x] Run `openspec validate add-python-intro-course --strict --no-interactive`

### Phase 5: Documentation

- [x] Update course.md with chapter links
- [x] Verify chapter content matches learning objectives
- [x] Check exercise difficulty is appropriate (mostly difficulty: 1)
- [x] Ensure total exercise count is 18-24

## Validation Criteria

- All YAML passes strict validation
- All code examples run without errors
- All chapter references in problems are valid
- Exercise distribution: ~60% choice, ~30% fill-blank, ~10% algorithm
- Content follows project conventions
- All files use UTF-8 encoding

## Notes

- Use templates from `courses/_templates/` as starting points
- Copy templates, never edit them directly
- Focus on conceptual understanding rather than complex coding
- Keep code examples simple and well-commented
- Target audience: zero programming experience
