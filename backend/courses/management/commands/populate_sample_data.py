"""
Management command to populate sample Python courses, chapters, and algorithm problems
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import ChoiceProblem, Course, Chapter, Problem, AlgorithmProblem, TestCase

from django.contrib.auth.hashers import make_password
class Command(BaseCommand):
    help = 'Populate the database with sample Python courses, chapters, and algorithm problems'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create a default user if none exists
        default_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'student@example.com',
                'is_active': True,
                'password': make_password('123456')
            }
        )
        
        # Check if sample data already exists
        if Course.objects.filter(title="Python编程入门").exists():
            self.stdout.write(
                self.style.WARNING('Sample data already exists. Skipping.')
            )
            return

        # Create Python Programming Course
        python_course = Course.objects.create(
            title="Python编程入门",
            description="学习Python编程的基础知识，包括语法、数据结构、函数等概念。"
        )
        
        self.stdout.write(f'Created course: {python_course.title}')

        # Create chapters for Python Programming Course
        chapter1 = Chapter.objects.create(
            course=python_course,
            title="Python基础语法",
            content="""
### 🚀 Python基础语法概览

欢迎来到 Python 的世界！本章将带你了解 Python 编程的最基础要素，为后续深入学习打下坚实基础。

#### 1. 变量与数据类型

在 Python 中，**变量**用于存储数据值。Python 是一种动态类型语言，你不需要提前声明变量的类型。

* **赋值操作**: 使用等号（`=`）进行赋值。
    ```python
    # 整数类型 (int)
    age = 30
    
    # 浮点数类型 (float)
    pi = 3.14159
    
    # 字符串类型 (str)
    name = "Alice"
    
    # 布尔类型 (bool)
    is_student = True
    ```
* **变量命名规则**:
    * 必须以字母或下划线 (`_`) 开头。
    * 不能以数字开头。
    * 只能包含字母、数字和下划线。
    * 大小写敏感 (`myVar` 和 `myvar` 是不同的)。
    * 不能使用 Python **关键字**（如 `for`, `if`, `class` 等）。

#### 2. 基本输入与输出

* **输出**: 使用内置的 `print()` 函数将内容显示到控制台。
    ```python
    print("Hello, World!")
    print("我的年龄是:", age)
    ```
* **输入**: 使用内置的 `input()` 函数获取用户的输入（返回类型始终是字符串 `str`）。
    ```python
    user_input = input("请输入你的名字: ")
    print("你好，" + user_input)
    ```

#### 3. 运算符

Python 提供了多种运算符来执行算术、比较和逻辑操作。

| 类型 | 运算符 | 示例 | 描述 |
| :--- | :--- | :--- | :--- |
| **算术** | `+`, `-`, `*`, `/` | `5 + 3` | 加、减、乘、除 |
| | `//` | `10 // 3` (结果为 3) | **整除** |
| | `%` | `10 % 3` (结果为 1) | **取模**（余数） |
| | `**` | `2 ** 3` (结果为 8) | **幂运算** |
| **比较** | `==`, `!=`, `>`, `<`, `>=`, `<=` | `age > 18` | 比较两个值 |
| **逻辑** | `and`, `or`, `not` | `True and False` | 逻辑与、或、非 |

#### 4. 字符串基础操作

字符串是 Python 中常用的数据类型，用于存储文本信息。

* **引号**: 可以使用单引号 (`'`)、双引号 (`"`) 或三引号 (`\"\"\"` 或 `'''`) 定义字符串。
* **连接**: 使用 `+` 运算符连接字符串。
    ```python
    greeting = "你好" + " " + "Python" # "你好 Python"
    ```
* **格式化**: 使用 f-string (Python 3.6+) 是最推荐的格式化方式。
    ```python
    city = "北京"
    message = f"我住在 {city}。" # 变量嵌入
    ```

---

**学完本章，你将能够：**

* 理解变量的定义、赋值和命名规则。
* 掌握 Python 的基本数据类型（整数、浮点数、字符串、布尔值）。
* 使用 `print()` 和 `input()` 进行基本的输入输出。
* 熟练运用基本的算术、比较和逻辑运算符。

