---
title: "统计文件行数"
type: "algorithm"
difficulty: 1
chapter: 14
time_limit: 1000
memory_limit: 256
solution_name:
  python: "count_lines"
code_template:
  python: |
    def count_lines(filename):
        """
        统计指定文件的行数

        Args:
            filename: 文件名（字符串）

        Returns:
            文件的行数（整数）
        """
        # 在这里实现你的代码
        # 使用 with 语句打开文件并统计行数
        pass
test_cases:
  - input: "[\"example.txt\"]"
    output: "3"
    is_sample: true
    note: "假设 example.txt 包含3行文本"
  - input: "[\"empty.txt\"]"
    output: "0"
    is_sample: false
    note: "假设 empty.txt 是空文件"
  - input: "[\"single.txt\"]"
    output: "1"
    is_sample: false
    note: "假设 single.txt 包含1行文本"
  - input: "[\"data.txt\"]"
    output: "10"
    is_sample: false
    note: "假设 data.txt 包含10行文本"
  - input: "[\"notes.txt\"]"
    output: "5"
    is_sample: false
    note: "假设 notes.txt 包含5行文本"
---

## 题目描述

编写一个函数，统计指定文件的行数。

### 输入格式
文件名字符串，如 "example.txt"

### 输出格式
文件的行数（整数）

### 示例

**输入：**
```
"example.txt"
```

**输出：**
```
3
```

### 提示
使用 `with open(filename, "r") as file:` 打开文件，然后遍历文件行来统计行数。

### 注意事项
- 必须使用 with 语句打开文件
- 确保代码的正确性和效率
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*
