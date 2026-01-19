---
title: "变量与数据类型"
order: 2
---
## 变量与数据类型

### 章节概述

本章将介绍Python中变量和数据类型的概念。变量是存储数据的容器，而数据类型决定了数据的性质和可进行的操作。理解这些概念是掌握Python编程的关键。

### 知识点 1：变量的定义与使用

**描述：**

变量是程序中用于存储数据的命名位置。你可以把变量想象成一个贴有标签的盒子，盒子里可以存放各种数据。在Python中，创建变量非常简单——只需要给变量赋值即可。

**示例代码：**
```python
# 创建变量的基本方式：变量名 = 值
name = "小明"
age = 18
height = 1.75
is_student = True

# 使用变量
print(name)  # 输出：小明
print(age)   # 输出：18

# 变量可以重新赋值
age = 19
print(age)   # 输出：19

# 使用变量进行计算
age_next_year = age + 1
print(age_next_year)  # 输出：20

# 变量命名规则
user_name = "张三"  # 好的命名：清晰描述变量用途
x = "李四"          # 不好的命名：不清楚x代表什么
```

**解释：**

在Python中：
- `=`是赋值符号，不是数学中的等于
- 变量名必须以字母或下划线开头，不能以数字开头
- 变量名只能包含字母、数字和下划线
- 变量名区分大小写（`name`和`Name`是不同的变量）
- 不能使用Python的关键字（如`if`、`for`、`while`等）作为变量名

**变量命名最佳实践：**
- 使用有意义的名称
- 多个单词用下划线连接（snake_case）
- 避免使用单字母变量名（除循环变量外）

---

### 知识点 2：基本数据类型

**描述：**

Python中有几种基本数据类型，每种类型用于存储不同种类的数据。最常用的基本数据类型包括：

1. **整数（int）**：没有小数部分的数字，可以是正数、负数或零
2. **浮点数（float）**：带有小数部分的数字
3. **字符串（str）**：用引号包围的文本
4. **布尔值（bool）**：只有两个值，`True`或`False`

**示例代码：**
```python
# 整数（int）
count = 42
temperature = -10
population = 1400000000

# 浮点数（float）
pi = 3.14159
price = 19.99
negative_float = -0.5

# 字符串（str）
message1 = "Hello"     # 双引号
message2 = 'World'     # 单引号
message3 = """多行字符串
可以跨多行"""          # 三引号

# 布尔值（bool）
is_raining = True
is_sunny = False
has_permission = True

# 查看变量的类型
print(type(count))        # <class 'int'>
print(type(pi))           # <class 'float'>
print(type(message1))     # <class 'str'>
print(type(is_raining))   # <class 'bool'>
```

**解释：**

- **整数**可以是任意大小，Python会自动处理大整数运算
- **浮点数**的小数部分可以是0，如`3.0`
- **字符串**可以用单引号、双引号或三引号创建
  - 单引号和双引号效果相同
  - 三引号用于多行字符串
- **布尔值**首字母必须大写（`True`/`False`，而非`true`/`false`）
- `type()`函数返回变量的数据类型

---

### 知识点 3：类型转换

**描述：**

有时候我们需要将一种数据类型转换为另一种数据类型，这称为**类型转换**或**类型强制转换**。Python提供了内置函数来实现这些转换。

**示例代码：**
```python
# 转换为整数
num1 = int("123")        # 字符串转整数
num2 = int(3.14)         # 浮点数转整数（截断小数部分）
num3 = int(True)         # 布尔值转整数（True=1, False=0）

print(num1)  # 123
print(num2)  # 3（注意不是四舍五入）
print(num3)  # 1

# 转换为浮点数
float1 = float("3.14")   # 字符串转浮点数
float2 = float(42)       # 整数转浮点数

print(float1)  # 3.14
print(float2)  # 42.0

# 转换为字符串
str1 = str(123)          # 数字转字符串
str2 = str(3.14)
str3 = str(True)

print(str1)  # "123"
print(str2)  # "3.14"
print(str3)  # "True"

# 转换为布尔值
print(bool(0))           # False
print(bool(1))           # True
print(bool(""))          # False（空字符串）
print(bool("hello"))     # True（非空字符串）
print(bool([]))          # False（空列表）
print(bool([1, 2]))      # True（非空列表）

# 实际应用示例
age_str = "18"
age_int = int(age_str)
age_next_year = age_int + 1
print(f"明年你将{age_next_year}岁")  # 明年你将19岁
```

**解释：**

- **int()**：转换为整数
  - 浮点数转整数会直接截断小数部分（不四舍五入）
  - 字符串必须包含有效的数字表示

- **float()**：转换为浮点数
  - 整数转换后会添加`.0`

- **str()**：转换为字符串
  - 几乎任何类型都可以转换为字符串

- **bool()**：转换为布尔值
  - 以下值转换为`False`：`0`、`0.0`、`""`（空字符串）、`[]`（空列表）、`None`
  - 其他所有值转换为`True`

**注意：**如果字符串无法转换为数字，会引发`ValueError`错误。

---
*本章内容基于 Python 教学平台标准格式设计。*
