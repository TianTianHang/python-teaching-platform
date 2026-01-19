---
title: "循环控制"
order: 3
---
## 循环控制

### 章节概述

循环控制语句可以改变循环的正常执行流程。Python提供了break、continue和pass等语句来控制循环。本章将详细介绍这些控制语句的用法，以及如何使用嵌套循环解决复杂问题。

### 知识点 1：break语句

**描述：**

break语句用于立即退出循环，跳过循环体中剩余的语句。当break执行时，程序会跳出整个循环结构，继续执行循环后面的代码。break可以用于for循环和while循环。

**示例代码：**
```python
# 在for循环中使用break
for i in range(10):
    if i == 5:
        break  # 当i等于5时退出循环
    print(i)

# 输出：0 1 2 3 4

# 在while循环中使用break
count = 0
while count < 10:
    if count == 5:
        break
    print(count)
    count += 1

# 输出：0 1 2 3 4

# 实际应用：查找列表中第一个满足条件的元素
numbers = [12, 45, 23, 67, 34, 89]
target = 23
found = False

for num in numbers:
    if num == target:
        found = True
        break  # 找到了，不需要继续遍历

if found:
    print(f"找到数字{target}")
else:
    print(f"未找到数字{target}")

# 输出：找到数字23

# 实际应用：用户输入验证
while True:
    password = input("请输入密码：")
    if password == "123456":
        print("密码正确！")
        break  # 退出循环
    else:
        print("密码错误，请重试。")

# 在嵌套循环中，break只退出内层循环
for i in range(3):
    for j in range(3):
        if j == 1:
            break  # 只退出内层循环
        print(f"i={i}, j={j}")

# 输出：
# i=0, j=0
# i=1, j=0
# i=2, j=0
```

**解释：**

**break的执行流程：**
1. 当程序执行到break语句时
2. 立即退出当前循环（不是多层循环）
3. 继续执行循环后面的代码

**break的典型使用场景：**
1. **查找元素**：找到目标后立即退出，节省时间
2. **用户输入验证**：直到输入正确才退出
3. **条件终止**：满足特定条件时退出循环
4. **无限循环退出**：使用`while True`时通过break退出

**break的注意事项：**
- break只退出它所在的那一层循环
- 在嵌套循环中，break不会影响外层循环
- break之后的代码不会执行
- 如果在try-except块中使用break，finally块仍然会执行

---

### 知识点 2：continue语句

**描述：**

continue语句用于跳过当前循环的剩余代码，直接进入下一次循环迭代。与break不同，continue不会退出循环，只是结束本次迭代。continue可以用于for循环和while循环。

**示例代码：**
```python
# 在for循环中使用continue
for i in range(5):
    if i == 2:
        continue  # 跳过i等于2的情况
    print(i)

# 输出：0 1 3 4（注意：2被跳过了）

# 实际应用：只处理奇数
for i in range(10):
    if i % 2 == 0:
        continue  # 跳过偶数
    print(f"奇数：{i}")

# 输出：奇数：1 奇数：3 奇数：5 奇数：7 奇数：9

# 实际应用：过滤列表中的无效数据
scores = [85, -1, 92, 76, -1, 88]  # -1表示缺考
for score in scores:
    if score == -1:
        continue  # 跳过缺考的学生
    print(f"成绩：{score}")

# 输出：
# 成绩：85
# 成绩：92
# 成绩：76
# 成绩：88

# 实际应用：密码验证
while True:
    password = input("请输入密码：")
    if len(password) < 6:
        print("密码长度至少6位，请重试。")
        continue  # 跳过后续验证

    if password == "123456":
        print("密码正确！")
        break
    else:
        print("密码错误，请重试。")

# continue vs break的区别
print("break示例：")
for i in range(5):
    if i == 2:
        break
    print(i)

# 输出：0 1

print("\ncontinue示例：")
for i in range(5):
    if i == 2:
        continue
    print(i)

# 输出：0 1 3 4
```

**解释：**

**continue的执行流程：**
1. 当程序执行到continue语句时
2. 跳过本次循环剩余的代码
3. 返回到循环开始，进行下一次迭代
4. 不会退出循环

