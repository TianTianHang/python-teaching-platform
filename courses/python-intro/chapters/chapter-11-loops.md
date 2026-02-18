---
title: "控制流 - 循环"
order: 11
unlock_conditions:
  type: "prerequisite"
  prerequisites: [11]
---

## 控制流 - 循环

### 章节概述

循环是编程中的重要概念，它允许程序重复执行特定的代码块。本章将学习 Python 中的两种主要循环：while 循环和 for 循环，以及如何控制循环的执行。

### 知识点 1：while 循环

**描述：**
while 循环在条件为真时重复执行代码块，直到条件变为假为止。

**基本语法：**
```python
while 条件:
    # 条件为真时重复执行的代码
    # 注意：必须有改变条件的方式，否则会无限循环
```

**示例代码：**
```python-exec
# 基本的 while 循环
count = 1

while count <= 5:
    print("计数：", count)
    count += 1  # 增加计数器，否则会无限循环

print("循环结束")
```

**注意事项：**
- 必须有改变条件的机制，避免无限循环
- 循环条件最终会变为 False
- 缩进非常重要，表示循环体

**避免无限循环：**
```python-exec
# 安全的计数器示例
count = 1

while count <= 3:
    print("当前计数：", count)
    count += 1

print("循环完成，count =", count)
```

### 知识点 2：for 循环

**描述：**
for 循环用于遍历可迭代对象（如列表、字符串、范围等）的每个元素。

**基本语法：**
```python
for 变量 in 可迭代对象:
    # 对每个元素执行的代码
```

**遍历列表：**
```python-exec
# 遍历列表
fruits = ["苹果", "香蕉", "橙子"]

for fruit in fruits:
    print("我喜欢吃：", fruit)
```

**使用 range() 函数：**
```python-exec
# range() 函数生成数字序列
for i in range(5):  # 0, 1, 2, 3, 4
    print("i =", i)

# range(start, end)
for i in range(2, 6):  # 2, 3, 4, 5
    print("i =", i)

# range(start, end, step)
for i in range(1, 10, 2):  # 1, 3, 5, 7, 9
    print("i =", i)
```

**遍历字符串：**
```python-exec
# 遍历字符串
message = "Hello"

for char in message:
    print("字符：", char)
```

### 知识点 3：循环控制语句

**描述：**
循环控制语句可以改变循环的执行流程，包括 break、continue 和 pass。

**break 语句：** 退出循环
```python-exec
# 使用 break 退出循环
fruits = ["苹果", "香蕉", "橙子", "葡萄", "西瓜"]

for fruit in fruits:
    print("水果：", fruit)
    if fruit == "橙子":
        print("找到了橙子，退出循环")
        break  # 立即退出循环
```

**continue 语句：** 跳过当前迭代
```python-exec
# 使用 continue 跳过当前迭代
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

for num in numbers:
    if num % 2 == 0:  # 如果是偶数
        continue  # 跳过这次循环
    print("奇数：", num)
```

**pass 语句：** 占位符
```python-exec
# pass 用作占位符
for i in range(3):
    if i == 1:
        pass  # 什么都不做
    else:
        print("i =", i)
```

### 知识点 4：嵌套循环

**描述：**
循环可以嵌套，即在循环内部包含另一个循环。

**示例代码：**
```python-exec
# 嵌套循环示例
# 打印乘法表
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} × {j} = {i*j}", end="  ")
    print()  # 换行

print("\n")

# 打印星号图案
rows = 3
for i in range(rows):
    for j in range(i + 1):
        print("*", end=" ")
    print()
```

**使用嵌套循环处理二维数据：**
```python-exec
# 二维列表（矩阵）
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

for row in matrix:
    for element in row:
        print(element, end=" ")
    print()
```

### 知识点 5：循环中的 else 子句

**描述：**
Python 的循环可以带有 else 子句，else 块在循环正常结束时（没有被 break 中断）执行。

