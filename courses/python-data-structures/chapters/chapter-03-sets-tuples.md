---
title: "集合与元组"
order: 3
---
## 集合与元组

### 章节概述

Python除了列表和字典外，还提供了两种重要的数据结构：集合和元组。集合是一个无序的、可变的、不重复的元素集合；元组是一个有序的、不可变的序列。本章将详细介绍这两种数据结构的特点和用法。

### 知识点 1：元组的创建与使用

**描述：**

元组（tuple）是Python中的基本数据结构之一，它是一个有序的、不可变的序列。元组使用小括号`()`创建，元素之间用逗号分隔。虽然看起来和列表很像，但元组一旦创建就不能修改。

**示例代码：**
```python
# 创建元组
# 空元组
empty_tuple = ()

# 单个元素的元组（注意逗号）
single_element = (42,)

# 多个元素的元组
coordinates = (3, 4, 5)
colors = ("红色", "绿色", "蓝色")

# 不用括号的元组
points = 1, 2, 3, 4  # 也是元组

# 创建元组的多种方式
tuple_from_list = tuple([1, 2, 3])
tuple_from_string = tuple("hello")
tuple_from_range = tuple(range(5))

print(f"坐标：{coordinates}")
print(f"颜色：{colors}")
print(f"点：{points}")
print(f"从列表创建：{tuple_from_list}")
print(f"从字符串创建：{tuple_from_string}")
print(f"从range创建：{tuple_from_range}")

# 元组的索引和切片
print(f"第一个颜色：{colors[0]}")
print(f"最后一个颜色：{colors[-1]}")
print(f"前两个颜色：{colors[:2]}")

# 元组的长度和成员检查
print(f"元组长度：{len(colors)}")
print(f"'绿色'在元组中：{'绿色' in colors}")

# 元组的基本特性
print(f"坐标是元组：{isinstance(coordinates, tuple)}")
print(f"坐标不可变：{not hasattr(coordinates, 'append')}")

# 元组不可变性（关键特性）
try:
    colors[0] = "黄色"  # 尝试修改元组
except TypeError as e:
    print(f"错误：{e}")

# 元组可以包含可变元素
nested_tuple = (1, [2, 3, 4])
print(f"嵌套元组：{nested_tuple}")

# 虽然元组不可变，但它的可变元素可以修改
nested_tuple[1].append(5)
print(f"修改后的嵌套元组：{nested_tuple}")

# 元组的解包（unpacking）
x, y, z = coordinates
print(f"x={x}, y={y}, z={z}")

# 交换变量的值（元组解包的应用）
a, b = 10, 20
print(f"交换前：a={a}, b={b}")
a, b = b, a
print(f"交换后：a={a}, b={b}")

# 实际应用：函数返回多个值
def calculate_statistics(numbers):
    """计算统计信息"""
    total = sum(numbers)
    average = total / len(numbers)
    maximum = max(numbers)
    minimum = min(numbers)
    return total, average, maximum, minimum  # 返回一个元组

stats = calculate_statistics([1, 2, 3, 4, 5])
print(f"总和：{stats[0]}, 平均值：{stats[1]:.1f}, 最大值：{stats[2]}, 最小值：{stats[3]}")

# 使用变量接收返回值
total, average, max_val, min_val = stats
print(f"直接接收：总和={total}, 平均值={average:.1f}")

# 元组的方法（元组是有限的，因为它是不可变的）
t = (1, 2, 2, 3, 2, 4)
print(f"元组t：{t}")
print(f"2出现的次数：{t.count(2)}")      # 3
print(f"2的索引：{t.index(2)}")          # 1（第一个匹配的）
print(f"3的索引：{t.index(3)}")          # 3
```

**解释：**

**元组的特点：**
- **有序**：元素按顺序排列，有索引
- **不可变**：创建后不能修改、添加或删除元素
- **可包含任意类型**：数字、字符串、列表、其他元组等
- **语法灵活**：小括号可以省略（单个元素除外）

**元组的创建方式：**
1. 直接使用`()`：`(1, 2, 3)`
2. 不使用括号：`1, 2, 3`
3. 使用`tuple()`函数：
   - `tuple([1, 2, 3])`：从列表创建
   - `tuple("hello")`：从字符串创建
   - `tuple(range(5))`：从range创建

**元组的不可变性：**
- 元组本身的元素不能修改
- 如果元组包含可变对象（如列表），对象的内容可以修改
- 修改对象本身会报错，但修改对象的属性是允许的

