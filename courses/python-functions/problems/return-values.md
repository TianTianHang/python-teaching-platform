---
title: "返回值"
type: "choice"
difficulty: 1
chapter: 1
is_multiple_choice: false
options:
  A: "无"
  B: "None"
  C: "0"
  D: "空字符串"
correct_answer: "B"
---
## 题目描述

执行以下代码，`result` 的值是什么？

```python
def my_function():
    print("Hello")

result = my_function()
```

### 题目内容

执行以下代码，`result` 的值是什么？

```python
def my_function():
    print("Hello")

result = my_function()
```

A. 无

B. None

C. 0

D. 空字符串

### 正确答案

B

### 详细解析

**正确答案：B**

**解析：**

这个题目考察的是**函数返回值**的概念。在Python中，如果函数没有使用 `return` 语句返回值，或者只写了 `return` 而没有指定返回值，函数会返回 `None`。

**执行过程分析：**

```python
def my_function():
    print("Hello")  # 执行打印操作
    # 没有 return 语句

result = my_function()
# 1. 函数被调用
# 2. 执行 print("Hello")，输出 "Hello"
# 3. 函数结束，没有遇到 return 语句
# 4. 自动返回 None
# 5. result 被赋值为 None

print(result)  # None
print(type(result))  # <class 'NoneType'>
```

**各选项分析：**

- ❌ **A. 无** - 错误
  - 函数调用一定会返回一个值
  - Python中不存在"无返回值"的情况
  - 即使没有 return，也会返回 None

- ✅ **B. None** - 正确
  - `None` 是Python中的一个特殊值
  - 表示"没有值"或"空值"
  - 是 NoneType 类型的唯一实例

- ❌ **C. 0** - 错误
  - 0 是一个整数
  - 不是函数的默认返回值
  - 如果要返回0，必须明确写出 `return 0`

- ❌ **D. 空字符串** - 错误
  - 空字符串 `""` 是一个有效的字符串对象
  - 不是函数的默认返回值
  - 如果要返回空字符串，必须明确写出 `return ""`

**return 语句的各种情况：**

```python
# 情况1：没有 return 语句
def func1():
    print("Hello")

result = func1()  # result = None

# 情况2：只有 return，没有返回值
def func2():
    print("Hello")
    return

result = func2()  # result = None

# 情况3：return None
def func3():
    print("Hello")
    return None

result = func3()  # result = None

# 情况4：return 一个值
def func4():
    print("Hello")
    return 100

result = func4()  # result = 100

# 情况5：return 多个值（实际是元组）
def func5():
    return 1, 2, 3

result = func5()  # result = (1, 2, 3)
```

**print vs return 的区别：**

```python
# print：在控制台显示内容，不返回值（返回None）
def print_function():
    print("Hello")

print_function()  # 输出：Hello
result = print_function()  # 输出：Hello
print(result)  # 输出：None

# return：从函数返回一个值
def return_function():
    return "Hello"

return_function()  # 不输出任何内容
result = return_function()
print(result)  # 输出：Hello
```

**实际应用示例：**

```python
# 错误示例：混淆print和return
def add_wrong(a, b):
    print(a + b)  # 只打印，不返回

result = add_wrong(3, 5)  # 输出：8
print(result * 2)  # 报错！NoneType * 2 不支持

# 正确示例：使用return
def add_correct(a, b):
    return a + b  # 返回结果

result = add_correct(3, 5)
print(result * 2)  # 输出：16
```

**函数可以返回多个值：**

```python
def calculate(numbers):
    """计算多个统计值"""
    total = sum(numbers)
    average = total / len(numbers)
    maximum = max(numbers)
    minimum = min(numbers)
    return total, average, maximum, minimum

# 返回的是一个元组
result = calculate([1, 2, 3, 4, 5])
print(result)  # (15, 3.0, 5, 1)

# 可以解包到多个变量
total, avg, max_val, min_val = calculate([1, 2, 3, 4, 5])
print(f"总和: {total}, 平均: {avg}")
```

### 相关知识点

- **return 语句**：用于从函数返回值
- **None 类型**：表示空值或没有值
- **函数调用**：执行函数并获得返回值
- **元组解包**：将返回的多个值赋给多个变量

### 进阶思考

**为什么Python设计为函数必须返回值？**

Python的函数设计哲学是"一切皆表达式"，每个函数调用都会产生一个返回值。这样做的好处：

1. **一致性**：所有函数调用都有返回值，行为统一
2. **链式调用**：可以将函数作为另一个函数的参数
   ```python
   print(len("hello"))  # 5
   ```
3. **函数式编程**：支持高阶函数和函数组合
   ```python
   result = list(map(str, [1, 2, 3]))  # ['1', '2', '3']
   ```

**返回值的设计原则：**
- 函数应该做一件事并返回结果
- 如果函数修改了传入的可变对象，可以不返回
- 如果函数计算了新值，必须返回
- None 表示"没有有意义的返回值"

---
*本题目基于 Python 教学平台标准格式设计。*
