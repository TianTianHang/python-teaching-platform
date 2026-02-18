---
title: "列表推导式与生成器"
order: 12
unlock_conditions:
  type: "prerequisite"
  prerequisites: [11]
---

## 列表推导式与生成器

### 章节概述

列表推导式是Python中一种简洁高效的数据处理方式，而生成器是一种特殊的迭代器。本章将学习如何使用列表推导式创建列表，以及使用生成器来处理大量数据。

### 知识点 1：列表推导式基础

**描述：**
列表推导式是创建列表的简洁方式，用一行代码就能完成原本需要多行循环代码的任务。

**基本语法：**
```python-exec
# 传统方式
squares = []
for i in range(1, 6):
    squares.append(i * i)
print(f"传统方式：{squares}")

# 列表推导式
squares = [i * i for i in range(1, 6)]
print(f"列表推导式：{squares}")

# 更多例子
numbers = [1, 2, 3, 4, 5]
doubles = [x * 2 for x in numbers]
evens = [x for x in range(10) if x % 2 == 0]
print(f"翻倍：{doubles}")
print(f"偶数：{evens}")
```

### 知识点 2：带条件的列表推导式

**描述：**
可以在列表推导式中添加条件，过滤出符合条件的元素。

**条件过滤：**
```python-exec
# 基本条件
numbers = range(1, 21)
even_squares = [x * x for x in numbers if x % 2 == 0]
print(f"偶数平方：{even_squares}")

# 多个条件
divisible_by_3_5 = [x for x in range(30) if x % 3 == 0 and x % 5 == 0]
print(f"能被3和5整除：{divisible_by_3_5}")

# 文字示例
words = ["Python", "is", "great", "and", "powerful"]
long_words = [word for word in words if len(word) > 4]
print(f"长单词：{long_words}")
```

### 知识点 3：嵌套列表推导式

**描述：**
可以在列表推导式内部再使用列表推导式，处理嵌套数据结构。

**嵌套处理：**
```python-exec
# 二维矩阵转置
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

transposed = [[row[i] for row in matrix] for i in range(3)]
print(f"转置矩阵：{transposed}")

# 扁平化嵌套列表
nested_list = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
flat = [item for sublist in nested_list for item in sublist]
print(f"扁平化：{flat}")

# 过滤嵌套
nested_numbers = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
even_nested = [sublist for sublist in nested_numbers if 3 in sublist]
print(f"包含3的子列表：{even_nested}")
```

### 知识点 4：集合推导式和字典推导式

**描述：**
类似列表推导式，也可以创建集合和字典。

**其他推导式：**
```python-exec
# 集合推导式（自动去重）
words = "hello world hello python"
unique_words = {word for word in words.split()}
print(f"不重复单词：{unique_words}")

# 字典推导式
names = ["Alice", "Bob", "Charlie"]
lengths = {name: len(name) for name in names}
print(f"名字长度：{lengths}")

# 字典键值交换
original = {1: "a", 2: "b", 3: "c"}
swapped = {v: k for k, v in original.items()}
print(f"交换后：{swapped}")
```

### 知识点 5：生成器表达式

**描述：**
生成器表达式与列表推导式类似，但不创建列表，而是返回一个生成器对象，按需产生数据。

**生成器基础：**
```python-exec
# 列表推导式（立即创建）
numbers = range(1, 1000000)
squares_list = [x * x for x in numbers]
print(f"列表推导式类型：{type(squares_list)}")

# 生成器表达式（延迟计算）
squares_gen = (x * x for x in numbers)
print(f"生成器类型：{type(squares_gen)}")

# 获取生成器的值
print(f"前5个平方数：")
for i, square in enumerate(squares_gen):
    print(square, end=" ")
    if i >= 4:
        break
```

### 知识点 6：生成器函数

**描述：**
使用yield关键字的函数称为生成器函数，每次yield都会暂停函数并返回一个值。

**生成器函数：**
```python-exec
# 简单生成器
def count_up_to(n):
    """生成从1到n的数字"""
    i = 1
    while i <= n:
        yield i
        i += 1

# 使用生成器
numbers = count_up_to(5)
print(f"生成器对象：{numbers}")

# 逐个获取
print("数字：")
for num in numbers:
    print(num, end=" ")

# 斐波那契数列
def fibonacci(n):
    """生成斐波那契数列"""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

print("\n斐波那契数列：")
for num in fibonacci(8):
    print(num, end=" ")
```

### 章节总结

本章我们学习了：
- 列表推导式的基本语法和优势
- 带条件的列表推导式
- 嵌套列表推导式的使用
- 集合推导式和字典推导式
- 生成器表达式（内存高效）
- 生成器函数和yield关键字

### 下一步

掌握了列表推导式和生成器后，让我们学习文件操作，了解如何读取和写入文件。

---
*本章内容基于 Python 教学平台标准格式设计。*
