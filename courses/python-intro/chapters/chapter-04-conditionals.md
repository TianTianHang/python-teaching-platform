---
title: "控制流 - 条件语句"
order: 4
unlock_conditions:
  type: "prerequisite"
  prerequisites: [3]
---

## 控制流 - 条件语句

### 章节概述

条件语句是编程中的核心概念之一，它允许程序根据不同的条件执行不同的代码路径。本章将学习 Python 中的 if、if-else 和 if-elif-else 语句。

### 知识点 1：if 语句

**描述：**
if 语句是最基本的条件语句，当条件为真时，执行其对应的代码块。

**基本语法：**
```python
if 条件:
    # 条件为真时执行的代码
    # 注意：使用缩进（通常是4个空格）
```

**示例代码：**
```python-exec
# 基本的 if 语句
age = 20

if age >= 18:
    print("你已经成年了！")

print("这条语句总是会执行的")
```

**条件判断：**
```python-exec
# 使用比较运算符作为条件
score = 85

if score >= 60:
    print("恭喜，你及格了！")

# 使用布尔变量
is_raining = True

if is_raining:
    print("记得带伞！")
```

### 知识点 2：if-else 语句

**描述：**
if-else 语句在条件为真时执行一个代码块，为假时执行另一个代码块。

**基本语法：**
```python
if 条件:
    # 条件为真时执行的代码
else:
    # 条件为假时执行的代码
```

**示例代码：**
```python-exec
# if-else 语句
age = 16

if age >= 18:
    print("你已经成年了")
else:
    print("你还未成年")

# 分数等级判断
score = 75

if score >= 90:
    print("优秀")
else:
    print("需要继续努力")
```

**更复杂的条件判断：**
```python-exec
# 多个条件
score = 85

if score >= 60:
    print("及格")
    if score >= 90:
        print("优秀")
    else:
        print("良好")
else:
    print("不及格")
```

### 知识点 3：if-elif-else 语句

**描述：**
if-elif-else 语句用于处理多个条件，按顺序检查，执行第一个满足条件的代码块。

**基本语法：**
```python
if 条件1:
    # 条件1为真时执行的代码
elif 条件2:
    # 条件2为真时执行的代码
elif 条件3:
    # 条件3为真时执行的代码
else:
    # 所有条件都不满足时执行的代码
```

**示例代码：**
```python-exec
# if-elif-else 语句
score = 75

if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

**天气判断示例：**
```python-exec
# 天气判断
weather = "sunny"

if weather == "sunny":
    print("今天阳光明媚，适合出门")
elif weather == "rainy":
    print("下雨了，记得带伞")
elif weather == "cloudy":
    print("多云，有点凉爽")
else:
    print("天气未知，请查看天气预报")
```

### 知识点 4：嵌套条件语句

**描述：**
条件语句可以嵌套使用，即在一个条件语句内部包含另一个条件语句。

**示例代码：**
```python-exec
# 嵌套条件语句
age = 20
has_id = True

if age >= 18:
    print("你已经成年了")
    if has_id:
        print("可以办理身份证")
    else:
        print("没有身份证，不能办理")
else:
    print("你还未成年")

# 学生成绩判断
score = 88
is_regular_student = True

if is_regular_student:
    if score >= 90:
        print("学生：优秀")
    elif score >= 80:
        print("学生：良好")
    elif score >= 60:
        print("学生：及格")
    else:
        print("学生：不及格")
else:
    print("不是学生，成绩评定标准不同")
```

### 知识点 5：条件表达式（三元运算符）

**描述：**
Python 提供了一种简洁的条件表达式语法，也称为三元运算符。

**基本语法：**
```python
value_if_true if condition else value_if_false
```

**示例代码：**
```python-exec
# 简单的条件表达式
age = 20
status = "成年" if age >= 18 else "未成年"
print(status)

# 在表达式中使用
score = 85
message = f"成绩是{score}，{'及格' if score >= 60 else '不及格'}"
print(message)

# 更复杂的条件表达式
x = 15
y = 20
max_value = x if x > y else y
print(f"最大值是：{max_value}")
```

### 知识点 6：布尔逻辑和短路运算

**描述：**
Python 支持布尔逻辑，并且有短路运算的特性。短路运算意味着在复杂表达式中，一旦结果已经确定，就不会继续计算剩余部分。

**布尔逻辑示例：**
```python-exec
# 布尔逻辑
is_adult = True
has_id = False

if is_adult and has_id:
    print("可以进入夜店")
else:
    print("不能进入夜店")

if is_adult or has_id:
    print("可以进入某些场所")
else:
    print("不能进入任何场所")
```

**短路运算：**
```python-exec
# 短路运算示例
def check_true():
    print("检查 True")
    return True

def check_false():
    print("检查 False")
    return False

# and 的短路：如果第一个是 False，不会检查第二个
print("False and check_true():")
result = False and check_true()  # 不会调用 check_true()
print("结果：", result)

# or 的短路：如果第一个是 True，不会检查第二个
print("\nTrue or check_false():")
result = True or check_false()  # 不会调用 check_false()
print("结果：", result)
```

### 知识点 7：条件语句的常见用法

**描述：**
条件语句在实际编程中有多种常用模式，掌握这些模式能帮助你写出更清晰的代码。

**模式 1：检查多个条件**
```python-exec
# 检查多个条件
x = 15
y = 20

if x > 10 and y > 10:
    print("x 和 y 都大于 10")

if x > 10 or y > 10:
    print("x 或 y 大于 10")

if not x < 10:
    print("x 不小于 10")
```

**模式 2：范围检查**
```python-exec
# 范围检查
score = 85

if 60 <= score <= 100:
    print("成绩在有效范围内")
    if score >= 90:
        print("优秀")
    elif score >= 80:
        print("良好")
    elif score >= 60:
        print("及格")
else:
    print("成绩无效")
```

**模式 3：判断空值**
```python-exec
# 判断空值
name = ""
age = 0

if not name:
    print("姓名为空")

if not age:
    print("年龄为0")
```

### 知识点 8：条件语句的最佳实践

**描述：**
使用条件语句时，遵循一些最佳实践可以让代码更易读、更易维护。

**最佳实践：**

```python-exec
# 清晰的命名
temperature = 25
if temperature > 30:
    print("天气炎热")
elif temperature > 20:
    print("天气温暖")
else:
    print("天气凉爽")

# 提前返回避免深层嵌套
def process_user(user):
    if not user:
        return False  # 快速失败

    if not user.get("age"):
        return False

    if user["age"] < 18:
        return False

    # 处理有效用户
    return True

# 使用字典映射代替长 if-elif 链
grade_map = {
    90: "优秀",
    80: "良好",
    60: "及格"
}

score = 85
grade = grade_map.get(score, "不及格")
print(f"成绩等级：{grade}")
```

### 章节总结

本章我们学习了：
- if 语句的基本用法
- if-else 语句的条件分支
- if-elif-else 语句的多条件判断
- 嵌套条件语句的使用
- 条件表达式（三元运算符）
- 布尔逻辑和短路运算
- 条件语句的常见用法
- 条件语句的最佳实践

### 下一步

掌握了条件语句后，让我们在下一章学习控制流中的循环语句，它们能让程序重复执行特定的代码。

---
*本章内容基于 Python 教学平台标准格式设计。*
