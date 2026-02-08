---
title: "字符串转列表"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "str_to_list"
code_template:
  python: |
    def str_to_list(s):
        """
        将字符串转换为字符列表

        Args:
            s: 一个字符串

        Returns:
            list: 包含字符串中每个字符的列表
        """
        # 请在此实现你的代码
        # 提示：使用 list() 函数
        pass
test_cases:
  - input: '"hello"'
    output: '["h","e","l","l","o"]'
    is_sample: true
  - input: '"abc"'
    output: '["a","b","c"]'
    is_sample: true
  - input: '""'
    output: "[]"
    is_sample: false
  - input: '"a"'
    output: '["a"]'
    is_sample: false
  - input: '"123"'
    output: '["1","2","3"]'
    is_sample: false
---
## 题目描述

编写一个函数，将字符串转换为包含每个字符的列表。

### 输入格式

一个字符串 s。

### 输出格式

返回一个包含字符串中每个字符的列表。

### 示例

**输入：**
```
"hello"
```

**输出：**
```
["h", "e", "l", "l", "o"]
```

### 提示

使用 `list()` 函数将字符串转换为字符列表：`list(s)`

### 注意事项

- 空字符串转换为空列表
- 每个字符（包括空格）都成为列表中的一个元素
- 中文字符也计为一个字符

---
*本题目基于 Python 教学平台标准格式设计。*
