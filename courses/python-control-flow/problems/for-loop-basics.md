---
title: "for循环基础"
type: "choice"
difficulty: 1
chapter: 2
is_multiple_choice: false
options:
  A: "[1, 4, 9]"
  B: "[1, 2, 3, 4]"
  C: "[0, 1, 2, 3]"
  D: "[1, 2, 3]"
correct_answer: "A"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
result = []
for i in range(1, 4):
    result.append(i * i)
print(result)
```

### 题目内容

A. [1, 4, 9]
B. [1, 2, 3, 4]
C. [0, 1, 2, 3]
D. [1, 2, 3]

### 解析

**正确答案：A**

**详细解析：**

这道题考查for循环和range()函数的使用。

**代码执行分析：**

1. `result = []`：创建一个空列表
2. `for i in range(1, 4)`：
   - range(1, 4)生成1, 2, 3（不包含4）
   - i依次取值为1, 2, 3
3. 每次循环：
   - i=1：`result.append(1 * 1)` = `result.append(1)` → result = [1]
   - i=2：`result.append(2 * 2)` = `result.append(4)` → result = [1, 4]
   - i=3：`result.append(3 * 3)` = `result.append(9)` → result = [1, 4, 9]
4. `print(result)`：输出[1, 4, 9]

**range()函数详解：**
- `range(start, stop)`：生成从start到stop-1的整数序列
- range(1, 4)生成：1, 2, 3
- 不包含stop参数（这里是4）

**选项分析：**
- **选项 A（正确）**：正确，计算平方后得到1, 4, 9
- **选项 B**：这是range(1, 5)的结果，但没有平方运算
- **选项 C**：这是range(4)的结果，但没有平方运算
- **选项 D**：这是range(1, 4)的结果，但没有平方运算

**常见错误：**
```python
# 错误1：range参数范围搞错
for i in range(4):  # 生成0, 1, 2, 3
    # 会得到[0, 1, 4, 9]，而不是[1, 4, 9]

# 错误2：忘记平方
result = []
for i in range(1, 4):
    result.append(i)  # 会得到[1, 2, 3]

# 错误3：range参数写错
for i in range(1, 5):  # 生成1, 2, 3, 4
    # 会得到[1, 4, 9, 16]
```

**相似示例：**
```python
# 计算前10个偶数的平方
squares = []
for i in range(1, 11):
    squares.append(i * 2)

# 计算斐波那契数列
fib = [0, 1]
for i in range(2, 10):
    fib.append(fib[i-1] + fib[i-2])
```

### 相关知识点
- for循环基础
- range()函数的使用
- list.append()方法
- 列表操作

---
*本题基于 Python 教学平台标准格式设计。*
