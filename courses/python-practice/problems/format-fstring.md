---
title: "使用 f-string 格式化"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "format_fstring"
code_template:
  python: |
    def format_fstring(name, age):
        """
        使用 f-string 格式化字符串

        Args:
            name: 名字（字符串）
            age: 年龄（整数）

        Returns:
            str: 格式化后的字符串 "My name is {name} and I am {age} years old"
        """
        # 请在此实现你的代码
        # 提示：使用 f-string 语法 f"文本 {变量} 更多文本"
        pass
test_cases:
  - input: '["Tom",18]'
    output: '"My name is Tom and I am 18 years old"'
    is_sample: true
  - input: '["Alice",20]'
    output: '"My name is Alice and I am 20 years old"'
    is_sample: true
  - input: '["Bob",30]'
    output: '"My name is Bob and I am 30 years old"'
    is_sample: false
  - input: '["Charlie",25]'
    output: '"My name is Charlie and I am 25 years old"'
    is_sample: false
  - input: '["David",40]'
    output: '"My name is David and I am 40 years old"'
    is_sample: false
---
## 题目描述

编写一个函数，使用 f-string 将名字和年龄插入到字符串中。

### 输入格式

[名字 name, 年龄 age]。

### 输出格式

返回格式化后的字符串：`"My name is {name} and I am {age} years old"`

### 示例

**输入：**
```
["Tom", 18]
```

**输出：**
```
"My name is Tom and I am 18 years old"
```

### 提示

使用 f-string 语法（Python 3.6+）：
```python
f"My name is {name} and I am {age} years old"
```

### 注意事项

- f-string 以字母 `f` 开头，后跟字符串
- 使用花括号 `{}` 包裹变量名
- f-string 是 Python 推荐的字符串格式化方式
- 变量会被自动转换为字符串

---
*本题目基于 Python 教学平台标准格式设计。*
