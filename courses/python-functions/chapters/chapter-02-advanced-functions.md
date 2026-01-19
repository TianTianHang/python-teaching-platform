---
title: "函数进阶"
order: 2
---
## 函数进阶

### 章节概述

在前一章中，我们学习了函数的基础知识。本章将深入探讨函数的高级特性，包括默认参数、可变参数、作用域规则和lambda表达式。掌握这些高级特性，你将能够编写更灵活、更强大的Python代码。

### 知识点 1：默认参数与可变参数

**描述：**

Python函数支持多种参数传递方式，包括默认参数、可变位置参数(*args)和可变关键字参数(**kwargs)。这些特性让函数更加灵活和通用。

**示例代码：**
```python
# 默认参数
def greet(name, greeting="你好"):
    """带有默认参数的函数"""
    return f"{greeting}，{name}！"

print(greet("张三"))                    # 你好，张三！
print(greet("李四", "早上好"))           # 早上好，李四！

# 可变位置参数 (*args)
def sum_all(*numbers):
    """接收任意数量的位置参数"""
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3))                # 6
print(sum_all(10, 20, 30, 40, 50))     # 150
print(sum_all())                        # 0

# 可变关键字参数 (**kwargs)
def create_profile(**info):
    """接收任意数量的关键字参数"""
    profile = {}
    for key, value in info.items():
        profile[key] = value
    return profile

profile1 = create_profile(name="王五", age=25, city="北京")
print(profile1)
# {'name': '王五', 'age': 25, 'city': '北京'}

# 混合使用各种参数
def complex_function(a, b, c=10, *args, **kwargs):
    """演示所有参数类型"""
    print(f"a={a}, b={b}, c={c}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")

complex_function(1, 2)
# a=1, b=2, c=10
# args=()
# kwargs={}

complex_function(1, 2, 3, 4, 5, x=100, y=200)
# a=1, b=2, c=3
# args=(4, 5)
# kwargs={'x': 100, 'y': 200}

# 实际应用：灵活的购物车函数
def add_to_cart(cart, *items, **options):
    """向购物车添加商品"""
    for item in items:
        cart.append(item)

    # 处理选项
    if "discount" in options:
        discount = options["discount"]
        print(f"应用 {discount}% 折扣")

    if "shipping" in options:
        shipping = options["shipping"]
        print(f"配送方式: {shipping}")

    return cart

my_cart = []
add_to_cart(my_cart, "苹果", "香蕉", "橙子", discount=10, shipping="快递")
print(f"购物车: {my_cart}")

# 实际应用：计算器函数
def calculate(operation, *args):
    """执行多种计算操作"""
    if operation == "sum":
        return sum(args)
    elif operation == "avg":
        return sum(args) / len(args) if args else 0
    elif operation == "max":
        return max(args) if args else None
    elif operation == "min":
        return min(args) if args else None
    else:
        return "未知操作"

print(calculate("sum", 1, 2, 3, 4, 5))      # 15
print(calculate("avg", 10, 20, 30))         # 20.0
print(calculate("max", 5, 8, 3, 9, 2))      # 9
```

**解释：**

**默认参数：**
- 在函数定义时为参数指定默认值
- 调用时不提供该参数，则使用默认值
- 默认参数必须放在非默认参数之后
- **重要**：默认参数在函数定义时只计算一次，避免使用可变对象作为默认值

```python
# 错误示例：可变默认参数
def bad_append(item, list=[]):  # 不要这样做
    list.append(item)
    return list

# 正确做法：使用 None 作为默认值
def good_append(item, list=None):
    if list is None:
        list = []
    list.append(item)
    return list
```

**可变位置参数 (*args)：**
- 使用 `*` 作为前缀，收集所有额外的位置参数
- 在函数内部，`args` 是一个元组
- 可以接收任意数量的位置参数
- 常用于不确定需要多少参数的情况

**可变关键字参数 (**kwargs)：**
- 使用 `**` 作为前缀，收集所有额外的关键字参数
- 在函数内部，`kwargs` 是一个字典
- 可以接收任意数量的关键字参数
- 常用于配置选项、命名参数等场景

**参数顺序规则：**
```python
def correct_order(a, b, c=1, *args, **kwargs):
    pass

# 1. 普通位置参数
# 2. 默认参数
# 3. 可变位置参数 (*args)
# 4. 可变关键字参数 (**kwargs)
```

**实际应用场景：**
- **装饰器**：使用 *args 和 **kwargs 传递任意参数
- **API封装**：灵活的参数配置
- **数据处理**：批量处理任意数量的数据项
- **配置函数**：接收多种配置选项

---

### 知识点 2：作用域与命名空间

**描述：**

作用域决定了变量在代码中的可见性和生命周期。Python采用LEGB规则来查找变量：Local → Enclosing → Global → Built-in。

