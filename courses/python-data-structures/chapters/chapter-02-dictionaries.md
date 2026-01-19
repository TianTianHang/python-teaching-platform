---
title: "字典"
order: 2
---
## 字典

### 章节概述

字典是Python中的另一个核心数据结构，它存储键值对（key-value pairs）的映射关系。字典提供了一种高效的数据查找方式，可以在常数时间内找到对应的值。本章将详细介绍字典的创建、访问、修改和常用方法。

### 知识点 1：字典的创建与访问

**描述：**

字典是Python中的可变映射类型，使用大括号`{}`创建，键值对之间用逗号分隔，键和值之间用冒号`:`分隔。字典中的键必须是不可变类型（如字符串、数字、元组），值可以是任意类型。

**示例代码：**
```python
# 创建字典
# 空字典
empty_dict = {}

# 字面量方式创建
student = {
    "name": "小明",
    "age": 18,
    "grade": "高三",
    "scores": {"math": 95, "english": 88}
}

# 使用dict()函数创建
person = dict(name="张三", age=25, city="北京")

# 创建嵌套字典
school = {
    "name": "第一中学",
    "departments": {
        "math": {"teacher": "王老师", "students": 40},
        "english": {"teacher": "李老师", "students": 38}
    }
}

# 访问字典值
print(student["name"])      # 小明
print(student["age"])       # 18
print(student["scores"]["math"])  # 95

# 使用get方法（更安全）
print(student.get("name"))      # 小明
print(student.get("gender"))    # None（键不存在时返回None）
print(student.get("gender", "未知"))  # 未知（可以指定默认值）

# 检查键是否存在
print("name" in student)       # True
print("gender" in student)     # False

# 访嵌套字典
print(school["departments"]["math"]["teacher"])  # 王老师

# 获取所有键、值、键值对
print(student.keys())      # dict_keys(['name', 'age', 'grade', 'scores'])
print(student.values())    # dict_values(['小明', 18, '高三', {...}])
print(student.items())     # dict_items([('name', '小明'), ('age', 18), ...])

# 实际应用：用户信息字典
user = {
    "user_id": 1001,
    "username": "python_lover",
    "email": "user@example.com",
    "is_active": True,
    "last_login": "2024-01-15 10:30:00",
    "roles": ["student", "editor"]
}

# 访问用户信息
print(f"用户名：{user['username']}")
print(f"邮箱：{user['email']}")
print(f"角色：{', '.join(user['roles'])}")

# 检查用户状态
if user["is_active"]:
    print("用户处于活跃状态")
else:
    print("用户已禁用")
```

**解释：**

**字典的特点：**
- **键值对存储**：每个键对应一个值，形成映射关系
- **键必须是唯一的**：重复的键会被覆盖
- **键必须是不可变的**：字符串、数字、元组等可以作为键
- **值可以是任意类型**：包括列表、字典等可变类型
- **无序**（在Python 3.7+中保持插入顺序）

**访问字典的方法：**
1. **直接访问**：`dict[key]`
   - 优点：语法简洁
   - 缺点：键不存在时会抛出`KeyError`

2. **get方法**：`dict.get(key, default=None)`
   - 优点：键不存在时返回默认值
   - 缺点：语法稍长

**字典的键：**
- 必须是哈希的（hashable）
- 不可变类型：字符串、数字、元组
- 不可变类型：列表、字典、集合等不可作为键

**字典的值：**
- 可以是任意类型
- 可以是可变类型（如列表、字典）

**字典的遍历：**
```python
# 遍历键
for key in student:
    print(key)

# 遍历值
for value in student.values():
    print(value)

# 遍历键值对
for key, value in student.items():
    print(f"{key}: {value}")
```

---

### 知识点 2：字典的常用方法

**描述：**

Python字典提供了丰富的方法，用于添加、删除、修改字典元素，以及进行各种查询和操作。掌握这些方法是高效使用字典的关键。

