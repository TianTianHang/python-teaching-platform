---
title: "集合"
order: 8
unlock_conditions:
  type: "prerequisite"
  prerequisites: [7]
---

## 集合

### 章节概述

集合是Python中用于存储唯一元素的无序数据结构。本章将学习如何创建集合、进行集合运算、使用集合方法，以及集合在实际编程中的应用。

### 知识点 1：集合的创建和特点

**描述：**
集合使用花括号 {} 创建，或使用 set() 函数。集合中的元素必须是唯一的，且是无序的。

**创建集合：**
```python-exec
# 使用花括号创建
fruits = {"苹果", "香蕉", "橙子"}
print(f"水果集合：{fruits}")

# 使用 set() 函数
numbers = set([1, 2, 3, 3, 4, 4, 5])  # 自动去重
print(f"数字集合：{numbers}")

# 创建空集合
empty_set = set()
print(f"空集合：{empty_set}")

# 从字符串创建字符集合
chars = set("hello")
print(f"字符集合：{chars}")
```

### 知识点 2：集合的基本操作

**描述：**
集合支持添加、删除元素，以及检查元素是否存在。

**基本操作：**
```python-exec
# 添加元素
fruits = {"苹果", "香蕉"}
print(f"原始：{fruits}")

fruits.add("橙子")
print(f"添加后：{fruits}")

# 添加多个元素
fruits.update(["葡萄", "西瓜"])
print(f"更新后：{fruits}")

# 删除元素
fruits.remove("香蕉")
print(f"删除'香蕉'后：{fruits}")

# 安全删除（元素不存在不报错）
fruits.discard("草莓")
print(f"尝试删除'草莓'：{fruits}")

# 弹出任意元素
popped = fruits.pop()
print(f"弹出的元素：{popped}")
print(f"弹出后：{fruits}")
```

### 知识点 3：集合运算

**描述：**
集合支持多种数学运算，如并集、交集、差集和对称差集。

**集合运算：**
```python-exec
# 创建两个集合
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

print(f"集合A：{A}")
print(f"集合B：{B}")

# 并集（所有元素）
union = A | B
print(f"并集：{union}")

# 交集（共同元素）
intersection = A & B
print(f"交集：{intersection}")

# 差集（A有B没有的）
difference = A - B
print(f"差集：{difference}")

# 对称差集（独有的元素）
symmetric_diff = A ^ B
print(f"对称差集：{symmetric_diff}")
```

### 知识点 4：集合的常用方法

**描述：**
集合提供了许多内置方法，方便进行各种操作。

**常用方法：**
```python-exec
# 创建集合
fruits = {"苹果", "香蕉", "橙子", "苹果"}  # 重复会被去重

print(f"集合长度：{len(fruits)}")

# 检查元素
print(f"'苹果'在集合中：{'苹果' in fruits}")
print(f"'葡萄'在集合中：{'葡萄' in fruits}")

# 复制集合
fruits_copy = fruits.copy()
print(f"复制：{fruits_copy}")

# 清空集合
fruits.clear()
print(f"清空后：{fruits}")

# 集合比较
A = {1, 2, 3}
B = {1, 2, 3}
C = {1, 2}

print(f"A是B的子集：{A.issubset(B)}")
print(f"B是A的超集：{B.issuperset(C)}")
```

### 知识点 5：集合 vs 列表

**描述：**
集合和列表都是容器，但它们有不同的特点和使用场景。

**比较：**
```python-exec
# 列表和集合的对比
list_data = [1, 2, 2, 3, 3, 3]  # 可重复，有序
set_data = {1, 2, 2, 3, 3, 3}    # 自动去重，无序

print(f"列表：{list_data}")
print(f"集合：{set_data}")

# 查找速度比较
import time

# 列表查找
start = time.time()
result = 3 in list_data
end = time.time()
print(f"列表查找时间：{(end-start)*1000:.6f}秒")

# 集合查找
start = time.time()
result = 3 in set_data
end = time.time()
print(f"集合查找时间：{(end-start)*1000:.6f}秒")
```

### 知识点 6：集合的应用场景

**描述：**
集合在编程中有很多实用的应用场景。

**应用场景：**
```python-exec
# 场景1：去除重复
data = [1, 2, 2, 3, 4, 4, 5]
unique = list(set(data))
print(f"去重后：{unique}")

# 场景2：共同好友
user1_friends = {"Alice", "Bob", "Charlie", "David"}
user2_friends = {"Bob", "Charlie", "Eve", "Frank"}

common = user1_friends & user2_friends
print(f"共同好友：{common}")

# 场景3：条件筛选
numbers = range(1, 21)
even = {x for x in numbers if x % 2 == 0}  # 集合推导式
print(f"偶数：{even}")
```

### 章节总结

本章我们学习了：
- 集合的创建方式和特点（唯一、无序）
- 集合的基本操作（添加、删除）
- 集合的数学运算（并集、交集等）
- 集合的常用方法
- 集合与列表的比较
- 集合的实际应用场景

### 下一步

掌握了集合后，让我们学习列表推导式与生成器，这是Python中处理数据的高效方法。

---
*本章内容基于 Python 教学平台标准格式设计。*
