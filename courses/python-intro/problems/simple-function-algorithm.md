---
title: "简单计算器"
type: "algorithm"
difficulty: 1
chapter: 13
time_limit: 1000
memory_limit: 256
solution_name:
  python: "calculate_grade"
code_template:
  python: |
    def calculate_grade(score):
        """
        根据分数返回等级

        Args:
            score: 学生分数（0-100之间的整数）

        Returns:
            分数对应的等级：
            90-100: '优秀'
            80-89: '良好'
            70-79: '中等'
            60-69: '及格'
            0-59: '不及格'
        """
        # 在这里实现你的代码
        pass
test_cases:
  - input: "[[95]]"
    output: "['优秀']"
    is_sample: true
  - input: "[[85]]"
    output: "['良好']"
    is_sample: false
  - input: "[[75]]"
    output: "['中等']"
    is_sample: false
  - input: "[[65]]"
    output: "['及格']"
    is_sample: false
  - input: "[[45]]"
    output: "['不及格']"
    is_sample: false
---

## 题目描述

编写一个函数，根据输入的学生分数返回对应的等级。

### 输入格式
一个整数，表示学生分数（0-100之间）

### 输出格式
字符串，表示分数对应的等级：
- 90-100: '优秀'
- 80-89: '良好'
- 70-79: '中等'
- 60-69: '及格'
- 0-59: '不及格'

### 示例

**输入：**
```
95
```

**输出：**
```
优秀
```

**输入：**
```
85
```

**输出：**
```
良好
```

### 提示
可以使用 if-elif-else 结构来判断分数范围。

### 注意事项
- 确保代码的正确性和效率
- 处理边界情况（如正好是90分）
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*