**示例代码：**
```python-exec
# 循环正常结束，执行 else
numbers = [1, 2, 3, 4, 5]

for num in numbers:
    print(num, end=" ")
else:
    print("\n循环正常结束")

print("\n")

# 循环被 break 中断，不执行 else
for num in numbers:
    print(num, end=" ")
    if num == 3:
        print("\n检测到3，退出循环")
        break
else:
    print("\n这部分不会执行")
```

### 知识点 6：while 和 for 的选择

**描述：**
while 和 for 循环各有适用场景，了解它们的区别有助于选择合适的循环方式。

**while 循环适用场景：**
- 不确定循环次数
- 条件复杂
- 需要更多的控制

```python-exec
# while 循环示例：输入验证
while True:
    age = input("请输入你的年龄（1-120）：")
    if age.isdigit():
        age = int(age)
        if 1 <= age <= 120:
            print(f"有效年龄：{age}")
            break
        else:
            print("年龄超出范围，请重新输入")
    else:
        print("请输入有效的数字")
```

**for 循环适用场景：**
- 遍历序列
- 确定循环次数
- 更简洁

```python-exec
# for 循环示例：处理列表
scores = [85, 92, 78, 90, 88]

# 计算平均分
total = 0
for score in scores:
    total += score
average = total / len(scores)
print(f"平均分：{average:.2f}")

# 查找最高分
max_score = scores[0]
for score in scores:
    if score > max_score:
        max_score = score
print(f"最高分：{max_score}")
```

### 知识点 7：循环的优化技巧

**描述：**
编写高效循环的技巧，避免常见的性能问题。

**技巧 1：避免在循环中修改可迭代对象**
```python-exec
# 错误示例：在循环中修改列表
numbers = [1, 2, 3, 4, 5]

for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)  # 这会导致问题

print("修改后的列表：", numbers)

# 正确做法：创建新列表或使用列表推导式
numbers = [1, 2, 3, 4, 5]
even_numbers = [num for num in numbers if num % 2 == 0]
print("偶数列表：", even_numbers)
```

**技巧 2：减少不必要的计算**
```python-exec
# 不好的做法：在循环中重复计算
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = 0

for i in range(len(numbers)):
    total += numbers[i] * 2  # 每次都乘以2

print("总和：", total)

# 更好的做法：避免重复计算
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
multiplied = [num * 2 for num in numbers]
total = sum(multiplied)
print("总和：", total)
```

**技巧 3：使用 enumerate 获取索引和值**
```python-exec
# 使用 enumerate 同时获取索引和值
fruits = ["苹果", "香蕉", "橙子"]

for index, fruit in enumerate(fruits):
    print(f"索引 {index}: {fruit}")
```

### 知识点 8：循环的常见模式

**描述：**
循环在实际编程中有一些常见模式，掌握这些模式能快速解决类似问题。

**模式 1：累加器模式**
```python-exec
# 累加器模式
numbers = [1, 2, 3, 4, 5]
sum_total = 0

for num in numbers:
    sum_total += num

print(f"总和：{sum_total}")
```

**模式 2：计数器模式**
```python-exec
# 计数器模式
words = ["apple", "banana", "apple", "orange", "apple"]
count = 0

for word in words:
    if word == "apple":
        count += 1

print(f"apple 出现次数：{count}")
```

**模式 3：查找模式**
```python-exec
# 查找模式
numbers = [10, 20, 30, 40, 50]
target = 30
found = False

for num in numbers:
    if num == target:
        found = True
        break

print(f"找到 {target}：{found}")
```

**模式 4：过滤模式**
```python-exec
# 过滤模式
numbers = [1, 2, 3, 4, 5, 6]
even_numbers = []

for num in numbers:
    if num % 2 == 0:
        even_numbers.append(num)

print(f"偶数：{even_numbers}")
```

### 章节总结

本章我们学习了：
- while 循环的基本用法和注意事项
- for 循环的遍历操作
- 循环控制语句：break、continue、pass
- 嵌套循环的使用
- 循环的 else 子句
- while 和 for 的选择场景
- 循环的优化技巧
- 循环的常见模式

### 下一步

掌握了循环语句后，让我们在下一章学习列表，这是 Python 中最常用的数据结构之一。

---
*本章内容基于 Python 教学平台标准格式设计。*
