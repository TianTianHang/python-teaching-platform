---
title: "分数转等级"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "score_to_grade"
code_template:
  python: |
    def score_to_grade(score):
        """
        将分数转换为等级

        Args:
            score: 分数（0-100）

        Returns:
            str: 等级（A/B/C/D/F）
        """
        # 请在此实现你的代码
        # 提示：使用 if/elif/else 语句
        pass
test_cases:
  - input: "95"
    output: '"A"'
    is_sample: true
  - input: "85"
    output: '"B"'
    is_sample: true
  - input: "72"
    output: '"C"'
    is_sample: false
  - input: "60"
    output: '"D"'
    is_sample: false
  - input: "45"
    output: '"F"'
    is_sample: false
---
## 题目描述

编写一个函数，根据分数返回对应的等级：
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: 0-59

### 输入格式

一个整数 score（0-100）。

### 输出格式

返回对应的等级字符串（"A"、"B"、"C"、"D" 或 "F"）。

### 示例

**输入：**
```
95
```

**输出：**
```
"A"
```

### 提示

:::tip{title="提示" state="collapsed"}
使用 if/elif/else 语句：
```python
if score >= 90:
    return "A"
elif score >= 80:
    return "B"
elif score >= 70:
    return "C"
elif score >= 60:
    return "D"
else:
    return "F"
```
:::

### 注意事项
- 等级判断从高到低进行（先判断 A，再 B，以此类推）
- 边界值（如 90、80 等）属于较高等级
- 测试用例保证分数在 0-100 范围内

---
*本题目基于 Python 教学平台标准格式设计。*