**元组的使用场景：**
1. **函数返回多个值**：函数返回的是一个元组
2. **常量数据**：不需要修改的数据
3. **字典的键**：元组可以作为字典的键（因为不可变）
4. **序列打包和解包**：方便的多变量赋值

**元组解包（Unpacking）：**
```python
# 基本解包
a, b, c = (1, 2, 3)

# 交换变量
a, b = b, a

# 解包可变长度
first, *rest = [1, 2, 3, 4, 5]  # first=1, rest=[2, 3, 4, 5]

# 使用下划线忽略不需要的值
x, y, _ = (10, 20, 30)  # 只使用x和y，忽略30
```

---

### 知识点 2：集合的创建与操作

**描述：**

集合（set）是Python中的无序、可变、不重复的元素集合。集合使用大括号`{}`创建或使用`set()`函数创建。集合主要用于去重和成员测试。

**示例代码：**
```python
# 创建集合
# 使用大括号
fruits = {"苹果", "香蕉", "橙子", "苹果"}  # 注意重复的"苹果"会被去重
print(f"集合：{fruits}")

# 使用set()函数
numbers = set([1, 2, 2, 3, 4, 4, 5])
print(f"数字集合：{numbers}")

# 从字符串创建
char_set = set("hello world")
print(f"字符集合：{char_set}")

# 空集合
empty_set = set()  # 注意：{}创建的是空字典，不是空集合

# 集合的基本操作
print(f"集合长度：{len(fruits)}")
print(f"'苹果'在集合中：{'苹果' in fruits}")
print(f"'西瓜'在集合中：{'西瓜' in fruits}")

# 添加元素
fruits.add("葡萄")
print(f"添加葡萄：{fruits}")

# 移除元素
fruits.remove("香蕉")  # 如果元素不存在会抛出KeyError
print(f"移除香蕉：{fruits}")

fruits.discard("西瓜")  # 如果元素不存在不会报错
print(f"尝试移除西瓜：{fruits}")

# 随机移除并返回一个元素
removed = fruits.pop()
print(f"随机移除：{removed}")
print(f"剩余：{fruits}")

# 清空集合
# fruits.clear()
print(f"清空后的集合：{fruits}")

# 集合的数学运算
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}

# 并集（union）
union = A | B  # 或 A.union(B)
print(f"A ∪ B = {union}")

# 交集（intersection）
intersection = A & B  # 或 A.intersection(B)
print(f"A ∩ B = {intersection}")

# 差集（difference）
difference = A - B  # 或 A.difference(B)
print(f"A - B = {difference}")

# 对称差集（symmetric difference）
symmetric_diff = A ^ B  # 或 A.symmetric_difference(B)
print(f"A Δ B = {symmetric_diff}")

# 子集和超集
small_set = {1, 2}
print(f"{small_set}是A的子集：{small_set.issubset(A)}")
print(f"A是{small_set}的超集：{A.issuperset(small_set)}")

# 不相交集合
disjoint = {1, 2, 3} & {4, 5, 6}
print(f"是否不相交：{len(disjoint) == 0}")

# 实际应用：去重
numbers = [1, 2, 2, 3, 4, 4, 5, 5, 5]
unique_numbers = list(set(numbers))
print(f"原始列表：{numbers}")
print(f"去重后：{unique_numbers}")

# 实际应用：查找共同好友
user1_friends = {"张三", "李四", "王五", "赵六"}
user2_friends = {"李四", "王五", "钱七", "孙八"}

# 共同好友
common_friends = user1_friends & user2_friends
print(f"共同好友：{common_friends}")

# 只有一个好友的好友
only_in_user1 = user1_friends - user2_friends
only_in_user2 = user2_friends - user1_friends
print(f"只有用户1的好友：{only_in_user1}")
print(f"只有用户2的好友：{only_in_user2}")

# 全部好友（并集）
all_friends = user1_friends.union(user2_friends)
print(f"所有好友：{all_friends}")

# 实际应用：过滤有效数据
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
valid_numbers = {x for x in data if x % 2 == 0}  # 集合推导式
print(f"偶数集合：{valid_numbers}")
```

**解释：**

**集合的特点：**
- **无序**：元素没有固定的顺序
- **可变**：可以添加、删除元素
- **不重复**：自动去除重复元素
- **元素必须是可哈希的**：必须是不可变类型（不能是列表、字典）

**集合的创建方式：**
1. 使用大括号：`{1, 2, 3}`
2. 使用`set()`函数：
   - `set([1, 2, 3])`：从列表创建
   - `set("hello")`：从字符串创建
   - `set()`：创建空集合

**集合的数学运算：**

