---
title: "获取绝对值"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "get_absolute"
code_template:
  python: |
    def get_absolute(n):
        """
        获取数字的绝对值

        Args:
            n: 一个整数

        Returns:
            int: n 的绝对值
        """
        # 请在此实现你的代码
        # 提示：使用 abs() 函数
        pass
test_cases:
  - input: "5"
    output: "5"
    is_sample: true
  - input: "-3"
    output: "3"
    is_sample: true
  - input: "0"
    output: "0"
    is_sample: false
  - input: "-100"
    output: "100"
    is_sample: false
  - input: "42"
    output: "42"
    is_sample: false
---
## 题目描述

编写一个函数，获取一个整数的绝对值。

### 输入格式

一个整数 n。

### 输出格式

返回 n 的绝对值。

### 示例

**输入：**
```
-3
```

**输出：**
```
3
```

### 提示

:::tip{title="提示" state="collapsed"}
使用 Python 内置的 `abs()` 函数可以获取数字的绝对值。
:::

### 注意事项

- 绝对值是指一个数在数轴上所对应点到原点的距离
- 0 的绝对值是 0
- 负数的绝对值是它的相反数
- 正数的绝对值是它本身

---
*本题目基于 Python 教学平台标准格式设计。*
