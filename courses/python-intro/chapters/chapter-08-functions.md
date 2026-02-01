---
title: "函数基础"
order: 8
unlock_conditions:
  type: "prerequisite"
  prerequisites: [7]
---

## 函数基础

### 章节概述

函数是编程中的核心概念，它允许我们将代码组织成可重用的模块。本章将学习 Python 中的函数定义、调用、参数、返回值等基础知识。

### 知识点 1：什么是函数

**描述：**
函数是组织好的、可重复使用的、用来实现单一或相关联功能的代码块。函数的主要优点包括：
- 代码复用：避免重复编写相同的代码
- 模块化：将复杂问题分解为小问题
- 可维护性：修改函数只需改一处
- 可读性：代码更清晰易懂

**函数的基本结构：**
```python
def function_name(parameters):
    """
    函数文档字符串（可选）
    """
    # 函数体
    return result  # 可选
```

**定义和调用函数：**
```python-exec
# 定义函数
def greet():
    print("你好，世界！")
    print("欢迎学习 Python 函数！")

# 调用函数
greet()
print("函数调用结束")
```

### 知识点 2：函数参数

**描述：**
函数可以接收输入参数，使函数更加灵活和通用。

**带参数的函数：**
```python-exec
# 带参数的函数
def greet_person(name):
    print(f"你好，{name}！")
    print(f"很高兴认识你，{name}！")

# 调用带参数的函数
greet_person("张三")
greet_person("李四")
```

**多个参数：**
```python-exec
# 多个参数的函数
def student_info(name, age, major):
    print(f"学生信息：")
    print(f"姓名：{name}")
    print(f"年龄：{age}")
    print(f"专业：{major}")

# 调用多个参数的函数
student_info("王五", 20, "计算机科学")
```

**参数的类型提示（可选）：**
```python-exec
# 带类型提示的函数（Python 3.5+）
def add_numbers(a: int, b: int) -> int:
    return a + b

result = add_numbers(5, 3)
print(f"5 + 3 = {result}")
```

### 知识点 3：返回值

**描述：**
函数可以通过 return 语句返回结果，使函数不仅可以执行操作，还可以计算并返回值。

**基本返回值：**
```python-exec
# 返回单个值
def square(x):
    return x ** 2

result = square(5)
print(f"5 的平方是：{result}")

# 使用返回值
print(f"10 的平方是：{square(10)}")
```

**返回多个值：**
```python-exec
# 返回多个值
def get_student_info():
    name = "张三"
    age = 20
    score = 85.5
    return name, age, score

# 接收多个返回值
name, age, score = get_student_info()
print(f"姓名：{name}，年龄：{age}，成绩：{score}")
```

**返回字典：**
```python-exec
# 返回字典
def create_student_dict(name, age, score):
    return {
        "name": name,
        "age": age,
        "score": score,
        "grade": "A" if score >= 90 else "B"
    }

student = create_student_dict("李四", 21, 92.5)
print("学生字典：", student)
```

### 知识点 4：函数的文档字符串

**描述：**
文档字符串（docstring）是函数的说明文字，可以帮助其他开发者理解函数的用途。

**文档字符串的格式：**
```python-exec
# 带文档字符串的函数
def calculate_area(length, width):
    """
    计算矩形的面积

    参数：
        length: 矩形的长度
        width: 矩形的宽度

    返回：
        矩形的面积
    """
    area = length * width
    return area

# 使用 help() 查看文档字符串
help(calculate_area)

# 调用函数
result = calculate_area(5, 3)
print(f"面积：{result}")
```

**文档字符串风格：**
```python-exec
# Google 风格的文档字符串
def greet(name, greeting="你好"):
    """
    打印问候语

    Args:
        name (str): 要问候的人名
        greeting (str, optional): 问候语，默认为"你好"

    Returns:
        None: 无返回值，直接打印
    """
    print(f"{greeting}，{name}！")

greet("张三")
greet("李四", "早上好")
```

### 知识点 5：参数的类型

**描述：**
Python 函数支持多种参数类型，包括位置参数、默认参数、关键字参数等。

**位置参数：**
```python-exec
# 位置参数
def add(a, b):
    return a + b

print("3 + 5 =", add(3, 5))  # 按位置传递
print("5 + 3 =", add(5, 3))  # 参数位置不同
```

**默认参数：**
```python-exec
# 默认参数
def greet(name, greeting="你好"):
    return f"{greeting}，{name}！"

print(greet("张三"))          # 使用默认问候语
print(greet("李四", "早上好")) # 自定义问候语
```

**关键字参数：**
```python-exec
# 关键字参数
def student_info(name, age, major="计算机科学"):
    return {
        "name": name,
        "age": age,
        "major": major
    }

# 使用关键字参数
print(student_info("王五", 20))
print(student_info("赵六", 21, "数学"))
print(student_info(age=22, name="钱七", major="物理"))
```

### 知识点 6：函数的作用域

**描述：**
函数有自己的作用域，变量在函数内部定义后，其作用域仅限于函数内部。

**局部变量：**
```python-exec
# 局部变量
def test_function():
    x = 10  # 局部变量
    print(f"函数内部：x = {x}")

test_function()
# print(x)  # 这会报错，x 在函数外部不可见
```

