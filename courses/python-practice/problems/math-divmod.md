---
title: "获取商和余数"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "get_quotient_remainder"
code_template:
  python: |
    def get_quotient_remainder(dividend, divisor):
        """
        获取除法的商和余数

        Args:
            dividend: 被除数（整数）
            divisor: 除数（非零整数）

        Returns:
            list: [商, 余数]
        """
        # 请在此实现你的代码
        # 提示：使用 divmod() 函数或 % 和 // 运算符
        pass
test_cases:
  - input: "[10,3]"
    output: "[3,1]"
    is_sample: true
  - input: "[20,4]"
    output: "[5,0]"
    is_sample: true
  - input: "[17,5]"
    output: "[3,2]"
    is_sample: false
  - input: "[100,7]"
    output: "[14,2]"
    is_sample: false
  - input: "[7,2]"
    output: "[3,1]"
    is_sample: false
---
## 题目描述

编写一个函数，获取整数除法的商和余数。

### 输入格式

两个整数 [dividend, divisor]，divisor 为非零整数。

### 输出格式

返回一个列表 [商, 余数]。

### 示例

**输入：**
```
[10, 3]
```

**输出：**
```
[3, 1]
```

### 提示

- 使用 `divmod(a, b)` 函数可以同时获取商和余数
- 或者分别使用 `//`（整除）和 `%`（取余）运算符

### 注意事项

- 余数的绝对值总是小于除数的绝对值
- 当能整除时，余数为 0

---
*本题目基于 Python 教学平台标准格式设计。*
