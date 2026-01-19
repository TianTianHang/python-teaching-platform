---
title: "基本计算器"
type: "algorithm"
difficulty: 1
chapter: 3
time_limit: 1000
memory_limit: 256
solution_name:
  python: "calculate"
code_template:
  python: |
    def calculate(a, b, operation):
        """
        基本计算器

        Args:
            a: 第一个数（整数或浮点数）
            b: 第二个数（整数或浮点数）
            operation: 运算符，字符串类型，可以是 '+', '-', '*', '/'

        Returns:
            计算结果，如果是除法且b为0，返回字符串 "Error: Division by zero"
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "[10, 5, \"+\"]"
    output: "15"
    is_sample: true
  - input: "[10, 3, \"*\"]"
    output: "30"
    is_sample: false
  - input: "[10, 2, \"/\"]"
    output: "5.0"
    is_sample: false
  - input: "[10, 0, \"/\"]"
    output: "\"Error: Division by zero\""
    is_sample: false
  - input: "[10, 4, \"-\"]"
    output: "6"
    is_sample: false
---
## 题目描述

编写一个函数，实现基本的四则运算计算器。

### 输入格式

函数接收三个参数：
- `a`：第一个数（整数或浮点数）
- `b`：第二个数（整数或浮点数）
- `operation`：运算符（字符串类型），可以是以下值之一：
  - `'+'`：加法
  - `'-'`：减法
  - `'*'`：乘法
  - `'/'`：除法

### 输出格式

返回计算结果：
- 对于`'+'`、`'-'`、`'*'`运算，返回相应的计算结果
- 对于`'/'`运算：
  - 如果`b`不为0，返回除法结果（浮点数）
  - 如果`b`为0，返回字符串`"Error: Division by zero"`

### 示例

**示例1：加法**
```python
calculate(10, 5, '+')
# 返回：15
```

**示例2：乘法**
```python
calculate(10, 3, '*')
# 返回：30
```

**示例3：除法（正常情况）**
```python
calculate(10, 2, '/')
# 返回：5.0
```

**示例4：除法（除数为零）**
```python
calculate(10, 0, '/')
# 返回："Error: Division by zero"
```

**示例5：减法**
```python
calculate(10, 4, '-')
# 返回：6
```

### 提示

1. 使用`if-elif-else`结构来判断运算符类型
2. 除法运算需要检查除数是否为0
3. Python的除法运算符`/`总是返回浮点数

**示例代码框架：**
```python
def calculate(a, b, operation):
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Invalid operation"
```

### 注意事项
- 除法运算需要处理除数为0的情况
- 确保正确处理所有四种运算符
- 返回值的类型要正确（数字或错误字符串）

---
*本题目基于 Python 教学平台标准格式设计。*
