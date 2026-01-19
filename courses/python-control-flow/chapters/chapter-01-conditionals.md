---
title: "条件语句"
order: 1
---
## 条件语句

### 章节概述

条件语句是编程中最基础也是最重要的流程控制结构。它允许程序根据不同的条件执行不同的代码块，是实现程序逻辑判断的基础。本章将详细介绍Python中的if条件语句及其各种形式。

### 知识点 1：if语句的基本用法

**描述：**

if语句用于判断某个条件是否成立，如果条件成立（即条件表达式的值为`True`），则执行if后面的代码块。在Python中，代码块通过**缩进**来标识，通常使用4个空格的缩进。

**示例代码：**
```python
# 基本的if语句
age = 18

if age >= 18:
    print("你已经成年了")
    print("可以考取驾照")

print("程序结束")  # 这行代码不在if块中，总是执行

# 输出：
# 你已经成年了
# 可以考取驾照
# 程序结束
```

**解释：**

- `if`关键字后面跟着一个条件表达式（如`age >= 18`）
- 条件表达式后面必须有一个**冒号**（:）
- 冒号后面的代码块必须**缩进**（通常4个空格）
- 只有当条件为`True`时，缩进的代码块才会被执行
- 不缩进的代码（如`print("程序结束")`）不受if语句影响

**缩进规则：**
- Python使用缩进来组织代码块，这是Python的特色
- 同一级别的代码必须有相同的缩进
- 缩进可以使用空格或Tab，但推荐使用4个空格
- 不要混用空格和Tab

---

### 知识点 2：if-else与if-elif-else结构

**描述：**

if语句可以与else和elif组合，提供更复杂的条件判断逻辑：
- `else`：当if条件不成立时执行的代码块
- `elif`（else if的缩写）：当if条件不成立，但elif条件成立时执行的代码块

**示例代码：**
```python
# if-else结构
score = 75

if score >= 60:
    print("恭喜你，及格了！")
else:
    print("很遗憾，你需要补考。")

# if-elif-else结构
grade = 85

if grade >= 90:
    letter = 'A'
    print("优秀！")
elif grade >= 80:
    letter = 'B'
    print("良好！")
elif grade >= 70:
    letter = 'C'
    print("中等！")
elif grade >= 60:
    letter = 'D'
    print("及格！")
else:
    letter = 'F'
    print("不及格！")

print(f"你的等级是：{letter}")

# 实际应用：判断闰年
year = 2024

if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
    print(f"{year}是闰年")
else:
    print(f"{year}不是闰年")

# 输出：2024是闰年
```

**解释：**

**if-else结构：**
- `else`关键字后面也必须有冒号
- `else`后面不需要条件表达式
- `else`块是可选的

**if-elif-else结构：**
- 可以有多个`elif`块
- 条件按顺序检查，一旦某个条件为`True`，执行对应代码块后结束
- `else`块是可选的，表示"以上所有条件都不满足"时的情况
- `elif`是Python的特有语法，比其他语言的`else if`更简洁

**执行流程：**
1. 检查if条件，如果为`True`，执行if块，然后结束
2. 如果if条件为`False`，检查第一个elif条件
3. 如果某个elif条件为`True`，执行该elif块，然后结束
4. 如果所有条件都为`False`，执行else块（如果有）

---

### 知识点 3：嵌套条件语句

**描述：**

条件语句可以嵌套使用，即在一个if语句的代码块中再包含另一个if语句。嵌套可以有多层，但为了代码可读性，建议不要超过3层。

**示例代码：**
```python
# 嵌套if语句示例
age = 25
has_ticket = True
has_id_card = True

if age >= 18:
    print("你已成年")
    if has_ticket:
        print("你有票")
        if has_id_card:
            print("验证通过，可以入场")
        else:
            print("请出示身份证")
    else:
        print("请先购票")
else:
    print("未成年禁止入内")

# 输出：
# 你已成年
# 你有票
# 验证通过，可以入场

# 实际应用：成绩评级系统
score = 85
attendance_rate = 0.95

if score >= 60:
    if attendance_rate >= 0.9:
        if score >= 90:
            result = "优秀学员"
        else:
            result = "合格学员"
    else:
        result = "成绩合格但出勤不足"
else:
    result = "不合格"

print(f"评价：{result}")  # 评价：合格学员

# 使用逻辑运算符简化嵌套
# 上面的嵌套可以改写为：
if score >= 60 and attendance_rate >= 0.9:
    if score >= 90:
        result = "优秀学员"
    else:
        result = "合格学员"
elif score >= 60:
    result = "成绩合格但出勤不足"
else:
    result = "不合格"
```

**解释：**

**嵌套if语句：**
- 内层if语句是外层if语句代码块的一部分
- 内层if语句需要额外的缩进
- 外层条件必须满足，才会检查内层条件

**嵌套的注意事项：**
1. **缩进层级**：每嵌套一层增加一级缩进（4个空格）
2. **可读性**：过深的嵌套（超过3层）会降低代码可读性
3. **使用逻辑运算符**：有时可以用`and`、`or`运算符简化嵌套
4. **提前返回**：在函数中，可以使用`return`提前退出，减少嵌套

**优化嵌套的建议：**
```python
# 不推荐：过深的嵌套
if condition1:
    if condition2:
        if condition3:
            do_something()

# 推荐：提前返回（guard clauses）
if not condition1:
    return
if not condition2:
    return
if not condition3:
    return
do_something()

# 或使用逻辑运算符
if condition1 and condition2 and condition3:
    do_something()
```

---
*本章内容基于 Python 教学平台标准格式设计。*
