---
title: "算法题标题"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "functionName"
code_template:
  python: |
    def functionName(args):
        """
        函数描述

        Args:
            args: 参数描述

        Returns:
            返回值描述
        """
        # 请在此实现你的代码
        # 思路：简要说明解题思路
        pass
test_cases:
  - input: "[示例输入]"
    output: "[示例输出]"
    is_sample: true
  - input: "[测试输入1]"
    output: "[测试输出1]"
    is_sample: false
unlock_conditions:
  type: "prerequisite"
  prerequisites: ["choice-problem-template.md"]
  minimum_percentage: 100
# 解锁条件示例
# 以下示例展示如何使用 unlock_conditions 字段，请根据需要选择或修改：

# 示例 1：前置题目解锁
# unlock_conditions:
#   type: "prerequisite"
#   prerequisites: ["hello-world.md", "variable-basics.md"]
#   minimum_percentage: 100

# 示例 2：日期解锁
# unlock_conditions:
#   type: "date"
#   unlock_date: "2024-12-31T23:59:59"

# 示例 3：组合解锁（前置题目 + 日期）
# unlock_conditions:
#   type: "both"
#   prerequisites: ["hello-world.md", "variable-basics.md"]
#   unlock_date: "2024-12-31T23:59:59"
#   minimum_percentage: 80
---
## 题目描述

编写一个函数实现[功能说明]。

### 输入格式
[输入数据的格式说明]

### 输出格式
[输出数据的格式说明]

### 示例

**输入：**
```
[示例输入内容]
```

**输出：**
```
[示例输出内容]
```

### 提示
（可选）
[解题提示或建议]

### 注意事项
- 确保代码的正确性和效率
- 处理边界情况
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*