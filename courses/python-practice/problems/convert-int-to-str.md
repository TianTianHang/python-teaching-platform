---
title: "整数转字符串"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "int_to_str"
code_template:
  python: |
    def int_to_str(n):
        """
        将整数转换为字符串

        Args:
            n: 一个整数

        Returns:
            str: 转换后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用 str() 函数
        pass
test_cases:
  - input: "123"
    output: '"123"'
    is_sample: true
  - input: "42"
    output: '"42"'
    is_sample: true
  - input: "0"
    output: '"0"'
    is_sample: false
  - input: "-10"
    output: '"-10"'
    is_sample: false
  - input: "1000"
    output: '"1000"'
    is_sample: false
---
## 题目描述

编写一个函数，将整数转换为字符串类型。

### 输入格式

一个整数 n。

### 输出格式

返回转换后的字符串。

### 示例

**输入：**
```
123
```

**输出：**
```
"123"
```

### 提示

使用 `str()` 函数将整数转换为字符串：`str(n)`

### 注意事项

- 正数转换后不带正号
- 负数转换后保留负号
- 0 转换为 "0"

---
*本题目基于 Python 教学平台标准格式设计。*
