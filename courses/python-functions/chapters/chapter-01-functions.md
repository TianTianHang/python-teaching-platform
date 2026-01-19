---
title: "函数基础"
order: 1
---
## 函数基础

### 章节概述

函数是Python编程中最重要、最常用的概念之一。函数是一个封装好的、可重用的代码块，它接收输入（参数），执行特定的任务，并返回结果。通过本章学习，你将掌握函数的基本定义、调用方式和参数处理。

### 知识点 1：函数的定义与调用

**描述：**

函数是组织代码的基本单位。通过定义函数，我们可以将相关的代码封装在一起，并给它一个名字。当需要执行这些代码时，只需要调用函数名即可。函数的定义和调用是Python编程的基础。

**示例代码：**
```python
# 定义一个简单的函数
def greet():
    """打印问候语"""
    print("你好，Python！")

# 调用函数
greet()  # 输出：你好，Python！

# 定义一个带参数的函数
def greet_person(name):
    """向指定的人问候"""
    print(f"你好，{name}！")

# 调用带参数的函数
greet_person("小明")  # 输出：你好，小明！
greet_person("张三")  # 输出：你好，张三！

# 定义一个带返回值的函数
def add(a, b):
    """计算两个数的和"""
    return a + b

# 调用带返回值的函数
result = add(5, 3)
print(f"5 + 3 = {result}")  # 输出：5 + 3 = 8

# 函数返回多个值
def get_student_info(student_id):
    """获取学生信息"""
    # 模拟数据库查询
    students = {
        1001: {"name": "张三", "age": 18, "grade": "高三"},
        1002: {"name": "李四", "age": 17, "grade": "高二"}
    }
    return students.get(student_id, None)

# 使用元组解包接收多个返回值
info = get_student_info(1001)
if info:
    print(f"姓名：{info['name']}, 年龄：{info['age']}, 年级：{info['grade']}")
else:
    print("未找到该学生信息")

# 实际应用：计算圆的面积和周长
def circle_info(radius):
    """计算圆的面积和周长"""
    import math
    area = math.pi * radius ** 2
    circumference = 2 * math.pi * radius
    return area, circumference

# 调用并解包结果
area, circumference = circle_info(5)
print(f"半径为5的圆：面积={area:.2f}, 周长={circumference:.2f}")
```

**解释：**

**函数定义语法：**
```python
def 函数名(参数列表):
    """文档字符串"""
    函数体
    return 返回值（可选）
```

**关键字说明：**
- `def`：定义函数的关键字
- `函数名`：函数的名称，遵循变量命名规则
- `参数列表`：用逗号分隔的参数列表，可以为空
- `return`：返回结果关键字，可以省略（此时返回None）

**函数调用：**
- 函数名后加括号`()`，括号内传入实际参数
- 没有参数时也要写`()`
- 调用函数才会执行函数体内的代码

**函数的三种类型：**

1. **无参数、无返回值**：
   ```python
   def say_hello():
       print("Hello!")
   ```

2. **有参数、无返回值**：
   ```python
   def say_hello(name):
       print(f"Hello, {name}!")
   ```

3. **有参数、有返回值**：
   ```python
   def add(a, b):
       return a + b
   ```

**函数文档字符串（docstring）：**
- 函数定义后的第一个字符串，用于说明函数的功能
- 使用`help(函数名)`可以查看文档字符串
- 也可以使用`函数名.__doc__`访问

**函数的执行流程：**
1. 程序遇到`def`时，定义函数但不执行函数体
2. 调用函数时，才开始执行函数体
3. 执行到`return`或函数末尾时结束
4. 返回值被调用者接收

**实际应用示例：**
```python
# 简单的计算器
def calculator(num1, num2, operator):
    """简单的计算器"""
    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    elif operator == "/":
        if num2 != 0:
            return num1 / num2
        else:
            return "错误：除数不能为0"
    else:
        return "错误：不支持的运算符"

# 测试计算器
print(calculator(10, 5, "+"))  # 15
print(calculator(10, 5, "/"))  # 2.0
print(calculator(10, 0, "/"))  # 错误：除数不能为0
```

---

### 知识点 2：参数传递

**描述：**

参数是函数与外部进行数据交互的接口。Python支持多种参数传递方式，包括位置参数、关键字参数、默认参数等。理解参数传递机制是编写灵活函数的关键。