**示例代码：**
```python
# 创建一个字典
person = {"name": "张三", "age": 25, "city": "北京"}

# 添加和修改元素
person["gender"] = "男"        # 添加新键值对
print(person)                 # {'name': '张三', 'age': 25, 'city': '北京', 'gender': '男'}

person["age"] = 26            # 修改已存在的值
print(person)                 # {'name': '张三', 'age': 26, 'city': '北京', 'gender': '男'}

# 更新字典（合并字典）
new_info = {"city": "上海", "email": "zhangsan@example.com"}
person.update(new_info)
print(person)                 # 城市被更新，邮箱被添加
# {'name': '张三', 'age': 26, 'city': '上海', 'gender': '男', 'email': 'zhangsan@example.com'}

# 删除元素
removed_email = person.pop("email")  # 删除并返回值
print(f"删除的邮箱：{removed_email}")  # 删除的邮箱：zhangsan@example.com
print(person)                       # email已被删除

removed_age = person.pop("age", 0)   # 如果键不存在，返回默认值0
print(removed_age)                  # 26

del person["city"]                  # 直接删除键值对
print(person)                       # city已被删除

# 清空字典
backup = person.copy()  # 创建备份
person.clear()
print(f"清空后的字典：{person}")  # 清空后的字典：{}
print(f"备份：{backup}")

# 字典查询方法
student_scores = {
    "张三": {"math": 95, "english": 88},
    "李四": {"math": 87, "english": 92},
    "王五": {"math": 92, "english": 85}
}

# 获取学生列表
students = list(student_scores.keys())
print(f"所有学生：{students}")  # ['张三', '李四', '王五']

# 获取所有成绩
scores = student_scores.values()
print(f"所有学生成绩：{scores}")

# 获取张三的数学成绩
math_score = student_scores["张三"]["math"]
print(f"张三的数学成绩：{math_score}")

# 使用setdefault（如果有键则获取，没有则设置并返回）
grade = student_scores.setdefault("李四", {"math": 0, "english": 0})["math"]
print(f"李四的数学成绩：{grade}")  # 87

# 实际应用：商品库存管理
inventory = {
    "商品A": {"price": 99.9, "stock": 100, "category": "electronics"},
    "商品B": {"price": 49.9, "stock": 200, "category": "clothing"},
    "商品C": {"price": 29.9, "stock": 150, "category": "books"}
}

# 添加新商品
inventory["商品D"] = {"price": 79.9, "stock": 50, "category": "electronics"}

# 更新商品价格
inventory["商品A"]["price"] = 89.9
inventory["商品B"]["stock"] -= 10  # 减少库存

# 查询库存
for product, info in inventory.items():
    print(f"{product}: 价格{info['price']}，库存{info['stock']}，类别{info['category']}")

# 统计各类商品数量
categories = {}
for product in inventory.values():
    category = product["category"]
    categories[category] = categories.get(category, 0) + 1

print(f"\n商品分类统计：{categories}")
```

**解释：**

**字典常用方法分类：**

1. **添加和修改**：
   - `dict[key] = value`：直接赋值
   - `dict.update(dict2)`：用另一个字典更新
   - `dict.setdefault(key, default)`：获取值，如果不存在则设置默认值

2. **删除元素**：
   - `dict.pop(key, default)`：删除并返回值
   - `del dict[key]`：直接删除
   - `dict.clear()`：清空字典

3. **查询方法**：
   - `dict.get(key, default)`：安全获取值
   - `dict.keys()`：获取所有键
   - `dict.values()`：获取所有值
   - `dict.items()`：获取所有键值对

4. **其他方法**：
   - `dict.copy()`：创建副本
   - `dict.__len__()`：`len(dict)`获取键的数量

**使用场景：**
- **添加元素**：直接赋值或使用`update()`
- **删除元素**：使用`pop()`（需要返回值）或`del`（不需要返回值）
- **修改元素**：直接赋值
- **查询元素**：使用`get()`更安全

**字典操作的性能：**
- **访问**：O(1) - 哈希查找，非常快
- **添加/删除**：O(1) - 平均情况
- **更新**：O(1)
- **查找键是否存在**：`key in dict` 也是 O(1)

**字典推导式：**
```python
# 创建字典
squares = {x: x*x for x in range(1, 6)}
print(squares)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# 过滤字典
scores = {"张三": 95, "李四": 87, "王五": 92, "赵六": 78}
passing_scores = {k: v for k, v in scores.items() if v >= 90}
print(passing_scores)  # {'张三': 95, '王五': 92}
```

**字典和列表的选择：**
```python
# 使用字典：查找速度快
student_records = {
    1001: {"name": "张三", "score": 95},
    1002: {"name": "李四", "score": 87},
    1003: {"name": "王五", "score": 92}
}
# 查找O(1)
score = student_records[1001]["score"]

# 使用列表：顺序存储，查找慢
student_records = [
    {"id": 1001, "name": "张三", "score": 95},
    {"id": 1002, "name": "李四", "score": 87},
    {"id": 1003, "name": "王五", "score": 92}
]
# 查找O(n)
record = next(r for r in student_records if r["id"] == 1001)
```

---

### 知识点 3：字典的遍历

**描述：**

字典遍历是字典操作中最常用的功能之一。Python提供了多种遍历字典的方式，可以遍历键、值或键值对。掌握这些遍历方法可以帮助你高效处理字典数据。

