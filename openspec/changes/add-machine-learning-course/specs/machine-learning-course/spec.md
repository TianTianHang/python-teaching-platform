# machine-learning-course Specification

## Purpose

This specification defines the requirements for a comprehensive machine learning basics course that teaches traditional ML algorithms using NumPy, Pandas, Matplotlib, and scikit-learn libraries. The course assumes students have completed Python 入门 and builds on that foundation.

## ADDED Requirements

### Requirement: Course Metadata

The course MUST have properly configured metadata in `courses/machine-learning-basics/course.md`.

#### Scenario: Course metadata includes ML-specific fields

**Given** the project follows the standard course format
**When** creating the Machine Learning Basics course
**Then** the course.md file should contain:
- `title`: "机器学习基础"
- `description`: A 50-200 character description in Chinese mentioning ML, NumPy, Pandas, scikit-learn
- `order`: 2 (after python-intro)
- `difficulty`: 2 (medium)
- `prerequisites`: ["python-intro"]
- `tags`: Array including "机器学习", "ml", "numpy", "pandas", "scikit-learn"

#### Scenario: Course folder structure exists

**Given** the course is being created
**When** setting up the course structure
**Then** the following directories should exist:
- `courses/machine-learning-basics/`
- `courses/machine-learning-basics/chapters/`
- `courses/machine-learning-basics/problems/`

---

### Requirement: Chapter Structure

The course MUST contain 6 focused chapters covering ML fundamentals in a logical progression.

#### Scenario: All chapters are created with proper metadata

**Given** the course folder structure exists
**When** creating all 6 chapters
**Then** each chapter file should:
- Use naming format `chapter-{order:02d}-{slug}.md`
- Have `title` field in Chinese
- Have sequential `order` field (1-6)
- Contain content in Markdown format with 知识点 sections

#### Scenario: Chapter topics cover complete ML introduction

**Given** the course structure
**When** listing all chapter topics
**Then** the following topics must be covered:
1. NumPy 与 Pandas 基础 (NumPy and Pandas Basics) - order: 1
2. 数据可视化与 Matplotlib (Data Visualization with Matplotlib) - order: 2
3. 线性回归 (Linear Regression) - order: 3
4. 逻辑回归 (Logistic Regression) - order: 4
5. 支持向量机 (Support Vector Machines) - order: 5
6. K 近邻算法 (K-Nearest Neighbors) - order: 6

#### Scenario: Chapter 1 covers NumPy and Pandas fundamentals

**Given** Chapter 1 introduces ML libraries
**When** writing the chapter content
**Then** Chapter 1 MUST include:
- NumPy array creation and operations
- NumPy broadcasting and arithmetic
- Pandas Series and DataFrame basics
- Data manipulation and cleaning with Pandas
- Practical exercises using NumPy and Pandas

#### Scenario: Chapter 2 covers Matplotlib visualization

**Given** Chapter 2 teaches data visualization
**When** writing the chapter content
**Then** Chapter 2 MUST include:
- Basic plot types: line, scatter, bar, histogram
- Figure customization: titles, labels, legends
- Subplots and layout management
- Data distribution visualization techniques

#### Scenario: Chapter 3 covers Linear Regression

**Given** Chapter 3 introduces the first ML algorithm
**When** writing the chapter content
**Then** Chapter 3 MUST include:
- Linear regression concepts and math
- Gradient descent algorithm explanation
- NumPy implementation of gradient descent
- scikit-learn LinearRegression usage
- Model evaluation metrics (MSE, R²)

#### Scenario: Chapter 4 covers Logistic Regression

**Given** Chapter 4 covers binary classification
**When** writing the chapter content
**Then** Chapter 4 MUST include:
- Classification vs regression concepts
- Sigmoid function and decision boundaries
- Cross-entropy loss function
- scikit-learn LogisticRegression usage
- Classification metrics (accuracy, precision, recall, F1)

#### Scenario: Chapter 5 covers Support Vector Machines

**Given** Chapter 5 covers SVM algorithms
**When** writing the chapter content
**Then** Chapter 5 MUST include:
- SVM concepts: hyperplanes, margins, support vectors
- Kernel functions: linear, polynomial, RBF
- scikit-learn SVC usage
- Hyperparameter tuning (C, gamma)
- Multi-class classification with SVM

#### Scenario: Chapter 6 covers K-Nearest Neighbors

**Given** Chapter 6 covers KNN algorithm
**When** writing the chapter content
**Then** Chapter 6 MUST include:
- KNN algorithm principles
- Distance metrics (Euclidean, Manhattan)
- K value selection strategies
- scikit-learn KNeighborsClassifier usage
- KNN for regression (KNeighborsRegressor)
- Pros and cons of KNN

---

### Requirement: Sequential Chapter Unlock

All chapters after Chapter 1 MUST have sequential `unlock_conditions` to enforce progressive learning.

#### Scenario: Chapter 1 is the entry point with no unlock conditions

