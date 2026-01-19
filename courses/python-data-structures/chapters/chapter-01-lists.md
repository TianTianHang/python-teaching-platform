---
title: "列表"
order: 1
---
## 列表

### 章节概述

列表是Python中最常用、最灵活的数据结构。它是一个有序的、可变的序列，可以存储任意类型的数据。通过本章的学习，你将掌握列表的基本操作、切片操作和常用方法，能够灵活运用列表处理各种数据。

### 知识点 1：列表的创建与基本操作

**描述：**

列表是Python中的一种可变序列，使用方括号`[]`创建，元素之间用逗号分隔。列表可以包含任意类型的数据，包括数字、字符串、布尔值，甚至是其他列表。

**示例代码：**
```python
# 创建列表
# 空列表
empty_list = []

# 包含不同类型元素的列表
mixed_list = [1, "hello", True, 3.14]

# 列表的嵌套（二维列表）
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# 列表的索引（从0开始）
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
print(fruits[0])      # 苹果
print(fruits[2])      # 橙子
print(fruits[-1])     # 葡萄（负数索引：-1表示最后一个，-2表示倒数第二个）

# 列表的长度
print(len(fruits))    # 4

# 检查元素是否存在
print("苹果" in fruits)    # True
print("西瓜" in fruits)    # False

# 通过索引修改元素
fruits[0] = "红苹果"
print(fruits)         # ['红苹果', '香蕉', '橙子', '葡萄']

# 常见错误：超出索引范围
try:
    print(fruits[5])   # IndexError: list index out of range
except IndexError as e:
    print(f"错误：{e}")
```

**解释：**

**列表的特点：**
- **有序**：元素按顺序排列，有固定的索引
- **可变**：可以修改、添加、删除元素
- **可以包含任何类型**：数字、字符串、布尔值、其他列表等
- **可重复**：允许重复的元素

**索引系统：**
- **正向索引**：从0开始，0表示第一个元素，1表示第二个，依此类推
- **负向索引**：-1表示最后一个，-2表示倒数第二个，依此类推
- **切片索引**：后面会详细介绍

**常用操作：**
- `len(list)`：获取列表长度
- `element in list`：检查元素是否存在
- `list[index]`：访问元素
- `list[index] = new_value`：修改元素

**列表的最佳实践：**
```python
# 避免在循环中修改列表
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    if fruit == "香蕉":
        fruits.remove(fruit)  # 这会导致问题

# 推荐的做法：
fruits = ["苹果", "香蕉", "橙子"]
new_fruits = []
for fruit in fruits:
    if fruit != "香蕉":
        new_fruits.append(fruit)
# 或者使用列表推导式
new_fruits = [f for f in fruits if f != "香蕉"]
```

---

### 知识点 2：列表切片

**描述：**

切片是Python列表的一个强大功能，允许你获取列表的子序列。使用切片可以方便地获取列表的一部分，而不需要遍历整个列表。

**示例代码：**
```python
# 基本切片
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 获取子列表
print(numbers[2:5])      # [2, 3, 4]（包含索引2，不包含5）
print(numbers[0:3])      # [0, 1, 2]
print(numbers[5:])       # [5, 6, 7, 8, 9]（从索引5到末尾）
print(numbers[:5])       # [0, 1, 2, 3, 4]（从头到索引5）

# 负数索引切片
print(numbers[-3:])      # [7, 8, 9]（最后3个）
print(numbers[:-3])      # [0, 1, 2, 3, 4, 5, 6]（除了最后3个）
print(numbers[-5:-2])    # [5, 6, 7]

# 步长切片（step）
print(numbers[::2])      # [0, 2, 4, 6, 8]（每隔1个取一个）
print(numbers[1::2])     # [1, 3, 5, 7, 9]（从索引1开始，每隔1个取一个）
print(numbers[::3])      # [0, 3, 6, 9]（每隔2个取一个）

# 反向切片
print(numbers[::-1])     # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]（反转列表）

# 复制列表
numbers_copy = numbers[:]  # 或 numbers_copy = numbers.copy()
print(numbers_copy is numbers)  # False，是不同的列表

# 修改切片
numbers[1:4] = [10, 20, 30]
print(numbers)           # [0, 10, 20, 30, 4, 5, 6, 7, 8, 9]

# 替换切片（长度可以不同）
numbers[0:2] = [100, 200, 300, 400]
print(numbers)           # [100, 200, 300, 400, 20, 30, 4, 5, 6, 7, 8, 9]

# 实际应用：处理用户数据
users = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]

# 前3个用户
top_users = users[:3]
print(f"前3名用户：{top_users}")

# 活跃用户（第2到第4个）
active_users = users[1:4]
print(f"活跃用户：{active_users}")

# 新注册用户（最后3个）
new_users = users[-3:]
print(f"新注册用户：{new_users}")
```

**解释：**

**切片语法：**
`list[start:end:step]`
- `start`：起始索引（包含），默认为0
- `end`：结束索引（不包含），默认为列表末尾
- `step`：步长，默认为1

**切片要点：**
1. **包含start，不包含end**：`[2:5]`获取索引2、3、4
2. **负数索引**：-1表示最后一个
3. **省略值**：
   - `start`省略：从开头开始
   - `end`省略：到结尾结束
   - `step`省略：步长为1
4. **步长可以为负**：实现反向遍历

