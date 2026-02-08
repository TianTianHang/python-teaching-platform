---
title: "计算幂次方"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "calculate_power"
code_template:
  python: |
    def calculate_power(base, exponent):
        """
        计算幂次方

        Args:
            base: 底数（整数）
            exponent: 指数（非负整数）

        Returns:
            int: base 的 exponent 次方
        """
        # 请在此实现你的代码
        # 提示：使用 ** 运算符或 pow() 函数
        pass
test_cases:
  - input: "[2,3]"
    output: "8"
    is_sample: true
  - input: "[3,2]"
    output: "9"
    is_sample: true
  - input: "[5,0]"
    output: "1"
    is_sample: false
  - input: "[10,2]"
    output: "100"
    is_sample: false
  - input: "[2,10]"
    output: "1024"
    is_sample: false
---
## 题目描述

编写一个函数，计算底数的指数次方。

### 输入格式

两个整数 [base, exponent]，其中 exponent 为非负整数。

### 输出格式

返回 base 的 exponent 次方的结果。

### 示例

**输入：**
```
[2, 3]
```

**输出：**
```
8
```

### 提示

- 使用 `**` 运算符：`2 ** 3` 等于 8
- 或者使用 `pow()` 函数：`pow(2, 3)` 等于 8

### 注意事项

- 任何数的 0 次方都等于 1
- 1 的任何次方都等于 1

---
*本题目基于 Python 教学平台标准格式设计。*