**示例代码：**
```python
# 位置参数（必须按顺序传入）
def power(base, exponent):
    """计算base的exponent次方"""
    return base ** exponent

# 按位置调用
result = power(2, 3)  # 2的3次方 = 8
print(f"2的3次方 = {result}")

# 按位置调用，顺序很重要
result = power(3, 2)  # 3的2次方 = 9
print(f"3的2次方 = {result}")

# 关键字参数（按参数名传入，顺序不重要）
def describe_person(name, age, city):
    """描述一个人的信息"""
    return f"{name}今年{age}岁，住在{city}。"

# 按关键字调用
result = describe_person(
    name="小明",
    age=18,
    city="北京"
)
print(result)

# 关键字参数可以打乱顺序
result = describe_person(
    city="上海",
    age=20,
    name="小红"
)
print(result)

# 位置参数和关键字参数混合使用
def student_info(name, age, grade="高中"):
    """学生信息"""
    return f"{name}，{age}岁，{grade}年级"

# 第一个参数用位置，后面用关键字
info = student_info("小华", 19, grade="高二")
print(info)

# 默认参数（定义时给默认值）
def greet_with_default(name="朋友"):
    """带默认问候语的问候函数"""
    return f"你好，{name}！"

# 使用默认值
print(greet_with_default())  # 你好，朋友！
print(greet_with_default("小明"))  # 你好，小明！

# 默认参数的陷阱（可变对象）
def add_item(items=[], new_item=None):
    """向列表添加新项（有陷阱的实现）"""
    if new_item is not None:
        items.append(new_item)
    return items

# 调用函数
print(add_item())  # []
print(add_item([1, 2, 3], 4))  # [1, 2, 3, 4]

# 问题：多次调用不传参数
print(add_item())  # [] 看起来没问题
print(add_item())  [] 还是没问题
print(add_item())  [] 看起来没问题
print(add_item())  [] 看起来没问题

# 实际上有问题（请看下面的正确实现）
print("修正后的实现：")

def add_item_fixed(items=None, new_item=None):
    """修正后的实现"""
    if items is None:
        items = []
    if new_item is not None:
        items.append(new_item)
    return items

print(add_item_fixed())  # []
print(add_item_fixed())  # []
print(add_item_fixed())  # []

# 不定数量的参数（*args和**kwargs）
def calculate_average(*numbers):
    """计算任意数量数字的平均值"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# 可以传入任意数量的位置参数
print(calculate_average(1, 2, 3))  # 2.0
print(calculate_average(10, 20, 30, 40))  # 25.0
print(calculate_average())  # 0

def print_student_info(**info):
    """打印学生信息的关键字参数"""
    for key, value in info.items():
        print(f"{key}: {value}")

print_student_info(name="小明", age=18, grade="高三", city="北京")
# 输出：
# name: 小明
# age: 18
# grade: 高三
# city: 北京

# 混合使用所有参数类型
def complex_function(a, b, *args, **kwargs):
    """使用所有参数类型的函数示例"""
    print(f"位置参数：a={a}, b={b}")
    print(f"可变位置参数：{args}")
    print(f"可变关键字参数：{kwargs}")

complex_function(1, 2, 3, 4, 5, name="小明", age=18)
# 输出：
# 位置参数：a=1, b=2
# 可变位置参数：(3, 4, 5)
# 可变关键字参数：{'name': '小明', 'age': 18}

# 实际应用：通用数据处理函数
def process_data(data, operation="sum", **options):
    """
    处理数据的通用函数

    Args:
        data: 数据列表
        operation: 操作类型，默认为"sum"
        **options: 其他选项
    """
    if not data:
        return 0

    if operation == "sum":
        return sum(data)
    elif operation == "average":
        return sum(data) / len(data)
    elif operation == "max":
        return max(data)
    elif operation == "min":
        return min(data)
    elif operation == "multiply":
        result = 1
        for num in data:
            result *= num
        return result
    else:
        return f"不支持的operation：{operation}"

# 使用默认参数
print(process_data([1, 2, 3, 4]))  # 10（sum）

# 指定操作类型
print(process_data([1, 2, 3, 4], operation="average"))  # 2.5

# 使用其他选项
print(process_data([1, 2, 3, 4], operation="max", precision=2))  # 4
```

**解释：**

**参数类型：**

1. **位置参数（Positional Arguments）**：
   - 按定义顺序传入
   - 必须传入，不能省略
   - 示例：`power(2, 3)`

