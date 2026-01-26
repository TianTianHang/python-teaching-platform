---
title: "列表"
order: 6
---

## 列表

### 章节概述

列表是 Python 中最基本、最常用的数据结构之一。它是一个有序的集合，可以包含任意类型的元素，并且是可变的。本章将详细介绍列表的创建、访问、操作和遍历。

### 知识点 1：什么是列表

**描述：**
列表是 Python 中的一种数据结构，用于存储多个元素。列表具有以下特点：
- 有序：元素按照添加的顺序排列
- 可变：可以修改列表中的元素
- 可以包含任意类型的元素
- 可以包含重复的元素

**创建列表：**
```python-exec
# 创建空列表
empty_list = []
print("空列表：", empty_list)

# 创建包含元素的列表
fruits = ["苹果", "香蕉", "橙子"]
print("水果列表：", fruits)

# 创建包含不同类型的列表
mixed_list = [1, "hello", 3.14, True, [1, 2, 3]]
print("混合列表：", mixed_list)
```

**访问列表元素：**
```python-exec
# 通过索引访问元素（从0开始）
fruits = ["苹果", "香蕉", "橙子", "葡萄"]

print("第一个水果：", fruits[0])     # 索引 0
print("第二个水果：", fruits[1])     # 索引 1
print("最后一个水果：", fruits[-1])  # 索引 -1（倒数第一个）
print("倒数第二个水果：", fruits[-2]) # 索引 -2（倒数第二个）
```

### 知识点 2：列表的基本操作

**描述：**
列表支持多种操作，包括添加、删除、修改和检查元素。

**修改元素：**
```python-exec
# 通过索引修改元素
fruits = ["苹果", "香蕉", "橙子"]
print("修改前：", fruits)

fruits[1] = "梨子"  # 修改第二个元素
print("修改后：", fruits)
```

**添加元素：**
```python-exec
# 使用 append() 在末尾添加
fruits = ["苹果", "香蕉"]
print("原始列表：", fruits)

fruits.append("橙子")  # 在末尾添加
print("append 后：", fruits)

# 使用 insert() 在指定位置插入
fruits.insert(1, "梨子")  # 在索引1处插入
print("insert 后：", fruits)

# 使用 extend() 扩展列表
more_fruits = ["葡萄", "西瓜"]
fruits.extend(more_fruits)
print("extend 后：", fruits)
```

**删除元素：**
```python-exec
# 列表操作演示
numbers = [1, 2, 3, 4, 5]
print("原始列表：", numbers)

# 使用 remove() 删除指定值
numbers.remove(3)  # 删除第一个值为3的元素
print("remove(3) 后：", numbers)

# 使用 pop() 删除并返回最后一个元素
last = numbers.pop()
print("pop() 结果：", last)
print("pop() 后：", numbers)

# 使用 del 删除指定索引
del numbers[0]  # 删除索引0的元素
print("del numbers[0] 后：", numbers)

# 清空列表
numbers.clear()
print("clear() 后：", numbers)
```

### 知识点 3：列表切片

**描述：**
切片是获取列表子序列的操作，非常灵活且强大。

**基本切片：**
```python-exec
# 切片操作
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 获取子列表（不包含结束索引）
print("numbers[2:5]：", numbers[2:5])  # [2, 3, 4]

# 从开头切片
print("numbers[:3]：", numbers[:3])    # [0, 1, 2]

# 到结尾切片
print("numbers[7:]：", numbers[7:])    # [7, 8, 9]

# 复制整个列表
print("numbers[:]：", numbers[:])      # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

**步长切片：**
```python-exec
# 步长切片
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 使用步长
print("numbers[::2]：", numbers[::2])  # 每隔一个取一个 [0, 2, 4, 6, 8]
print("numbers[1:8:2]：", numbers[1:8:2])  # 从1开始，到8结束，步长2 [1, 3, 5, 7]

# 反向切片
print("numbers[::-1]：", numbers[::-1])  # 反转列表 [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

**负索引切片：**
```python-exec
# 负索引切片
numbers = [0, 1, 2, 3, 4, 5]

print("numbers[-3:]：", numbers[-3:])   # 最后3个元素 [3, 4, 5]
print("numbers[:-2]：", numbers[:-2])   # 除了最后2个的所有元素 [0, 1, 2, 3]
```

### 知识点 4：列表的遍历

**描述：**
遍历列表是常见的操作，有几种不同的方式可以遍历列表中的所有元素。

**使用 for 循环遍历：**
```python-exec
# 基本遍历
fruits = ["苹果", "香蕉", "橙子", "葡萄"]

for fruit in fruits:
    print(f"水果：{fruit}")
```

**使用索引遍历：**
```python-exec
# 使用索引遍历
fruits = ["苹果", "香蕉", "橙子", "葡萄"]

for i in range(len(fruits)):
    print(f"索引 {i}：{fruits[i]}")
```

**使用 enumerate 同时获取索引和值：**
```python-exec
# 使用 enumerate
fruits = ["苹果", "香蕉", "橙子", "葡萄"]

for index, fruit in enumerate(fruits):
    print(f"索引 {index}：{fruit}")
```

**遍历列表的同时修改列表：**
```python-exec
# 注意：不要在遍历列表的同时修改它
# 下面是错误的做法，会导致问题
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
# bad_fruits = []
# for fruit in fruits:
#     if fruit != "香蕉":
#         bad_fruits.append(fruit)

# 正确的做法：创建新列表
good_fruits = [fruit for fruit in fruits if fruit != "香蕉"]
print("筛选后的水果：", good_fruits)
```

### 知识点 5：列表的方法

**描述：**
列表有很多内置方法，用于执行各种操作。

