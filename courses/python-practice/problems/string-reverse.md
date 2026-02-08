---
title: "字符串反转"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "reverse_string"
code_template:
  python: |
    def reverse_string(s):
        """
        反转字符串

        Args:
            s: 一个字符串

        Returns:
            str: 反转后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用切片 [::-1] 反转字符串
        pass
test_cases:
  - input: '"hello"'
    output: '"olleh"'
    is_sample: true
  - input: '"Python"'
    output: '"nohtyP"'
    is_sample: true
  - input: '""'
    output: '""'
    is_sample: false
  - input: '"a"'
    output: '"a"'
    is_sample: false
  - input: '"12345"'
    output: '"54321"'
    is_sample: false
---
## 题目描述

编写一个函数，将字符串反转。

### 输入格式

一个字符串 s。

### 输出格式

返回反转后的字符串。

### 示例

**输入：**
```
"hello"
```

**输出：**
```
"olleh"
```

### 提示

使用字符串切片 `[::-1]` 可以反转字符串：`s[::-1]`

### 注意事项

- `[::]` 语法中，第一个冒号前后是起始和结束位置（留空表示从头到尾）
- 第二个冒号后的 `-1` 表示步长为 -1，即反向遍历
- 空字符串反转后仍是空字符串

---
*本题目基于 Python 教学平台标准格式设计。*
