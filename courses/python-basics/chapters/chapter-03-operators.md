---
title: "运算符与表达式"
order: 3
---
## 运算符与表达式

### 章节概述

运算符是用于执行运算的特殊符号。Python提供了多种运算符，包括算术运算符、比较运算符、逻辑运算符等。本章将详细介绍这些运算符的用法和优先级规则。

### 知识点 1：算术运算符

**描述：**

算术运算符用于执行数学运算，如加、减、乘、除等。Python支持所有基本的算术运算符。

**示例代码：**
```python
# 基本算术运算
a = 10
b = 3

print(a + b)   # 加法：13
print(a - b)   # 减法：7
print(a * b)   # 乘法：30
print(a / b)   # 除法（结果总是浮点数）：3.3333...
print(a % b)   # 取模（余数）：1
print(a ** b)  # 幂运算：10的3次方=1000
print(a // b)  # 整除（向下取整）：3

# 负数的整除
print(-10 // 3)   # -4（向下取整，-3.33向下是-4）
print(10 // -3)   # -4
print(-10 // -3)  # 3

# 实际应用示例
# 计算圆的面积
radius = 5
area = 3.14159 * radius ** 2
print(f"圆的面积是：{area:.2f}")  # 圆的面积是：78.54

# 温度转换：摄氏度转华氏度
celsius = 25
fahrenheit = celsius * 9/5 + 32
print(f"{celsius}°C = {fahrenheit}°F")  # 25°C = 77.0°F
```

**解释：**

- **`+` 加法**：两数相加
- **`-` 减法**：两数相减
- **`*` 乘法**：两数相乘
- **`/` 除法**：真除法，结果总是浮点数
- **`%` 取模**：返回除法的余数
- **`**` 幂运算**：计算x的y次方
- **`//` 整除**：向下取整除法

**整除特别注意：**
- 整除总是向下取整（向负无穷方向），而不是简单的截断
- `10 // 3 = 3`（3.33向下是3）
- `-10 // 3 = -4`（-3.33向下是-4）

---

### 知识点 2：比较运算符

**描述：**

比较运算符用于比较两个值，返回布尔值（`True`或`False`）。它们常用于条件判断中。

**示例代码：**
```python
# 基本比较运算
a = 10
b = 5

print(a == b)   # 等于：False
print(a != b)   # 不等于：True
print(a > b)    # 大于：True
print(a < b)    # 小于：False
print(a >= b)   # 大于等于：True
print(a <= b)   # 小于等于：False

# 字符串比较（按字母顺序）
str1 = "apple"
str2 = "banana"
print(str1 < str2)  # True（a在b前面）

# 实际应用示例
age = 18
is_adult = age >= 18
print(f"是否成年：{is_adult}")  # 是否成年：True

score = 85
is_pass = score >= 60
print(f"是否及格：{is_pass}")  # 是否及格：True

# 判断数字是否在某个范围内
num = 50
in_range = 0 <= num <= 100
print(f"数字在0-100范围内：{in_range}")  # True
```

**解释：**

- **`==` 等于**：注意是两个等号，一个是赋值，两个是比较
- **`!=` 不等于**：如果两个值不相等则返回`True`
- **`>` 大于**：左边大于右边
- **`<` 小于**：左边小于右边
- **`>=` 大于等于**：左边大于或等于右边
- **`<=` 小于等于**：左边小于或等于右边

**字符串比较：**
Python按字典序（字母顺序）比较字符串，从第一个字符开始逐个比较。

**链式比较：**
Python支持链式比较，如`0 <= num <= 100`，这比`num >= 0 and num <= 100`更简洁。

---

### 知识点 3：逻辑运算符

**描述：**

逻辑运算符用于组合多个条件，返回布尔值。Python有三个逻辑运算符：`and`（与）、`or`（或）、`not`（非）。

**示例代码：**
```python
# and 运算：两个条件都为True时结果为True
print(True and True)    # True
print(True and False)   # False
print(False and False)  # False

# or 运算：至少一个条件为True时结果为True
print(True or True)     # True
print(True or False)    # True
print(False or False)   # False

# not 运算：取反
print(not True)   # False
print(not False)  # True

# 实际应用示例
age = 25
has_ticket = True

# 判断是否可以进入电影院（年龄>=18 且有票）
can_enter = age >= 18 and has_ticket
print(f"可以进入电影院：{can_enter}")  # True

# 判断是否享受优惠（年龄<18 或 年龄>65）
age = 70
is_discount = age < 18 or age > 65
print(f"享受优惠：{is_discount}")  # True

# 判断密码是否有效（长度>=8 且包含数字）
password = "abc123"
is_valid = len(password) >= 8 and any(c.isdigit() for c in password)
print(f"密码有效：{is_valid}")  # False（长度不足8）

# 短路求值示例
# and：如果第一个为False，不会计算第二个
result = False and print("这不会打印")
print(result)  # False

# or：如果第一个为True，不会计算第二个
result = True or print("这不会打印")
print(result)  # True
```

**解释：**

**and（与）运算：**
- `True and True` = `True`
- 其他所有情况都是`False`
- 短路：如果第一个条件为`False`，不会计算第二个条件

**or（或）运算：**
- `False or False` = `False`
- 其他所有情况都是`True`
- 短路：如果第一个条件为`True`，不会计算第二个条件

**not（非）运算：**
- `not True` = `False`
- `not False` = `True`

**短路求值：**
逻辑运算符采用"短路"求值策略，这意味着：
- `A and B`：如果A为`False`，不会计算B（因为结果必定是`False`）
- `A or B`：如果A为`True`，不会计算B（因为结果必定是`True`）

这个特性可以提高效率，也用于条件判断中避免错误（如`x != 0 and 1/x > 0`，避免除零错误）。

---

### 运算符优先级

当表达式中有多个运算符时，Python会按照优先级顺序进行计算。常见运算符的优先级（从高到低）：

1. 括号 `()`
2. 幂运算 `**`
3. 正负号 `+x` `-x`
4. 乘除模 `*` `/` `//` `%`
5. 加减 `+` `-`
6. 比较运算符 `==` `!=` `>` `<` `>=` `<=`
7. 逻辑非 `not`
8. 逻辑与 `and`
9. 逻辑或 `or`

**示例：**
```python
result = 2 + 3 * 4        # 14（先乘后加）
result = (2 + 3) * 4      # 20（括号优先）
result = 10 > 5 and 7 < 3 # False（先比较，再and）
```

**建议：**当表达式复杂时，使用括号明确运算顺序，这样代码更易读。

---
*本章内容基于 Python 教学平台标准格式设计。*
