---
title: "运算符"
order: 3
---

## 运算符

### 章节概述

运算符是用于执行各种操作的符号，如算术运算、比较运算和逻辑运算。本章将介绍 Python 中的各种运算符及其使用方法。

### 知识点 1：算术运算符

**描述：**
算术运算符用于执行基本的数学运算，包括加、减、乘、除等。

**基本算术运算符：**

```python-exec
# 基本算术运算
a = 10
b = 3

print(f"a = {a}, b = {b}")
print("加法：", a + b)      # 13
print("减法：", a - b)      # 7
print("乘法：", a * b)      # 30
print("除法：", a / b)      # 3.333...
print("整除：", a // b)     # 3 (去掉小数部分)
print("取余：", a % b)      # 1 (余数)
print("幂运算：", a ** b)   # 1000 (10的3次方)
```

**自增和自减：**

```python-exec
# 自增运算
x = 5
print("x =", x)
x = x + 1  # x 现在是 6
print("x + 1 =", x)

# 简化的写法
y = 5
y += 3  # 等同于 y = y + 3
print("y += 3 =", y)

# 其他自运算
z = 10
z *= 2  # z = z * 2
print("z *= 2 =", z)
```

### 知识点 2：比较运算符

**描述：**
比较运算符用于比较两个值的关系，返回布尔值（True 或 False）。

**比较运算符：**

```python-exec
a = 10
b = 20
c = 10

print(f"a = {a}, b = {b}, c = {c}")
print("a == b：", a == b)   # False (等于)
print("a != b：", a != b)   # True (不等于)
print("a < b：", a < b)     # True (小于)
print("a > b：", a > b)     # False (大于)
print("a <= b：", a <= b)   # True (小于等于)
print("a >= b：", a >= b)   # False (大于等于)

# 也可以比较字符串
str1 = "apple"
str2 = "banana"
print("\n字符串比较：")
print("str1 == str2：", str1 == str2)
print("str1 < str2：", str1 < str2)  # 按字母顺序比较
```

### 知识点 3：逻辑运算符

**描述：**
逻辑运算符用于组合多个条件，主要有 `and`、`or` 和 `not`。

**逻辑运算符：**

```python-exec
x = 5
y = 10
z = 15

print(f"x = {x}, y = {y}, z = {z}")

# and 运算符（所有条件都为真，结果才为真）
print(x < y and y < z)    # True (x < y 为真且 y < z 为真)
print(x < y and z < y)    # False (虽然 x < y 为真，但 z < y 为假)

# or 运算符（任意一个条件为真，结果就为真）
print(x < y or z < y)     # True (x < y 为真)
print(x > y or z < y)     # False (两个条件都为假)

# not 运算符（取反）
print(not x < y)         # False (x < y 为 True，取反为 False)
print(not x > y)         # True (x > y 为 False，取反为 True)
```

**逻辑运算的真值表：**

```
and 运算：
True and True → True
True and False → False
False and True → False
False and False → False

or 运算：
True or True → True
True or False → True
False or True → True
False or False → False

not 运算：
not True → False
not False → True
```

### 知识点 4：身份运算符

**描述：**
身份运算符用于比较两个对象的内存地址，判断它们是否是同一个对象。

**身份运算符：**

```python-exec
# 身份运算符
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print("a =", a)
print("b =", b)
print("c =", c)

# is 运算符（判断是否为同一个对象）
print("\na is b：", a is b)    # False (虽然是相同的值，但不是同一个对象)
print("a is c：", a is c)    # True (c 引用同一个对象)
print("a is not b：", a is not b)  # True

# == 和 is 的区别
print("a == b：", a == b)    # True (值相等)
print("a == c：", a == c)    # True (值相等)
```

### 知识点 5：成员运算符

**描述：**
成员运算符用于检查一个值是否在序列（如列表、字符串等）中。

**成员运算符：**

