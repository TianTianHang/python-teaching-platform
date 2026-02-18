---
title: "过滤列表中的偶数"
type: "algorithm"
difficulty: 1
chapter: 12
time_limit: 1000
memory_limit: 256
solution_name:
  python: "filter_even"
code_template:
  python: |
    def filter_even(numbers):
        """
        使用列表推导式过滤出列表中的所有偶数

        Args:
            numbers: 整数列表

        Returns:
            只包含偶数的列表
        """
        # 在这里实现你的代码，使用列表推导式
        pass
test_cases:
  - input: "[[1,2,3,4,5,6,7,8,9,10]]"
    output: "[2,4,6,8,10]"
    is_sample: true
  - input: "[[11,13,15,17]]"
    output: "[]"
    is_sample: false
  - input: "[[2,4,6,8]]"
    output: "[2,4,6,8]"
    is_sample: false
  - input: "[[1,3,5,7,9]]"
    output: "[]"
    is_sample: false
  - input: "[[10,20,30,40,50]]"
    output: "[10,20,30,40,50]"
    is_sample: false
---

## 题目描述

使用列表推导式，编写一个函数过滤出列表中的所有偶数。

### 输入格式
一个整数列表，如 [1, 2, 3, 4, 5]

### 输出格式
一个只包含偶数的列表

### 示例

**输入：**
```
[1,2,3,4,5,6,7,8,9,10]
```

**输出：**
```
[2,4,6,8,10]
```

### 提示
使用列表推导式 `[x for x in numbers if x % 2 == 0]`

### 注意事项
- 必须使用列表推导式实现
- 确保代码的正确性和效率
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*
