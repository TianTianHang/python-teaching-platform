---
title: "以下哪种方法可以在 CPython 中获取函数执行的字节码？"
type: "choice"
difficulty: 3
chapter: 1
is_multiple_choice: false
options:
  A: "sys._getframe().f_code.co_code"
  B: "inspect.getsource()"
  C: "dis.dis()"
  D: "func.__code__"
correct_answer: "A"
---

## 题目描述

以下哪种方法可以在 CPython 中获取函数执行的字节码？

### 选项

- A: sys._getframe().f_code.co_code
- B: inspect.getsource()
- C: dis.dis()
- D: func.__code__

