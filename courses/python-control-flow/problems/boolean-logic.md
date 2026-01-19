---
title: "布尔逻辑"
type: "choice"
difficulty: 1
chapter: 1
is_multiple_choice: false
options:
  A: "False"
  B: "True"
  C: "None"
  D: "程序报错"
correct_answer: "A"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
a = True
b = False
c = True
result = (a and b) or (c and not b)
print(result)
```

### 题目内容

A. False
B. True
C. None
D. 程序报错

### 解析

**正确答案：A**

**详细解析：**

这道题考查布尔逻辑运算和运算符优先级。

**代码执行分析：**

1. 定义布尔变量：
   - `a = True`
   - `b = False`
   - `c = True`

2. 计算`result = (a and b) or (c and not b)`：
   - 先计算括号内的表达式
   - 第一个括号：`a and b` = `True and False` = `False`
   - 第二个括号：`c and not b` = `True and not(False)` = `True and True` = `True`
   - 最后：`False or True` = `True`

3. 输出`result`，即`True`

**布尔运算详解：**

**and（与）运算：**
- `True and True` = `True`
- `True and False` = `False`
- `False and True` = `False`
- `False and False` = `False`
- 规律：只有都为`True`时结果才为`True`

**or（或）运算：**
- `True or True` = `True`
- `True or False` = `True`
- `False or True` = `True`
- `False or False` = `False`
- 规律：只要有一个为`True`，结果就为`True`

**not（非）运算：**
- `not True` = `False`
- `not False` = `True`
- 规律：取反

**运算符优先级：**
1. `not` > `and` > `or`
2. 括号可以改变优先级

**按优先级重新计算：**
```python
result = (a and b) or (c and not b)
      = (True and False) or (True and not(False))
      = False or (True and True)
      = False or True
      = True
```

**选项分析：**
- **选项 A**：应该是True，不是False
- **选项 B（正确）**：计算结果确实是True
- **选项 C**：None表示空值，不是布尔运算结果
- **选项 D**：代码语法正确，不会报错

**常见错误：**
```python
# 错误1：忽略优先级
result = a and b or c and not b  # 与使用括号的效果相同
# 但这样写可读性差，建议使用括号

# 错误2：混淆运算顺序
result = a and b or c and not b
# 正确：先计算and，再计算or
# 不是：从左到右
```

**验证示例：**
```python
a, b, c = True, False, True
print((a and b) or (c and not b))  # 输出：True
```

### 相关知识点
- 布尔逻辑运算：and、or、not
- 运算符优先级
- 括号的使用
- 短路求值

---
*本题基于 Python 教学平台标准格式设计。*