**常用列表方法：**
```python-exec
# 列表方法演示
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

print("原始列表：", numbers)

# 排序
numbers_copy1 = numbers.copy()
numbers_copy1.sort()
print("排序后：", numbers_copy1)

# 反转
numbers_copy2 = numbers.copy()
numbers_copy2.reverse()
print("反转后：", numbers_copy2)

# 查找元素位置
print("5 的索引：", numbers.index(5))  # 4
print("1 的索引：", numbers.index(1))  # 1（第一个1的位置）

# 计数
print("1 的出现次数：", numbers.count(1))  # 2

# 其他方法
numbers_copy3 = numbers.copy()
numbers_copy3.pop(2)  # 删除索引2的元素
print("pop(2) 后：", numbers_copy3)
```

**字符串方法（列表特有）：**
```python-exec
# 只在列表中存在的方法
empty_list = []
empty_list.append(1)  # 添加
print("append(1)：", empty_list)
empty_list.insert(0, 2)  # 插入
print("insert(0, 2)：", empty_list)

# 其他方法
print("列表长度：", len(empty_list))
print("最小值：", min(empty_list))
print("最大值：", max(empty_list))
print("总和：", sum(empty_list))
```

### 知识点 6：列表的嵌套

**描述：**
列表可以嵌套，即列表的元素可以是另一个列表，这可以用来表示二维或多维数据。

**创建嵌套列表：**
```python-exec
# 二维列表（矩阵）
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print("矩阵：", matrix)

# 访问元素
print("第一行：", matrix[0])
print("第一行第二列：", matrix[0][1])
```

**遍历嵌套列表：**
```python-exec
# 遍历二维列表
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# 嵌套循环遍历
for row in matrix:
    for element in row:
        print(element, end=" ")
    print()

# 使用列表推导式
flat_list = [element for row in matrix for element in row]
print("展平后的列表：", flat_list)
```

### 知识点 7：列表推导式

**描述：**
列表推导式是 Python 中创建列表的简洁方式，它允许你在一行代码中生成列表。

**基本语法：**
```python
[表达式 for 变量 in 可迭代对象 if 条件]
```

**简单列表推导式：**
```python-exec
# 创建平方列表
squares = [x ** 2 for x in range(1, 6)]
print("平方列表：", squares)

# 带条件的列表推导式
even_numbers = [x for x in range(1, 11) if x % 2 == 0]
print("偶数列表：", even_numbers)

# 字符串操作
words = ["hello", "world", "python", "list"]
uppercase_words = [word.upper() for word in words if len(word) > 5]
print("大写单词（长度>5）：", uppercase_words)
```

**复杂的列表推导式：**
```python-exec
# 多重循环
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [item for row in matrix for item in row]
print("展平的列表：", flattened)

# 数学运算
numbers = [1, 2, 3, 4, 5]
processed = [x * 2 + 1 for x in numbers if x % 2 == 1]
print("处理后的列表：", processed)
```

### 知识点 8：列表与字符串的转换

**描述：**
列表和字符串可以相互转换，这在处理文本数据时非常有用。

**字符串转列表：**
```python-exec
# 字符串拆分为列表
text = "hello world"
char_list = list(text)  # 每个字符作为一个元素
print("字符列表：", char_list)

# 按分隔符拆分
word_list = text.split()  # 默认按空格拆分
print("单词列表：", word_list)

# 按指定分隔符拆分
csv_data = "apple,banana,orange"
fruit_list = csv_data.split(",")
print("水果列表：", fruit_list)
```

**列表转字符串：**
```python-exec
# 列表转字符串
fruits = ["苹果", "香蕉", "橙子"]

# 直接转换（会包含引号）
print("直接转换：", str(fruits))

# join 方法（推荐）
result = "，".join(fruits)
print("join 结果：", result)

# 使用 join 处理数字列表
numbers = [1, 2, 3, 4, 5]
numbers_str = "-".join(str(num) for num in numbers)
print("数字连接：", numbers_str)
```

### 知识点 9：列表的常见用法

**描述：**
列表在实际编程中有多种常见用法，掌握这些用法能提高编程效率。

**用法 1：堆栈操作（后进先出）**
```python-exec
# 使用列表实现堆栈
stack = []
print("初始栈：", stack)

# 入栈
stack.append("第一个")
stack.append("第二个")
stack.append("第三个")
print("入栈后：", stack)

# 出栈
item = stack.pop()
print("出栈：", item)
print("出栈后：", stack)
```

**用法 2：队列操作（先进先出）**
```python-exec
# 使用列表实现队列（但更推荐使用 collections.deque）
queue = []
print("初始队列：", queue)

# 入队
queue.append("客户1")
queue.append("客户2")
queue.append("客户3")
print("入队后：", queue)

# 出队（效率较低）
item = queue.pop(0)  # 从头部弹出
print("出队：", item)
print("出队后：", queue)
```

**用法 3：去重**
```python-exec
# 去重的方法
numbers = [1, 2, 2, 3, 4, 4, 4, 5]

# 使用 set（会改变顺序）
unique1 = list(set(numbers))
print("去重后（set）：", unique1)

# 保持顺序的去重
unique2 = []
for num in numbers:
    if num not in unique2:
        unique2.append(num)
print("去重后（保持顺序）：", unique2)
```

### 章节总结

本章我们学习了：
- 列表的创建和基本概念
- 列表的基本操作（添加、删除、修改）
- 列表切片的使用方法
- 列表的多种遍历方式
- 列表的内置方法
- 列表的嵌套和多层列表
- 列表推导式的强大功能
- 列表与字符串的相互转换
- 列表的常见应用场景

### 下一步

掌握了列表后，让我们在下一章学习字典，这是另一种重要的数据结构，它使用键值对来存储数据。

---
*本章内容基于 Python 教学平台标准格式设计。*
