---
title: "print()函数的使用"
type: "choice"
difficulty: 1
chapter: 1
is_multiple_choice: false
options:
  A: "Hello World!"
  B: "Hello World! Goodbye!"
  C: "Hello World!Goodbye!"
  D: "程序会报错"
correct_answer: "C"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
print("Hello World!", end="")
print("Goodbye!")
```

### 题目内容

A. Hello World!
B. Hello World! Goodbye!
C. Hello World!Goodbye!
D. 程序会报错

### 解析

**正确答案：C**

**详细解析：**

这道题考查的是`print()`函数的`end`参数的用法。

- **默认行为**：`print()`函数默认在输出结束后会添加一个换行符（`\n`），所以通常每次`print()`都会在新的一行输出。

- **end参数**：我们可以使用`end`参数来改变这一行为。`end=""`表示输出结束后不添加任何字符，直接结束。

**代码执行过程：**
1. 第一个`print("Hello World!", end="")`输出"Hello World!"，然后**不换行**
2. 第二个`print("Goodbye!")`输出"Goodbye!"，然后换行
3. 最终输出结果为：`Hello World!Goodbye!`（两个字符串连在一起）

**其他选项分析：**
- **选项A**：如果第一个`print()`有默认的换行，输出会是两行，但这里使用了`end=""`
- **选项B**：需要使用`end=" "`才会添加空格，如`print("Hello World!", end=" ")`
- **选项D**：这段代码语法完全正确，不会报错

**相关示例：**
```python
# 默认行为
print("Hello")
print("World")
# 输出：
# Hello
# World

# 使用end参数
print("Hello", end=" ")
print("World")
# 输出：
# Hello World

# 自定义结尾字符
print("Hello", end="!!!\n")
print("World")
# 输出：
# Hello!!!
# World
```

### 相关知识点
- `print()`函数的基本用法
- `end`参数：控制输出结束时的字符（默认是换行符`\n`）
- `sep`参数：控制多个参数之间的分隔符（默认是空格）
- 转义字符：`\n`表示换行

---
*本题基于 Python 教学平台标准格式设计。*
