---
title: "函数定义"
type: "choice"
difficulty: 1
chapter: 1
is_multiple_choice: false
options:
  A: "def my_function():"
  B: "function my_function():"
  C: "create my_function():"
  D: "define my_function():"
correct_answer: "A"
---
## 题目描述

在Python中，下列哪个是定义函数的正确语法？

### 题目内容

在Python中，下列哪个是定义函数的正确语法？

A. `def my_function():`

B. `function my_function():`

C. `create my_function():`

D. `define my_function():`

### 正确答案

A

### 详细解析

**正确答案：A**

**解析：**

Python使用 `def` 关键字来定义函数，这是"define"的缩写。

**完整语法：**
```python
def function_name(parameters):
    """函数文档字符串"""
    # 函数体
    return value
```

**各选项分析：**

- ✅ **A. `def my_function():`** - 正确
  - `def` 是Python定义函数的关键字
  - 函数名后面必须跟括号（即使没有参数）
  - 函数定义行必须以冒号结尾

- ❌ **B. `function my_function():`** - 错误
  - `function` 不是Python的关键字
  - 这可能是JavaScript或PHP的语法

- ❌ **C. `create my_function():`** - 错误
  - `create` 不是Python的关键字
  - Python中不存在这种语法

- ❌ **D. `define my_function():`** - 错误
  - `define` 不是Python的关键字
  - 应该使用 `def` 而非 `define`

**函数定义示例：**
```python
# 无参数函数
def greet():
    print("Hello, World!")

# 有参数函数
def greet_person(name):
    print(f"Hello, {name}!")

# 有返回值函数
def add(a, b):
    return a + b

# 调用函数
greet()              # Hello, World!
greet_person("张三")  # Hello, 张三!
result = add(3, 5)   # result = 8
```

**重要规则：**
1. 函数名必须以字母或下划线开头
2. 函数名可以包含字母、数字和下划线
3. 函数名区分大小写
4. 函数名应该具有描述性
5. 函数定义行必须以冒号 `:` 结尾
6. 函数体必须缩进（通常是4个空格）

**函数命名规范：**
```python
# 好的函数名（使用小写和下划线）
def calculate_average():
    pass

def get_user_data():
    pass

# 不推荐的函数名（使用驼峰命名）
def CalculateAverage():  # 不推荐
    pass

# 错误的函数名
def 123function():  # 错误：以数字开头
    pass

def my-function():  # 错误：使用连字符
    pass
```

### 相关知识点

- **函数定义**：使用 `def` 关键字定义函数
- **函数调用**：使用函数名加括号调用函数
- **函数参数**：在括号中定义参数
- **函数返回值**：使用 `return` 语句返回值

### 进阶思考

为什么Python选择使用 `def` 而不是 `function`？

1. **简洁性**：`def` 更简短，符合Python简洁的设计理念
2. **历史原因**：Python的语法受到ABC语言的影响，ABC使用 `def`
3. **可读性**：`def` 很快就能识别出这是函数定义
4. **一致性**：Python中其他关键字也很简洁（如 `if`, `for`, `while`）

```python
# Python风格（简洁）
def my_function():
    pass

# 如果使用function（不简洁）
function my_function():
    pass
```

---
*本题目基于 Python 教学平台标准格式设计。*
