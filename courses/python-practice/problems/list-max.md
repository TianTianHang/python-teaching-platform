---
title: "找列表最大值"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "find_max"
code_template:
  python: |
    def find_max(numbers):
        """
        找出列表中的最大值

        Args:
            numbers: 一个整数列表

        Returns:
            int: 列表中的最大值
        """
        # 请在此实现你的代码
        # 提示：使用 max() 函数
        pass
test_cases:
  - input: "[1,5,3,9,2]"
    output: "9"
    is_sample: true
  - input: "[10,20,30,40]"
    output: "40"
    is_sample: true
  - input: "[5]"
    output: "5"
    is_sample: false
  - input: "[-1,-5,-3]"
    output: "-1"
    is_sample: false
  - input: "[100,50,75,25]"
    output: "100"
    is_sample: false
---
## 题目描述

编写一个函数，找出整数列表中的最大值。

### 输入格式

一个整数列表 numbers。

### 输出格式

返回列表中的最大值。

### 示例

**输入：**
```
[1, 5, 3, 9, 2]
```

**输出：**
```
9
```

### 提示

使用 Python 内置的 `max()` 函数：`max(numbers)`

### 注意事项

- 列表至少包含一个元素
- 列表可能包含负数
- 如果列表只有一个元素，返回该元素

---
*本题目基于 Python 教学平台标准格式设计。*
