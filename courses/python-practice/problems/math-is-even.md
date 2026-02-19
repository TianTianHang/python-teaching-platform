---
title: "判断奇偶性"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "is_even"
code_template:
  python: |
    def is_even(n):
        """
        判断一个整数是否为偶数

        Args:
            n: 一个整数

        Returns:
            bool: 如果 n 是偶数返回 True，否则返回 False
        """
        # 请在此实现你的代码
        # 提示：使用 % 运算符判断能否被 2 整除
        pass
test_cases:
  - input: "4"
    output: "true"
    is_sample: true
  - input: "7"
    output: "false"
    is_sample: true
  - input: "0"
    output: "true"
    is_sample: false
  - input: "-2"
    output: "true"
    is_sample: false
  - input: "13"
    output: "false"
    is_sample: false
---
## 题目描述

编写一个函数，判断一个整数是否为偶数。

### 输入格式

一个整数 n。

### 输出格式

返回布尔值，偶数返回 true，奇数返回 false。

### 示例

**输入：**
```
4
```

**输出：**
```
true
```

### 提示

:::tip{title="提示" state="collapsed"}
使用 `%`（取余）运算符判断数字能否被 2 整除：
- `n % 2 == 0` 表示 n 是偶数
- `n % 2 != 0` 表示 n 是奇数
:::

### 注意事项

- 0 是偶数
- 负数也可以是偶数（如 -2, -4）
- 布尔值返回格式为小写：true/false

---
*本题目基于 Python 教学平台标准格式设计。*
