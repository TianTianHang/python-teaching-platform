---
title: "找列表最小值"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "find_min"
code_template:
  python: |
    def find_min(numbers):
        """
        找出列表中的最小值

        Args:
            numbers: 一个整数列表

        Returns:
            int: 列表中的最小值
        """
        # 请在此实现你的代码
        # 提示：使用 min() 函数
        pass
test_cases:
  - input: "[1,5,3,9,2]"
    output: "1"
    is_sample: true
  - input: "[10,20,30,40]"
    output: "10"
    is_sample: true
  - input: "[7]"
    output: "7"
    is_sample: false
  - input: "[-1,-5,-3]"
    output: "-5"
    is_sample: false
  - input: "[100,50,75,25]"
    output: "25"
    is_sample: false
---
## 题目描述

编写一个函数，找出整数列表中的最小值。

### 输入格式

一个整数列表 numbers。

### 输出格式

返回列表中的最小值。

### 示例

**输入：**
```
[1, 5, 3, 9, 2]
```

**输出：**
```
1
```

### 提示

使用 Python 内置的 `min()` 函数：`min(numbers)`

### 注意事项

- 列表至少包含一个元素
- 负数比正数小
- 如果列表只有一个元素，返回该元素

---
*本题目基于 Python 教学平台标准格式设计。*
