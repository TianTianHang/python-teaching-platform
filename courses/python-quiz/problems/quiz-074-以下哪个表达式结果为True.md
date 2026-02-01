---
title: "以下哪个表达式结果为True"
type: "choice"
difficulty: 3
chapter: 1
is_multiple_choice: false
options:
  A: "[] is []
[] is []  # False
# 每次创建新列表对象，内存地址不同"
  B: "{} == {}
{} == {}  # True
# == 比较内容，两个空字典内容相等"
  C: "() is ()
() is ()  # 可能是True（由于小对象驻留）
# 空元组可能被重用，但不保证"
  D: "set() is set()
set() is set()  # False
# 每次创建新集合对象
"
correct_answer: "B"
---

## 题目描述

以下哪个表达式结果为True

### 选项

- A: [] is []
[] is []  # False
# 每次创建新列表对象，内存地址不同
- B: {} == {}
{} == {}  # True
# == 比较内容，两个空字典内容相等
- C: () is ()
() is ()  # 可能是True（由于小对象驻留）
# 空元组可能被重用，但不保证
- D: set() is set()
set() is set()  # False
# 每次创建新集合对象


