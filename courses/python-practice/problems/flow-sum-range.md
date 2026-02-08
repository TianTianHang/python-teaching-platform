---
title: "计算范围内数的和"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "sum_range"
code_template:
  python: |
    def sum_range(start, end):
        """
        计算从 start 到 end（包含）的所有整数之和

        Args:
            start: 起始整数
            end: 结束整数

        Returns:
            int: 范围内所有整数之和
        """
        # 请在此实现你的代码
        # 提示：使用 range() 和 for 循环，或直接使用 sum() 函数
        pass
test_cases:
  - input: "[1,5]"
    output: "15"
    is_sample: true
  - input: "[1,10]"
    output: "55"
    is_sample: true
  - input: "[3,3]"
    output: "3"
    is_sample: false
  - input: "[0,3]"
    output: "6"
    is_sample: false
  - input: "[10,12]"
    output: "33"
    is_sample: false
---
## 题目描述

编写一个函数，计算从 start 到 end（包含两端）的所有整数之和。

### 输入格式

两个整数 [start, end]，其中 start ≤ end。

### 输出格式

返回从 start 到 end（包含）的所有整数之和。

### 示例

**输入：**
```
[1, 5]
```

**输出：**
```
15
```

（1 + 2 + 3 + 4 + 5 = 15）

### 提示

方法 1：使用 range() 和 for 循环：
```python
total = 0
for i in range(start, end + 1):
    total += i
return total
```

方法 2：使用 sum() 函数：
```python
return sum(range(start, end + 1))
```

### 注意事项
- range(start, end + 1) 会生成从 start 到 end（包含）的整数
- 如果 start == end，返回 start 本身
- 可以处理负数范围

---
*本题目基于 Python 教学平台标准格式设计。*
