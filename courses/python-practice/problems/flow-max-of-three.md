---
title: "三个数最大值"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "max_of_three"
code_template:
  python: |
    def max_of_three(a, b, c):
        """
        找出三个数中的最大值

        Args:
            a: 第一个数
            b: 第二个数
            c: 第三个数

        Returns:
            int: 三个数中的最大值
        """
        # 请在此实现你的代码
        # 提示：使用 if/elif/else 语句比较三个数
        pass
test_cases:
  - input: "[1,5,3]"
    output: "5"
    is_sample: true
  - input: "[10,20,15]"
    output: "20"
    is_sample: true
  - input: "[7,7,7]"
    output: "7"
    is_sample: false
  - input: "[-1,0,1]"
    output: "1"
    is_sample: false
  - input: "[100,50,75]"
    output: "100"
    is_sample: false
---
## 题目描述

编写一个函数，使用 if/elif/else 语句找出三个数中的最大值。

### 输入格式

三个整数 [a, b, c]。

### 输出格式

返回三个数中的最大值。

### 示例

**输入：**
```
[1, 5, 3]
```

**输出：**
```
5
```

### 提示

使用 if/elif/else 语句进行比较：
```python
if a >= b and a >= c:
    return a
elif b >= a and b >= c:
    return b
else:
    return c
```

或者使用嵌套的 if 语句。

### 注意事项

- 如果三个数相等，返回其中任意一个
- 处理负数的情况
- 也可以使用 max() 函数，但本题目练习 if 语句

---
*本题目基于 Python 教学平台标准格式设计。*