| 运算 | 符号 | 方法 | 说明 |
|------|------|------|------|
| 并集 | `A | B` | `A.union(B)` | 所有元素的集合 |
| 交集 | `A & B` | `A.intersection(B)` | 共同元素的集合 |
| 差集 | `A - B` | `A.difference(B)` | A中但不在B中的元素 |
| 对称差集 | `A ^ B` | `A.symmetric_difference(B)` | 只在A或只在B中的元素 |

**集合的方法：**

| 方法 | 说明 |
|------|------|
| `add(element)` | 添加元素 |
| `remove(element)` | 移除元素（不存在时报错） |
| `discard(element)` | 移除元素（不存在时不报错） |
| `pop()` | 随机移除并返回元素 |
| `clear()` | 清空集合 |
| `union(set)` | 并集 |
| `intersection(set)` | 交集 |
| `difference(set)` | 差集 |
| `copy()` | 复制集合 |

**集合与列表的区别：**

| 特性 | 列表 | 集合 |
|------|------|------|
| 是否有序 | 有序 | 无序 |
| 是否可变 | 可变 | 可变 |
| 是否允许重复 | 允许 | 不允许 |
| 元素类型 | 任意 | 必须可哈希 |
| 查找速度 | O(n) | O(1) |

---

### 知识点 3：集合的运算

**描述：**

集合运算是集合最强大的功能之一，包括数学运算（并、交、差、对称差）和逻辑运算。这些运算是基于集合的数学理论实现的，非常适合处理数据去重、查找交集等场景。

**示例代码：**
```python
# 创建几个测试集合
students_class_a = {"张三", "李四", "王五", "赵六", "钱七"}
students_class_b = {"王五", "赵六", "孙八", "周九", "吴十"}
students_class_c = {"张三", "李四", "孙八", "郑十一"}

# 基本集合运算
print("=== 基本集合运算 ===")
print(f"班级A：{students_class_a}")
print(f"班级B：{students_class_b}")
print(f"班级C：{students_class_c}")

# 并集（Union）- 所有学生
all_students = students_class_a | students_class_b | students_class_c
print(f"\n所有学生（A∪B∪C）：{all_students}")

# 交集（Intersection）- 同时在多个班级的学生
ab_common = students_class_a & students_class_b  # A和B的交集
abc_common = students_class_a & students_class_b & students_class_c  # 三个班级的交集
print(f"\n同时上A和B课的学生：{ab_common}")
print(f"同时上A、B、C三节课的学生：{abc_common}")

# 差集（Difference）
only_a = students_class_a - students_class_b  # 只上A课的学生
b_only = students_class_b - students_class_a  # 只上B课的学生
print(f"\n只上A课的学生：{only_a}")
print(f"只上B课的学生：{b_only}")

# 对称差集（Symmetric Difference）- 只在一个班级的学生
only_one_class = students_class_a ^ students_class_b
print(f"\n只上A或B课的学生：{only_one_class}")

# 混合运算示例
print("\n=== 混合运算示例 ===")
# 只在A班或B班，但不在C班的学生
result = (students_class_a ^ students_class_b) - students_class_c
print(f"只在A或B班，不在C班的学生：{result}")

# 在A班但不在B班，或B班但不在A班的学生
same_result = (students_class_a - students_class_b) | (students_class_b - students_class_a)
print(f"A班独有或B班独有：{same_result}")

# 实际应用：选修课分析
选修_math = {"张三", "李四", "王五", "赵六"}
选修_english = {"王五", "赵六", "孙八", "周九"}
选修_physics = {"张三", "孙八", "郑十一", "钱七"}

print("\n=== 选修课分析 ===")
# 选了至少一门课的学生
all_course_students =选修_math |选修_english |选修_physics
print(f"选课总人数：{len(all_course_students)}")

# 同时选了math和english的学生
math_english =选修_math &选修_english
print(f"同时选math和english的学生：{math_english}")

# 只选了math的学生
only_math =选修_math -选修_english -选修_physics
print(f"只选math的学生：{only_math}")

# 选了math但没有选english的学生
math_without_english =选修_math -选修_english
print(f"选math但没选english的学生：{math_without_english}")

# 选了至少两门课的学生
two_or_more_courses = (选修_math &选修_english) | (选修_math &选修_physics) | (选修_english &选修_physics)
print(f"选了至少两门课的学生：{two_or_more_courses}")

# 实际应用：数据分析
print("\n=== 数据分析 ===")
# 产品类别
categories = {
    "电子产品": {"手机", "电脑", "平板", "耳机"},
    "服装": {"衬衫", "裤子", "裙子", "鞋子"},
    "食品": {"水果", "蔬菜", "肉类", "零食"}
}

# 用户购买记录
purchases = {
    "用户1": {"手机", "衬衫", "水果"},
    "用户2": {"电脑", "裤子", "蔬菜"},
    "用户3": {"平板", "手机", "水果", "零食"}
}

# 查购买了电子产品的用户
electronics_buyers = {"用户1", "用户3"}

# 购买了食品但没购买电子产品的用户
food_without_electronics = purchases.keys() - {"用户1", "用户3"}

# 购买了服装的用户
clothing_buyers = {"用户1", "用户2"}

# 验证运算的等价性
print("=== 集合运算的性质验证 ===")
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6, 7}
C = {5, 6, 7, 8, 9}

# 交换律：A ∪ B = B ∪ A
union1 = A | B
union2 = B | A
print(f"A ∪ B = {union1}")
print(f"B ∪ A = {union2}")
print(f"交换律验证：{union1 == union2}")

# 结合律：(A ∪ B) ∪ C = A ∪ (B ∪ C)
left = (A | B) | C
right = A | (B | C)
print(f"\n结合律验证：{(A | B) | C == A | (B | C)}")

# 分配律：A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)
left = A & (B | C)
right = (A & B) | (A & C)
print(f"\n分配律验证：{A & (B | C) == (A & B) | (A & C)}")

# 实际应用：性能比较
print("\n=== 性能比较：列表vs集合查找 ===")
import time

# 准备测试数据
large_list = list(range(1000000))
large_set = set(range(1000000))

# 测试列表查找
start = time.time()
result_list = 999999 in large_list
end = time.time()
print(f"列表查找耗时：{end - start:.6f}秒，结果：{result_list}")

# 测试集合查找
start = time.time()
result_set = 999999 in large_set
end = time.time()
print(f"集合查找耗时：{end - start:.6f}秒，结果：{result_set}")

# 集合推导式
print("\n=== 集合推导式 ===")
# 生成1-100的平方数集合
squares = {x*x for x in range(1, 101)}
print(f"1-100的平方数（前5个）：{list(squares)[:5]}...")

# 生成1-100的偶数集合
evens = {x for x in range(1, 101) if x % 2 == 0}
print(f"1-100的偶数数量：{len(evens)}")

# 实际应用：找出唯一的解决方案
print("\n=== 实际应用：找出唯一的解决方案 ===")
solutions = [
    {"A", "B", "C"},
    {"A", "B", "D"},
    {"A", "C", "D"},
    {"B", "C", "D"},
]

# 找出只在第一个解决方案中的元素
unique_elements = set()
for i, solution in enumerate(solutions):
    if i == 0:
        unique_elements = solution
    else:
        unique_elements = unique_elements - solution

print(f"只在第一个解决方案中的元素：{unique_elements}")

# 找出在所有解决方案中都出现的元素
common_to_all = solutions[0].copy()
for solution in solutions[1:]:
    common_to_all &= solution

print(f"在所有解决方案中都出现的元素：{common_to_all}")
```

