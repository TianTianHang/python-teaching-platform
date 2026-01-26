---
title: "变量与数据类型"
order: 2
---

## 变量与数据类型

### 章节概述

变量是编程中最基本的概念之一，它就像一个容器，可以存储各种类型的数据。本章将学习如何使用变量、Python 的基本数据类型以及如何进行类型转换。

### 知识点 1：什么是变量

**描述：**
变量是程序中用于存储数据的命名位置。你可以把变量想象成一个贴了标签的盒子，盒子里可以存放不同的内容。

**变量的创建和使用：**

```python-exec
# 创建变量并赋值
name = "张三"
age = 25
height = 1.75

# 使用变量
print("姓名：", name)
print("年龄：", age)
print("身高：", height)
```

**解释：**
- `=` 是赋值运算符，将右侧的值赋给左侧的变量
- 变量名在左侧，值在右侧
- 变量一旦创建，就可以反复使用

### 知识点 2：变量命名规则

**描述：**
Python 对变量命名有一些规则，必须遵守这些规则，否则程序会报错。

**命名规则：**
- 只能包含字母、数字和下划线
- 不能以数字开头
- 不能使用 Python 的关键字（如 `if`、`for`、`while` 等）
- 区分大小写（`name` 和 `Name` 是不同的变量）
- 建议使用有意义的名称

**有效的变量名：**
```python-exec
# 有效的变量名
user_name = "李四"
user_age = 30
score1 = 95
_score = 100

# 打印这些变量
print(user_name, user_age, score1, _score)
```

**无效的变量名示例：**
- `2name` - 不能以数字开头
- `user-name` - 不能使用连字符
- `class` - 不能使用关键字
- `user name` - 不能包含空格

**命名建议（PEP 8 规范）：**
```python-exec
# 推荐的命名方式：使用小写字母和下划线
first_name = "王"
last_name = "小明"
student_age = 18

# 不推荐的命名方式（虽然可以运行）
FirstName = "王"  # 应使用小写
a = 18  # 应使用有意义的名称
```

### 知识点 3：基本数据类型 - 整数和浮点数

**描述：**
Python 中有多种数据类型，最基本的是数值类型：整数（int）和浮点数（float）。

**整数（int）：**
整数是没有小数部分的数字，可以是正数、负数或零。

```python-exec
# 整数示例
num1 = 10
num2 = -5
num3 = 0

print("num1 =", num1)
print("num2 =", num2)
print("num3 =", num3)

# 查看数据类型
print("num1 的类型是：", type(num1))
```

**浮点数（float）：**
浮点数是带有小数部分的数字。

```python-exec
# 浮点数示例
pi = 3.14159
temperature = -12.5
price = 99.99

print("圆周率 =", pi)
print("温度 =", temperature)
print("价格 =", price)

# 查看数据类型
print("pi 的类型是：", type(pi))
```

**数值运算：**
```python-exec
# 基本运算
a = 10
b = 3

print("加法：", a + b)      # 13
print("减法：", a - b)      # 7
print("乘法：", a * b)      # 30
print("除法：", a / b)      # 3.333... (浮点数)
print("整除：", a // b)     # 3 (整数)
print("取余：", a % b)      # 1
print("幂运算：", a ** b)   # 1000
```

### 知识点 4：基本数据类型 - 字符串

**描述：**
字符串（str）是由字符组成的序列，用于表示文本。在 Python 中，字符串可以使用单引号、双引号或三引号来创建。

**字符串的创建：**
```python-exec
# 使用单引号
str1 = 'Hello'

# 使用双引号
str2 = "World"

# 使用三引号（可以跨越多行）
str3 = '''这是一个
多行字符串'''

print(str1)
print(str2)
print(str3)
```

**字符串的拼接：**
```python-exec
# 字符串拼接
first_name = "张"
last_name = "三"
full_name = first_name + last_name

print("完整姓名：", full_name)

# 字符串与数字拼接需要先转换
age = 25
message = "我今年 " + str(age) + " 岁"
print(message)
```

### 知识点 5：基本数据类型 - 布尔值

**描述：**
布尔值（bool）只有两个可能的值：`True`（真）和 `False`（假）。布尔值常用于条件判断。

```python-exec
# 布尔值示例
is_student = True
is_working = False
has_license = True

print("是学生：", is_student)
print("在工作：", is_working)
print("有驾照：", has_license)

# 查看数据类型
print("is_student 的类型是：", type(is_student))

# 比较运算返回布尔值
print("5 > 3：", 5 > 3)
print("10 == 10：", 10 == 10)
```

### 知识点 6：类型转换

**描述：**
有时需要将一种数据类型转换为另一种类型，Python 提供了内置的类型转换函数。

**类型转换函数：**
- `int()` - 转换为整数
- `float()` - 转换为浮点数
- `str()` - 转换为字符串

```python-exec
# 转换为整数
num1 = int("123")
num2 = int(3.7)  # 会截断小数部分
print("int('123') =", num1)
print("int(3.7) =", num2)

# 转换为浮点数
num3 = float("3.14")
num4 = float(5)
print("float('3.14') =", num3)
print("float(5) =", num4)

# 转换为字符串
text1 = str(100)
text2 = str(3.14)
print("str(100) =", text1)
print("str(3.14) =", text2)
```

**注意：** 不是所有类型都能相互转换
```python-exec
# 这样会报错
try:
    invalid = int("abc")
except:
    print("无法将 'abc' 转换为整数")

# 但可以转换包含数字的字符串
valid = int("123")
print("int('123') =", valid)
```

### 知识点 7：输入和输出

**描述：**
程序经常需要与用户交互，获取用户输入并显示结果。

**输出 - print() 函数：**
```python-exec
# 基本输出
print("Hello, Python!")

# 输出多个内容（用逗号分隔）
name = "小明"
age = 18
print("姓名：", name, "年龄：", age)

# 使用 f-string 格式化输出（推荐）
print(f"姓名：{name}，年龄：{age}")
```

**输入 - input() 函数：**
```python-exec
# 注意：在 Jupyter 中，input() 需要在单独的单元格中运行
# 下面的代码演示了 input 的用法

# 获取用户输入
name = input("请输入你的姓名：")
print("你好，", name)

# 注意：input() 总是返回字符串类型
age_str = input("请输入你的年龄：")
print("你的年龄是：", age_str)
print("年龄的类型是：", type(age_str))

# 如果需要数值，需要进行类型转换
age = int(input("请输入你的年龄："))
print("明年你将", age + 1, "岁")
```

### 知识点 8：动态类型和类型检查

**描述：**
Python 是动态类型语言，变量的类型在运行时确定，并且可以改变。

```python-exec
# 动态类型示例
x = 10        # x 是整数
print("x =", x, "类型是", type(x))

x = "Hello"   # x 现在是字符串
print("x =", x, "类型是", type(x))

x = 3.14      # x 现在是浮点数
print("x =", x, "类型是", type(x))

# 使用 type() 检查类型
a = 42
b = "Python"
c = True

print("\n类型检查：")
print(f"a = {a}, 类型是 {type(a)}")
print(f"b = {b}, 类型是 {type(b)}")
print(f"c = {c}, 类型是 {type(c)}")
```

### 章节总结

本章我们学习了：
- 变量的概念和使用
- 变量命名规则和最佳实践
- 基本数据类型：整数、浮点数、字符串、布尔值
- 类型转换的方法
- 输入和输出的使用
- Python 的动态类型特性

### 下一步

掌握了变量和数据类型后，让我们在下一章学习运算符，了解如何对这些数据进行各种运算。

---
*本章内容基于 Python 教学平台标准格式设计。*
