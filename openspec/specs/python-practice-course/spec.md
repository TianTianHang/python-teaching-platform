# python-practice-course Specification

## Purpose
TBD - created by archiving change add-python-practice-course. Update Purpose after archive.
## Requirements
### Requirement: Course Structure

The course MUST be created as `courses/python-practice/` with a minimal structure containing only algorithm problems.

#### Scenario: Course directory structure

**Given** a new practice course is being created
**When** setting up the directory structure
**Then** the following should exist:
- `courses/python-practice/course.md`
- `courses/python-practice/problems/`
- No chapters directory required

#### Scenario: Course uses problems-only format

**Given** the practice course design
**When** structuring the course content
**Then** the course MUST:
- Not include any chapter files
- Contain only algorithm problem files
- Allow problems to be accessed without chapter prerequisites

---

### Requirement: Course Metadata

The course MUST have properly configured metadata targeting Python beginners.

#### Scenario: Course frontmatter is configured

**Given** the course.md file
**When** writing the YAML frontmatter
**Then** it MUST contain:
- `title`: "Python 实践练习"
- `description`: 50-200 character description in Chinese
- `order`: A unique numeric order
- `difficulty`: 1 (beginner level)
- `tags`: Including "python", "practice", "algorithm", "字符串", "列表", "字典", "元组", "集合", "类型转换", "格式化", "控制流"

#### Scenario: Course description sets clear expectations

**Given** the course metadata
**When** a learner views the course
**Then** the description should:
- Emphasize it's for practice (no theory chapters)
- Mention the comprehensive Python language coverage
- Indicate it's beginner-friendly

---

### Requirement: Problem Distribution

The course MUST contain 35-45 algorithm problems distributed across multiple knowledge categories.

#### Scenario: Problem category distribution

**Given** the course problem set
**When** counting problems by category
**Then** the distribution should be approximately:
- 5 basic math problems
- 6 string problems
- 6 list problems
- 6 dictionary problems
- 3 tuple problems
- 4 set problems
- 4 type conversion problems
- 3 string formatting problems
- 4 control flow problems

#### Scenario: All problems are algorithm type

**Given** any problem in the course
**When** checking the problem type
**Then** it MUST be:
- `type: "algorithm"`
- `difficulty: 1` (simple/beginner)
- NOT have a `chapter` field (course is problems-only)

#### Scenario: Problem files use descriptive naming

**Given** a problem file
**When** naming the file
**Then** it should follow the pattern:
- Math problems: `math-{operation}.md`
- String problems: `string-{operation}.md`
- List problems: `list-{operation}.md`
- Dictionary problems: `dict-{operation}.md`
- Tuple problems: `tuple-{operation}.md`
- Set problems: `set-{operation}.md`
- Type conversion: `convert-{from}-{to}.md`
- Formatting: `format-{operation}.md`
- Control flow: `flow-{operation}.md`

---

### Requirement: Basic Math Problems

Math problems MUST teach basic numeric operations with beginner-friendly descriptions.

#### Scenario: Math problem covers a single operation

**Given** a math problem
**When** reading the problem description
**Then** it should focus on:
- One primary math operation (abs, power, round, divmod, even/odd)
- Simple numeric input/output
- Clear example showing expected behavior

#### Scenario: Math problem includes helpful hints

**Given** a math problem
**When** reading the hints section
**Then** it should mention:
- Which built-in function or operator to use
- Example of the syntax
- Any edge cases (negative numbers, zero)

#### Scenario: Required math operations are covered

**Given** the complete set of math problems
**When** listing all covered operations
**Then** the following MUST be included:
- Getting absolute value
- Calculating power
- Rounding numbers
- Getting quotient and remainder
- Checking even/odd

---

### Requirement: String Problems

String problems MUST teach basic string operations with beginner-friendly descriptions.

#### Scenario: String problem covers a single operation

**Given** a string problem
**When** reading the problem description
**Then** it should focus on:
- One primary string operation (length, concat, case, reverse, count, strip)
- Simple input/output without complex parsing
- Clear example showing expected behavior

