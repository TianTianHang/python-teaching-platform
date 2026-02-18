---
title: "字典"
order: 9
unlock_conditions:
  type: "prerequisite"
  prerequisites: [6]
---

## 字典

### 章节概述

字典是 Python 中另一个重要的数据结构，它使用键值对（key-value）来存储数据。字典提供了快速的查找、插入和删除操作，非常适合需要按名称访问数据的场景。

### 知识点 1：什么是字典

**描述：**
字典是 Python 中的可变映射类型，它存储键值对。字典的特点包括：
- 键是唯一的，不能重复
- 值可以是任意类型
- 键必须是不可变类型（如字符串、数字、元组等）
- 无序的（在 Python 3.7+ 中，字典保持插入顺序）

**创建字典：**
```python-exec
# 创建空字典
empty_dict = {}
print("空字典：", empty_dict)

# 创建包含键值对的字典
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5,
    "is_active": True
}
print("学生信息：", student)

# 使用 dict() 函数创建
student2 = dict(name="李四", age=21, score=90.0)
print("学生信息2：", student2)

# 从键值对列表创建
items = [("name", "王五"), ("age", 22), ("score", 88.0)]
student3 = dict(items)
print("学生信息3：", student3)
```

**访问字典元素：**
```python-exec
# 通过键访问值
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5,
    "is_active": True
}

print("姓名：", student["name"])
print("年龄：", student["age"])

# 使用 get() 方法（推荐）
print("姓名：", student.get("name"))
print("不存在的键：", student.get("address", "不存在"))  # 提供默认值
```

### 知识点 2：字典的基本操作

**描述：**
字典支持多种操作，包括添加、修改、删除键值对。

**修改元素：**
```python-exec
# 修改键值对
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5
}
print("修改前：", student)

student["score"] = 90  # 修改分数
print("修改后：", student)
```

**添加元素：**
```python-exec
# 添加新键值对
student = {
    "name": "张三",
    "age": 20
}
print("原始字典：", student)

student["score"] = 85.5  # 添加分数
print("添加分数后：", student)

student["major"] = "计算机科学"  # 添加专业
print("添加专业后：", student)

# 使用 update() 方法批量更新
student.update({"score": 90, "grade": "A"})
print("update 后：", student)
```

**删除元素：**
```python-exec
# 删除元素
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5,
    "major": "计算机科学"
}
print("原始字典：", student)

# 使用 del 删除指定键
del student["major"]
print("del major 后：", student)

# 使用 pop() 删除并返回值
score = student.pop("score")
print("pop(score) 结果：", score)
print("pop 后：", student)

# 使用 popitem() 删除最后一个键值对
item = student.popitem()
print("popitem() 结果：", item)
print("popitem() 后：", student)

# 清空字典
student.clear()
print("clear() 后：", student)
```

### 知识点 3：字典的键和值

**描述：**
字典的键和值有其特定的要求，了解这些要求有助于正确使用字典。

**键的要求：**
```python-exec
# 可以作为键的类型
valid_dict = {
    1: "数字键",           # 整数
    "name": "字符串键",    # 字符串
    (1, 2): "元组键",      # 元组（不可变）
    True: "布尔键"        # 布尔值
}
print("有效键的字典：", valid_dict)

# 列表不能作为键（列表是可变的）
try:
    invalid_dict = { [1, 2]: "错误" }
except TypeError as e:
    print("错误：", e)
```

**获取键和值：**
```python-exec
# 获取键、值、键值对
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5,
    "major": "计算机科学"
}

# 获取所有键
keys = student.keys()
print("所有键：", list(keys))

# 获取所有值
values = student.values()
print("所有值：", list(values))

# 获取所有键值对
items = student.items()
print("所有键值对：", list(items))
```

### 知识点 4：字典的遍历

**描述：**
遍历字典是常见的操作，可以遍历键、值或键值对。

**遍历键：**
```python-exec
# 遍历键
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5,
    "major": "计算机科学"
}

print("遍历键：")
for key in student:
    print(key)
```

**遍历值：**
```python-exec
# 遍历值
print("\n遍历值：")
for value in student.values():
    print(value)
```

**遍历键值对：**
```python-exec
# 遍历键值对
print("\n遍历键值对：")
for key, value in student.items():
    print(f"{key}: {value}")
```

**使用 enumerate：**
```python-exec
# 使用 enumerate
print("\n使用 enumerate：")
for index, (key, value) in enumerate(student.items()):
    print(f"{index}. {key}: {value}")
```

### 知识点 5：字典的方法

**描述：**
字典有很多内置方法，用于执行各种操作。

**常用字典方法：**
```python-exec
# 字典方法演示
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5,
    "major": "计算机科学"
}

# copy() 方法
student_copy = student.copy()
print("复制后的字典：", student_copy)

# keys() 和 values() 方法
print("\n键：", list(student.keys()))
print("值：", list(student.values()))

# items() 方法
print("\n键值对：", list(student.items()))

# get() 方法（安全访问）
print("\n使用 get()：")
print("name:", student.get("name"))
print("phone:", student.get("phone", "未提供"))

# setdefault() 方法
print("\n使用 setdefault()：")
student.setdefault("phone", "123-456-7890")
print("设置默认值后：", student)

# update() 方法
student2 = {"age": 21, "grade": "B"}
student.update(student2)
print("更新后：", student)

# pop() 和 popitem() 方法
print("\n删除操作：")
removed = student.pop("major")
print("删除的值：", removed)
print("删除后：", student)
```

