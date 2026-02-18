---
title: "数字(Number)"
order: 3
unlock_conditions:
  type: "prerequisite"
  prerequisites: [2]
---

## 数字(Number)

### 章节概述

本章将学习Python中的数字类型，包括整数、浮点数的基本运算，以及如何使用math模块进行数学计算和random模块生成随机数。

### 知识点 1：整数和浮点数

**描述：**
Python中最常用的数字类型是整数(int)和浮点数(float)。整数是没有小数部分的数字，浮点数是带有小数部分的数字。

**数字类型的表示：**
```python-exec
# 整数
a = 10
b = -5
c = 0

print(f"整数：{a}, {b}, {c}")
print(f"a的类型是：{type(a)}")

# 浮点数
pi = 3.14
temperature = -12.5
price = 99.99

print(f"浮点数：{pi}, {temperature}, {price}")
print(f"pi的类型是：{type(pi)}")

# 科学计数法
large = 1.5e8  # 1.5 * 10^8
print(f"科学计数法：{large}")
```

### 知识点 2：基本数学运算

**描述：**
Python提供了丰富的数学运算符，可以进行加减乘除、整除、取余和幂运算。

**算术运算：**
```python-exec
a = 10
b = 3

print(f"a = {a}, b = {b}")
print(f"加法：{a} + {b} = {a + b}")
print(f"减法：{a} - {b} = {a - b}")
print(f"乘法：{a} * {b} = {a * b}")
print(f"除法：{a} / {b} = {a / b:.2f}")
print(f"整除：{a} // {b} = {a // b}")
print(f"取余：{a} % {b} = {a % b}")
print(f"幂运算：{a} ** {b} = {a ** b}")
```

### 知识点 3：类型转换

**描述：**
有时需要在不同的数字类型之间进行转换，Python提供了int()、float()等函数来实现类型转换。

**类型转换示例：**
```python-exec
# 浮点数转整数
pi = 3.14159
int_pi = int(pi)
print(f"int(3.14159) = {int_pi}")

# 字符串转数字
num_str = "42"
num = int(num_str)
print(f"int('42') = {num}")

price_str = "19.99"
price = float(price_str)
print(f"float('19.99') = {price}")

# 数字转字符串
age = 25
age_str = str(age)
print(f"str(25) = '{age_str}'")
```

### 知识点 4：math 模块

**描述：**
math模块提供了许多数学函数，如平方根、幂运算、三角函数等。

**常用 math 函数：**
```python-exec
import math

# 基本数学函数
x = 16
print(f"平方根：math.sqrt({x}) = {math.sqrt(x)}")

# 幂运算
print(f"2的3次方：math.pow(2, 3) = {math.pow(2, 3)}")

# 向上取整和向下取整
num = 3.7
print(f"向上取整：math.ceil({num}) = {math.ceil(num)}")
print(f"向下取整：math.floor({num}) = {math.floor(num)}")

# 常数
print(f"圆周率：math.pi = {math.pi}")
print(f"自然常数：math.e = {math.e}")
```

### 知识点 5：random 模块

**描述：**
random模块用于生成随机数，在游戏、模拟等场景中非常有用。

**生成随机数：**
```python-exec
import random

# 生成随机整数
dice = random.randint(1, 6)
print(f"掷骰子：{dice}")

# 生成随机浮点数
rand_float = random.random()
print(f"随机浮点数：{rand_float:.3f}")

# 从列表中随机选择
fruits = ["苹果", "香蕉", "橙子"]
choice = random.choice(fruits)
print(f"随机选择：{choice}")
```

### 知识点 6：数字格式化

**描述：**
在输出数字时，可以使用格式化来控制显示的格式，如小数位数、对齐方式等。

**格式化输出：**
```python-exec
pi = 3.1415926

# 保留小数位数
print(f"保留2位小数：{pi:.2f}")
print(f"保留4位小数：{pi:.4f}")

# 百分比
rate = 0.7854
print(f"百分比：{rate:.1%}")

# 千位分隔符
population = 1234567890
print(f"人口：{population:,}")
```

### 章节总结

本章我们学习了：
- 整数和浮点数的基本概念
- 基本数学运算符的使用
- 数字类型之间的转换
- math模块的常用函数
- random模块生成随机数
- 数字格式化输出

### 下一步

掌握了数字类型后，让我们学习运算符，了解Python中各种运算符的用法和优先级。

---
*本章内容基于 Python 教学平台标准格式设计。*
