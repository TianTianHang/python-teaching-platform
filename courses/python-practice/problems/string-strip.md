---
title: "去除首尾空格"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "strip_whitespace"
code_template:
  python: |
    def strip_whitespace(s):
        """
        去除字符串首尾的空格

        Args:
            s: 一个字符串

        Returns:
            str: 去除首尾空格后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用 strip() 方法
        pass
test_cases:
  - input: '"  hello  "'
    output: '"hello"'
    is_sample: true
  - input: '"  Python  "'
    output: '"Python"'
    is_sample: true
  - input: '"no spaces"'
    output: '"no spaces"'
    is_sample: false
  - input: '"   leading"'
    output: '"leading"'
    is_sample: false
  - input: '"trailing   "'
    output: '"trailing"'
    is_sample: false
---
## 题目描述

编写一个函数，去除字符串首尾的所有空格。

### 输入格式

一个字符串 s。

### 输出格式

返回去除首尾空格后的字符串。

### 示例

**输入：**
```
"  hello  "
```

**输出：**
```
"hello"
```

### 提示

使用字符串的 `strip()` 方法：`s.strip()`

### 注意事项

- strip() 只去除首尾的空格，不会影响中间的空格
- 如果字符串首尾没有空格，返回原字符串
- 也可以使用 lstrip() 只去除左边空格，或 rstrip() 只去除右边空格

---
*本题目基于 Python 教学平台标准格式设计。*
