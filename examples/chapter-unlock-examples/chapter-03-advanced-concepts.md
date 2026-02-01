---
title: "Python 高级概念"
order: 3
unlock_conditions:
  type: "all"
  prerequisites: [1, 2]
---

## Python 高级概念

### 章节概述

本章将介绍 Python 的高级概念，包括函数、模块、异常处理和面向对象编程。通过学习本章内容，你将能够编写更加复杂和结构化的 Python 程序。

### 知识点 1：函数定义和使用

**描述：**
函数是 Python 中的一等公民，可以作为参数传递给其他函数，也可以作为返回值。函数使用 `def` 关键字定义。

**示例代码：**
```python
# 定义函数
def greet(name):
    """函数：向用户问候"""
    return f"你好，{name}！欢迎学习Python。"

# 带默认参数的函数
def power(base, exponent=2):
    """计算 base 的 exponent 次方"""
    return base ** exponent

# 可变参数函数
def sum_numbers(*numbers):
    """计算任意数字的和"""
    return sum(numbers)

# 使用函数
print(greet("李四"))
print(f"2的3次方：{power(2, 3)}")
print(f"1到5的和：{sum_numbers(1, 2, 3, 4, 5)}")
```

**解释：**
Python 的函数支持参数类型丰富，包括位置参数、关键字参数、默认参数和可变参数。函数可以有返回值，也可以没有返回值（默认返回 None）。

### 知识点 2：面向对象编程基础

**描述：**
Python 支持面向对象编程，使用类和对象来组织代码。类定义了对象的属性和方法。

**示例代码：**
```python
# 定义类
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"我是{self.name}，今年{self.age}岁。"

    def birthday(self):
        self.age += 1
        return f"{self.name}生日快乐！现在{self.age}岁了。"

# 创建对象
student1 = Student("王五", 20)
print(student1.introduce())

# 调用方法
print(student1.birthday())
print(student1.introduce())
```

**解释：**
Python 的类使用 `class` 关键字定义，`__init__` 方法是构造函数。类的方法使用 `self` 参数来引用对象本身。通过类可以创建多个实例（对象）。

**关键要点：**
- 函数可以提高代码的复用性
- 类和对象有助于组织复杂的代码结构
- 方法操作对象的状态
- 面向对象编程可以更好地模拟现实世界

---

*本章内容基于 Python 教学平台标准格式设计。*
