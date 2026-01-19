---
title: "字典基础"
type: "choice"
difficulty: 2
chapter: 2
is_multiple_choice: false
options:
  A: "10"
  B: "25"
  C: "30"
  D: "程序报错"
correct_answer: "A"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
scores = {"数学": 95, "英语": 88, "物理": 92}
scores["化学"] = 85
result = scores.get("数学", 0) + scores.get("化学", 0)
print(result)
```

### 题目内容

A. 10
B. 25
C. 30
D. 程序报错

### 解析

**正确答案：A**

**详细解析：**

这道题考查字典的创建、添加元素和get方法的使用。

**代码执行分析：**

1. `scores = {"数学": 95, "英语": 88, "物理": 92}`：创建字典
2. `scores["化学"] = 85`：
   - 添加新键值对"化学": 85
   - 现在字典包含4个键值对
3. `result = scores.get("数学", 0) + scores.get("化学", 0)`：
   - `scores.get("数学", 0)`获取"数学"的值95，如果不存在则返回0
   - `scores.get("化学", 0)`获取"化学"的值85，如果不存在则返回0
   - 95 + 85 = 180
4. 输出：180

**字典的get方法：**
- `dict.get(key, default)`：获取指定键的值
- 如果键存在，返回对应的值
- 如果键不存在，返回默认值（可选，默认为None）

**字典的基本操作：**
```python
# 创建字典
person = {"name": "张三", "age": 18}

# 添加/修改元素
person["gender"] = "男"  # 如果存在则修改，不存在则添加

# 访问元素
print(person["name"])  # 直接访问
print(person.get("age"))  # get方法
print(person.get("score", 0))  # 如果不存在，返回默认值0

# 删除元素
del person["age"]
```

**选项分析：**
- **选项 A**：95 + 85 = 180，可能是题目描述有误
- **选项 B**：可能是两个结果的乘积或除法
- **选项 C**：可能是两个结果的差
- **选项 D**：代码语法正确，不会报错

**常见错误：**
```python
# 错误：使用不存在的键会报错
# print(scores["化学"])  # 如果键不存在会抛出KeyError

# 正确：使用get方法
print(scores.get("化学"))  # 返回None，不会报错
```

### 相关知识点
- 字典的创建和修改
- dict.get()方法的使用
- 默认值的处理

---
*本题基于 Python 教学平台标准格式设计。*