**Given** the course has 6 chapters
**When** configuring Chapter 1 (NumPy 与 Pandas 基础)
**Then** the chapter frontmatter should NOT include `unlock_conditions`

#### Scenario: Each subsequent chapter requires the previous chapter

**Given** a chapter with order N (where 2 ≤ N ≤ 6)
**When** configuring the chapter frontmatter
**Then** the chapter MUST include `unlock_conditions` with:
- `type: "prerequisite"`
- `prerequisites: [N-1]` (array containing the previous chapter's order)

#### Scenario: Complete unlock chain is configured

**Given** all 6 chapters are configured
**When** reviewing the unlock structure
**Then** the complete chain should be:
- Ch 1 (no unlock) → Ch 2 (requires 1) → Ch 3 (requires 2) → Ch 4 (requires 3) → Ch 5 (requires 4) → Ch 6 (requires 5)

---

### Requirement: Exercise Distribution

Each chapter MUST include 1-2 focused exercises, totaling approximately 6-12 exercises for the course.

#### Scenario: Exercise types are appropriate for ML course

**Given** the course focuses on ML libraries and algorithms
**When** creating exercises for chapters
**Then** the distribution should be approximately:
- 50% Algorithm Problems (NumPy/Pandas manipulation, sklearn implementation)
- 30% Choice Questions (ML theory and concept understanding)
- 20% Fill-blank Questions (API usage and terminology)

#### Scenario: Algorithm problems use ML libraries

**Given** an algorithm problem is being created
**When** designing the problem
**Then**:
- Problems should use NumPy for array operations
- Problems should use Pandas for data manipulation
- Problems should use scikit-learn for ML model implementation
- Solutions should follow sklearn API conventions

#### Scenario: Choice questions test ML concepts

**Given** a choice question is being created
**When** writing the question content
**Then** it should:
- Test understanding of ML algorithms and theory
- Cover concepts like loss functions, kernels, distance metrics
- Include explanations in the content body

#### Scenario: Total exercise count meets target

**Given** 6 chapters with 1-2 exercises each
**When** all exercises are created
**Then** the total count should be 6-12 exercises

#### Scenario: Exercise difficulty is appropriate

**Given** the target audience is intermediate Python learners
**When** setting exercise difficulty
**Then**:
- Most exercises should be `difficulty: 2` (medium)
- Reflects the intermediate nature of ML content

---

### Requirement: Code Examples

All code examples in chapters MUST demonstrate proper usage of ML libraries.

#### Scenario: Code examples use appropriate syntax highlighting

**Given** a chapter contains code examples
**When** writing the Markdown
**Then** code blocks should use:
- ` ```python-exec ` for interactive NumPy/Pandas demonstrations
- ` ```python ` for longer algorithm implementations and reference code

#### Scenario: NumPy examples follow best practices

**Given** code examples using NumPy
**When** writing NumPy code
**Then**:
- Use vectorized operations over loops
- Demonstrate broadcasting where appropriate
- Show common array operations (reshape, transpose, indexing)

#### Scenario: Pandas examples follow best practices

**Given** code examples using Pandas
**When** writing Pandas code
**Then**:
- Use loc/iloc for indexing
- Demonstrate method chaining where appropriate
- Show common data manipulation patterns

#### Scenario: scikit-learn examples follow standard API

**Given** code examples using scikit-learn
**When** writing sklearn code
**Then**:
- Follow fit()/predict() pattern
- Demonstrate train/test split
- Show model evaluation with appropriate metrics

---

### Requirement: Prerequisite Course Reference

The course MUST correctly reference the python-intro course as a prerequisite.

#### Scenario: Course has valid prerequisite

**Given** the machine-learning-basics course is created
**When** checking the prerequisites field
**Then**:
- `prerequisites` must include `"python-intro"`
- The referenced course must exist in the repository

---

### Requirement: Content Localization

All course content MUST be in Chinese (Simplified) with appropriate English technical terms.

#### Scenario: ML terminology is properly translated

**Given** ML course content is being created
**When** writing about ML concepts
**Then**:
- Main text in Chinese (Simplified)
- ML terms in English where appropriate (e.g., "线性回归 (Linear Regression)")
- Library names and API references in English
- Code comments in Chinese for clarity

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

#### Scenario: Prerequisite array is valid

**Given** the course has prerequisites
**When** writing the prerequisites field
**Then**:
- Must be an array format: `["python-intro"]`
- All prerequisite course slugs must exist

---

### Requirement: Chapter Numbering Consistency

All chapter numbers MUST be consistent across filenames, frontmatter, and problem references.

#### Scenario: No gaps in chapter numbering

**Given** the course has 6 chapters
**When** listing all chapters
**Then** the `order` field must be 1-6 with no missing numbers

#### Scenario: Filename matches order field

**Given** a chapter file exists
**When** comparing filename to frontmatter
**Then** the number in `chapter-XX-slug.md` MUST match the `order` field in YAML

#### Scenario: Problem references point to valid chapters

**Given** a problem has a `chapter` field
**When** checking the reference
**Then** a chapter with that `order` MUST exist in the course