**示例代码：**
```python
# 全局变量与局部变量
global_var = "全局变量"

def test_scope():
    local_var = "局部变量"
    print(f"函数内访问全局变量: {global_var}")  # 可以访问
    print(f"函数内访问局部变量: {local_var}")    # 可以访问

test_scope()
print(f"函数外访问全局变量: {global_var}")       # 可以访问
# print(local_var)  # 报错：函数外无法访问局部变量

# 修改全局变量（需要使用 global 关键字）
count = 0

def increment():
    global count  # 声明使用全局变量
    count += 1
    print(f"函数内 count = {count}")

increment()  # count = 1
increment()  # count = 2
print(f"函数外 count = {count}")  # count = 2

# 嵌套函数的作用域（Enclosing）
def outer_function():
    enclosing_var = "外部函数变量"

    def inner_function():
        nonlocal enclosing_var  # 声明使用外层函数变量
        enclosing_var = "已修改"
        print(f"内部函数访问: {enclosing_var}")

    inner_function()
    print(f"外部函数访问: {enclosing_var}")

outer_function()
# 内部函数访问: 已修改
# 外部函数访问: 已修改

# LEGB 规则演示
x = "全局 level"

def outer():
    x = "外部函数 level"

    def inner():
        x = "内部函数 level"
        print(f"内部函数 x = {x}")  # 使用内部函数的 x

    inner()
    print(f"外部函数 x = {x}")      # 使用外部函数的 x

outer()
print(f"全局 x = {x}")              # 使用全局的 x

# 实际应用：计数器闭包
def create_counter():
    """创建一个计数器函数"""
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter

# 创建多个独立的计数器
counter1 = create_counter()
counter2 = create_counter()

print(counter1())  # 1
print(counter1())  # 2
print(counter2())  # 1
print(counter1())  # 3

# 实际应用：配置管理器
def config_manager(default_config):
    """创建一个配置管理器"""
    config = default_config.copy()

    def get_config(key):
        return config.get(key)

    def set_config(key, value):
        config[key] = value

    def update_config(new_config):
        config.update(new_config)

    return {
        "get": get_config,
        "set": set_config,
        "update": update_config
    }

app_config = config_manager({"debug": True, "version": "1.0"})
print(app_config["get"]("debug"))     # True
app_config["set"]("debug", False)
print(app_config["get"]("debug"))     # False
```

**解释：**

**LEGB 查找规则：**
Python按以下顺序查找变量：
1. **L (Local)**: 局部作用域，函数内部定义的变量
2. **E (Enclosing)**: 嵌套作用域，外层函数的变量
3. **G (Global)**: 全局作用域，模块级别定义的变量
4. **B (Built-in)**: 内置作用域，Python内置的名称

```python
# LEGB 示例
x = 10  # Global

def outer():
    x = 20  # Enclosing

    def inner():
        x = 30  # Local
        print(x)  # 输出 30 (使用 Local)

    inner()

outer()
print(x)  # 输出 10 (使用 Global)
```

**global 关键字：**
- 用于在函数内部修改全局变量
- 不使用 `global` 时，函数内对全局变量的赋值会创建一个新的局部变量
- 使用 `global` 后，函数内对变量的修改会影响全局变量

```python
count = 0

def modify_global():
    global count
    count = 100  # 修改全局变量

def create_local():
    count = 50   # 创建局部变量

modify_global()
print(count)  # 100
```

**nonlocal 关键字：**
- 用于在嵌套函数中修改外层函数的变量
- 类似 `global`，但作用于嵌套作用域
- 只能用于嵌套函数中

```python
def outer():
    x = 10

    def inner():
        nonlocal x
        x = 20  # 修改外层函数的 x

    inner()
    print(x)  # 20
```

**作用域的最佳实践：**
1. **避免滥用全局变量**：全局变量会增加代码耦合度
2. **使用参数传递**：优先通过参数传递数据，而非依赖全局变量
3. **封装状态**：使用闭包和类来封装相关状态
4. **明确作用域**：使用 `global` 和 `nonlocal` 时要有明确目的

**实际应用场景：**
- **计数器**：使用闭包维护独立的状态
- **配置管理**：使用作用域隔离配置
- **状态机**：使用嵌套函数管理状态转换
- **事件处理**：使用闭包保存事件上下文

---

### 知识点 3：lambda表达式与匿名函数

**描述：**

lambda表达式是一种创建匿名函数的简洁方式。它适用于简单的一次性函数，特别是在高阶函数（如map、filter、sorted）中非常有用。

