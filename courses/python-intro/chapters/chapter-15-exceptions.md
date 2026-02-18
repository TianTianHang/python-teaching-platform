---
title: "异常处理"
order: 15
unlock_conditions:
  type: "prerequisite"
  prerequisites: [14]
---

## 异常处理

### 章节概述

程序运行时可能会出现各种错误，异常处理是Python中处理这些错误的方式。本章将学习如何捕获和处理异常，使程序更加健壮。

### 知识点 1：异常的基本概念

**描述：**
异常是程序运行时发生的错误，如除零错误、文件不存在等。使用try-except可以捕获和处理这些异常。

**异常处理基础：**
```python-exec
# 可能发生错误的代码
try:
    # 尝试执行的代码
    result = 10 / 0
except ZeroDivisionError:
    # 处理除零错误
    print("错误：不能除以零！")
    result = None

print(f"结果：{result}")

# 不同类型异常
try:
    num = int("abc")
except ValueError:
    print("错误：无法转换为数字！")
```

### 知识点 2：捕获多个异常

**描述：**
一个try块可以捕获多种不同类型的异常，分别处理。

**多异常处理：**
```python-exec
# 多个except子句
def handle_input(user_input):
    try:
        # 尝试各种操作
        num = int(user_input)
        result = 10 / num
        print(f"结果：{result}")
    except ValueError:
        print("错误：请输入一个有效的数字！")
    except ZeroDivisionError:
        print("错误：不能除以零！")
    except Exception as e:
        print(f"未知错误：{e}")

# 测试不同的错误
handle_input("abc")      # ValueError
handle_input("0")        # ZeroDivisionError
handle_input("5")        # 正常
```

### 知识点 3：try-except-else结构

**描述：**
try语句可以配合else使用，当没有异常发生时执行else块。

**try-else：**
```python-exec
# 使用else
try:
    filename = "data.txt"
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
        print(f"文件长度：{len(content)}")
except FileNotFoundError:
    print("错误：文件不存在！")
except Exception as e:
    print(f"其他错误：{e}")
else:
    # 没有异常时执行
    print("文件读取成功！")
    # 这里可以处理文件内容
```

### 知识点 4：finally语句

**描述：**
finally块无论是否发生异常都会执行，通常用于清理资源。

**finally：**
```python-exec
def process_file(filename):
    file = None
    try:
        file = open(filename, "r", encoding="utf-8")
        content = file.read()
        print(f"内容：{content}")
        return "成功"
    except FileNotFoundError:
        print("错误：文件不存在！")
        return "失败"
    finally:
        # 无论是否出错都会执行
        if file:
            file.close()
        print("文件已关闭")

# 测试
result = process_file("data.txt")
print(f"处理结果：{result}")
```

### 知识点 5：raise语句

**描述：**
可以使用raise主动抛出异常，用于错误条件检查。

**主动抛出异常：**
```python-exec
def check_age(age):
    """检查年龄是否合法"""
    if age < 0:
        raise ValueError("年龄不能为负数！")
    elif age > 150:
        raise ValueError("年龄不能超过150岁！")
    else:
        return "年龄合法"

# 测试
try:
    result = check_age(-5)
    print(result)
except ValueError as e:
    print(f"错误：{e}")

try:
    result = check_age(200)
    print(result)
except ValueError as e:
    print(f"错误：{e}")

try:
    result = check_age(25)
    print(result)
except ValueError as e:
    print(f"错误：{e}")
```

### 知识点 6：自定义异常

**描述：**
可以通过继承Exception类创建自定义异常类型。

**自定义异常：**
```python-exec
# 创建自定义异常
class BankError(Exception):
    """银行相关异常"""
    pass

class InsufficientBalance(BankError):
    """余额不足"""
    pass

class NegativeAmount(BankError):
    """金额为负数"""
    pass

# 使用自定义异常
def withdraw(balance, amount):
    if amount < 0:
        raise NegativeAmount("取款金额不能为负数！")
    if amount > balance:
        raise InsufficientBalance("余额不足！")
    return balance - amount

# 测试
try:
    balance = 1000
    print(f"当前余额：{balance}")

    # 尝试取款
    new_balance = withdraw(balance, -500)
    print(f"取款后余额：{new_balance}")
except BankError as e:
    print(f"银行错误：{e}")
```

### 章节总结

本章我们学习了：
- 异常的基本概念和try-except结构
- 捕获多种异常的方法
- try-except-else的使用
- finally语句的清理作用
- raise语句主动抛出异常
- 自定义异常类的创建

### 下一步

掌握了异常处理后，让我们学习模块与包，了解如何组织和管理Python代码。

---
*本章内容基于 Python 教学平台标准格式设计。*
