---
title: "获取字符串长度"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "get_string_length"
code_template:
  python: |
    def get_string_length(s):
        """
        获取字符串的长度

        Args:
            s: 一个字符串

        Returns:
            int: 字符串的长度
        """
        # 请在此实现你的代码
        # 提示：使用 len() 函数
        pass
test_cases:
  - input: '"hello"'
    output: "5"
    is_sample: true
  - input: '"Python"'
    output: "6"
    is_sample: true
  - input: '""'
    output: "0"
    is_sample: false
  - input: '"a b c"'
    output: "5"
    is_sample: false
  - input: '"12345"'
    output: "5"
    is_sample: false
---
## 题目描述

编写一个函数，获取字符串的长度（字符个数）。

### 输入格式

一个字符串 s。

### 输出格式

返回字符串的长度（整数）。

### 示例

**输入：**
```
"hello"
```

**输出：**
```
5
```

### 提示

使用 Python 内置的 `len()` 函数可以获取字符串的长度：`len(s)`

### 注意事项

- 空字符串的长度为 0
- 空格也是字符，会被计入长度
- 中文字符也计为一个字符

---
*本题目基于 Python 教学平台标准格式设计。*