现在，尝试完成本章的练习题，巩固你的基础知识吧！

            """,
            order=1
        )
        
        self.stdout.write(f'Created chapter: {chapter1.title}')

        chapter2 = Chapter.objects.create(
            course=python_course,
            title="控制结构",
            content='''
### 🚦 控制结构：让你的代码动起来

代码的执行流程并非总是一条直线。**控制结构**允许你根据不同的条件执行不同的代码块，或者重复执行特定的代码，是实现复杂逻辑的关键。

#### 1. 条件语句 (if, elif, else)

条件语句用于根据表达式的布尔值（`True` 或 `False`）来决定执行哪一部分代码。

* **基本 `if` 结构**:
    ```python
    score = 85
    if score >= 60:
        print("及格了！")
    ```

* **`if...else` 结构**:
    ```python
    temp = 25
    if temp > 30:
        print("天气炎热，请注意防暑。")
    else:
        print("温度适宜。")
    ```

* **多重条件 `if...elif...else`**: `elif` 是 "else if" 的缩写，允许你检查多个条件。
    ```python
    grade = 92
    if grade >= 90:
        print("A")
    elif grade >= 80:
        print("B")
    elif grade >= 70:
        print("C")
    else:
        print("D")
    ```
    > **⚠️ 注意缩进**: 在 Python 中，代码块（如 `if` 语句内部）是通过**缩进**（通常是 4 个空格）来定义的。

#### 2. 循环结构 (for 循环)

**`for` 循环**常用于遍历序列（如列表、字符串或元组）中的元素，或者执行固定次数的操作。

* **遍历序列**:
    ```python
    fruits = ["apple", "banana", "cherry"]
    for fruit in fruits:
        print(f"我喜欢吃 {fruit}")
    ```

* **使用 `range()` 函数**: `range(start, stop, step)` 常用于生成一系列数字，进行固定次数的循环。
    ```python
    # 从 0 到 4 (不包含 5)
    for i in range(5):
        print(i)
        
    # 从 1 到 10，步长为 2 (1, 3, 5, 7, 9)
    for j in range(1, 11, 2):
        print(j)
    ```

#### 3. 循环结构 (while 循环)

**`while` 循环**在给定条件为 `True` 时重复执行代码块。

* **基本 `while` 结构**:
    ```python
    count = 0
    while count < 3:
        print(f"循环次数: {count}")
        count = count + 1 # 必须有条件更新，否则会是无限循环
    ```
    > **💡 警惕无限循环**: 如果 `while` 循环的条件始终为 `True`，程序将无限执行。

#### 4. 循环控制语句 (break 和 continue)

* **`break`**: **立即**退出当前所在的整个循环（`for` 或 `while`）。
    ```python
    for i in range(10):
        if i == 5:
            break  # 当 i 等于 5 时，退出循环
        print(i)
    # 输出: 0, 1, 2, 3, 4
    ```

* **`continue`**: **跳过**当前循环的剩余代码，直接进入下一次循环的迭代。
    ```python
    for i in range(5):
        if i == 2:
            continue # 当 i 等于 2 时，跳过 print，直接进入 i=3 的迭代
        print(i)
    # 输出: 0, 1, 3, 4
    ```

---

**学完本章，你将能够：**

* 使用 `if`、`elif` 和 `else` 实现代码的条件分支。
* 使用 `for` 循环遍历数据结构或执行固定次数的操作。
* 使用 `while` 循环根据条件重复执行代码。
* 使用 `break` 和 `continue` 灵活控制循环的执行流程。

现在，尝试解决本章的练习题，特别是著名的 **FizzBuzz问题**，它就是对控制结构的绝佳实践！
            ''',
            order=2
        )
        
        self.stdout.write(f'Created chapter: {chapter2.title}')

        chapter3 = Chapter.objects.create(
            course=python_course,
            title="函数与模块",
            content='''
### 🧩 函数与模块：组织和重用代码

在编写复杂的程序时，将代码分解成可管理、可重用的块是至关重要的。**函数 (Functions)** 和 **模块 (Modules)** 就是实现这一目标的工具。

#### 1. 函数的定义与调用

**函数**是一段执行特定任务的代码块，可以提高代码的**重用性**和**可读性**。

* **定义函数**: 使用 `def` 关键字定义函数。
    ```python
    def greet(name):
        """
        这个函数用于向指定的名字问好。
        (这是函数的文档字符串 Docstring)
        """
        print(f"你好, {name}!")

    # 调用函数
    greet("张三")
    # 输出: 你好, 张三!
    ```

* **返回值**: 使用 `return` 语句将结果返回给函数的调用者。如果没有 `return` 语句，函数默认返回 `None`。
    ```python
    def add(a, b):
        result = a + b
        return result

    sum_result = add(10, 5) # sum_result 的值为 15
    print(sum_result)
    ```

#### 2. 函数参数

函数参数定义了函数需要接收哪些输入。

* **位置参数**: 必须按照定义的顺序传入。
* **关键字参数**: 通过指定参数名来传入，可以不按顺序。
    ```python
    def power(base, exp=2): # exp=2 是默认值
        return base ** exp

    # 位置参数调用
    print(power(3, 4))   # 3的4次方，结果 81

    # 关键字参数调用
    print(power(exp=3, base=2)) # 2的3次方，结果 8
    
    # 使用默认值
    print(power(5)) # 5的2次方，结果 25
    ```

* **可变参数 (\*args 和 \*\*kwargs)**:
    * `*args`: 接收任意数量的**位置参数**，并将它们作为一个元组 (tuple) 传入。
    * `**kwargs`: 接收任意数量的**关键字参数**，并将它们作为一个字典 (dict) 传入。

#### 3. 变量作用域 (Scope)

变量的作用域决定了代码中的哪些部分可以访问某个变量。

* **局部变量 (Local)**: 在函数内部定义的变量，只能在该函数内部访问。
* **全局变量 (Global)**: 在函数外部定义的变量，可以在程序的任何地方访问。
    ```python
    global_var = "我是全局的"

    def my_function():
        local_var = "我是局部的"
        print(global_var) # 可以访问全局变量
        
    my_function()
    # print(local_var) # 错误：在外部无法访问局部变量
    ```
    > **🔑 `global` 关键字**: 如果想在函数内部修改一个全局变量，需要使用 `global` 关键字声明。

#### 4. 模块和包

* **模块 (Module)**: 一个包含 Python 定义和语句的文件（以 `.py` 为后缀）。
* **导入 (Import)**: 使用 `import` 语句可以将其他模块中的功能引入到当前文件中。

* **导入方式**:
    ```python
    # 导入整个模块
    import math
    print(math.sqrt(16)) # 使用 模块名.函数名

    # 导入模块中的特定函数
    from random import randint
    print(randint(1, 10)) # 直接使用 函数名
    
    # 导入并设置别名
    import time as t
    t.sleep(1)
    ```

* **内置模块**: Python 提供了大量的标准库模块，如 `math`（数学运算）、`random`（随机数）、`os`（操作系统交互）等，你无需安装即可直接使用。

---

**学完本章，你将能够：**

* 正确定义和调用函数，并使用 `return` 返回结果。
* 理解和使用函数的参数（位置参数、关键字参数、默认参数）。
* 区分局部变量和全局变量的作用域。
* 使用 `import` 语句导入 Python 模块，利用标准库功能。

本章的 **“有效的括号”** 问题将检验你对函数定义、参数传递以及数据结构（如栈）的综合运用能力。
            ''',
            order=3
        )
        
        self.stdout.write(f'Created chapter: {chapter3.title}')

        chapter4 = Chapter.objects.create(
            course=python_course,
            title="数据结构",
            content='''
### 🏗️ 数据结构：组织和管理数据

**数据结构**是组织和存储数据的方式，它决定了数据被访问和操作的效率。Python 内置了几种强大且灵活的数据结构，是进行数据处理的基础。

#### 1. 列表 (List)

**列表**是 Python 中最常用、最灵活的**可变 (Mutable)** 序列类型。它用于存储一系列有序的项目，可以包含不同类型的数据。

* **创建**: 使用方括号 `[]` 或 `list()`。
    ```python
    my_list = [1, "apple", 3.14, True]
    ```
* **特性**:
    * **有序**: 元素有固定的顺序，支持索引和切片。
    * **可变**: 元素可以被修改、添加或删除。
* **常用操作**:
    * `my_list[0]`：索引访问（返回 `1`）
    * `my_list.append(item)`：在末尾添加元素
    * `my_list.insert(index, item)`：在指定位置插入
    * `my_list.remove(item)`：删除第一个匹配的元素
    * `my_list.pop(index)`：删除并返回指定索引处的元素

#### 2. 元组 (Tuple)

**元组**是与列表相似的序列类型，但它是**不可变 (Immutable)** 的。通常用于存储一旦创建就不应更改的数据集合。

* **创建**: 使用圆括号 `()` 或 `tuple()`。
    ```python
    my_tuple = (10, 20, "hello")
    ```
* **特性**:
    * **有序**: 支持索引和切片。
    * **不可变**: 一旦创建，不能修改、添加或删除元素。
* **使用场景**: 函数的多个返回值、字典的键（因为不可变）。

#### 3. 字典 (Dictionary)

**字典**是一种**无序**的**可变**集合，以 **键-值对 (Key-Value Pair)** 的形式存储数据。键必须是唯一的且不可变类型（如字符串、数字或元组）。

* **创建**: 使用花括号 `{}` 或 `dict()`。
    ```python
    person = {"name": "Bob", "age": 25, "city": "Shanghai"}
    ```
* **特性**:
    * **可变**: 可以添加、修改和删除键值对。
    * **通过键访问**: 通过键而不是索引来检索值。
* **常用操作**:
    * `person["name"]`：通过键访问值（返回 `"Bob"`）
    * `person["age"] = 26`：修改值
    * `person["job"] = "Engineer"`：添加新的键值对
    * `person.keys()`：获取所有键
    * `person.values()`：获取所有值

#### 4. 集合 (Set)

**集合**是一个**无序**的**可变**集合，其中元素是唯一的（不包含重复项）。它常用于执行数学上的集合操作，如并集、交集等。

* **创建**: 使用花括号 `{}` 或 `set()` (创建空集合必须用 `set()`)。
    ```python
    my_set = {1, 2, 3, 2, 1} # 自动去重，实际存储 {1, 2, 3}
    ```
* **特性**:
    * **无序**: 不支持索引和切片。
    * **元素唯一**: 自动去除重复元素。
    * **可变**: 可以添加和删除元素。
* **常用操作**:
    * `my_set.add(4)`：添加元素
    * `my_set.remove(1)`：删除元素
    * `set1 | set2`：并集
    * `set1 & set2`：交集

---

**学完本章，你将能够：**

* 理解列表、元组、字典和集合四种核心数据结构的区别和适用场景。
* 掌握列表作为可变序列的各种增删改查操作。
* 利用字典的键-值特性高效地存储和检索数据。
* 应用数据结构的特性来解决实际问题，例如本章的 **“合并两个有序数组”** 问题，这需要高效利用列表（数组）的操作。

你已经掌握了 Python 编程的基础，现在可以尝试挑战更高级的算法和数据处理任务了！
            ''',
            order=4
        )
        
        self.stdout.write(f'Created chapter: {chapter4.title}')

        # Create algorithm problems for Chapter 1
        problem1 = Problem.objects.create(
            chapter=chapter1,
            type='algorithm',
            title="两数之和",
            content="给定一个整数数组和一个目标值，找出数组中和为目标值的两个数的下标。",
            difficulty=1
        )
        
        algorithm_problem1 = AlgorithmProblem.objects.create(
            problem=problem1,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def twoSum(nums, target):\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "twoSum"
            }
        )
        
        # Add test cases for two sum problem
        TestCase.objects.create(
            problem=algorithm_problem1,
            input_data="[[2, 7, 11, 15], 9]",
            expected_output="[0, 1]",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem1,
            input_data="[[3, 2, 4], 6]",
            expected_output="[1, 2]",
        )
        
        TestCase.objects.create(
            problem=algorithm_problem1,
            input_data="[[3, 3], 6]",
            expected_output="[0, 1]"
        )
        
        self.stdout.write(f'Created problem: {problem1.title}')
        
        problem2 = Problem.objects.create(
            chapter=chapter1,
            type='algorithm',
            title="回文数判断",
            content="判断一个整数是否是回文数。回文数是指正序（从左向右）和倒序（从右向左）读都是一样的整数。",
            difficulty=1
        )
        
        algorithm_problem2 = AlgorithmProblem.objects.create(
            problem=problem2,
            time_limit=1000,
            memory_limit=256,
            code_template={
                "python": "def isPalindrome(x: int) -> bool:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "isPalindrome"
            }
        )
        
        # Add test cases for palindrome problem
        TestCase.objects.create(
            problem=algorithm_problem2,
            input_data="[121]",
            expected_output="true",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem2,
            input_data="[-121]",
            expected_output="false"
        )
        
        TestCase.objects.create(
            problem=algorithm_problem2,
            input_data="[10]",
            expected_output="false"
        )
        
        self.stdout.write(f'Created problem: {problem2.title}')

        # Create algorithm problems for Chapter 2
        problem3 = Problem.objects.create(
            chapter=chapter2,
            type='algorithm',
            title="FizzBuzz问题",
            content="写一个程序，输出从 1 到 n 的数字。但是，当数字是 3 的倍数时，输出 'Fizz'；当数字是 5 的倍数时，输出 'Buzz'；当数字是 3 和 5 的倍数时，输出 'FizzBuzz'。",
            difficulty=1
        )
        
        algorithm_problem3 = AlgorithmProblem.objects.create(
            problem=problem3,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def fizzBuzz(n: int) -> list:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "fizzBuzz"
            }
        )
        
        # Add test cases for FizzBuzz problem
        TestCase.objects.create(
            problem=algorithm_problem3,
            input_data="[15]",
            expected_output='["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]',
            is_sample=True
        )
        
        self.stdout.write(f'Created problem: {problem3.title}')

        # Create algorithm problems for Chapter 3
        problem4 = Problem.objects.create(
            chapter=chapter3,
            type='algorithm',
            title="有效的括号",
            content="给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串，判断字符串是否有效。",
            difficulty=2
        )
        
        algorithm_problem4 = AlgorithmProblem.objects.create(
            problem=problem4,
            time_limit=1000,
            memory_limit=256,
            code_template={
                "python": "def isValid(s: str) -> bool:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "isValid"
            }
        )
        
        # Add test cases for valid parentheses problem
        TestCase.objects.create(
            problem=algorithm_problem4,
            input_data='["()"]',
            expected_output="true",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem4,
            input_data='["()[]{}"]',
            expected_output="true"
        )
        
        TestCase.objects.create(
            problem=algorithm_problem4,
            input_data='["(]"]',
            expected_output="false"
        )
        
        self.stdout.write(f'Created problem: {problem4.title}')

        # Create algorithm problems for Chapter 4
        problem5 = Problem.objects.create(
            chapter=chapter4,
            type='algorithm',
            title="合并两个有序数组",
            content="给定两个排序后的数组 A 和 B，其中 A 的末端有足够的缓冲空间容纳 B。编写一个方法，将 B 合并入 A 并排序。",
            difficulty=2
        )
        
        algorithm_problem5 = AlgorithmProblem.objects.create(
            problem=problem5,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def merge(nums1: list, m: int, nums2: list, n: int) -> None:\n    # 请在此实现你的代码（直接修改 nums1）\n    pass"
            },
            solution_name={
                "python": "merge"
            }
        )
        
        # Add test cases for merge sorted array problem
        TestCase.objects.create(
            problem=algorithm_problem5,
            input_data="[[1,2,3,0,0,0], 3, [2,5,6], 3]",
            expected_output="[1,2,2,3,5,6]",
            is_sample=True
        )
        
        self.stdout.write(f'Created problem: {problem5.title}')

        # Create an additional advanced problem for Chapter 4
        problem6 = Problem.objects.create(
            chapter=chapter4,
            type='algorithm',
            title="旋转数组中查找元素",
            content="给定一个经过旋转的升序数组和一个目标值，若目标值存在于数组中则返回其下标，否则返回 -1。",
            difficulty=3
        )
        
        algorithm_problem6 = AlgorithmProblem.objects.create(
            problem=problem6,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def search(nums: list, target: int) -> int:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "search"
            }
        )
        
        # Add test cases for rotated array search
        TestCase.objects.create(
            problem=algorithm_problem6,
            input_data="[[4,5,6,7,0,1,2], 0]",
            expected_output="4",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem6,
            input_data="[[4,5,6,7,0,1,2], 3]",
            expected_output="-1"
        )
        
        self.stdout.write(f'Created problem: {problem6.title}')
        # Chapter 1: Python基础语法 -> 变量命名
        choice_prob1 = Problem.objects.create(
            chapter=chapter1,
            type='choice',
            title="以下哪个是合法的 Python 变量名？",
            content="请选择符合 Python 变量命名规则的选项。",
            difficulty=1
        )
        ChoiceProblem.objects.create(
            problem=choice_prob1,
            options={
                "A": "123abc",
                "B": "my-variable",
                "C": "_private_var",
                "D": "class"
            },
            correct_answer="C",
            is_multiple_choice=False
        )
        self.stdout.write(f'Created choice problem: {choice_prob1.title}')

        # Chapter 2: 控制结构 -> 循环与条件
        choice_prob2 = Problem.objects.create(
            chapter=chapter2,
            type='choice',
            title="以下哪段代码会输出数字 0 到 4？",
            content="选择正确的 Python 代码片段。",
            difficulty=1
        )
        ChoiceProblem.objects.create(
            problem=choice_prob2,
            options={
                "A": "for i in range(5): print(i)",
                "B": "for i in range(1,5): print(i)",
                "C": "while i < 5: print(i)",
                "D": "for i in [0,1,2,3]: print(i)"
            },
            correct_answer="A",
            is_multiple_choice=False
        )
        self.stdout.write(f'Created choice problem: {choice_prob2.title}')

        # Chapter 3: 函数与模块 -> 函数定义
        choice_prob3 = Problem.objects.create(
            chapter=chapter3,
            type='choice',
            title="关于 Python 函数，以下说法正确的是？",
            content="请选择正确的描述。",
            difficulty=2
        )
        ChoiceProblem.objects.create(
            problem=choice_prob3,
            options={
                "A": "函数必须有 return 语句",
                "B": "函数参数不能有默认值",
                "C": "函数可以嵌套定义",
                "D": "lambda 函数可以包含多条语句"
            },
            correct_answer="C",
            is_multiple_choice=False
        )
        self.stdout.write(f'Created choice problem: {choice_prob3.title}')

        # Chapter 4: 数据结构 -> 列表与字典
        choice_prob4 = Problem.objects.create(
            chapter=chapter4,
            type='choice',
            title="以下哪些是可变（mutable）数据类型？（可多选）",
            content="Python 中的数据类型分为可变与不可变，请选择所有可变类型。",
            difficulty=2
        )
        ChoiceProblem.objects.create(
            problem=choice_prob4,
            options={
                "A": "list",
                "B": "tuple",
                "C": "dict",
                "D": "set"
            },
            correct_answer=["A", "C", "D"],
            is_multiple_choice=True
        )
        self.stdout.write(f'Created choice problem: {choice_prob4.title}')
        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data for Python teaching platform!')
        )