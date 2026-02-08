---
title: "统计正数个数"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "count_positive"
code_template:
  python: |
    def count_positive(numbers):
        """
        统计列表中正数的个数

        Args:
            numbers: 一个整数列表

        Returns:
            int: 正数的个数
        """
        # 请在此实现你的代码
        # 提示：使用 for 循环和 if 语句
        pass
test_cases:
  - input: "[1,-2,3,-4,5]"
    output: "3"
    is_sample: true
  - input: "[-1,-2,-3]"
    output: "0"
    is_sample: true
  - input: "[0,1,2,3]"
    output: "3"
    is_sample: false
  - input: "[10,20,30]"
    output: "3"
    is_sample: false
  - input: "[]"
    output: "0"
    is_sample: false
---
## 题目描述

编写一个函数，统计列表中正数的个数。

### 输入格式

一个整数列表 numbers。

### 输出格式

返回列表中正数的个数。

### 示例

**输入：**
```
[1, -2, 3, -4, 5]
```

**输出：**
```
3
```

### 提示

使用 for 循环和 if 语句：
```python
count = 0
for num in numbers:
    if num > 0:
        count += 1
return count
```

### 注意事项

- 0 不是正数，不计入统计
- 空列表返回 0
- 负数不计入统计
- 也可以使用列表推导式：`len([x for x in numbers if x > 0])`

---
*本题目基于 Python 教学平台标准格式设计。*
