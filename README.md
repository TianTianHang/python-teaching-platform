# Python 教学平台课程内容

本仓库存储 Python 教学平台的课程文档内容，使用多文件 Markdown + YAML frontmatter 格式编写。

## 🚀 快速开始

1. **阅读格式规范** → [docs/format-specification.md](docs/format-specification.md)
2. **使用课程模板** → [courses/_templates/](courses/_templates/)
3. **编写课程内容** → [courses/](courses/)
4. **提交 PR 审阅** → [贡献指南](#贡献指南)

## 📁 目录结构

```
course-content/
├── README.md                      # 本文件
├── courses/                       # 课程目录
│   ├── _templates/               # 课程模板（请勿直接编辑）
│   │   ├── course.md             # 课程元数据模板
│   │   ├── chapters/             # 章节模板
│   │   │   └── chapter-00-template.md
│   │   └── problems/             # 题目模板
│   │       ├── algorithm-problem-template.md
│   │       ├── choice-problem-template.md
│   │       └── fill-blank-problem-template.md
│   └── {course-slug}/            # 具体课程目录
│       ├── course.md             # 课程元数据和简介
│       ├── chapters/             # 章节目录
│       │   ├── chapter-01-intro.md
│       │   └── chapter-02-basics.md
│       └── problems/             # 题目目录
│           ├── two-sum.md
│           └── variable-naming.md
├── docs/                         # 文档和指南
│   ├── course-authoring-guide.md  # 课程创作指南
│   ├── format-specification.md    # 格式规范
│   └── troubleshooting.md         # 故障排查
├── media/                        # 媒体资源
│   ├── images/                   # 图片资源
│   └── code/                     # 代码示例
└── scripts/                      # 辅助脚本
```

## 📖 导入课程

在应用代码分支中运行管理命令：

```bash
# 导入所有课程（从课程仓库路径）
cd /path/to/python-teaching-platform/backend
uv run python manage.py import_course_from_repo /path/to/course-content --update

# 查看导入选项
uv run python manage.py import_course_from_repo --help
```

## 📝 贡献指南

### 创建新课程

1. **创建课程目录结构**
   ```bash
   # 在 courses/ 目录下创建新课程文件夹
   mkdir -p courses/your-course-slug/{chapters,problems}
   ```

2. **复制并编辑模板文件**
   ```bash
   # 复制课程模板
   cp courses/_templates/course.md courses/your-course-slug/course.md

   # 复制章节模板
   cp courses/_templates/chapters/chapter-00-template.md \
      courses/your-course-slug/chapters/chapter-01-intro.md

   # 复制题目模板（根据需要选择算法题、选择题或填空题）
   cp courses/_templates/problems/algorithm-problem-template.md \
      courses/your-course-slug/problems/two-sum.md
   cp courses/_templates/problems/choice-problem-template.md \
      courses/your-course-slug/problems/variable-naming.md
   cp courses/_templates/problems/fill-blank-problem-template.md \
      courses/your-course-slug/problems/python-basics-fill-blank.md
   ```

3. **编辑文件内容**
   - 修改 YAML frontmatter 中的元数据
   - 编写具体的课程内容
   - 确保所有必填字段都已填写
   - 遵循格式规范要求

4. **验证格式**
   - 参考 [format-specification.md](docs/format-specification.md) 检查格式
   - 确保文件命名符合规范
   - 验证 YAML frontmatter 语法正确

5. **提交更改**
   ```bash
   git add courses/your-course-slug/
   git commit -m "Add course: Your Course Title"
   git push origin branch-name
   ```

### 文件命名规范

- **课程目录**: `kebab-case` 格式（如 `python-basics`）
- **课程文件**: 每个课程目录下必须包含 `course.md`
- **章节文件**: `chapter-{order:02d}-{slug}.md`（如 `chapter-01-variables.md`）
- **题目文件**: `{slug}.md`（如 `two-sum.md`）
- **排序规则**: 按数字序号排序（01, 02, 03...）

### 质量要求

- ✅ **内容准确**：确保代码、语法、概念正确
- ✅ **格式规范**：严格遵循格式规范
- ✅ **循序渐进**：从易到难，知识点覆盖全面
- ✅ **实用性强**：提供实际应用场景和案例
- ✅ **测试用例**：包含足够的测试用例验证学习效果

## 🎯 课程要求

### 章节要求
- 每个课程建议包含 4-8 个章节
- 章节内容要详细，包含知识点讲解
- 每个章节至少包含 2-3 个练习题

### 题目要求
- **算法题**：提供题目描述、输入输出说明、示例、代码模板和测试用例
- **选择题**：提供清晰的题目、选项、正确答案（支持单选和多选）
- **填空题**：提供带空白标记的内容、答案配置（支持多种格式）
- 难度分级：1（简单）、2（中等）、3（困难）

### 测试用例要求
- 每个算法题至少包含 1 个示例测试用例（`is_sample: true`）
- 至少包含 3-5 个完整的测试用例
- 测试用例要覆盖边界情况

## 🔧 编辑提示

### 使用 Markdown 编辑器
推荐使用支持 YAML frontmatter 和语法高亮的编辑器，如：
- VS Code（配合 YAML 和 Markdown 插件）
- Typora
- Obsidian
- Cursor

### 课程文件 (course.md)

每个课程必须包含 YAML frontmatter：

```yaml
---
title: "Python编程入门"
description: "从零开始学习Python编程，掌握Python基础语法、数据结构和编程思想。"
order: 1
difficulty: 1
prerequisites: []
tags: ["python", "基础", "编程入门"]
---

# Python编程入门

欢迎来到本课程！
```

### 章节文件 (chapter-XX-slug.md)

每个章节必须包含 YAML frontmatter：

```yaml
---
title: "Python基础语法"
order: 1
---

## Python基础语法

### 章节概述

本章介绍 Python 的基础语法...

### 知识点 1：变量和数据类型

**描述：**
Python 是一种动态类型语言...

**示例代码：**
```python
# 变量赋值
name = "Python"
version = 3.11
```

**解释：**
详细解释代码的含义...
```

### 算法题文件 (slug.md)

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

编写一个函数，接受一个整数数组 `nums` 和一个目标值 `target`...

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
```

### 选择题文件 (slug.md)

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
```

### 填空题文件 (slug.md)

```yaml
---
title: "Python基础概念填空"
type: "fillblank"
difficulty: 1

content_with_blanks: |
  Python 是一种 [blank1] 编程语言。
  它的设计哲学强调代码的 [blank2]。

blanks:
  blank1:
    answers: ["高级", "解释型"]
    case_sensitive: false
  blank2:
    answers: ["可读性"]
    case_sensitive: false

blank_count: 2
---

## 题目描述

填写 Python 编程语言的基础概念。

### 题目内容
根据题目描述，在空白处填写正确的答案。
```

## 📚 文档资源

- **[格式规范](docs/format-specification.md)** - 详细的文件格式和 YAML 字段说明
- **[课程创作指南](docs/course-authoring-guide.md)** - 逐步课程创作教程
- **[故障排查](docs/troubleshooting.md)** - 常见问题和解决方案

## ⚠️ 注意事项

1. **不要直接编辑模板文件**：模板文件位于 `courses/_templates/` 目录，仅供复制使用
2. **YAML 语法**：确保 YAML frontmatter 中的字符串使用引号，数组使用 JSON 格式
3. **文件编码**：所有文件必须使用 UTF-8 编码
4. **测试用例格式**：算法题的测试用例输入输出必须是有效的 JSON 字符串
5. **版本控制**：建议为每个新课程创建单独的分支进行开发

## 🤝 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/my-course`)
3. 提交更改 (`git commit -m 'Add course: My Course'`)
4. 推送到分支 (`git push origin feature/my-course`)
5. 创建 Pull Request

在 PR 描述中请说明：
- 课程的学习目标
- 目标受众
- 主要章节和知识点
- 题目数量和类型

## 📞 获取帮助

如果您在创建课程时遇到问题：

1. 查看 [故障排查指南](docs/troubleshooting.md)
2. 参考 [课程创作指南](docs/course-authoring-guide.md)
3. 查看模板文件中的示例
4. 提交 Issue 寻求帮助

---

*本仓库基于 Python 教学平台标准课程格式设计。*
*如有更新，请参考最新版本的文档。*
