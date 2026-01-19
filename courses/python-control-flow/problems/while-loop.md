---
title: "while循环"
type: "choice"
difficulty: 1
chapter: 2
is_multiple_choice: false
options:
  A: "[2, 4, 6, 8]"
  B: "[4, 6, 8, 10]"
  C: "[2, 4, 6, 8, 10]"
  D: "[1, 2, 3, 4, 5]"
correct_answer: "C"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
result = []
i = 2
while i <= 10:
    result.append(i)
    i += 2
print(result)
```

### 题目内容

A. [2, 4, 6, 8]
B. [4, 6, 8, 10]
C. [2, 4, 6, 8, 10]
D. [1, 2, 3, 4, 5]

### 解析

**正确答案：C**

**详细解析：**

这道题考查while循环的执行流程。

**代码执行分析：**

1. `result = []`：创建空列表
2. `i = 2`：初始化变量i为2
3. while循环条件：`i <= 10`
   - 第一次循环：i=2 <= 10 → True
     - `result.append(2)` → result = [2]
     - `i += 2` → i = 4
   - 第二次循环：i=4 <= 10 → True
     - `result.append(4)` → result = [2, 4]
     - `i += 2` → i = 6
   - 第三次循环：i=6 <= 10 → True
     - `result.append(6)` → result = [2, 4, 6]
     - `i += 2` → i = 8
   - 第四次循环：i=8 <= 10 → True
     - `result.append(8)` → result = [2, 4, 6, 8]
     - `i += 2` → i = 10
   - 第五次循环：i=10 <= 10 → True
     - `result.append(10)` → result = [2, 4, 6, 8, 10]
     - `i += 2` → i = 12
   - 第六次循环：i=12 <= 10 → False，退出循环
4. `print(result)`：输出[2, 4, 6, 8, 10]

**while循环的关键点：**
1. **循环条件**：`i <= 10`，当i=10时仍然满足条件
2. **循环变量更新**：`i += 2`，每次循环增加2
3. **包含边界**：10是包含在结果中的
4. **退出条件**：当i=12时，`i <= 10`为False，退出循环

**选项分析：**
- **选项 A**：缺少10，因为while条件是`i <= 10`，10应该被包含
- **选项 B**：从4开始，缺少2
- **选项 C（正确）**：正确，包含了2, 4, 6, 8, 10
- **选项 D**：这是range(1, 6)的结果，不是偶数

**常见错误：**
```python
# 错误1：条件写错
while i < 10:  # 10不会被包含
    # 会得到[2, 4, 6, 8]

# 错误2：忘记更新循环变量
i = 2
while i <= 10:
    result.append(i)
    # i += 2 忘写了，会进入无限循环！

# 错误3：初始值写错
i = 1  # 从1开始
# 会得到[1, 3, 5, 7, 9]
```

**使用range()实现相同功能：**
```python
# 使用for循环和range()更简洁
result = []
for i in range(2, 11, 2):  # range(2, 11, 2)生成2, 4, 6, 8, 10
    result.append(i)

# 或者使用列表推导式
result = [i for i in range(2, 11, 2)]
```

### 相关知识点
- while循环的基本用法
- 循环条件的判断
- 循环变量的更新
- 避免无限循环

---
*本题基于 Python 教学平台标准格式设计。*