**示例代码：**
```python
# lambda 基本语法
# lambda 参数: 表达式

# 普通函数 vs lambda
def square(x):
    return x ** 2

square_lambda = lambda x: x ** 2

print(square(5))           # 25
print(square_lambda(5))    # 25

# 多参数 lambda
add = lambda x, y: x + y
print(add(3, 4))  # 7

# lambda 与 sorted()
students = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 78}
]

# 按分数排序
sorted_by_score = sorted(students, key=lambda s: s["score"])
print([s["name"] for s in sorted_by_score])  # ['王五', '张三', '李四']

# 按姓名排序
sorted_by_name = sorted(students, key=lambda s: s["name"])
print([s["name"] for s in sorted_by_name])  # ['张三', '李四', '王五']

# lambda 与 map()
numbers = [1, 2, 3, 4, 5]

# 将所有数字平方
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# 将所有数字转换为字符串
strings = list(map(lambda x: str(x), numbers))
print(strings)  # ['1', '2', '3', '4', '5']

# lambda 与 filter()
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 筛选偶数
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# 筛选大于5的数字
greater_than_five = list(filter(lambda x: x > 5, numbers))
print(greater_than_five)  # [6, 7, 8, 9, 10]

# lambda 与列表推导式
# 使用 lambda
squares = list(map(lambda x: x ** 2, range(1, 6)))
print(squares)  # [1, 4, 9, 16, 25]

# 使用列表推导式（更 Pythonic）
squares = [x ** 2 for x in range(1, 6)]
print(squares)  # [1, 4, 9, 16, 25]

# 实际应用：数据转换
products = [
    {"name": "苹果", "price": 5.5},
    {"name": "香蕉", "price": 3.2},
    {"name": "橙子", "price": 4.8}
]

# 提取所有商品名称
names = list(map(lambda p: p["name"], products))
print(names)  # ['苹果', '香蕉', '橙子']

# 提取所有商品价格
prices = list(map(lambda p: p["price"], products))
print(prices)  # [5.5, 3.2, 4.8]

# 筛选价格大于4的商品
expensive = list(filter(lambda p: p["price"] > 4, products))
print([p["name"] for p in expensive])  # ['苹果', '橙子']

# 实际应用：复杂排序
words = ["apple", "banana", "cherry", "date", "elderberry"]

# 按长度排序
sorted_by_length = sorted(words, key=lambda w: len(w))
print(sorted_by_length)  # ['date', 'apple', 'banana', 'cherry', 'elderberry']

# 按最后一个字母排序
sorted_by_last = sorted(words, key=lambda w: w[-1])
print(sorted_by_last)  # ['apple', 'banana', 'cherry', 'date', 'elderberry']

# 实际应用：条件表达式
get_grade = lambda score: "优秀" if score >= 90 else "良好" if score >= 80 else "及格"
print(get_grade(95))  # 优秀
print(get_grade(85))  # 良好
print(get_grade(75))  # 及格

# lambda 的限制
# lambda 只能包含单个表达式
# 以下操作无法用 lambda 实现：
def complex_function(x):
    if x > 0:
        result = x * 2
    else:
        result = x * 3
    return result

# 对于复杂逻辑，应使用普通函数
```

**解释：**

**lambda 语法：**
```python
lambda 参数1, 参数2, ...: 表达式
```

**lambda 的特点：**
- **匿名**：不需要函数名
- **简洁**：单行表达式
- **即时**：通常在使用时定义
- **限制**：只能包含一个表达式

**lambda 与普通函数的区别：**

| 特性 | lambda | def 函数 |
|------|--------|----------|
| 函数名 | 无 | 有 |
| 语句数量 | 单个表达式 | 多个语句 |
| 复杂度 | 简单 | 可以很复杂 |
| 可读性 | 较差 | 较好 |
| 文档字符串 | 无 | 可以有 |

**lambda 的使用场景：**

1. **高阶函数参数**：
```python
sorted(iterable, key=lambda x: x.field)
map(lambda x: x * 2, iterable)
filter(lambda x: x > 0, iterable)
```

2. **简单回调**：
```python
button.on_click(lambda: print("点击"))
```

3. **一次性函数**：
```python
# 使用 lambda
result = (lambda x: x ** 2)(5)  # 25

# 不如直接使用
result = 5 ** 2  # 25
```

**lambda 的最佳实践：**
1. **保持简单**：lambda 只应用于简单逻辑
2. **优先使用列表推导式**：对于 map/filter 操作
3. **避免复杂 lambda**：超过一行的逻辑应该用 def
4. **考虑可读性**：团队协作时应优先使用命名函数

```python
# 好的 lambda
sorted(words, key=lambda w: len(w))

# 不好的 lambda（太复杂）
bad = lambda x: x * 2 if x > 0 else x * 3 if x < 0 else 0

# 应该用普通函数
def process_number(x):
    if x > 0:
        return x * 2
    elif x < 0:
        return x * 3
    else:
        return 0
```

**实际应用场景：**
- **数据排序**：灵活的排序键
- **数据转换**：map 和 reduce 操作
- **数据过滤**：filter 操作
- **GUI 编程**：事件回调
- **函数式编程**：高阶函数组合

---
*本章内容基于 Python 教学平台标准格式设计。*
