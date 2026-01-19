---
title: "变量的命名规则"
type: "choice"
difficulty: 1
chapter: 2
is_multiple_choice: false
options:
  A: "user_name"
  B: "2nd_place"
  C: "class"
  D: "my-variable"
correct_answer: "A"
---
## 题目描述

以下变量名中，哪一个是符合Python命名规则的？

### 题目内容

A. user_name
B. 2nd_place
C. class
D. my-variable

### 解析

**正确答案：A**

**详细解析：**

这道题考查Python变量的命名规则。让我们逐一分析每个选项：

- **选项 A（正确）**：`user_name`是一个合法的变量名
  - 以字母开头
  - 只包含字母和下划线
  - 使用了snake_case命名风格（单词间用下划线连接），这是Python推荐的命名风格
  - 不是Python的关键字

- **选项 B（错误）**：`2nd_place`不是合法的变量名
  - **不能以数字开头**
  - 如果改为`place_2`或`second_place`就是合法的

- **选项 C（错误）**：`class`不是合法的变量名
  - `class`是Python的**关键字**（保留字）
  - 关键字有特殊含义，不能作为变量名使用
  - Python的关键字包括：`if`、`else`、`for`、`while`、`def`、`class`、`return`等

- **选项 D（错误）**：`my-variable`不是合法的变量名
  - **不能包含连字符（-）**
  - 连字符会被解释为减号运算符
  - 应该使用下划线：`my_variable`

**Python变量命名规则总结：**
1. 必须以字母（a-z，A-Z）或下划线（_）开头
2. 不能以数字开头
3. 只能包含字母、数字和下划线
4. 不能使用Python的关键字
5. 区分大小写（`name`和`Name`是不同的变量）

**推荐的命名风格：**
- 变量和函数：`snake_case`（如`user_name`、`calculate_sum`）
- 类名：`PascalCase`（如`UserController`、`DataBase`）
- 常量：`UPPER_SNAKE_CASE`（如`MAX_SIZE`、`PI`）

### 相关知识点
- Python变量命名规则
- Python关键字（keywords）
- snake_case命名规范
- PEP 8代码风格指南

---
*本题基于 Python 教学平台标准格式设计。*