**解释：**

**集合运算的性质：**

1. **交换律**：
   - `A ∪ B = B ∪ A`
   - `A ∩ B = B ∩ A`
   - `A ^ B = B ^ A`

2. **结合律**：
   - `(A ∪ B) ∪ C = A ∪ (B ∪ C)`
   - `(A ∩ B) ∩ C = A ∩ (B ∩ C)`

3. **分配律**：
   - `A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)`
   - `A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)`

**集合运算的应用场景：**

1. **去重**：自动去除重复元素
2. **查找共同元素**：使用交集运算
3. **查找差异**：使用差集运算
4. **数据清洗**：过滤无效数据
5. **关系分析**：分析数据间的关系

**集合推导式：**
```python
# 基本语法：{expression for item in iterable if condition}
numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
evens = {x for x in numbers if x % 2 == 0}
squares = {x*x for x in range(1, 6)}
```

**集合与列表的性能比较：**

| 操作 | 列表时间复杂度 | 集合时间复杂度 |
|------|----------------|----------------|
| `in` | O(n) | O(1) |
| `remove` | O(n) | O(1) |
| 添加元素 | O(1) | O(1)（平均） |
| 并集 | O(n+m) | O(n+m) |

**选择集合的理由：**
1. **快速查找**：O(1)时间复杂度
2. **自动去重**：保持数据唯一性
3. **集合运算**：方便进行数学运算
4. **内存效率**：对于大量唯一数据，集合比列表更省内存

---
*本章内容基于 Python 教学平台标准格式设计。*
