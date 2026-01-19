---
title: "break和continue"
type: "choice"
difficulty: 1
chapter: 3
is_multiple_choice: false
options:
  A: "1 3"
  B: "1 2 3"
  C: "1 2 4"
  D: "1 2 3 4"
correct_answer: "A"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
for i in range(1, 5):
    if i == 2:
        continue
    elif i == 4:
        break
    print(i, end=" ")
```

### 题目内容

A. 1 3
B. 1 2 3
C. 1 2 4
D. 1 2 3 4

### 解析

**正确答案：A**

**详细解析：**

这道题考查break和continue语句的使用。

**代码执行分析：**

for循环遍历1到4（range(1, 5)生成1, 2, 3, 4）：

- i=1：
  - i==2？False
  - i==4？False
  - print(1) → 输出"1 "

- i=2：
  - i==2？True
  - 执行continue，跳过本次循环剩余代码
  - 不会执行print(i)
  - 进入下一次循环

- i=3：
  - i==2？False
  - i==4？False
  - print(3) → 输出"3 "

- i=4：
  - i==2？False
  - i==4？True
  - 执行break，退出整个循环
  - 不会执行print(i)
  - 循环结束

**最终输出**："1 3 "

**break vs continue对比：**

| 特性 | break | continue |
|------|-------|----------|
| 作用 | 退出整个循环 | 跳过本次迭代 |
| 执行位置 | 跳出循环 | 继续下一次循环 |
| 影响范围 | 整个循环 | 只影响当前迭代 |
| 本题中 | i=4时退出循环 | i=2时跳过 |

**选项分析：**
- **选项 A（正确）**：i=2被continue跳过，i=4被break退出
- **选项 B**：包含了i=2，但i=2应该被跳过
- **选项 C**：包含了i=4，但i=4时已经break退出
- **选项 D**：包含了所有数字，忽略了break和continue

**验证示例：**
```python
# 只输出1, 3
for i in range(1, 5):
    if i == 2:
        continue
    elif i == 4:
        break
    print(i, end=" ")
# 输出：1 3
```

### 相关知识点
- break语句：退出整个循环
- continue语句：跳过本次迭代
- 循环控制语句的使用场景
- 循环的执行流程

---
*本题基于 Python 教学平台标准格式设计。*