#### Scenario: String problem includes helpful hints

**Given** a string problem
**When** reading the hints section
**Then** it should mention:
- Which string method or operation to use
- Example of the method syntax
- Any edge cases to consider

#### Scenario: Required string operations are covered

**Given** the complete set of string problems
**When** listing all covered operations
**Then** the following MUST be included:
- Getting string length
- String concatenation
- Case conversion (upper/lower)
- String reversal
- Character counting
- Removing whitespace

---

### Requirement: List Problems

List problems MUST teach basic list operations with beginner-friendly descriptions.

#### Scenario: List problem covers a single operation

**Given** a list problem
**When** reading the problem description
**Then** it should focus on:
- One primary list operation (max, min, indexing, filter, unique, merge)
- Simple numeric or string lists
- Clear example showing expected behavior

#### Scenario: List problem includes helpful hints

**Given** a list problem
**When** reading the hints section
**Then** it should mention:
- Which list method or built-in function to use
- Example of the operation syntax
- Whether a loop or built-in function is preferred

#### Scenario: Required list operations are covered

**Given** the complete set of list problems
**When** listing all covered operations
**Then** the following MUST be included:
- Finding maximum value
- Finding minimum value
- List indexing (accessing elements)
- Filtering elements (e.g., even numbers)
- Removing duplicates
- Merging lists

---

### Requirement: Dictionary Problems

Dictionary problems MUST teach basic dictionary operations with beginner-friendly descriptions.

#### Scenario: Dictionary problem covers a single operation

**Given** a dictionary problem
**When** reading the problem description
**Then** it should focus on:
- One primary dictionary operation (get, add, check key, count, invert, merge)
- Simple key-value pairs
- Clear example showing expected behavior

#### Scenario: Dictionary problem includes helpful hints

**Given** a dictionary problem
**When** reading the hints section
**Then** it should mention:
- Which dictionary method to use
- How to handle missing keys
- Whether a loop or dictionary method is preferred

#### Scenario: Required dictionary operations are covered

**Given** the complete set of dictionary problems
**When** listing all covered operations
**Then** the following MUST be included:
- Getting value by key
- Adding new key-value pair
- Checking if key exists
- Counting item frequency
- Inverting key-value pairs
- Merging dictionaries

---

### Requirement: Tuple Problems

Tuple problems MUST teach basic tuple operations with beginner-friendly descriptions.

#### Scenario: Tuple problem covers a single operation

**Given** a tuple problem
**When** reading the problem description
**Then** it should focus on:
- One primary tuple operation (access, merge, convert)
- Simple tuple inputs
- Clear example showing expected behavior

#### Scenario: Tuple problem includes helpful hints

**Given** a tuple problem
**When** reading the hints section
**Then** it should mention:
- Tuples are immutable (cannot be modified)
- Which operation to use
- Difference from lists where relevant

#### Scenario: Required tuple operations are covered

**Given** the complete set of tuple problems
**When** listing all covered operations
**Then** the following MUST be included:
- Accessing tuple elements by index
- Merging tuples
- Converting tuple to list

---

### Requirement: Set Problems

Set problems MUST teach basic set operations with beginner-friendly descriptions.

#### Scenario: Set problem covers a single operation

**Given** a set problem
**When** reading the problem description
**Then** it should focus on:
- One primary set operation (create, union, intersection, difference)
- Simple set operations
- Clear example showing expected behavior

#### Scenario: Set problem includes helpful hints

**Given** a set problem
**When** reading the hints section
**Then** it should mention:
- Sets contain only unique elements
- Which operator or method to use
- Visual representation of the operation (Venn diagram concept)

#### Scenario: Required set operations are covered

**Given** the complete set of set problems
**When** listing all covered operations
**Then** the following MUST be included:
- Creating set from list (removing duplicates)
- Union of two sets
- Intersection of two sets
- Difference of two sets

---

### Requirement: Type Conversion Problems