2. **关键字参数（Keyword Arguments）**：
   - 按参数名传入
   - 可以打乱顺序
   - 示例：`describe_person(name="小明", age=18)`

3. **默认参数（Default Parameters）**：
   - 定义时给默认值
   - 调用时可以不传入
   - 示例：`def greet(name="朋友")`

4. **可变位置参数（*args）**：
   - 收集多余的位置参数到元组
   - 示例：`def func(*args):`

5. **可变关键字参数（**kwargs）**：
   - 收集多余的关键字参数到字典
   - 示例：`def func(**kwargs):`

**参数传递规则：**
1. **顺序规则**：位置参数 → 默认参数 → 可变位置参数 → 可变关键字参数
2. **混合使用**：可以混合使用，但必须按顺序
3. **默认参数陷阱**：
   - 默认参数在函数定义时创建，不是在每次调用时
   - 可变对象（如列表、字典）作为默认参数会有问题
   - 推荐使用`None`作为默认值，然后在函数内创建对象

**参数类型签名：**
```python
# 正确的参数类型定义顺序
def func(pos1, pos2, default1="default", *args, kw1, kw2="kw_default", **kwargs):
    pass
```

**实际应用技巧：**
```python
# 使用*args和**kwargs编写更灵活的函数
def flexible_function(prefix="Result: ", **kwargs):
    """灵活处理任意关键字参数"""
    result = {}
    for key, value in kwargs.items():
        result[key] = value * 2  # 假设每个值都是数字
    return {prefix: result}

# 使用示例
print(flexible_function(num1=10, num2=20, num3=30))
# 输出：{'Result: ': {'num1': 20, 'num2': 40, 'num3': 60}}
```

---

### 知识点 3：返回值

**描述：**

返回值是函数执行后返回给调用者的结果。Python函数可以返回一个值、多个值或没有返回值（返回None）。掌握返回值的使用可以让函数更加灵活和强大。

**示例代码：**
```python
# 没有return语句的函数（返回None）
def print_message(message):
    """只打印消息，不返回任何值"""
    print(message)

result = print_message("你好，Python！")
print(f"函数返回值：{result}")  # 函数返回值：None

# 返回单个值
def square(number):
    """返回一个值的平方"""
    return number * number

result = square(5)
print(f"5的平方：{result}")  # 5的平方：25

# 返回多个值（实际上返回一个元组）
def get_student_info_tuple(student_id):
    """返回多个值（元组）"""
    students = {
        1001: ("张三", 18, "高三"),
        1002: ("李四", 17, "高二")
    }
    return students.get(student_id, ("未知", 0, "未知"))

# 接收返回的元组
name, age, grade = get_student_info_tuple(1001)
print(f"姓名：{name}, 年龄：{age}, 年级：{grade}")

# 返回字典
def get_student_info_dict(student_id):
    """返回字典格式的学生信息"""
    students = {
        1001: {"name": "张三", "age": 18, "grade": "高三"},
        1002: {"name": "李四", "age": 17, "grade": "高二"}
    }
    return students.get(student_id, {"name": "未知", "age": 0, "grade": "未知"})

# 接收返回的字典
info = get_student_info_dict(1001)
print(f"学生信息：{info}")

# 条件返回
def check_even(number):
    """检查一个数是否是偶数"""
    if number % 2 == 0:
        return True
    else:
        return False

# 使用条件返回
for num in range(1, 11):
    if check_even(num):
        print(f"{num}是偶数")
    else:
        print(f"{num}是奇数")

# 提前返回（guard clauses）
def validate_score(score):
    """验证分数是否有效"""
    if not isinstance(score, (int, float)):
        return False
    if score < 0 or score > 100:
        return False
    return True

# 多个return语句
def classify_score(score):
    """将分数分类"""
    if not validate_score(score):
        return "无效分数"

    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"

# 测试分类
scores = [95, 85, 72, 58, -5, "abc"]
for score in scores:
    print(f"分数{score}：{classify_score(score)}")

# 返回None的情况
def process_data(data, threshold):
    """处理数据，满足条件返回结果，否则返回None"""
    if len(data) < threshold:
        print(f"数据长度不足（需要{threshold}个）")
        return None

    # 处理数据
    result = sum(data) / len(data)
    if result > 100:
        return result * 0.9  # 超过100打9折

    return result

# 使用返回值
data1 = [50, 60, 70, 80]
result1 = process_data(data1, 3)
if result1 is not None:
    print(f"处理结果：{result1:.2f}")

data2 = [50]
result2 = process_data(data2, 3)
if result2 is not None:
    print(f"处理结果：{result2:.2f}")
else:
    print("数据处理失败")

# 实际应用：复杂数据处理函数
def analyze_numbers(numbers, analysis_type="basic"):
    """
    分析数字列表的函数

    Args:
        numbers: 数字列表
        analysis_type: 分析类型，可以是"basic"、"advanced"或"detailed"

    Returns:
        根据分析类型返回不同的结果
    """
    if not numbers:
        return {"error": "列表不能为空"}

    if analysis_type == "basic":
        return {
            "count": len(numbers),
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "max": max(numbers),
            "min": min(numbers)
        }
    elif analysis_type == "advanced":
        basic_stats = analyze_numbers(numbers, "basic")
        return {
            **basic_stats,
            "median": sorted(numbers)[len(numbers)//2],
            "range": max(numbers) - min(numbers),
            "variance": sum((x - basic_stats["average"])**2 for x in numbers) / len(numbers)
        }
    elif analysis_type == "detailed":
        advanced_stats = analyze_numbers(numbers, "advanced")
        return {
            **advanced_stats,
            "sorted": sorted(numbers),
            "duplicates": len(numbers) - len(set(numbers)),
            "is_all_positive": all(x > 0 for x in numbers)
        }
    else:
        return {"error": f"不支持的分析类型：{analysis_type}"}

# 测试分析函数
numbers = [1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10]

# 基础分析
print("基础分析：")
print(analyze_numbers(numbers, "basic"))

# 高级分析
print("\n高级分析：")
print(analyze_numbers(numbers, "advanced"))

# 详细分析
print("\n详细分析：")
print(analyze_numbers(numbers, "detailed"))

# 错误分析
print("\n错误分析：")
print(analyze_numbers(numbers, "unknown_type"))
```

