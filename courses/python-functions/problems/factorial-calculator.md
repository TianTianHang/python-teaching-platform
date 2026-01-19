---
title: "阶乘计算"
type: "algorithm"
difficulty: 2
chapter: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "factorial"
code_template:
  python: |
    def factorial(n):
        """
        计算n的阶乘

        Args:
            n: 非负整数

        Returns:
            返回n的阶乘结果
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "5"
    output: "120"
    is_sample: true
  - input: "0"
    output: "1"
    is_sample: false
  - input: "10"
    output: "3628800"
    is_sample: false
unlock_conditions:
  type: "prerequisite"
  prerequisites: ["function-definition.md", "parameters-arguments.md", "return-values.md"]
---
## 题目描述

编写一个函数，计算给定非负整数的阶乘。阶乘的定义为：n! = n × (n-1) × (n-2) × ... × 2 × 1，特别地，0! = 1。

### 输入格式

函数接收一个参数：
- `n`：非负整数

### 输出格式

返回 n 的阶乘结果。

### 示例

**示例1：**
```python
factorial(5)
# 返回：120
# 解释：5! = 5 × 4 × 3 × 2 × 1 = 120
```

**示例2：**
```python
factorial(0)
# 返回：1
# 解释：0! = 1（数学定义）
```

**示例3：**
```python
factorial(10)
# 返回：3628800
# 解释：10! = 10 × 9 × 8 × 7 × 6 × 5 × 4 × 3 × 2 × 1 = 3628800
```

### 提示

1. 使用循环或递归实现阶乘计算
2. 注意边界情况：0! = 1
3. 可以使用迭代方式（for/while循环）或递归方式
4. 递归的终止条件是 n == 0 或 n == 1

**方法1：使用循环**
```python
def factorial(n):
    if n == 0:
        return 1

    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

**方法2：使用递归**
```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

**方法3：使用 while 循环**
```python
def factorial(n):
    if n == 0:
        return 1

    result = 1
    while n > 1:
        result *= n
        n -= 1
    return result
```

**方法4：使用 reduce（函数式编程）**
```python
from functools import reduce

def factorial(n):
    if n == 0:
        return 1
    return reduce(lambda x, y: x * y, range(1, n + 1))
```

### 注意事项

- n 是非负整数（n >= 0）
- 0! = 1 是数学定义
- 对于较大的 n，结果会很大
- 递归方式在 n 很大时可能导致栈溢出
- 循环方式通常比递归方式更高效

### 算法分析

**时间复杂度**：O(n)
- 需要执行 n 次乘法运算

**空间复杂度**：
- 循环方式：O(1)
- 递归方式：O(n)（递归调用栈）

### 数学知识

**阶乘的性质：**
- n! = n × (n-1)!
- 0! = 1
- 1! = 1
- n! 增长非常快

**阶乘的前几个值：**
- 0! = 1
- 1! = 1
- 2! = 2
- 3! = 6
- 4! = 24
- 5! = 120
- 6! = 720
- 7! = 5040
- 8! = 40320
- 9! = 362880
- 10! = 3628800

### 实际应用

阶乘在数学和计算机科学中有很多应用：

1. **排列组合**：
   - n 个不同物品的全排列数量是 n!
   - 从 n 个物品中选 k 个的排列数是 n!/(n-k)!

2. **概率论**：
   - 二项分布的公式中包含阶乘
   - 计算组合数 C(n,k) = n!/(k!(n-k)!)

3. **泰勒级数**：
   - sin(x) = x - x³/3! + x⁵/5! - ...
   - cos(x) = 1 - x²/2! + x⁴/4! - ...
   - eˣ = 1 + x + x²/2! + x³/3! + ...

### 进阶挑战

如果你想挑战更高级的内容：

1. **使用缓存优化递归**：
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

2. **处理大数**：
   - Python 的整数可以无限大，不需要担心溢出
   - 其他语言可能需要使用特殊的大数类型

3. **计算组合数**：
```python
def combination(n, k):
    """计算组合数 C(n,k)"""
    return factorial(n) // (factorial(k) * factorial(n - k))
```

---
*本题目基于 Python 教学平台标准格式设计。*