Type conversion problems MUST teach basic type conversion operations with beginner-friendly descriptions.

#### Scenario: Type conversion problem covers a single conversion

**Given** a type conversion problem
**When** reading the problem description
**Then** it should focus on:
- One primary conversion operation (str to int, int to str, etc.)
- Clear input and output types
- Clear example showing expected behavior

#### Scenario: Type conversion problem includes helpful hints

**Given** a type conversion problem
**When** reading the hints section
**Then** it should mention:
- Which built-in function to use (int(), str(), list())
- Common pitfalls (e.g., trying to convert non-numeric string to int)

#### Scenario: Required type conversion operations are covered

**Given** the complete set of type conversion problems
**When** listing all covered operations
**Then** the following MUST be included:
- String to integer
- Integer to string
- List to joined string
- String to list (using list() or split())

---

### Requirement: String Formatting Problems

String formatting problems MUST teach basic string formatting operations with beginner-friendly descriptions.

#### Scenario: String formatting problem covers a single operation

**Given** a string formatting problem
**When** reading the problem description
**Then** it should focus on:
- One primary formatting operation (f-string, padding, joining)
- Clear example showing expected output format

#### Scenario: String formatting problem includes helpful hints

**Given** a string formatting problem
**When** reading the hints section
**Then** it should mention:
- Which formatting method to use
- Example of the syntax
- Python 3.6+ f-string syntax where applicable

#### Scenario: Required string formatting operations are covered

**Given** the complete set of string formatting problems
**When** listing all covered operations
**Then** the following MUST be included:
- F-string formatting
- String padding (zfill, rjust, ljust)
- Joining strings with separator

---

### Requirement: Control Flow Problems

Control flow problems MUST teach basic control flow patterns with beginner-friendly descriptions.

#### Scenario: Control flow problem covers a single pattern

**Given** a control flow problem
**When** reading the problem description
**Then** it should focus on:
- One primary control flow pattern (if/else, for loop)
- Clear logic requirements
- Clear example showing expected behavior

#### Scenario: Control flow problem includes helpful hints

**Given** a control flow problem
**When** reading the hints section
**Then** it should mention:
- Which control structure to use (if/elif/else, for loop)
- Basic syntax pattern
- How to structure the logic

#### Scenario: Required control flow operations are covered

**Given** the complete set of control flow problems
**When** listing all covered operations
**Then** the following MUST be included:
- Finding max of three numbers (if/elif/else)
- Counting positive numbers (for loop)
- Score to grade conversion (if/elif/else)
- Sum of range (range() function)

---

### Requirement: Problem Description Format

All problem descriptions MUST follow a consistent, beginner-friendly format.

#### Scenario: Problem description is concise

**Given** any problem in the course
**When** reading the problem description
**Then** it should:
- Be 1-2 sentences maximum
- Use simple language
- Clearly state the required operation
- Avoid technical jargon

#### Scenario: Problem includes hint section

**Given** any problem in the course
**When** reviewing the problem structure
**Then** it MUST include:
- A "### 提示" section
- Guidance on which data structure/operation to use
- Example syntax or method name
- Edge case considerations

#### Scenario: Problem has appropriate test cases

**Given** an algorithm problem
**When** reviewing test_cases in frontmatter
**Then** it MUST include:
- At least one `is_sample: true` test case
- 3-5 total test cases covering:
  - Normal case
  - Edge case (empty input, single element)
  - Boundary case

---

### Requirement: No Unlock Conditions

Problems in this practice course MUST NOT have unlock conditions to allow flexible practice.

#### Scenario: Problems are freely accessible

**Given** a learner accessing the course
**When** viewing any problem
**Then** the problem MUST NOT:
- Have `unlock_conditions` in frontmatter
- Require completion of other problems
- Have date-based restrictions

#### Scenario: Problems can be solved in any order

**Given** the course problem set
**When** a learner browses problems
**Then** they should be able to:
- Start with any problem
- Skip problems they find difficult
- Return to problems later