**continue的典型使用场景：**
1. **过滤数据**：跳过不符合条件的数据
2. **条件处理**：只处理满足特定条件的情况
3. **简化逻辑**：避免使用深层嵌套的if语句

**break vs continue：**
| 特性 | break | continue |
|------|-------|----------|
| 作用 | 退出整个循环 | 跳过本次迭代 |
| 循环次数 | 减少循环次数 | 不改变循环次数 |
| 后续代码 | 不执行本次剩余代码 | 不执行本次剩余代码 |
| 循环结束 | 立即结束 | 进入下一次迭代 |

**使用continue优化代码：**
```python
# 不推荐：深层嵌套
for item in items:
    if condition1:
        if condition2:
            if condition3:
                process(item)

# 推荐：使用continue（guard clauses）
for item in items:
    if not condition1:
        continue
    if not condition2:
        continue
    if not condition3:
        continue
    process(item)
```

---

### 知识点 3：循环嵌套

**描述：**

循环嵌套是指在一个循环体内再包含另一个循环。外层循环每执行一次，内层循环会完整执行一轮。循环嵌套常用于处理多维数据结构（如二维数组、矩阵）或生成复杂的输出模式。

**示例代码：**
```python
# 基本的嵌套循环
for i in range(3):
    for j in range(3):
        print(f"({i}, {j})", end=" ")
    print()  # 换行

# 输出：
# (0, 0) (0, 1) (0, 2)
# (1, 0) (1, 1) (1, 2)
# (2, 0) (2, 1) (2, 2)

# 实际应用：打印乘法表
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}×{i}={i*j}", end="\t")
    print()

# 输出：
# 1×1=1
# 1×2=2	2×2=4
# 1×3=3	2×3=6	3×3=9
# ...

# 实际应用：遍历二维列表（矩阵）
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

for row in matrix:
    for element in row:
        print(element, end=" ")
    print()

# 输出：
# 1 2 3
# 4 5 6
# 7 8 9

# 实际应用：查找矩阵中的最大值
matrix = [
    [12, 45, 23],
    [67, 34, 89],
    [56, 78, 90]
]

max_value = matrix[0][0]
for row in matrix:
    for element in row:
        if element > max_value:
            max_value = element

print(f"最大值是：{max_value}")  # 最大值是：90

# 实际应用：打印星号图案
# 打印直角三角形
for i in range(5):
    for j in range(i + 1):
        print("*", end=" ")
    print()

# 输出：
# *
# * *
# * * *
# * * * *
# * * * * *

# 打印九九乘法表（完整版）
for i in range(1, 10):
    for j in range(1, 10):
        print(f"{j}×{i}={i*j:2}", end="\t")
    print()
```

**解释：**

**嵌套循环的执行流程：**
1. 外层循环开始（i=0）
2. 内层循环完整执行一轮（j=0, 1, 2, ...）
3. 内层循环结束后
4. 外层循环继续（i=1）
5. 重复步骤2-4，直到外层循环结束

**嵌套循环的执行次数：**
- 如果外层循环执行n次，内层循环执行m次
- 则最内层代码块共执行n×m次
- 例如：两个`range(100)`的嵌套循环会执行100×100=10,000次

**嵌套循环的最佳实践：**
1. **控制嵌套层数**：尽量避免超过3层嵌套
2. **使用函数**：将内层循环提取为函数，提高可读性
3. **考虑效率**：嵌套循环的时间复杂度是O(n×m)，要注意性能
4. **使用break退出内层**：break只退出它所在的那一层循环

**三层嵌套示例：**
```python
# 遍历三维列表
three_dim = [
    [[1, 2], [3, 4]],
    [[5, 6], [7, 8]]
]

for i in range(len(three_dim)):
    for j in range(len(three_dim[i])):
        for k in range(len(three_dim[i][j])):
            print(three_dim[i][j][k], end=" ")
        print()
    print()
```

**使用函数优化嵌套：**
```python
# 不推荐：多层嵌套
for i in items:
    for j in sub_items:
        for k in details:
            process(i, j, k)

# 推荐：提取函数
def process_item(item, sub_item, detail):
    # 处理逻辑
    pass

for i in items:
    for j in sub_items:
        for k in details:
            process_item(i, j, k)
```

---
*本章内容基于 Python 教学平台标准格式设计。*
