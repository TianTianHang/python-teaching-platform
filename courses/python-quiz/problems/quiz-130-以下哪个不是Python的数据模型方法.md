---
title: "以下哪个不是Python的数据模型方法"
type: "choice"
difficulty: 2
chapter: 1
is_multiple_choice: false
options:
  A: "__add__** - 数据模型方法 ✓
python
class MyClass:
    def __add__(self, other):
        return MyClass()"
  B: "__str__** - 数据模型方法 ✓
python
class MyClass:
    def __str__(self):
        return "MyClass instance""
  C: "__contains__** - 数据模型方法 ✓
python
class MyContainer:
    def __contains__(self, item):
        return item in [1, 2, 3]"
  D: "__name__** - **不是**数据模型方法 ✗
python
def my_function():
    pass"
correct_answer: "D"
---

## 题目描述

以下哪个不是Python的数据模型方法

### 选项

- A: __add__** - 数据模型方法 ✓
python
class MyClass:
    def __add__(self, other):
        return MyClass()
- B: __str__** - 数据模型方法 ✓
python
class MyClass:
    def __str__(self):
        return "MyClass instance"
- C: __contains__** - 数据模型方法 ✓
python
class MyContainer:
    def __contains__(self, item):
        return item in [1, 2, 3]
- D: __name__** - **不是**数据模型方法 ✗
python
def my_function():
    pass

