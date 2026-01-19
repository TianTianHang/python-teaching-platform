---
title: "列表索引"
type: "choice"
difficulty: 2
chapter: 1
is_multiple_choice: false
options:
  A: "[1, 2, 3, 4]"
  B: "[2, 3, 4]"
  C: "[3, 4]"
  D: "[4]"
correct_answer: "A"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
numbers = [1, 2, 3, 4]
result = []
for i in range(len(numbers)):
    result.append(numbers[i])
print(result)
```

### 题目内容

A. [1, 2, 3, 4]
B. [2, 3, 4]
C. [3, 4]
D. [4]

### 解析

**正确答案：A**

**详细解析：**

这道题考查列表索引和for循环的使用。

**代码执行分析：**

1. `numbers = [1, 2, 3, 4]`：创建一个列表
2. `for i in range(len(numbers))`：
   - `len(numbers)`返回4
   - `range(4)`生成0, 1, 2, 3
3. 循环过程：
   - i=0：`numbers[0]`是1，`result.append(1)` → result = [1]
   - i=1：`numbers[1]`是2，`result.append(2)` → result = [1, 2]
   - i=2：`numbers[2]`是3，`result.append(3)` → result = [1, 2, 3]
   - i=3：`numbers[3]`是4，`result.append(4)` → result = [1, 2, 3, 4]
4. 输出：[1, 2, 3, 4]

**列表索引规则：**
- 列表的索引从0开始
- `numbers[0]`是第一个元素
- `numbers[1]`是第二个元素
- 依此类推

**range(len(numbers))的使用：**
- `len(numbers)`获取列表长度
- `range(n)`生成0到n-1的整数
- 这是遍历列表索引的常用方法

**选项分析：**
- **选项 A（正确）**：正确获取了列表的所有元素
- **选项 B**：这是`numbers[1:]`的结果
- **选项 C**：这是`numbers[2:]`的结果
- **选项 D**：这是`numbers[3:]`的结果

**更Pythonic的写法：**
```python
# 遍历列表元素（推荐）
result = []
for number in numbers:
    result.append(number)

# 或者使用列表推导式
result = [number for number in numbers]

# 或者直接复制列表
result = numbers.copy()
```

**索引的特殊情况：**
```python
# 负数索引（从后往前）
numbers[-1]  # 最后一个元素
numbers[-2]  # 倒数第二个元素

# 索引越界会报错
numbers[4]  # IndexError: list index out of range
```

### 相关知识点
- 列表索引（从0开始）
- range()函数的使用
- len()函数
- for循环遍历列表

---
*本题基于 Python 教学平台标准格式设计。*