### 知识点 6：字典的嵌套

**描述：**
字典可以嵌套，即字典的值可以是另一个字典，这可以表示复杂的数据结构。

**创建嵌套字典：**
```python-exec
# 嵌套字典
school = {
    "name": "第一中学",
    "classes": {
        "class1": {
            "name": "一年级一班",
            "teacher": "王老师",
            "students": ["张三", "李四", "王五"]
        },
        "class2": {
            "name": "一年级二班",
            "teacher": "李老师",
            "students": ["赵六", "钱七", "孙八"]
        }
    }
}

print("学校信息：", school)
print("\n一年级一班：", school["classes"]["class1"])
```

**访问嵌套字典：**
```python-exec
# 安全访问嵌套字典
def safe_get(d, keys, default=None):
    """安全获取嵌套字典的值"""
    for key in keys:
        if key in d:
            d = d[key]
        else:
            return default
    return d

print("\n使用安全访问：")
print("一年级一班的学生：", safe_get(school, ["classes", "class1", "students"]))
print("不存在的信息：", safe_get(school, ["classes", "class3"], "不存在"))
```

### 知识点 7：字典推导式

**描述：**
字典推导式类似于列表推导式，可以快速创建字典。

**基本用法：**
```python-exec
# 创建平方字典
numbers = [1, 2, 3, 4, 5]
squares = {x: x ** 2 for x in numbers}
print("平方字典：", squares)

# 带条件的字典推导式
even_squares = {x: x ** 2 for x in numbers if x % 2 == 0}
print("偶数平方字典：", even_squares)

# 字符串处理
words = ["apple", "banana", "orange"]
word_lengths = {word: len(word) for word in words}
print("单词长度字典：", word_lengths)
```

**从两个列表创建字典：**
```python-exec
# 使用 zip 合并两个列表
keys = ["name", "age", "score"]
values = ["张三", 20, 85.5]

student_dict = dict(zip(keys, values))
print("学生字典：", student_dict)

# 使用字典推导式
student_dict2 = {k: v for k, v in zip(keys, values)}
print("学生字典2：", student_dict2)
```

### 知识点 8：字典与列表的转换

**描述：**
字典和列表可以相互转换，这在处理数据时很有用。

**字典转列表：**
```python-exec
# 字典转列表
student = {
    "name": "张三",
    "age": 20,
    "score": 85.5
}

# 获取键列表
keys = list(student.keys())
print("键列表：", keys)

# 获取值列表
values = list(student.values())
print("值列表：", values)

# 获取键值对列表
items = list(student.items())
print("键值对列表：", items)

# 从键值对列表创建新字典
new_dict = dict(items)
print("新字典：", new_dict)
```

### 知识点 9：字典的常见用法

**描述：**
字典在实际编程中有多种常见用法，掌握这些用法能提高编程效率。

**用法 1：作为配置字典**
```python-exec
# 配置字典
config = {
    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "password"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8080
    }
}

print("数据库配置：", config["database"])
```

**用法 2：作为计数器**
```python-exec
# 使用字典计数
text = "hello world hello python"
word_count = {}

for word in text.split():
    word_count[word] = word_count.get(word, 0) + 1

print("词频统计：", word_count)
```

**用法 3：缓存字典**
```python-exec
# 简单的缓存实现
cache = {}

def expensive_operation(x):
    """模拟耗时操作"""
    print(f"计算 {x} 的平方...")
    return x * x

def get_square(x):
    if x not in cache:
        cache[x] = expensive_operation(x)
    return cache[x]

print("第一次调用：", get_square(5))
print("第二次调用（使用缓存）：", get_square(5))
print("缓存内容：", cache)
```

**用法 4：关联数据**
```python-exec
# 关联学生和成绩
students = ["张三", "李四", "王五"]
scores = [85, 90, 78]

student_scores = {}
for student, score in zip(students, scores):
    student_scores[student] = score

print("学生成绩：", student_scores)

# 查询成绩
print("张三的成绩：", student_scores.get("张三", "未找到"))
print("赵六的成绩：", student_scores.get("赵六", "未找到"))
```

### 章节总结

本章我们学习了：
- 字典的概念和特点
- 字典的创建和基本操作
- 键和值的要求
- 字典的多种遍历方式
- 字典的内置方法
- 字典的嵌套和复杂数据结构
- 字典推导式的使用
- 字典与列表的转换
- 字典的常见应用场景

### 下一步

掌握了字典后，让我们在最后一章学习函数基础，这是编程中的重要概念，能帮助我们实现代码的模块化和复用。

---
*本章内容基于 Python 教学平台标准格式设计。*
