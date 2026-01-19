---
title: "数据类型识别"
type: "choice"
difficulty: 1
chapter: 2
is_multiple_choice: false
options:
  A: "<class 'int'>"
  B: "<class 'float'>"
  C: "<class 'str'>"
  D: "<class 'bool'>"
correct_answer: "B"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
x = 3.14
print(type(x))
```

### 题目内容

A. <class 'int'>
B. <class 'float'>
C. <class 'str'>
D. <class 'bool'>

### 解析

**正确答案：B**

**详细解析：**

这道题考查Python的基本数据类型。

**代码分析：**
- `x = 3.14`：将浮点数`3.14`赋值给变量`x`
- `type(x)`：返回变量`x`的数据类型
- 因为`3.14`是一个带有小数部分的数字，所以它的类型是`float`（浮点数）
- 输出结果为：`<class 'float'>`

**Python基本数据类型回顾：**

| 类型 | 说明 | 示例 | type()输出 |
|------|------|------|------------|
| `int` | 整数 | `42`、`-10`、`0` | `<class 'int'>` |
| `float` | 浮点数 | `3.14`、`-0.5`、`2.0` | `<class 'float'>` |
| `str` | 字符串 | `"hello"`、`'world'` | `<class 'str'>` |
| `bool` | 布尔值 | `True`、`False` | `<class 'bool'>` |

**选项分析：**
- **选项 A**：`int`是整数类型，如`42`或`-10`，不包括小数点
- **选项 B（正确）**：`float`是浮点数类型，包含小数部分，`3.14`是典型的浮点数
- **选项 C**：`str`是字符串类型，必须用引号包围，如`"3.14"`
- **选项 D**：`bool`是布尔类型，只有`True`或`False`两个值

**注意：**
- 即使小数部分是0，如`3.0`，它仍然是`float`类型
- 要表示整数，使用`int()`转换：`int(3.14)`会得到`3`，类型变为`int`

### 相关知识点
- Python基本数据类型：int、float、str、bool
- `type()`函数的使用
- 浮点数的表示方法
- 如何区分整数和浮点数

---
*本题基于 Python 教学平台标准格式设计。*