**解释：**

**返回值类型：**

1. **没有return语句**：
   - 函数执行完毕后自动返回`None`
   - 适用于只需要执行操作，不需要返回结果的场景

2. **return单个值**：
   - 可以返回任何类型的值
   - 示例：`return number * number`

3. **return多个值**：
   - 实际上返回的是一个元组
   - 可以用多个变量接收，称为元组解包
   - 示例：`return a, b, c`

4. **返回None**：
   - 显式返回`None`用于表示某种状态
   - 常用于函数执行失败或不需要结果的情况

**return语句的要点：**
1. **执行顺序**：执行到return语句时，函数立即返回，后续代码不会执行
2. **多次return**：函数可以有多个return语句，但只能执行其中一个
3. **提前返回**：使用guard clauses（防护子句）让代码更清晰
4. **None的特殊处理**：使用`is not None`检查是否有效

**return与print的区别：**

| 特性 | return | print |
|------|--------|-------|
| 位置 | 函数内部 | 任何地方 |
| 目的 | 返回结果给调用者 | 输出到控制台 |
| 数据类型 | 任何类型 | 只能用于输出 |
| 使用场景 | 函数编程 | 调试、临时显示 |

**设计返回值的最佳实践：**

1. **一致性**：函数在不同情况下返回的数据类型应该一致
2. **错误处理**：使用异常或特殊的返回值（如None）表示错误
3. **文档说明**：在docstring中明确说明返回值的类型和含义
4. **简洁性**：返回简单、易用的数据结构

**实际应用场景：**

1. **数据处理**：`process_data()`返回处理后的数据和状态
2. **验证函数**：`validate_input()`返回布尔值和错误信息
3. **配置管理**：`get_config()`返回配置字典
4. **网络请求**：`fetch_data()`返回响应数据或错误

**返回值的高级技巧：**
```python
# 使用生成器函数返回多个值（惰性求值）
def generate_squares(n):
    """生成0到n的平方数"""
    for i in range(n + 1):
        yield i * i  # 使用yield而不是return

# 使用生成器
square_gen = generate_squares(5)
for square in square_gen:
    print(square)

# 使用字典返回复杂结构
def get_user_profile(user_id):
    """返回用户资料字典"""
    # 模拟数据库查询
    if user_id == 1:
        return {
            "id": 1,
            "name": "张三",
            "profile": {
                "age": 25,
                "city": "北京",
                "interests": ["编程", "阅读", "旅行"]
            }
        }
    return None
```

---
*本章内容基于 Python 教学平台标准格式设计。*