**示例代码：**
```python
# 创建一个字典
student_scores = {
    "张三": {"math": 95, "english": 88, "total": 183},
    "李四": {"math": 87, "english": 92, "total": 179},
    "王五": {"math": 92, "english": 85, "total": 177},
    "赵六": {"math": 78, "english": 95, "total": 173}
}

# 遍历键（学生姓名）
print("=== 遍历学生姓名 ===")
for name in student_scores:
    print(name)
# 或者
for name in student_scores.keys():
    print(name)

# 遍历值（成绩信息）
print("\n=== 遍历成绩信息 ===")
for scores in student_scores.values():
    print(scores)

# 遍历键值对
print("\n=== 遍历键值对 ===")
for name, scores in student_scores.items():
    print(f"{name}: 数学={scores['math']}, 英语={scores['english']}, 总分={scores['total']}")

# 带索引的遍历
print("\n=== 带索引的遍历 ===")
for index, (name, scores) in enumerate(student_scores.items(), 1):
    print(f"{index}. {name}: {scores}")

# 条件遍历
print("\n=== 条件遍历（数学成绩超过90分） ===")
for name, scores in student_scores.items():
    if scores["math"] >= 90:
        print(f"{name}: 数学={scores['math']}")

# 按值排序遍历
print("\n=== 按总分排序遍历 ===")
# 使用sorted函数按总分排序
sorted_students = sorted(student_scores.items(),
                        key=lambda x: x[1]["total"],
                        reverse=True)

for name, scores in sorted_students:
    print(f"{name}: 总分={scores['total']}（排名={sorted_students.index((name, scores)) + 1}）")

# 嵌套字典的遍历
print("\n=== 嵌套字典的遍历 ===")
for name, scores in student_scores.items():
    print(f"学生：{name}")
    for subject, score in scores.items():
        print(f"  {subject}: {score}")
    print()

# 实际应用：统计成绩
print("\n=== 成绩统计分析 ===")

# 计算各科平均分
math_scores = [scores["math"] for scores in student_scores.values()]
english_scores = [scores["english"] for scores in student_scores.values()]

print(f"数学平均分：{sum(math_scores)/len(math_scores):.1f}")
print(f"英语平均分：{sum(english_scores)/len(english_scores):.1f}")

# 找出最高分和最低分
highest_math = max(math_scores)
lowest_math = min(math_scores)

math_top_students = [name for name, scores in student_scores.items()
                     if scores["math"] == highest_math]

print(f"最高数学成绩：{highest_math}（学生：{', '.join(math_top_students)}）")
print(f"最低数学成绩：{lowest_math}")

# 统计成绩分布
print("\n=== 成绩分布统计 ===")
grade_ranges = {
    "优秀（90-100）": 0,
    "良好（80-89）": 0,
    "中等（70-79）": 0,
    "不及格（<70）": 0
}

for scores in student_scores.values():
    for score in scores.values():
        if isinstance(score, int):  # 跳过总分，只统计单科
            if score >= 90:
                grade_ranges["优秀（90-100）"] += 1
            elif score >= 80:
                grade_ranges["良好（80-89）"] += 1
            elif score >= 70:
                grade_ranges["中等（70-79）"] += 1
            else:
                grade_ranges["不及格（<70）"] += 1

for grade, count in grade_ranges.items():
    print(f"{grade}: {count}人次")

# 使用字典推导式进行复杂查询
print("\n=== 复杂查询示例 ===")
# 找出总分超过180的学生
top_students = {name: scores for name, scores in student_scores.items()
                if scores["total"] > 180}
print("总分超过180的学生：")
for name, scores in top_students.items():
    print(f"  {name}: {scores['total']}分")
```

**解释：**

**字典遍历的几种方式：**

1. **遍历键**：
   ```python
   for key in dict:
   for key in dict.keys():
   ```
   - 直接遍历字典默认遍历键
   - `keys()`显式获取所有键

2. **遍历值**：
   ```python
   for value in dict.values():
   ```
   - 直接遍历字典的所有值
   - 适合只需要值，不需要键的情况

3. **遍历键值对**：
   ```python
   for key, value in dict.items():
   ```
   - 最常用的方式，同时获取键和值
   - 适合需要同时操作键值的情况

**遍历的进阶技巧：**

1. **带索引的遍历**：
   ```python
   for index, (key, value) in enumerate(dict.items(), 1):
   ```

2. **排序遍历**：
   ```python
   # 按值排序
   sorted_items = sorted(dict.items(), key=lambda x: x[1], reverse=True)
   for key, value in sorted_items:
   ```

3. **条件遍历**：
   ```python
   # 使用列表推导式
   [key for key, value in dict.items() if condition]

   # 使用生成器表达式
   (key for key, value in dict.items() if condition)
   ```

**遍历的性能考虑：**
- `dict.items()`是最快的遍历方式
- `for key in dict`比`for key in dict.keys()`快一点
- 遍历字典的时间复杂度是O(n)

**实际应用技巧：**

1. **字典统计**：
```python
# 统计词频
text = "apple banana apple orange banana apple"
word_counts = {}
for word in text.split():
    word_counts[word] = word_counts.get(word, 0) + 1
```

2. **字典分组**：
```python
# 按类别分组
products = [
    {"name": "A", "category": "水果", "price": 10},
    {"name": "B", "category": "蔬菜", "price": 5},
    {"name": "C", "category": "水果", "price": 8}
]
category_groups = {}
for product in products:
    category = product["category"]
    category_groups.setdefault(category, []).append(product)
```

3. **字典过滤**：
```python
# 过滤符合条件的项
filtered = {k: v for k, v in dict.items() if condition}
```

**字典遍历的常见错误：**
```python
# 错误：在遍历时修改字典
for key in dict:
    if condition:
        dict[key] = new_value  # 可能导致问题
    elif condition2:
        dict.pop(key)          # 会改变遍历结构

# 正确的做法：创建新字典或先收集要删除的键
keys_to_remove = [key for key in dict if condition]
for key in keys_to_remove:
    dict.pop(key)
```

---
*本章内容基于 Python 教学平台标准格式设计。*
