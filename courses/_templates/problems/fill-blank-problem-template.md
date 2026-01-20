---
title: "填空题标题"
type: "fillblank"
difficulty: 1
chapter: 1  # 可选：题目所属章节的顺序号（不指定则不关联章节）

# 带空白标记的内容
content_with_blanks: |
  Python 是一种 [blank1] 编程语言。
  它的设计哲学强调代码的 [blank2] 和 [blank3]。

# 空白答案配置（三种格式）
# 格式1（详细）: 每个空单独配置答案和大小写敏感性
blanks:
  blank1:
    answers: ["高级", "解释型"]
    case_sensitive: false
  blank2:
    answers: ["可读性"]
    case_sensitive: false
  blank3:
    answers: ["简洁性", "简洁"]
    case_sensitive: false

# 格式2（简单）: 简化的数组格式
# blanks:
#   blanks: ["高级", "可读性", "简洁性"]
#   case_sensitive: false

# 格式3（推荐）: 每个空可以有多个备选答案
# blanks:
#   blanks:
#     - answers: ["高级", "解释型"]
#       case_sensitive: false
#     - answers: ["可读性"]
#       case_sensitive: false
#     - answers: ["简洁性", "简洁"]
#       case_sensitive: false

blank_count: 3  # 空白数量（可选，系统会自动计算）

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
[具体的问题内容说明，引导学生完成填空]

---
*本题基于 Python 教学平台标准格式设计。*
