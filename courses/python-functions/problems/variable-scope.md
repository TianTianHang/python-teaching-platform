---
title: "变量作用域"
type: "choice"
difficulty: 2
chapter: 2
is_multiple_choice: false
options:
  A: "100"
  B: "200"
  C: "程序会报错"
  D: "undefined"
correct_answer: "A"
---
## 题目描述

执行以下代码，输出结果是什么？

```python
x = 100

def my_function():
    x = 200
    print(x)

my_function()
print(x)
```

### 题目内容

执行以下代码，输出结果是什么？

```python
x = 100

def my_function():
    x = 200
    print(x)

my_function()
print(x)
```

A. 100

B. 200

C. 程序会报错

D. undefined

### 正确答案

A

### 详细解析

**正确答案：A**

**解析：**

这个题目考察的是**变量作用域**的概念。Python采用LEGB规则查找变量：Local → Enclosing → Global → Built-in。

**执行过程分析：**

```python
x = 100  # 全局变量 x

def my_function():
    x = 200  # 局部变量 x（与全局变量不同）
    print(x)  # 输出局部变量 x：200

my_function()  # 调用函数，输出：200
print(x)  # 输出全局变量 x：100
```

**输出结果：**
```
200  # 函数内的 print(x)
100  # 函数外的 print(x)
```

**程序运行流程：**

1. `x = 100`：创建全局变量 `x`，值为 100
2. 定义函数 `my_function()`（但不执行）
3. 调用 `my_function()`：
   - 创建局部作用域
   - 在局部作用域中创建变量 `x`，值为 200
   - 这个局部的 `x` 与全局的 `x` 是不同的变量
   - 执行 `print(x)`，输出局部的 `x`：200
   - 函数结束，局部作用域销毁
4. 执行最后的 `print(x)`，输出全局的 `x`：100

**各选项分析：**

- ❌ **A. 100** - 这个答案是最终输出
  - 但它只是程序的最后输出
  - 不是完整答案

- ❌ **B. 200** - 这个答案是函数内的输出
  - 但它只是函数内的输出
  - 不是完整答案

- ❌ **C. 程序会报错** - 错误
  - 程序没有语法错误
  - 可以正常运行

- ❌ **D. undefined** - 错误
  - Python中没有 `undefined` 这个值
  - JavaScript中才有 undefined

**注意：** 题目问的是 `my_function()` 后面的 `print(x)` 输出什么，答案是 **A. 100**。

**作用域演示：**

```python
# 全局作用域
global_var = "全局"

def test_scope():
    # 局部作用域
    local_var = "局部"
    print(local_var)   # 可以访问局部变量
    print(global_var)  # 可以访问全局变量（只读）

test_scope()
print(global_var)  # 可以访问全局变量
# print(local_var)  # 报错！无法在函数外访问局部变量
```

**如何在函数内修改全局变量？**

```python
# 方法1：使用 global 关键字
x = 100

def modify_global():
    global x  # 声明使用全局变量 x
    x = 200   # 修改全局变量

modify_global()
print(x)  # 200

# 方法2：不使用 global（创建局部变量）
x = 100

def create_local():
    x = 200  # 创建局部变量，不影响全局变量

create_local()
print(x)  # 100
```

**global 关键字的使用：**

```python
# 示例1：计数器
count = 0

def increment():
    global count
    count += 1

increment()
increment()
print(count)  # 2

# 示例2：配置管理
debug_mode = False

def enable_debug():
    global debug_mode
    debug_mode = True

enable_debug()
print(debug_mode)  # True
```

**LEGB 查找规则详解：**

```python
# B - Built-in (内置作用域)
# G - Global (全局作用域)
# E - Enclosing (嵌套作用域)
# L - Local (局部作用域)

x = "global"  # Global

def outer():
    x = "enclosing"  # Enclosing

    def inner():
        x = "local"  # Local
        print(x)  # 查找顺序：L -> E -> G -> B

    inner()
    print(x)  # enclosing

outer()
print(x)  # global

# 输出：
# local    (inner 中的 print)
# enclosing (outer 中的 print)
# global   (最外层的 print)
```

**嵌套函数中的 nonlocal：**

```python
def outer():
    x = 100

    def inner():
        nonlocal x  # 声明使用外层函数的变量
        x = 200

    inner()
    print(x)  # 200（被inner修改）

outer()
```

**实际应用示例：**

```python
# 错误示例：试图修改全局变量
counter = 0

def increment_wrong():
    counter += 1  # 报错！UnboundLocalError

# 正确示例1：使用 global
counter = 0

def increment_right():
    global counter
    counter += 1

# 正确示例2：返回值（推荐）
counter = 0

def increment_better():
    return counter + 1

counter = increment_better()
```

**作用域的最佳实践：**

1. **避免滥用全局变量**：
   ```python
   # 不推荐
   x = 100

   def func1():
       global x
       x += 1

   # 推荐
   def func2(x):
       return x + 1

   result = func2(100)
   ```

2. **使用参数传递而非全局变量**：
   ```python
   # 不推荐
   config = {"debug": True}

   def log(message):
       global config
       if config["debug"]:
           print(message)

   # 推荐
   def log(message, debug=True):
       if debug:
           print(message)
   ```

3. **优先使用返回值而非 global**：
   ```python
   # 推荐
   def calculate(x, y):
       result = x + y
       return result

   total = calculate(10, 20)
   ```

### 相关知识点

- **变量作用域**：变量的可见范围
- **全局变量**：在模块级别定义的变量
- **局部变量**：在函数内部定义的变量
- **global 关键字**：用于在函数内修改全局变量
- **LEGB 规则**：变量查找顺序（Local → Enclosing → Global → Built-in）

### 进阶思考

**为什么默认使用局部变量？**

这是为了**封装**和**避免副作用**：

```python
# 好的设计：函数独立
def calculate_total(items):
    tax_rate = 0.1  # 局部变量
    return sum(items) * (1 + tax_rate)

# 不好的设计：依赖全局变量
tax_rate = 0.1  # 全局变量

def calculate_total(items):
    return sum(items) * (1 + tax_rate)  # 依赖外部状态
```

**好处：**
1. **可预测性**：函数的行为只由参数决定
2. **可测试性**：不需要设置全局状态
3. **可重用性**：函数可以在任何地方使用
4. **避免冲突**：不同函数的同名变量不会冲突

**何时使用全局变量？**
- 常量配置（如 `DEBUG_MODE = True`）
- 单例模式
- 缓存和优化
- 但要谨慎使用，优先考虑类和闭包

---
*本题目基于 Python 教学平台标准格式设计。*
