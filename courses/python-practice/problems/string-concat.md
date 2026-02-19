---
title: "字符串连接"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "concat_strings"
code_template:
  python: |
    def concat_strings(s1, s2):
        """
        连接两个字符串

        Args:
            s1: 第一个字符串
            s2: 第二个字符串

        Returns:
            str: 连接后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用 + 运算符连接字符串
        pass
test_cases:
  - input: '["hello","world"]'
    output: '"helloworld"'
    is_sample: true
  - input: '["Python","编程"]'
    output: '"Python编程"'
    is_sample: true
  - input: '["abc","123"]'
    output: '"abc123"'
    is_sample: false
  - input: '["","test"]'
    output: '"test"'
    is_sample: false
  - input: '["hello",""]'
    output: '"hello"'
    is_sample: false
---
## 题目描述

编写一个函数，将两个字符串按顺序连接成一个新字符串。

### 输入格式

两个字符串 [s1, s2]。

### 输出格式

返回连接后的字符串。

### 示例

**输入：**
```
["hello", "world"]
```

**输出：**
```
"helloworld"
```

### 提示

:::tip{title="提示" state="collapsed"}
使用 `+` 运算符可以连接字符串：`s1 + s2`
:::

### 注意事项

- 字符串连接不会自动添加空格
- 空字符串与任何字符串连接都得到原字符串
- 可以使用 `+` 连接多个字符串

---
*本题目基于 Python 教学平台标准格式设计。*