**切片的常见用法：**
```python
# 获取列表的一部分
sub_list = my_list[1:5]

# 获取前n个元素
first_n = my_list[:n]

# 获取后n个元素
last_n = my_list[-n:]

# 反转列表
reversed_list = my_list[::-1]

# 复制列表
copy = my_list[:]
```

**注意：**
- 切片会创建一个新的列表，不会修改原列表
- 可以使用切片赋值来修改原列表
- 当使用切片赋值时，可以插入不同长度的序列

---

### 知识点 3：列表方法

**描述：**

Python列表提供了丰富的方法，用于对列表进行各种操作。这些方法可以分为：添加元素、删除元素、修改元素、排序、查找等几类。

**示例代码：**
```python
# 创建一个测试列表
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
numbers = [3, 1, 4, 1, 5, 9, 2]

# 添加元素的方法
fruits.append("西瓜")           # 在末尾添加
print(fruits)                  # ['苹果', '香蕉', '橙子', '葡萄', '西瓜']

fruits.insert(1, "梨子")        # 在指定位置插入
print(fruits)                  # ['苹果', '梨子', '香蕉', '橙子', '葡萄', '西瓜']

fruits.extend(["芒果", "草莓"])  # 扩展列表（合并）
print(fruits)                  # ['苹果', '梨子', '香蕉', '橙子', '葡萄', '西瓜', '芒果', '草莓']

# 删除元素的方法
fruits.remove("梨子")          # 删除指定值的元素
print(fruits)                  # ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '芒果', '草莓']

removed = fruits.pop()          # 删除并返回最后一个元素
print(f"删除的水果：{removed}")  # 删除的水果：草莓
print(fruits)                  # ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '芒果']

removed_index = fruits.pop(2)  # 删除并返回指定索引的元素
print(f"删除的水果：{removed_index}")  # 删除的水果：橙子
print(fruits)                  # ['苹果', '香蕉', '葡萄', '西瓜', '芒果']

fruits.clear()                 # 清空列表
print(fruits)                  # []

# 修改和查询的方法
numbers = [3, 1, 4, 1, 5, 9, 2]
print(numbers.count(1))         # 2（统计1出现的次数）
print(numbers.index(4))         # 2（查找4的索引，第一个匹配的）

# 排序方法
numbers.sort()                  # 原地排序
print(numbers)                  # [1, 1, 2, 3, 4, 5, 9]

numbers_desc = numbers.copy()
numbers_desc.sort(reverse=True)  # 降序排序
print(numbers_desc)             # [9, 5, 4, 3, 2, 1, 1]

# 反转列表
numbers.reverse()
print(numbers)                  # [9, 5, 4, 3, 2, 1, 1]

# 实际应用：学生成绩管理
students = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 78},
    {"name": "赵六", "score": 95},
    {"name": "钱七", "score": 88}
]

# 添加新学生
students.append({"name": "孙八", "score": 90})

# 按分数排序（降序）
students.sort(key=lambda x: x["score"], reverse=True)
print("成绩排名：")
for i, student in enumerate(students, 1):
    print(f"{i}. {student['name']}: {student['score']}分")

# 找到最高分和最低分
highest_score = max(student["score"] for student in students)
lowest_score = min(student["score"] for student in students)
print(f"最高分：{highest_score}, 最低分：{lowest_score}")

# 计算平均分
average_score = sum(student["score"] for student in students) / len(students)
print(f"平均分：{average_score:.1f}")
```

**解释：**

**列表方法分类：**

1. **添加元素**：
   - `append(element)`：在末尾添加一个元素
   - `insert(index, element)`：在指定位置插入元素
   - `extend(iterable)`：将可迭代对象的所有元素添加到列表

2. **删除元素**：
   - `remove(element)`：删除第一个匹配的元素
   - `pop(index)`：删除并返回指定索引的元素（默认最后一个）
   - `clear()`：清空列表

3. **查询和统计**：
   - `count(element)`：统计元素出现次数
   - `index(element)`：查找元素索引（第一个匹配的）
   - `len(list)`：获取列表长度（这是内置函数）

4. **排序和反转**：
   - `sort()`：原地排序（升序）
   - `sort(reverse=True)`：原地排序（降序）
   - `reverse()`：反转列表
   - `sorted()`：返回排序后的新列表（不修改原列表）

**重要提示：**
- `sort()`是原地排序，会修改原列表
- `sorted()`返回新列表，不修改原列表
- `append()`和`extend()`的区别：
  - `append([1,2])`：添加`[1,2]`作为单个元素
  - `extend([1,2])`：添加1和2作为两个元素

**实际应用技巧：**
```python
# 使用列表推导式进行过滤和转换
scores = [85, 92, 78, 95, 88]
# 获取及格的分数
passing_scores = [score for score in scores if score >= 60]

# 去重并排序
unique_scores = sorted(list(set(scores)))

# 统计各分数段人数
score_ranges = {
    "优秀": len([s for s in scores if s >= 90]),
    "良好": len([s for s in scores if 80 <= s < 90]),
    "及格": len([s for s in scores if 60 <= s < 80]),
    "不及格": len([s for s in scores if s < 60])
}
```

**列表的性能考虑：**
- 列表的添加和删除在末尾是O(1)时间复杂度
- 在中间或开头插入/删除是O(n)时间复杂度
- `in`操作符查找是O(n)时间复杂度
- 推荐使用集合（set）进行快速查找

---
*本章内容基于 Python 教学平台标准格式设计。*
