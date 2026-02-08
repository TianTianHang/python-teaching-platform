---
title: "四舍五入"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "round_number"
code_template:
  python: |
    def round_number(n):
        """
        对数字进行四舍五入

        Args:
            n: 一个浮点数

        Returns:
            int: 四舍五入后的整数
        """
        # 请在此实现你的代码
        # 提示：使用 round() 函数
        pass
test_cases:
  - input: "3.7"
    output: "4"
    is_sample: true
  - input: "2.3"
    output: "2"
    is_sample: true
  - input: "5.5"
    output: "6"
    is_sample: false
  - input: "10.1"
    output: "10"
    is_sample: false
  - input: "9.9"
    output: "10"
    is_sample: false
---
## 题目描述

编写一个函数，对浮点数进行四舍五入，返回最接近的整数。

### 输入格式

一个浮点数 n。

### 输出格式

返回四舍五入后的整数。

### 示例

**输入：**
```
3.7
```

**输出：**
```
4
```

### 提示

使用 Python 内置的 `round()` 函数可以对数字进行四舍五入。

### 注意事项

- Python 的 round() 函数采用"银行家舍入法"（四舍六入五取偶）
- 对于 .5 的情况，会舍入到最接近的偶数
- 例如：round(2.5) = 2，round(3.5) = 4

---
*本题目基于 Python 教学平台标准格式设计。*
