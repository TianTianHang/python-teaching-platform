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

### 题目 Frontmatter 通用字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `title` | string | 标题，必填 |
| `type` | string | 题目类型：`algorithm` 或 `choice`，必填 |
| `difficulty` | integer | 难度 1-3，必填 |

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
| `correct_answer` | string/array | - | 正确答案 |

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
```

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
---

## 题目描述

以下哪个是合法的 Python 变量名？

### 题目内容
- A: 123abc
- B: my-variable
- C: _private_var
- D: class

### 解析

**正确答案：** C

**详细解析：**
Python 变量命名规则：
1. 必须以字母或下划线开头
2. 不能以数字开头
3. 可以包含字母、数字和下划线
4. 不能使用 Python 关键字

选项 A 以数字开头，非法；
选项 B 包含连字符（-），非法；
选项 C 以下划线开头，合法；
选项 D 是 Python 关键字，非法。
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