```python-exec
# 列表示例
fruits = ["apple", "banana", "orange"]

print("fruits =", fruits)
print("'apple' in fruits：", "apple" in fruits)
print("'grape' in fruits：", "grape" in fruits)
print("'pear' not in fruits：", "pear" not in fruits)

# 字符串示例
text = "Hello, World!"
print("\n字符串示例：")
print("'H' in text：", 'H' in text)
print("'hello' in text：", 'hello' in text)
print("'!' not in text：", '!' not in text)
```

### 知识点 6：位运算符（了解）

**描述：**
位运算符直接对整数的二进制位进行操作。虽然不常用，但了解它们有助于理解底层操作。

```python-exec
# 位运算符示例
a = 5   # 二进制：0101
b = 3   # 二进制：0011

print("a =", a, "二进制：", bin(a))
print("b =", b, "二进制：", bin(b))

print("按位与（&）：", a & b)     # 1 (0101 & 0011 = 0001)
print("按位或（|）：", a | b)     # 7 (0101 | 0011 = 0111)
print("按位异或（^）：", a ^ b)    # 6 (0101 ^ 0011 = 0110)
print("按位取反（~）：", ~a)     # -6 (~0101 = 1010)
print("左移（<<）：", a << 1)    # 10 (0101 << 1 = 1010)
print("右移（>>）：", a >> 1)    # 2 (0101 >> 1 = 0010)
```

### 知识点 7：运算符优先级

**描述：**
当一个表达式包含多个运算符时，Python 会按照一定的优先级顺序执行。

**运算符优先级（从高到低）：**

```
1. ()
2. ** (幂运算)
3. +x, -x, ~x (正负号, 按位取反)
4. *, /, %, // (乘除, 取余, 整除)
5. +, - (加减)
6. <<, >> (移位)
7. & (按位与)
8. ^ (按位异或)
9. | (按位或)
10. ==, !=, <, >, <=, >= (比较)
11. is, is not (身份)
12. in, not in (成员)
13. not (逻辑非)
14. and (逻辑与)
15. or (逻辑或)
```

**示例：**

```python-exec
# 运算符优先级示例
result = 10 + 5 * 3  # 先乘后加
print("10 + 5 * 3 =", result)  # 25

# 使用括号改变优先级
result2 = (10 + 5) * 3  # 先加后乘
print("(10 + 5) * 3 =", result2)  # 45

# 逻辑运算符优先级
result3 = True or False and True  # and 的优先级高于 or
print("True or False and True =", result3)  # True

# 相当于：
# True or (False and True) → True or False → True
```

### 知识点 8：表达式的使用

**描述：**
表达式是由变量、运算符和函数调用组成的代码片段，它会返回一个值。

**简单表达式示例：**

```python-exec
# 算术表达式
sum_result = 5 + 3 * 2
print("5 + 3 * 2 =", sum_result)

# 比较表达式
is_adult = age >= 18  # age 需要先定义
age = 20
print("age >= 18：", is_adult)

# 复杂表达式
x = 10
y = 20
z = 30

# 使用括号提高可读性
complex_expr = (x + y) * z / 2
print(f"({x} + {y}) * {z} / 2 =", complex_expr)
```

**条件表达式（三元运算符）：**

```python-exec
# 条件表达式（三元运算符）
age = 18
result = "成年" if age >= 18 else "未成年"
print(result)

# 使用条件表达式
x = 10
max_value = x if x > 5 else 5
print(f"最大值：{max_value}")
```

### 章节总结

本章我们学习了：
- 算术运算符：+、-、*、/、//、%、**
- 比较运算符：==、!=、<、>、<=、>=
- 逻辑运算符：and、or、not
- 身份运算符：is、is not
- 成员运算符：in、not in
- 位运算符：&、|、^、~、<<、>>
- 运算符优先级
- 表达式的使用

### 下一步

掌握了运算符后，让我们在下一章学习控制流中的条件语句，这些语句是编程逻辑的基础。

---
*本章内容基于 Python 教学平台标准格式设计。*
