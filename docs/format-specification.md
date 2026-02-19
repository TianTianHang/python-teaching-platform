# 课程内容格式规范

本文档详细说明 Python 教学平台课程内容的标准格式规范，确保所有课程文档的一致性和可读性。

## 📋 目录

- [文件结构](#文件结构)
- [YAML Frontmatter](#yaml-frontmatter)
- [章节格式](#章节格式)
- [题目格式](#题目格式)
- [Markdown 规范](#markdown-规范)
- [质量要求](#质量要求)
- [模板使用](#模板使用)
- [常见错误](#常见错误)
- [支持](#支持)

## 📁 文件结构

### 标准目录结构

```
course-repository/
├── course-index.yaml                    # 可选的全局索引
├── courses/
│   ├── python-basics/                   # 课程文件夹（kebab-case）
│   │   ├── course.md                   # 课程元数据
│   │   ├── chapters/                   # 章节目录
│   │   │   ├── chapter-01-variables.md
│   │   │   └── chapter-02-control-flow.md
│   │   └── problems/                   # 题目目录
│   │       ├── two-sum.md              # 算法题
│   │       └── variable-naming.md      # 选择题
│   └── data-structures/
│       ├── course.md
│       ├── chapters/
│       └── problems/
└── assets/                             # 媒体资源
    └── images/
```

### 文件命名规范

- **课程文件夹**: `kebab-case` 格式（如 `python-basics`）
- **章节文件**: `chapter-{order:02d}-{slug}.md`（如 `chapter-01-variables.md`）
- **题目文件**: `{slug}.md`（如 `two-sum.md`）
- **课程元数据**: `course.md`（每个课程文件夹必需）
- **排序规则**: 按数字序号排序（01, 02, 03...）

## 🔧 YAML Frontmatter

### 必填字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `title` | string | 标题，必填 |
| `description` | string | 描述，必填（50-200字） |
| `order` | integer | 排序序号，必填 |

### 可选字段

| 字段名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `difficulty` | integer | `1` | 难度：`1`(简单)、`2`(中等)、`3`(困难) |
| `prerequisites` | array[] | `[]` | 前置课程列表 |
| `tags` | array[] | `[]` | 课程标签 |

### 课程 Frontmatter 示例

```yaml
---
title: "Python编程入门"
description: "从零开始学习Python编程，掌握Python基础语法、数据结构和编程思想。"
order: 1
difficulty: 1
prerequisites: []
tags: ["python", "基础", "编程入门"]
---
```

### 章节 Frontmatter 示例

```yaml
---
title: "Python基础语法"
order: 1
---
```

### 章节 Frontmatter 带解锁条件

```yaml
---
title: "Python进阶语法"
order: 2
unlock_conditions:
  type: prerequisite          # 解锁类型
  prerequisites:              # 前置章节 order 列表
    - 1
  unlock_date: "2025-03-01T00:00:00Z"  # 可选：解锁日期
---
```

### 章节解锁条件字段

章节可以设置 `unlock_conditions` 来控制学生访问权限。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `unlock_conditions` | dict | 章节解锁条件配置（可选） |
| └─ `type` | string | 解锁类型：`prerequisite`、`date`、`all`、`none` |
| └─ `prerequisites` | array[] | 前置章节 order 列表（整数） |
| └─ `unlock_date` | string | ISO 8601 格式的日期时间 |

### 章节解锁条件类型

| 类型 | 说明 | 必需字段 |
|------|------|----------|
| `none` | 无条件（默认） | 无 |
| `prerequisite` | 需要完成前置章节 | `prerequisites` |
| `date` | 指定日期后解锁 | `unlock_date` |
| `all` | 需要前置章节且指定日期后解锁 | `prerequisites`, `unlock_date` |

**注意**：章节解锁条件与题目解锁条件的区别：
- 章节前置条件使用 `order` 整数（如 `1`、`2`），题目使用文件名（如 `problem-01.md`）
- 章节解锁不支持 `minimum_percentage` 字段（全部完成或全部未完成）

### 题目 Frontmatter 通用字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `title` | string | 标题，必填 |
| `type` | string | 题目类型：`algorithm` 或 `choice`，必填 |
| `difficulty` | integer | 难度 1-3，必填 |
| `chapter` | integer | 所属章节顺序号（可选） |

### Chapter 字段说明

- `chapter` 字段为可选字段，用于将题目关联到特定章节
- 值为章节的 `order` 字段（章节顺序号），而非章节标题
- 如果指定的章节顺序号在课程中不存在，导入将失败并报错
- 如果不指定 `chapter` 字段，题目将不会关联到任何章节（`chapter=None`）
- 一个题目只能关联到一个章节

#### 使用示例

**关联到章节：**
```yaml
---
title: "变量赋值练习"
type: "algorithm"
difficulty: 1
chapter: 1  # 关联到 order=1 的章节
test_cases: [...]
solution_name: {python: variableAssignment}
---
```

**独立题目（不关联章节）：**
```yaml
---
title: "综合练习"
type: "algorithm"
difficulty: 2
# 未指定 chapter 字段，题目不关联到任何章节
test_cases: [...]
solution_name: {python: comprehensivePractice}
---
```

**错误示例（章节不存在）：**
```yaml
---
title: "错误示例"
type: "algorithm"
difficulty: 1
chapter: 99  # 如果课程中不存在 order=99 的章节，导入将失败
test_cases: [...]
solution_name: {python: errorExample}
---
```

**错误信息：**
```
ValueError: Chapter with order 99 not found in course 'Python基础'.
Problem '错误示例' cannot be imported.
Please ensure chapter order 99 exists in this course.
```

### 解锁条件字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `unlock_conditions` | dict | 解锁条件配置（可选） |
| └─ `type` | string | 解锁类型：`prerequisite`、`date`、`both`、`none` |
| └─ `prerequisites` | array[] | 前置题目文件名列表 |
| └─ `unlock_date` | string | ISO 8601 格式的日期时间 |
| └─ `minimum_percentage` | integer | 完成前置题目的最低百分比（0-100） |

### 解锁条件类型

| 类型 | 说明 | 必需字段 |
|------|------|----------|
| `none` | 无条件（默认） | 无 |
| `prerequisite` | 需要完成前置题目 | `prerequisites` |
| `date` | 指定日期后解锁 | `unlock_date` |
| `both` | 需要前置题目且指定日期后解锁 | `prerequisites`, `unlock_date` |

### 算法题特有字段

| 字段名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `time_limit` | integer | `1000` | 时间限制（毫秒） |
| `memory_limit` | integer | `256` | 内存限制（MB） |
| `solution_name` | dict | - | 函数名映射 |
| `test_cases` | array | - | 测试用例列表 |

### 选择题特有字段

| 字段名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `is_multiple_choice` | boolean | `false` | 是否多选 |
| `options` | dict | - | 选项字典（A-D） |
| `correct_answer` | string/array | - | 正确答案：单选为字符串，多选为数组 |

#### 选择题答案格式

**单选题：**
```yaml
correct_answer: "A"
```

**多选题：**
```yaml
is_multiple_choice: true
correct_answer: ["A", "B"]  # 多个答案用数组表示
```

### 填空题特有字段

| 字段名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `content_with_blanks` | text | - | 带空白标记的文本内容 |
| `blanks` | JSON | - | 空白答案配置 |
| `blank_count` | integer | - | 空白数量（可选，自动计算） |

#### 填空题空白格式

**格式1（推荐）：详细格式**
```yaml
blanks:
  blank1:
    answers: ["答案1", "备选答案"]
    case_sensitive: false
  blank2:
    answers: ["答案2"]
    case_sensitive: true
```

**格式2（简单）：简化数组格式**
```yaml
blanks:
  blanks: ["答案1", "答案2"]
  case_sensitive: false
```

**格式3：数组格式（支持多个答案）**
```yaml
blanks:
  blanks:
    - answers: ["答案1", "备选"]
      case_sensitive: false
    - answers: ["答案2"]
      case_sensitive: true
```

## 📖 章节格式

### 章节文件结构

每个章节都是一个独立的 markdown 文件，包含：
```yaml
---
title: "章节标题"
order: 1
---

## 章节标题

### 章节概述（可选）

简要概述本章内容和学习目标。

### 知识点 1：[知识点名称]

**描述：**
[详细的知识点描述]

**示例代码：**
```python
# 代码示例
def example_function():
    """函数描述"""
    # 代码实现
    pass
```

**解释：**
[对代码或概念的详细解释]


### 章节要求

- 每个章节至少包含 2-3 个知识点
- 代码示例必须正确且可运行
- 解释要详细，避免过于简略

## 📝 题目格式

### 算法题

#### 文件结构

```yaml
---
title: "两数之和"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "twoSum"
code_template:
  python: |
    def twoSum(nums, target):
        # 请在此实现你的代码
        pass
test_cases:
  - input: "[[2,7,11,15],9]"
    output: "[0,1]"
    is_sample: true
  - input: "[[3,2,4],6]"
    output: "[1,2]"
    is_sample: false
  # 解锁条件（可选）
  # unlock_conditions:
  #   type: "prerequisite"
  #   prerequisites: ["basic-arrays.md"]
  #   minimum_percentage: 100
---

## 题目描述

编写一个函数，接受一个整数数组 `nums` 和一个目标值 `target`，返回两个数的下标，使得它们的和等于 `target`。

### 输入格式
第一行：数组，用方括号表示
第二行：目标值

### 输出格式
返回两个数的下标，用方括号表示

### 示例

**输入：**
```
[2,7,11,15]
9
```

**输出：**
```
[0,1]
```

### 提示
你可以假设每种输入只会对应一个答案。

### 注意事项
- 确保代码的正确性和效率
- 处理边界情况
- 代码风格要符合 Python PEP 8 规范
```

### 选择题

#### 文件结构

```yaml
---
title: "Python变量命名规则"
type: "choice"
difficulty: 1
is_multiple_choice: false
options:
  A: "123abc"
  B: "my-variable"
  C: "_private_var"
  D: "class"
correct_answer: "C"
# 解锁条件（可选）
# unlock_conditions:
#   type: "date"
#   unlock_date: "2024-12-31T23:59:59"
---

## 题目描述

以下哪个是合法的 Python 变量名？

### 题目内容
- A: 123abc
- B: my-variable
- C: _private_var
- D: class

---
*本题基于 Python 教学平台标准格式设计。*
```

### 填空题

#### 文件结构

```yaml
---
title: "Python基础概念填空"
type: "fillblank"
difficulty: 1

# 带空白标记的内容
content_with_blanks: |
  Python 是一种 [blank1] 编程语言。
  它的设计哲学强调代码的 [blank2]。

# 空白答案配置（三种格式可选）
blanks:
  # 格式1：详细格式（推荐）
  blank1:
    answers: ["高级", "解释型"]
    case_sensitive: false
  blank2:
    answers: ["可读性", "可读性高"]
    case_sensitive: false

# 格式2：简化数组格式（简单）
# blanks:
#   blanks: ["高级", "可读性"]
#   case_sensitive: false

# 格式3：数组格式（每个空多个答案）
# blanks:
#   blanks:
#     - answers: ["高级", "解释型"]
#       case_sensitive: false
#     - answers: ["可读性"]
#       case_sensitive: false

blank_count: 2  # 空白数量（可选，系统会自动计算）
# 解锁条件（可选）
# unlock_conditions:
#   type: "prerequisite"
#   prerequisites: ["basic-concepts.md"]
#   minimum_percentage: 80
---

## 题目描述

填写 Python 编程语言的基础概念。

### 题目内容
根据题目描述，在空白处填写正确的答案。

---
*本题基于 Python 教学平台标准格式设计。*
```

## 🧪 测试用例格式

### 算法题测试用例

```yaml
test_cases:
  - input: "[[2,7,11,15],9]"
    output: "[0,1]"
    is_sample: true
  - input: "[[3,2,4],6]"
    output: "[1,2]"
    is_sample: false
```

#### 输入/输出格式规则

1. **数组/列表**: `[1,2,3]`
2. **字符串**: `"hello world"`
3. **整数**: `42`
4. **布尔值**: `true` 或 `false`
5. **null**: `null`
6. **对象**: `{"key": "value"}`

## 🔒 解锁条件

解锁条件用于控制题目和章节在平台上的可见性和可访问性，支持多种解锁方式。

### 题目解锁条件

#### 支持的解锁类型

| 类型 | 说明 | 必需字段 |
|------|------|----------|
| `none` | 无条件 | 无 |
| `prerequisite` | 需要完成前置题目 | `prerequisites` |
| `date` | 指定日期后解锁 | `unlock_date` |
| `both` | 需要前置题目且指定日期后解锁 | `prerequisites`, `unlock_date` |

### 解锁条件字段

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `type` | string | 解锁类型：`prerequisite`、`date`、`both`、`none` | `"prerequisite"` |
| `prerequisites` | array[] | 前置题目文件名列表 | `["basic.md", "intermediate.md"]` |
| `unlock_date` | string | ISO 8601 格式的日期时间 | `"2024-12-31T23:59:59"` |
| `minimum_percentage` | integer | 完成前置题目的最低百分比（0-100） | `80` |

### 格式规范

#### 必填字段规则

1. **`type` 字段**：必须为有效值，可选值：
   - `prerequisite` - 需要完成指定前置题目
   - `date` - 指定日期后解锁
   - `both` - 需要前置题目且指定日期后解锁
   - `none` - 无条件（默认值，可不设置）

2. **`prerequisites` 字段**（当 `type` 为 `prerequisite` 或 `both` 时必需）：
   - 必须是非空数组
   - 每个元素是非空字符串（文件名，包含 .md 扩展名）
   - 文件名相对于当前题目文件所在目录

3. **`unlock_date` 字段**（当 `type` 为 `date` 或 `both` 时必需）：
   - 必须是有效的 ISO 8601 格式字符串
   - 格式示例：`"2024-12-31T23:59:59"`
   - 解锁条件将在该时间点后自动满足

4. **`minimum_percentage` 字段**（可选）：
   - 必须是 0-100 之间的整数
   - 当指定时，用户需要完成指定比例的前置题目才能解锁
   - 不指定时，需要完成所有前置题目

### 示例

#### 示例 1：前置题目解锁

```yaml
---
title: "进阶算法"
type: "algorithm"
difficulty: 2
test_cases: [...]
solution_name: {python: advancedAlgorithm}
unlock_conditions:
  type: "prerequisite"
  prerequisites: ["basic-algorithm.md", "intermediate-algorithm.md"]
  minimum_percentage: 100
---
```

#### 示例 2：日期解锁

```yaml
---
title: "期末考试"
type: "choice"
difficulty: 3
options: {...}
correct_answer: "A"
unlock_conditions:
  type: "date"
  unlock_date: "2024-12-31T23:59:59"
---
```

#### 示例 3：组合解锁

```yaml
---
title: "综合项目"
type: "algorithm"
difficulty: 3
test_cases: [...]
solution_name: {python: comprehensiveProject}
unlock_conditions:
  type: "both"
  prerequisites: ["project-part1.md", "project-part2.md"]
  unlock_date: "2024-12-31T23:59:59"
  minimum_percentage: 80
---
```

### 注意事项

1. **文件名引用**：前置题目通过文件名引用，系统会自动从课程中查找对应题目
2. **同一课程**：所有前置题目必须在同一课程内
3. **导入顺序**：确保前置题目文件在引用前已经导入
4. **错误处理**：如果前置题目不存在，会记录警告并跳过该引用
5. **时间处理**：所有日期时间都使用服务器的本地时区
6. **性能考虑**：大量解锁条件可能影响页面加载性能，请合理使用

### 与导入功能的关系

解锁条件功能已经完全集成到课程导入服务中：

1. **解析**：从题目 markdown 的 frontmatter 中解析 `unlock_conditions` 字段
2. **验证**：验证格式的正确性，包括类型、必需字段、日期格式等
3. **创建**：自动创建 `ProblemUnlockCondition` 数据库记录
4. **链接**：建立题目之间的前置关系

### 常见问题

**Q: 如何设置默认的无解锁条件？**
A: 不设置 `unlock_conditions` 字段，或者设置 `type: "none"`

**Q: 前置题目不存在怎么办？**
A: 系统会记录警告日志，该前置题目引用将被忽略，其他正常引用会继续处理

**Q: 解锁日期格式有哪些要求？**
A: 必须是 ISO 8601 格式，推荐使用 `"YYYY-MM-DDTHH:MM:SS"` 格式

**Q: minimum_percentage 可以是小数吗？**
A: 不可以，必须是整数，范围 0-100

**Q: 一个题目可以有多个解锁条件吗？**
A: 解锁条件是互斥的，通过 `type` 字段指定一种解锁方式

### 章节解锁条件

章节解锁条件用于控制学生对章节内容的访问权限，支持基于前置章节和日期的解锁策略。

#### 支持的解锁类型

| 类型 | 说明 | 必需字段 |
|------|------|----------|
| `none` | 无条件（默认） | 无 |
| `prerequisite` | 需要完成前置章节 | `prerequisites` |
| `date` | 指定日期后解锁 | `unlock_date` |
| `all` | 需要前置章节且指定日期后解锁 | `prerequisites`, `unlock_date` |

#### 章节解锁条件字段

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `type` | string | 解锁类型：`prerequisite`、`date`、`all`、`none` | `"prerequisite"` |
| `prerequisites` | array[] | 前置章节 order 列表（整数） | `[1, 2]` |
| `unlock_date` | string | ISO 8601 格式的日期时间 | `"2024-12-31T23:59:59"` |

#### 章节解锁条件示例

**示例 1：前置章节解锁**
```yaml
---
title: "高级函数"
order: 3
unlock_conditions:
  type: "prerequisite"
  prerequisites: [1, 2]
---
```

**示例 2：多个前置章节解锁**
```yaml
---
title: "面向对象编程"
order: 5
unlock_conditions:
  type: "all"
  prerequisites: [1, 2, 3, 4]
---
```

**示例 3：日期解锁**
```yaml
---
title: "2025年春季课程"
order: 6
unlock_conditions:
  type: "date"
  unlock_date: "2025-03-01T00:00:00Z"
---
```

**示例 4：前置章节 + 日期解锁**
```yaml
---
title: "综合项目"
order: 10
unlock_conditions:
  type: "all"
  prerequisites: [8, 9]
  unlock_date: "2025-03-15T00:00:00Z"
---
```

#### 与题目解锁条件的区别

| 特性 | 题目解锁条件 | 章节解锁条件 |
|------|-------------|-------------|
| 前置条件引用 | 题目文件名（`problem-01.md`） | 章节 order（整数，如 `1`） |
| 完成百分比 | 支持 `minimum_percentage` | 不支持（全部完成或未完成） |
| 检验规则 | 检查文件是否存在 | 检查章节 order 是否存在 |
| 记录创建 | 创建 `ProblemUnlockCondition` | 创建 `ChapterUnlockCondition` |

#### 注意事项

1. **章节顺序引用**：前置章节通过 `order` 整数引用，而非文件名或标题
2. **同一课程**：所有前置章节必须在同一课程内
3. **导入顺序**：章节导入时分两阶段处理（先导入基础信息，再处理解锁条件）
4. **错误处理**：如果前置章节不存在，会记录警告并跳过该引用
5. **时间处理**：所有日期时间都使用服务器的本地时区
6. **循环依赖**：章节间的循环依赖会被检测并拒绝

#### 常见问题

**Q: 如何设置默认的无解锁条件？**
A: 不设置 `unlock_conditions` 字段，或者设置 `type: "none"`

**Q: 前置章节不存在怎么办？**
A: 系统会记录警告日志，该前置章节引用将被忽略，其他正常引用会继续处理

**Q: 解锁日期格式有哪些要求？**
A: 必须是 ISO 8601 格式，推荐使用 `"YYYY-MM-DDTHH:MM:SS"` 格式

**Q: 一个章节可以有多个解锁条件吗？**
A: 解锁条件是互斥的，通过 `type` 字段指定一种解锁方式

## 📒 Markdown 规范

### 代码块

```markdown
**代码模板：**
```python
def functionName(args):
    # 代码内容
    pass
```
```

### 列表

```markdown
- 有序列表
  1. 第一项
  2. 第二项

- 无序列表
  - 第一级
    - 第二级
```

### 表格

```markdown
| 列1 | 列2 |
|-----|-----|
| 数据1 | 数据2 |
```

### 强调

```markdown
**粗体文本**
*斜体文本*
~~删除线~~
```

### 可折叠块

```markdown
**基本语法：**
:::tip{title="提示内容"}
提示内容
:::

:::warning{title="警告内容"}
警告内容
:::

:::answer{title="答案内容"}
答案内容
:::

:::fold{title="可折叠内容"}
需要折叠的内容
:::
```

#### 带状态控制的可折叠块

```markdown
**明确指定状态：**
:::tip{title="提示" state="expanded"}
默认展开的提示
:::

:::answer{title="答案" state="collapsed"}
默认折叠的答案
:::

**使用类快捷方式：**
:::tip{.expanded}
等同于 state="expanded"
:::

:::fold{.collapsed .highlight}
折叠状态并添加高亮样式
:::
```

#### 属性语法规则

- `{title="标题"}` 或 `{title='标题'}` - 设置标题
- `{state=expanded}` 或 `{state="expanded"}` - 设置展开状态
- `{state=collapsed}` 或 `{state="collapsed"}` - 设置折叠状态
- `{.expanded}` 或 `{.collapsed}` - 状态类快捷方式
- `{state="expanded" title="标题"}` - 多个属性
- `{state=expanded .highlight}` - 混合属性样式

#### 默认状态

| 类型 | 默认状态 | 用途 |
|------|----------|------|
| `tip` | expanded | 一般性提示和补充说明 |
| `warning` | expanded | 重要警告和注意事项 |
| `answer` | collapsed | 题目答案和解答 |
| `fold` | collapsed | 通用可折叠内容 |

#### 带标签的可折叠块

```markdown
:::tip[ref-id]{title="参考标题"}
可以通过 ref-id 引用的内容
:::

### 算法题提示格式

所有 Python 练习题的提示内容必须使用可折叠块格式，支持渐进式提示。

#### 基本提示格式

```markdown
### 提示

:::tip{title="提示" state="collapsed"}
使用 Python 内置的 `max()` 函数：`max(numbers)`
:::
```

#### 多方法提示格式

对于有多种实现方法的问题，应使用多个可折叠块：

```markdown
### 提示

:::tip{title="方法一：使用循环" state="collapsed"}
使用 for 循环和条件判断：
```python
count = 0
for num in numbers:
    if num > 0:
        count += 1
return count
```
:::

:::tip{title="方法二：使用列表推导式" state="collapsed"}
使用列表推导式（更简洁）：
```python
return len([x for x in numbers if x > 0])
```
:::
```

#### 规范要求

1. **默认折叠**：所有提示必须使用 `state="collapsed"`，默认隐藏
2. **标题明确**：为每个方法提供清晰的标题（如方法一、方法二）
3. **代码嵌套**：代码块必须放在可折叠块内部，保持缩进
4. **渐进式**：复杂提示应分解为多个步骤或方法
5. **避免直接答案**：提示应该引导学生思考，不要直接给出完整代码
```

#### 在可折叠块内使用其他 Markdown

可折叠块支持所有标准 Markdown 内容，包括代码块、列表、链接等：

```markdown
:::tip{title="Python 示例"}
这里是如何使用列表推导式：

```python
squares = [x**2 for x in range(5)]
```

注意事项：
- 列表推导式不能包含复杂的逻辑
- 避免过度使用嵌套推导式
:::
```

## ✅ 质量要求

### 内容质量

- ✅ **准确性**：代码、语法、概念必须正确
- ✅ **完整性**：章节、知识点、题目要覆盖全面
- ✅ **逻辑性**：内容编排要有逻辑顺序
- ✅ **实用性**：提供实际应用场景和案例

### 格式规范

- ✅ **YAML Frontmatter**：所有必填字段必须填写
- ✅ **文件命名**：遵循命名规范
- ✅ **代码高亮**：使用正确的语言标识符
- ✅ **测试用例**：JSON 格式正确，至少一个示例用例

### 技术要求

- ✅ **代码可运行**：所有示例代码必须能正确执行
- ✅ **边界处理**：测试用例要覆盖边界情况
- ✅ **性能合理**：时间限制要合理，避免过高的内存限制
- ✅ **错误处理**：选择题解析要详细准确

## 📝 模板使用

### 使用方法

1. **复制模板**
   ```bash
   # 复制整个模板目录到你的课程目录
   cp -r /path/to/templates /path/to/your-course
   ```

2. **重命名文件**
   - 将 `course.md` 修改为你的课程元数据
   - 将章节文件重命名为 `chapter-01-*.md` 等
   - 将题目文件重命名为有意义的 slug

3. **编辑内容**
   - 修改 YAML frontmatter 的元数据
   - 编写具体的章节内容
   - 创建具体的题目

### 模板文件说明

- **`course.md`**：课程元数据和简介
- **`chapters/chapter-00-template.md`**：章节内容模板
- **`problems/algorithm-problem-template.md`**：算法题模板
- **`problems/choice-problem-template.md`**：选择题模板

## ⚠️ 常见错误

### YAML 语法错误

```yaml
# 错误：缺少引号
title: Python编程入门

# 正确：字符串需要引号
title: "Python编程入门"

# 错误：列表格式错误
tags: [python, 基础]

# 正确：JSON 格式数组
tags: ["python", "基础"]
```

### 文件命名错误

```markdown
# 错误：缺少 chapter- 前缀
01-variables.md

# 正确：必须使用 chapter- 前缀
chapter-01-variables.md
```

### 测试用例错误

```yaml
# 错误：JSON 格式不正确
- input: [1,2,3]
  output: "123"

# 正确：使用 JSON 字符串
- input: "[1,2,3]"
  output: "[1,2,3]"

# 错误：缺少 is_sample
- input: "\"()\""
  output: "true"

# 正确：至少有一个 is_sample=true
- input: "\"()\""
  output: "true"
  is_sample: true
```

### 代码错误

```python
# 错误：语法错误
def func(
    print("hello")

# 正确：语法正确
def func():
    print("hello")
```

## 📞 支持

如果发现格式错误或有疑问：

1. 查看 [故障排查指南](troubleshooting.md)
2. 参考 [课程创作指南](course-authoring-guide.md)
3. 使用模板文件作为参考
4. 联系课程内容团队

---

*本格式规范基于 Python 教学平台课程内容系统设计。*
*如有更新，请参考最新版本。*