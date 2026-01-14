---
title: "选择题标题"
type: "choice"
difficulty: 1
is_multiple_choice: false
options:
  A: "选项A内容"
  B: "选项B内容"
  C: "选项C内容"
  D: "选项D内容"
correct_answer: "A"

# 解锁条件示例
# 以下示例展示如何使用 unlock_conditions 字段，请根据需要选择或修改：

# 示例 1：前置题目解锁
# unlock_conditions:
#   type: "prerequisite"
#   prerequisites: ["basic-concept.md"]
#   minimum_percentage: 80

# 示例 2：日期解锁
# unlock_conditions:
#   type: "date"
#   unlock_date: "2024-12-31T23:59:59"

# 示例 3：组合解锁（前置题目 + 日期）
# unlock_conditions:
#   type: "both"
#   prerequisites: ["basic-concept.md", "intermediate-concept.md"]
#   unlock_date: "2024-12-31T23:59:59"
#   minimum_percentage: 100
---
## 题目描述

[详细的题目描述，包括问题背景和说明]

### 题目内容
[具体的问题内容，可以是概念理解、语法选择、逻辑推理等]

### 解析

**正确答案：** [正确答案]

**详细解析：**
[对每个选项的详细分析，说明正确和错误的原因]

- **选项 A**：[分析为什么正确或错误]
- **选项 B**：[分析为什么正确或错误]
- **选项 C**：[分析为什么正确或错误]
- **选项 D**：[分析为什么正确或错误]

### 相关知识点
- [知识点1说明]
- [知识点2说明]

---
*本题基于 Python 教学平台标准格式设计。*