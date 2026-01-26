---
title: "列表元素求和"
type: "algorithm"
difficulty: 1
chapter: 6
time_limit: 1000
memory_limit: 256
solution_name:
  python: "list_sum"
code_template:
  python: |
    def list_sum(numbers):
        """
        计算列表中所有元素的和

        Args:
            numbers: 数字列表

        Returns:
            列表中所有元素的和
        """
        # 在这里实现你的代码
        pass
test_cases:
  - input: "[[1,2,3,4,5]]"
    output: "[15]"
    is_sample: true
  - input: "[[10,20,30]]"
    output: "[60]"
    is_sample: false
  - input: "[[1,2,3,4,5,6,7,8,9,10]]"
    output: "[55]"
    is_sample: false
  - input: "[[0]]"
    output: "[0]"
    is_sample: false
  - input: "[[100,200,300]]"
    output: "[600]"
    is_sample: false
---

## 题目描述

编写一个函数，计算给定列表中所有元素的和。

### 输入格式
一个整数列表，如 [1, 2, 3, 4, 5]

### 输出格式
一个整数，表示列表所有元素的和

### 示例

**输入：**
```
[1,2,3,4,5]
```

**输出：**
```
15
```

### 提示
你可以使用内置的 sum() 函数，或者使用循环手动求和。

### 注意事项
- 确保代码的正确性和效率
- 处理空列表的情况
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*
