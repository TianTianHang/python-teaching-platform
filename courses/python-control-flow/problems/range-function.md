---
title: "range()函数"
type: "choice"
difficulty: 1
chapter: 2
is_multiple_choice: false
options:
  A: "[1, 2, 3]"
  B: "[0, 1, 2, 3]"
  C: "[1, 2, 3, 4]"
  D: "[0, 1, 2]"
correct_answer: "A"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
result = []
for i in range(1, 4):
    result.append(i)
print(result)
```

### 题目内容

A. [1, 2, 3]
B. [0, 1, 2, 3]
C. [1, 2, 3, 4]
D. [0, 1, 2]

### 解析

**正确答案：A**

**详细解析：**

这道题考查range()函数的基本用法。

**代码执行分析：**

1. `result = []`：创建空列表
2. `for i in range(1, 4)`：
   - range(1, 4)生成从1到4-1=3的整数序列
   - 即：1, 2, 3
3. 循环过程：
   - i=1：`result.append(1)` → result = [1]
   - i=2：`result.append(2)` → result = [1, 2]
   - i=3：`result.append(3)` → result = [1, 2, 3]
4. 输出：[1, 2, 3]

**range()函数的核心规则：**
- `range(start, stop)`生成从start到stop-1的整数
- 包含start，不包含stop
- 步长默认为1

**range()函数的三种形式：**

1. **`range(stop)`**：
   - 生成0到stop-1的整数
   - 例：`range(4)` → 0, 1, 2, 3

2. **`range(start, stop)`**：
   - 生成start到stop-1的整数
   - 例：`range(1, 4)` → 1, 2, 3
   - 本题使用的就是这种形式

3. **`range(start, stop, step)`**：
   - 生成start到stop-1的整数，步长为step
   - 例：`range(0, 10, 2)` → 0, 2, 4, 6, 8

**选项分析：**
- **选项 A（正确）**：正确，range(1, 4)生成1, 2, 3
- **选项 B**：这是range(4)的结果，从0开始
- **选项 C**：这是range(1, 5)的结果，stop是5而不是4
- **选项 D**：这是range(3)的结果，从0开始

**常见错误：**
```python
# 错误1：混淆start和stop
for i in range(4, 1):  # range(4, 1)是空的，因为4 > 1
    print(i)  # 不会输出任何内容

# 正确的倒序遍历：
for i in range(4, 0, -1):  # 4, 3, 2, 1

# 错误2：step为负数时的理解
for i in range(1, 4, -1):  # 空的，因为step是负数，但start < stop
    # 不会输出任何内容
```

**range()的使用示例：**
```python
# 生成0到9
for i in range(10):
    print(i)

# 生成5到15
for i in range(5, 16):
    print(i)

# 生成偶数
for i in range(0, 11, 2):
    print(i)  # 0, 2, 4, 6, 8, 10

# 生成奇数
for i in range(1, 11, 2):
    print(i)  # 1, 3, 5, 7, 9
```

### 相关知识点
- range()函数的三种形式
- range()的边界规则：包含start，不包含stop
- range()与for循环的结合使用
- 如何控制循环的起始和结束

---
*本题基于 Python 教学平台标准格式设计。*
