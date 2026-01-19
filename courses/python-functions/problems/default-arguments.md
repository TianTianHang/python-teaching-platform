---
title: "默认参数"
type: "choice"
difficulty: 2
chapter: 2
is_multiple_choice: false
options:
  A: "greet()"
  B: "greet('李四')"
  C: "greet(name='李四')"
  D: "以上都可以"
correct_answer: "D"
---
## 题目描述

有如下函数定义：
```python
def greet(name="张三"):
    print(f"你好，{name}！")
```

下列哪些调用方式是正确的？

### 题目内容

有如下函数定义：
```python
def greet(name="张三"):
    print(f"你好，{name}！")
```

下列哪些调用方式是正确的？

A. `greet()`

B. `greet('李四')`

C. `greet(name='李四')`

D. 以上都可以

### 正确答案

D

### 详细解析

**正确答案：D**

**解析：**

这个题目考察的是**默认参数**的使用。默认参数允许在调用函数时不提供某些参数，这些参数会使用预定义的默认值。

**函数分析：**

```python
def greet(name="张三"):
    print(f"你好，{name}！")
```

- `name` 是一个参数，默认值是 `"张三"`
- 调用时不提供 `name`，则使用默认值 `"张三"`
- 调用时提供 `name`，则使用提供的值

**各选项分析：**

- ✅ **A. `greet()`** - 正确
  - 不提供参数，使用默认值 `"张三"`
  - 输出：`你好，张三！`

- ✅ **B. `greet('李四')`** - 正确
  - 使用位置参数，提供值 `'李四'`
  - 输出：`你好，李四！`

- ✅ **C. `greet(name='李四')`** - 正确
  - 使用关键字参数，提供值 `'李四'`
  - 输出：`你好，李四！`

- ✅ **D. 以上都可以** - 正确
  - 所有调用方式都是合法的

**完整示例：**

```python
def greet(name="张三"):
    print(f"你好，{name}！")

# 调用方式1：使用默认值
greet()              # 你好，张三！

# 调用方式2：位置参数
greet('李四')         # 你好，李四！

# 调用方式3：关键字参数
greet(name='王五')    # 你好，王五！

# 调用方式4：关键字参数（带空格）
greet(name = '赵六')  # 你好，赵六！
```

**多个默认参数的示例：**

```python
def create_user(name, role="user", active=True):
    """创建用户"""
    return {
        "name": name,
        "role": role,
        "active": active
    }

# 只提供必需参数
user1 = create_user("张三")
# {'name': '张三', 'role': 'user', 'active': True}

# 提供部分参数
user2 = create_user("李四", role="admin")
# {'name': '李四', 'role': 'admin', 'active': True}

# 提供所有参数
user3 = create_user("王五", role="guest", active=False)
# {'name': '王五', 'role': 'guest', 'active': False}

# 使用关键字参数（顺序可以不同）
user4 = create_user("赵六", active=False, role="moderator")
# {'name': '赵六', 'role': 'moderator', 'active': False}
```

**默认参数的规则：**

1. **默认参数必须在最后**：
   ```python
   # 正确
   def func1(a, b, c=1):
       pass

   # 错误：默认参数不能在非默认参数前面
   def func2(a=1, b):
       pass
   ```

2. **默认值在函数定义时计算一次**：
   ```python
   # 危险示例：使用可变对象作为默认参数
   def bad_append(item, list=[]):  # 不要这样做！
       list.append(item)
       return list

   print(bad_append(1))  # [1]
   print(bad_append(2))  # [1, 2] - 使用了同一个列表！
   print(bad_append(3))  # [1, 2, 3]

   # 正确做法：使用 None 作为默认值
   def good_append(item, list=None):
       if list is None:
           list = []
       list.append(item)
       return list

   print(good_append(1))  # [1]
   print(good_append(2))  # [2]
   print(good_append(3))  # [3]
   ```

**实际应用示例：**

```python
# 配置函数
def connect_database(host="localhost", port=5432, database="mydb"):
    """连接数据库"""
    print(f"连接到 {host}:{port}/{database}")

connect_database()                           # localhost:5432/mydb
connect_database("192.168.1.100")            # 192.168.1.100:5432/mydb
connect_database(port=3306, database="test") # localhost:3306/test

# 格式化输出
def format_data(data, precision=2, separator=", "):
    """格式化数据"""
    formatted = separator.join(f"{x:.{precision}f}" for x in data)
    return formatted

numbers = [3.14159, 2.71828, 1.41421]
print(format_data(numbers))            # 3.14, 2.72, 1.41
print(format_data(numbers, 4, " | "))  # 3.1416 | 2.7183 | 1.4142
```

**默认参数的最佳实践：**

1. **使用不可变对象作为默认值**：
   ```python
   # 好
   def func(a, b=None):
       if b is None:
           b = []

   # 避免
   def func(a, b=[]):
       pass
   ```

2. **默认值应该是"常见"或"安全"的值**：
   ```python
   # 好：合理的默认值
   def send_email(subject, body, recipients=None):
       if recipients is None:
           recipients = []

   # 有争议：默认值可能不合适
   def delete_user(user_id, confirm=True):
       if confirm:
           # 需要确认
           pass
   ```

3. **为默认参数提供文档**：
   ```python
   def calculate(price, tax_rate=0.1, discount=0):
       """
       计算最终价格

       Args:
           price: 商品原价
           tax_rate: 税率，默认10%（0.1）
           discount: 折扣，默认无折扣（0）
       """
       return price * (1 + tax_rate) * (1 - discount)
   ```

### 相关知识点

- **默认参数**：参数有默认值，调用时可以省略
- **位置参数**：按顺序传递的参数
- **关键字参数**：使用参数名传递的参数
- **可变对象作为默认值**：需要特殊处理，避免共享状态

### 进阶思考

**为什么默认参数在定义时只计算一次？**

这是Python的设计决定，目的是提高性能：

```python
def func(default=[]):  # 这个列表只创建一次
    pass

# 每次调用时使用同一个列表对象
# 性能更好，但可能导致意外行为
```

**解决方案：使用None作为哨兵值**

```python
def func(default=None):
    if default is None:
        default = []  # 每次调用创建新列表
    # 使用 default
```

这种模式：
1. 性能开销很小（创建空列表很快）
2. 避免了共享状态的问题
3. 是Python社区的标准做法
4. 在官方文档和知名代码库中广泛使用

---
*本题目基于 Python 教学平台标准格式设计。*
