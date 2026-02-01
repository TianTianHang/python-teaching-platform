---
title: "以下哪个操作会创建新对象"
type: "choice"
difficulty: 3
chapter: 1
is_multiple_choice: false
options:
  A: "a = b = []
   # 创建一个列表，a和b指向同一个对象
   a = b = []
   a.append(1)
   print(b)  # [1]（b也受影响）"
  B: "a = []; b = a
   # 创建一个列表，b指向a指向的同一个对象
   a = []
   b = a
   a.append(2)
   print(b)  # [2]（b也受影响）
   "
  C: "a = []; b = a.copy()
   # 创建新列表，内容是原列表的副本
   a = [1, 2, 3]
   b = a.copy()  # 或 b = a[:]"
  D: "a = []; b = a.copy(); a = []; b = a[:]
   # 第一部分：a = []; b = a.copy() - 创建新对象
   # 第二部分：a = []; b = a[:] - a重新赋值，但b不会跟着变
   a = []
   b = a.copy()
   a = []
   b = a[:]  # b现在指向新的空列表"
correct_answer: "C"
---

## 题目描述

以下哪个操作会创建新对象

### 选项

- A: a = b = []
   # 创建一个列表，a和b指向同一个对象
   a = b = []
   a.append(1)
   print(b)  # [1]（b也受影响）
- B: a = []; b = a
   # 创建一个列表，b指向a指向的同一个对象
   a = []
   b = a
   a.append(2)
   print(b)  # [2]（b也受影响）
   
- C: a = []; b = a.copy()
   # 创建新列表，内容是原列表的副本
   a = [1, 2, 3]
   b = a.copy()  # 或 b = a[:]
- D: a = []; b = a.copy(); a = []; b = a[:]
   # 第一部分：a = []; b = a.copy() - 创建新对象
   # 第二部分：a = []; b = a[:] - a重新赋值，但b不会跟着变
   a = []
   b = a.copy()
   a = []
   b = a[:]  # b现在指向新的空列表

