---
title: "循环结构"
order: 2
---
## 循环结构

### 章节概述

循环是编程中最重要的概念之一，它允许我们重复执行某段代码多次。Python提供了两种主要的循环结构：for循环和while循环。掌握循环结构将让你能够高效地处理重复性任务和批量数据。

### 知识点 1：for循环基础

**描述：**

for循环用于遍历序列（如列表、字符串、元组）或其他可迭代对象。for循环会从序列中逐个取出元素，对每个元素执行一次循环体。

**示例代码：**
```python
# 遍历字符串
for char in "Python":
    print(char)

# 输出：
# P
# y
# t
# h
# o
# n

# 遍历列表
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(f"我喜欢吃{fruit}")

# 输出：
# 我喜欢吃苹果
# 我喜欢吃香蕉
# 我喜欢吃橙子

# 遍历数字范围（使用range）
for i in range(5):
    print(i)

# 输出：0 1 2 3 4

# 实际应用：计算1到100的和
total = 0
for i in range(1, 101):  # range(1, 101)生成1到100
    total += i

print(f"1到100的和是：{total}")  # 1到100的和是：5050

# 遍历字典
person = {"name": "小明", "age": 18, "city": "北京"}
for key in person:
    print(f"{key}: {person[key]}")

# 输出：
# name: 小明
# age: 18
# city: 北京
```

**解释：**

**for循环的基本语法：**
```python
for 变量 in 序列:
    循环体代码
```

- `for`关键字后面跟着一个变量名
- `in`关键字后面跟着一个序列或可迭代对象
- 冒号后面是缩进的循环体
- 每次循环，变量会取序列中的下一个值

**常见的可迭代对象：**
- 字符串：逐个字符遍历
- 列表：逐个元素遍历
- 元组：逐个元素遍历
- 字典：遍历键（默认）
- range对象：生成数字序列

**循环变量名：**
- 使用有意义的变量名（如`fruit`、`student`）
- 如果不需要使用循环变量，可以用`_`作为变量名

---

### 知识点 2：while循环

**描述：**

while循环在条件为`True`时会重复执行循环体。与for循环不同，while循环不遍历序列，而是根据条件决定是否继续循环。while循环适用于不确定循环次数的场景。

**示例代码：**
```python
# 基本的while循环
count = 0
while count < 5:
    print(f"count = {count}")
    count += 1  # 重要：更新循环变量，避免无限循环

# 输出：
# count = 0
# count = 1
# count = 2
# count = 3
# count = 4

# 实际应用：猜数字游戏
import random

secret_number = random.randint(1, 100)
guess = 0
attempts = 0

while guess != secret_number:
    guess = int(input("猜一个1到100之间的数字："))
    attempts += 1

    if guess < secret_number:
        print("太小了！")
    elif guess > secret_number:
        print("太大了！")

print(f"恭喜你猜对了！用了{attempts}次。")

# 使用while循环处理用户输入
while True:
    user_input = input("请输入命令（quit退出）：")
    if user_input == "quit":
        print("程序退出")
        break
    print(f"你输入了：{user_input}")

# 计算阶乘
n = 5
factorial = 1
while n > 0:
    factorial *= n
    n -= 1

print(f"5的阶乘是：{factorial}")  # 5的阶乘是：120
```

**解释：**

**while循环的基本语法：**
```python
while 条件:
    循环体代码
```

- `while`关键字后面跟着一个条件表达式
- 当条件为`True`时，执行循环体
- 每次循环结束后，重新检查条件
- 当条件变为`False`时，退出循环

**while循环的注意事项：**
1. **确保循环能够结束**：必须在循环体中更新条件相关的变量
2. **避免无限循环**：如果条件永远为`True`，程序会陷入死循环
3. **循环初始化**：循环前要正确初始化变量

**for vs while：**
- **for循环**：适合遍历已知序列或确定次数的循环
- **while循环**：适合不确定循环次数或根据条件判断的场景

**使用`while True`：**
```python
# while True常用于需要手动退出的场景
while True:
    # 执行某些操作
    if some_condition:
        break  # 使用break退出循环
```

---

### 知识点 3：range()函数详解

**描述：**

`range()`函数是Python的内置函数，用于生成一个数字序列。它经常与for循环配合使用，用于执行指定次数的循环。

**示例代码：**
```python
# range(stop) - 生成0到stop-1的整数
for i in range(5):
    print(i)

# 输出：0 1 2 3 4

# range(start, stop) - 生成start到stop-1的整数
for i in range(2, 6):
    print(i)

# 输出：2 3 4 5

# range(start, stop, step) - 生成带步长的序列
for i in range(0, 10, 2):
    print(i)

# 输出：0 2 4 6 8

# 反向遍历
for i in range(5, 0, -1):
    print(i)

# 输出：5 4 3 2 1

# 实际应用：遍历列表的索引
fruits = ["苹果", "香蕉", "橙子"]
for i in range(len(fruits)):
    print(f"索引{i}：{fruits[i]}")

# 输出：
# 索引0：苹果
# 索引1：香蕉
# 索引2：橙子

# 使用enumerate更Pythonic
for index, fruit in enumerate(fruits):
    print(f"索引{index}：{fruit}")

# 计算乘法表
for i in range(1, 10):
    for j in range(1, 10):
        print(f"{i}×{j}={i*j}", end="\t")
    print()  # 换行
```

**解释：**

**range()函数的三种形式：**

1. **`range(stop)`**
   - 生成从0到stop-1的整数
   - stop是必须参数
   - 示例：`range(5)`生成[0, 1, 2, 3, 4]

2. **`range(start, stop)`**
   - 生成从start到stop-1的整数
   - 包含start，不包含stop
   - 示例：`range(2, 6)`生成[2, 3, 4, 5]

3. **`range(start, stop, step)`**
   - 生成从start到stop-1的整数，步长为step
   - step可以是正数或负数
   - 示例：`range(0, 10, 2)`生成[0, 2, 4, 6, 8]
   - 示例：`range(10, 0, -2)`生成[10, 8, 6, 4, 2]

**重要特性：**
- range()返回的是一个range对象，不是列表
- range()是惰性的，只在需要时生成数字，节省内存
- 可以使用`list(range(n))`将range对象转换为列表

**常见用法：**
```python
# 执行n次循环
for i in range(n):
    do_something()

# 遍历索引
for i in range(len(sequence)):
    process(sequence[i])

# 倒序遍历
for i in range(len(sequence)-1, -1, -1):
    process(sequence[i])
```

---
*本章内容基于 Python 教学平台标准格式设计。*
