---
title: "参数与实参"
type: "choice"
difficulty: 1
chapter: 1
is_multiple_choice: false
options:
  A: "name = '李四'"
  B: "name: '李四'"
  C: "name == '李四'"
  D: "name('李四')"
correct_answer: "A"
---
## 题目描述

有如下函数定义：
```python
def greet(name):
    print(f"你好，{name}！")
```

下列哪种调用方式是正确的？

### 题目内容

有如下函数定义：
```python
def greet(name):
    print(f"你好，{name}！")
```

下列哪种调用方式是正确的？

A. `greet(name = '李四')`

B. `greet(name: '李四')`

C. `greet(name == '李四')`

D. `greet(name('李四'))`

### 正确答案

A

### 详细解析

**正确答案：A**

**解析：**

这个题目考察的是**关键字参数**的调用方式。Python支持两种参数传递方式：位置参数和关键字参数。

**参数传递方式：**

1. **位置参数**：按参数定义的顺序传递
   ```python
   greet('李四')  # 正确：'李四'会被赋值给name
   ```

2. **关键字参数**：使用 `参数名=值` 的形式
   ```python
   greet(name='李四')  # 正确：明确指定参数name的值
   ```

**各选项分析：**

- ✅ **A. `greet(name = '李四')`** - 正确
  - 这是关键字参数的正确语法
  - 使用 `参数名=值` 的形式
  - 等号两边可以有空格（虽然通常不写空格）

- ❌ **B. `greet(name: '李四')`** - 错误
  - `:` 用于类型注解或切片，不用于参数传递
  - 这不是有效的Python语法

- ❌ **C. `greet(name == '李四')`** - 错误
  - `==` 是比较运算符，会返回布尔值
  - 这相当于 `greet(True)` 或 `greet(False)`

- ❌ **D. `greet(name('李四'))`** - 错误
  - 这看起来像是函数调用
  - `name` 不是函数，无法调用

**完整示例：**
```python
def greet(name):
    print(f"你好，{name}！")

# 所有正确的调用方式
greet('李四')          # 位置参数
greet(name='李四')     # 关键字参数
greet(name = '李四')   # 关键字参数（等号两边有空格）
```

**关键字参数的优势：**

1. **代码更清晰**：
   ```python
   # 位置参数：不直观
   create_user('张三', 25, '北京')

   # 关键字参数：很清晰
   create_user(name='张三', age=25, city='北京')
   ```

2. **参数顺序灵活**：
   ```python
   def greet(first_name, last_name):
       print(f"{first_name} {last_name}")

   # 关键字参数可以改变顺序
   greet(last_name='王', first_name='小明')  # 小明 王
   ```

3. **避免参数混淆**：
   ```python
   def calculate(price, tax_rate, discount):
       return price * (1 + tax_rate) * (1 - discount)

   # 位置参数容易混淆
   calculate(100, 0.1, 0.2)

   # 关键字参数很清晰
   calculate(price=100, tax_rate=0.1, discount=0.2)
   ```

**位置参数与关键字参数混用：**
```python
def introduce(name, age, city):
    print(f"我是{name}，{age}岁，来自{city}")

# 混用时，位置参数必须在前面
introduce('张三', age=25, city='北京')  # 正确
introduce(name='张三', 25, city='北京')  # 错误！
```

### 相关知识点

- **位置参数**：按顺序传递的参数
- **关键字参数**：使用参数名传递的参数
- **参数传递**：将值传递给函数的过程
- **函数调用**：执行函数代码的方式

### 进阶思考

**什么时候应该使用关键字参数？**

1. **参数很多时**：提高代码可读性
   ```python
   def send_email(to, subject, body, cc=None, bcc=None, priority='normal'):
       pass

   # 使用关键字参数更清晰
   send_email(
       to='user@example.com',
       subject='Meeting',
       body='Let\\'s meet tomorrow',
       priority='high'
   )
   ```

2. **有默认参数时**：明确指定要修改的参数
   ```python
   def register(username, email, age=18, country='China'):
       pass

   register('zhangsan', 'zhang@example.com', country='USA')
   ```

3. **参数含义不明确时**：通过参数名说明意图
   ```python
   # 不明确
   calculate(False, True, 100)

   # 明确
   calculate(include_tax=False, apply_discount=True, price=100)
   ```

**最佳实践：**
- 定义函数时，参数不宜过多（超过5个考虑使用字典或配置对象）
- 调用函数时，对于boolean类型的参数优先使用关键字参数
- 在团队协作中，使用关键字参数可以提高代码可维护性

---
*本题目基于 Python 教学平台标准格式设计。*
