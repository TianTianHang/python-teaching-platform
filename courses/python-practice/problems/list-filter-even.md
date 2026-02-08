---
title: "过滤偶数"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "filter_even"
code_template:
  python: |
    def filter_even(numbers):
        """
        过滤出列表中的所有偶数

        Args:
            numbers: 一个整数列表

        Returns:
            list: 包含所有偶数的新列表
        """
        # 请在此实现你的代码
        # 提示：使用列表推导式 [x for x in numbers if x % 2 == 0]
        pass
test_cases:
  - input: "[1,2,3,4,5,6]"
    output: "[2,4,6]"
    is_sample: true
  - input: "[7,9,11]"
    output: "[]"
    is_sample: true
  - input: "[2,4,6,8]"
    output: "[2,4,6,8]"
    is_sample: false
  - input: "[1,3,5,7]"
    output: "[]"
    is_sample: false
  - input: "[10,15,20,25]"
    output: "[10,20]"
    is_sample: false
---
## 题目描述

编写一个函数，过滤出列表中的所有偶数，返回一个新列表。

### 输入格式

一个整数列表 numbers。

### 输出格式

返回一个包含所有偶数的新列表，保持原顺序。如果没有偶数，返回空列表。

### 示例

**输入：**
```
[1, 2, 3, 4, 5, 6]
```

**输出：**
```
[2, 4, 6]
```

### 提示

使用列表推导式筛选偶数：
```python
[x for x in numbers if x % 2 == 0]
```

### 注意事项

- 0 是偶数
- 负偶数（如 -2, -4）也符合条件
- 返回的是新列表，原列表不会被修改
- 如果没有偶数，返回空列表 []

---
*本题目基于 Python 教学平台标准格式设计。*