**全局变量：**
```python-exec
# 全局变量
global_var = 100

def test_function():
    print(f"函数内部访问全局变量：{global_var}")

test_function()
print(f"函数外部访问全局变量：{global_var}")
```

**修改全局变量：**
```python-exec
# 修改全局变量
counter = 0

def increment():
    global counter  # 声明使用全局变量
    counter += 1
    print(f"函数内部：counter = {counter}")

increment()
print(f"函数外部：counter = {counter}")
```

### 知识点 7：递归函数

**描述：**
递归函数是调用自身的函数，用于解决可以被分解为相似子问题的问题。

**递归示例：阶乘**
```python-exec
# 递归计算阶乘
def factorial(n):
    """
    计算阶乘
    n! = n × (n-1) × ... × 1
    """
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# 调用递归函数
print("5! =", factorial(5))
print("0! =", factorial(0))
```

**递归示例：斐波那契数列**
```python-exec
# 递归计算斐波那契数列
def fibonacci(n):
    """
    计算斐波那契数列的第n项
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)
    """
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

# 打印斐波那契数列
print("斐波那契数列前10项：")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### 知识点 8：高阶函数

**描述：**
高阶函数是接收函数作为参数或返回函数的函数。

**函数作为参数：**
```python-exec
# 函数作为参数
def apply_operation(numbers, operation):
    """
    对列表中的每个数字执行操作
    """
    return [operation(num) for num in numbers]

# 定义一些操作函数
def square(x):
    return x ** 2

def double(x):
    return x * 2

# 使用高阶函数
numbers = [1, 2, 3, 4, 5]
print("平方：", apply_operation(numbers, square))
print("加倍：", apply_operation(numbers, double))
```

**匿名函数（lambda）：**
```python-exec
# 使用 lambda 函数
numbers = [1, 2, 3, 4, 5]

# lambda 函数：匿名函数
squares = list(map(lambda x: x ** 2, numbers))
print("平方：", squares)

evens = list(filter(lambda x: x % 2 == 0, numbers))
print("偶数：", evens)
```

**返回函数：**
```python-exec
# 返回函数
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

# 创建不同的乘法函数
times2 = make_multiplier(2)
times3 = make_multiplier(3)

print("2 × 5 =", times2(5))
print("3 × 4 =", times3(4))
```

### 知识点 9：函数的最佳实践

**描述：**
编写函数时遵循一些最佳实践，能让代码更清晰、更易维护。

**最佳实践 1：函数命名**
```python-exec
# 好的函数命名
def calculate_average(numbers):
    """计算数字列表的平均值"""
    return sum(numbers) / len(numbers)

# 不好的函数命名
def calc_avg(nums):
    """计算数字列表的平均值"""
    return sum(nums) / len(nums)

# 使用示例
numbers = [10, 20, 30, 40, 50]
print(f"平均值：{calculate_average(numbers)}")
```

**最佳实践 2：参数验证**
```python-exec
# 参数验证
def validate_and_divide(a, b):
    """
    除法运算，带参数验证

    参数：
        a: 被除数
        b: 除数（不能为0）

    返回：
        a/b 的结果
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("参数必须是数字")

    if b == 0:
        raise ValueError("除数不能为0")

    return a / b

# 使用示例
try:
    print("10 / 2 =", validate_and_divide(10, 2))
    print("10 / 0 =", validate_and_divide(10, 0))  # 会抛出异常
except ValueError as e:
    print(f"错误：{e}")
```

**最佳实践 3：单一职责**
```python-exec
# 单一职责原则
def read_data(filename):
    """读取文件数据"""
    with open(filename, 'r') as f:
        return f.readlines()

def process_data(data):
    """处理数据"""
    return [line.strip() for line in data if line.strip()]

def write_data(data, filename):
    """写入数据到文件"""
    with open(filename, 'w') as f:
        f.write('\n'.join(data))

# 分别处理不同的任务
data = read_data("input.txt")
processed = process_data(data)
write_data(processed, "output.txt")
```

### 知识点 10：装饰器基础

**描述：**
装饰器是 Python 的一个重要特性，它允许你在不修改函数代码的情况下，扩展函数的功能。

**简单的装饰器：**
```python-exec
# 计时装饰器
import time

def timer(func):
    """计时装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间：{end_time - start_time:.4f}秒")
        return result
    return wrapper

# 使用装饰器
@timer
def slow_function():
    """一个慢函数"""
    time.sleep(1)
    print("慢函数执行完成")

slow_function()
```

**带参数的装饰器：**
```python-exec
# 重复执行装饰器
def repeat(times):
    """重复执行装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

# 使用带参数的装饰器
@repeat(3)
def hello():
    print("Hello!")

hello()
```

### 章节总结

本章我们学习了：
- 函数的定义和基本结构
- 函数参数的类型和使用
- 返回值的概念和应用
- 函数的文档字符串
- 参数的类型（位置、默认、关键字）
- 函数的作用域和变量
- 递归函数的使用
- 高阶函数的概念
- 函数的最佳实践
- 装饰器的基础知识

### 下一步

恭喜！你已经完成了 Python 入门课程的学习。掌握了这些基础知识后，你可以开始学习更高级的 Python 特性，如类和对象、模块和包、文件操作等。记得多练习，巩固所学的知识！

---
*本章内容基于 Python 教学平台标准格式设计。*
