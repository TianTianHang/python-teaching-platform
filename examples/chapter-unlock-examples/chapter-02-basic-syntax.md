---
title: "Python 基础语法"
order: 2
unlock_conditions:
  type: "prerequisite"
  prerequisites: [1]
---

## Python 基础语法

### 章节概述

本章将详细介绍 Python 的基础语法，包括变量、数据类型、运算符和控制语句。通过学习本章内容，你将能够掌握 Python 的基本语法规则。

### 知识点 1：变量和数据类型

**描述：**
Python 支持多种数据类型，包括整数（int）、浮点数（float）、字符串（str）、列表（list）、字典（dict）等。变量可以随时重新赋值和改变类型。

**示例代码：**
```python
# 基本数据类型
integer_var = 42
float_var = 3.14
string_var = "Python编程"
list_var = [1, 2, 3, 4, 5]
dict_var = {"name": "Python", "version": "3.9"}

# 类型查看
print(f"整数：{integer_var}, 类型：{type(integer_var)}")
print(f"浮点数：{float_var}, 类型：{type(float_var)}")
print(f"字符串：{string_var}, 类型：{type(string_var)}")
```

**解释：**
Python 的动态类型系统允许我们在程序运行时改变变量的类型。使用 `type()` 函数可以查看变量的类型。

### 知识点 2：运算符

**描述：**
Python 提供了丰富的运算符，包括算术运算符、比较运算符、逻辑运算符和赋值运算符。

**示例代码：**
```python
# 算术运算符
a = 10
b = 3

print(f"加法：{a} + {b} = {a + b}")
print(f"减法：{a} - {b} = {a - b}")
print(f"乘法：{a} * {b} = {a * b}")
print(f"除法：{a} / {b} = {a / b}")
print(f"整除：{a} // {b} = {a // b}")
print(f"取余：{a} % {b} = {a % b}")
print(f"幂运算：{a} ** {b} = {a ** b}")

# 比较运算符
print(f"a > b: {a > b}")
print(f"a < b: {a < b}")
print(f"a == b: {a == b}")
```

**解释：**
Python 的运算符使用与前缀/后缀表示法不同的中缀表示法，这使得代码更加易读。每种运算符都有特定的优先级，可以使用括号来改变运算顺序。

**关键要点：**
- 算术运算符用于数学计算
- 比较运算符返回布尔值（True/False）
- 逻辑运算符用于组合多个条件
- 使用括号可以明确控制运算顺序

---

*本章内容基于 Python 教学平台标准格式设计。*
