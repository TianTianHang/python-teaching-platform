---
title: "元组"
order: 7
unlock_conditions:
  type: "prerequisite"
  prerequisites: [6]
---

## 元组

### 章节概述

元组是Python中的另一种序列类型，与列表类似，但元组是不可变的。这意味着元组一旦创建就不能修改。本章将学习元组的创建、访问和基本操作。

### 知识点 1：元组的创建

**描述：**
元组使用圆括号 () 来创建，元素之间用逗号分隔。即使只有一个元素，也需要在后面加上逗号。

**创建元组：**
```python-exec
# 创建空元组
empty_tuple = ()
print(f"空元组：{empty_tuple}")

# 创建单元素元组（必须有逗号）
single_tuple = (1,)
print(f"单元素元组：{single_tuple}")

# 创建多元素元组
fruits = ("苹果", "香蕉", "橙子")
print(f"水果元组：{fruits}")

# 不使用圆括号（隐式创建）
coordinates = 100, 200
print(f"坐标：{coordinates}")
```

### 知识点 2：元组的访问

**描述：**
元组可以通过索引访问单个元素，通过切片访问子序列。

**访问元素：**
```python-exec
# 索引访问
colors = ("红", "绿", "蓝", "黄")

print(f"第1个颜色：{colors[0]}")
print(f"第2个颜色：{colors[1]}")
print(f"最后一个颜色：{colors[-1]}")

# 切片访问
print(f"前2个颜色：{colors[:2]}")
print(f"从第2个到第3个：{colors[1:3]}")

# 使用步长
print(f"隔一个取一个：{colors[::2]}")
print(f"反向：{colors[::-1]}")
```

### 知识点 3：元组的不可变性

**描述：**
元组是不可变对象，一旦创建就不能修改。这意味着不能添加、删除或修改元组中的元素。

**不可变性示例：**
```python-exec
numbers = (1, 2, 3)
print(f"原始元组：{numbers}")

# 尝试修改元素（会报错）
try:
    numbers[0] = 10
except TypeError as e:
    print(f"不能修改元素：{e}")

# 创建新元组来"修改"
new_numbers = (10,) + numbers[1:]
print(f"新元组：{new_numbers}")
```

### 知识点 4：元组的基本操作

**描述：**
虽然不能修改元组，但可以进行连接、重复等操作，还可以检查元素是否存在。

**基本操作：**
```python-exec
# 元组连接
tuple1 = (1, 2)
tuple2 = (3, 4)
combined = tuple1 + tuple2
print(f"连接后：{combined}")

# 元组重复
repeated = ("hello",) * 3
print(f"重复：{repeated}")

# 成员检查
fruits = ("苹果", "香蕉", "橙子")
print(f"'苹果'在元组中：{'苹果' in fruits}")
print(f"'葡萄'在元组中：{'葡萄' in fruits}")

# 查找元素位置
index = fruits.index("香蕉")
print(f"'香蕉'的索引：{index}")
```

### 知识点 5：元组解包

**描述：**
Python支持元组解包，可以将元组中的元素赋值给多个变量。

**元组解包：**
```python-exec
# 基本解包
point = (10, 20)
x, y = point

print(f"坐标：{point}")
print(f"x坐标：{x}")
print(f"y坐标：{y}")

# 交换变量
a, b = 1, 2
print(f"交换前：a={a}, b={b}")
a, b = b, a
print(f"交换后：a={a}, b={b}")

# 使用*号获取剩余元素
data = (1, 2, 3, 4, 5)
first, *rest = data
print(f"第一个：{first}")
print(f"其他：{rest}")
```

### 知识点 6：元组与列表的比较

**描述：**
元组和列表都是序列类型，但它们有不同的特点和适用场景。

**元组 vs 列表：**
```python-exec
# 创建元组和列表
tuple_data = (1, 2, 3)
list_data = [1, 2, 3]

print(f"元组：{tuple_data}，类型：{type(tuple_data)}")
print(f"列表：{list_data}，类型：{type(list_data)}")

# 内存占用
import sys
tuple_memory = sys.getsizeof(tuple_data)
list_memory = sys.getsizeof(list_data)
print(f"元组内存：{tuple_memory}字节")
print(f"列表内存：{list_memory}字节")

# 选择使用场景
print("使用元组：固定数据（如坐标）")
print("使用列表：需要修改的数据")
```

### 章节总结

本章我们学习了：
- 元组的创建方式和特点
- 通过索引和切片访问元素
- 元组的不可变性
- 元组的基本操作（连接、重复）
- 元组解包的使用方法
- 元组与列表的区别

### 下一步

掌握了元组后，让我们学习集合，这是Python中另一个重要的数据结构，用于存储无序且唯一的元素。

---
*本章内容基于 Python 教学平台标准格式设计。*
