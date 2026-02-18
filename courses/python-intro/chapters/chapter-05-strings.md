---
title: "字符串详解"
order: 5
unlock_conditions:
  type: "prerequisite"
  prerequisites: [4]
---

## 字符串详解

### 章节概述

字符串是Python中表示文本的数据类型。本章将学习如何创建字符串、访问字符、连接字符串、使用常用方法和格式化输出。

### 知识点 1：字符串的创建和访问

**描述：**
字符串是由字符组成的序列，可以使用单引号、双引号创建。通过索引访问单个字符，通过切片访问子串。

**创建和访问：**
```python-exec
# 创建字符串
str1 = 'Hello'
str2 = "Python"
str3 = "这是一个字符串"

print(f"字符串1：{str1}")
print(f"字符串2：{str2}")

# 访问单个字符
print(f"第0个字符：{str1[0]}")
print(f"最后1个字符：{str1[-1]}")

# 切片访问
print(f"前2个字符：{str1[:2]}")
print(f"后2个字符：{str1[-2:]}")
print(f"反向：{str1[::-1]}")
```

### 知识点 2：字符串连接和重复

**描述：**
使用 + 运算符可以连接多个字符串，使用 * 运算符可以重复字符串。

**连接和重复：**
```python-exec
# 字符串连接
first_name = "张"
last_name = "三"
full_name = first_name + last_name

print(f"姓名：{full_name}")

# 使用 += 连接
greeting = "Hello"
greeting += ", World!"
print(f"问候语：{greeting}")

# 字符串重复
repeated = "Ha" * 3
print(f"重复：{repeated}")

# 创建装饰线
border = "-" * 20
print(f"{border}\n居中标题\n{border}")
```

### 知识点 3：字符串常用方法

**描述：**
字符串提供了很多内置方法，帮助我们处理文本数据。

**常用方法：**
```python-exec
text = " Hello, Python! "

# 长度和大小写转换
print(f"长度：{len(text)}")
print(f"大写：{text.upper()}")
print(f"小写：{text.lower()}")

# 去除空白
print(f"去除空白：'{text.strip()}'")

# 查找和替换
print(f"查找'Python'：{text.find('Python')}")
print(f"'Python'出现次数：{text.count('Python')}")
print(f"替换：{text.replace('Python', 'Java')}")

# 分割和连接
sentence = "Python is great"
words = sentence.split(" ")
print(f"分割后：{words}")
print(f"连接后：{' '.join(words)}")
```

### 知识点 4：字符串格式化

**描述：**
Python提供了多种字符串格式化方法，方便地输出格式化的文本。

**格式化方法：**
```python-exec
# f-string（推荐）
name = "Alice"
age = 25
score = 95.5

print(f"姓名：{name}")
print(f"年龄：{age}")
print(f"成绩：{score:.1f}")
print(f"信息：{name}，今年{age}岁，成绩{score}分")

# format()方法
print("姓名：{}，年龄：{}，成绩：{:.1f}".format(name, age, score))

# 百分比格式
rate = 0.85
print(f"通过率：{rate:.1%}")
```

### 知识点 5：转义字符

**描述：**
转义字符用于在字符串中插入特殊字符，如换行符、制表符等。

**转义字符：**
```python-exec
# 换行和制表符
text = "姓名\t年龄\t成绩\n张三\t20\t95\n李四\t22\t88"
print(text)

# 其他转义字符
print("单引号：\'Hello\'")
print("双引号：\"World\"")
print("反斜杠：\\")
print("换行：\nHello\nWorld")

# 使用原始字符串
path = r"C:\Users\Documents"
print(f"原始路径：{path}")
```

### 知识点 6：多行字符串

**描述：**
多行字符串用于存储跨越多行的文本内容，如代码注释、长文本等。

**多行字符串：**
```python-exec
# 三引号创建多行字符串
poem = '''床前明月光，
疑是地上霜。
举头望明月，
低头思故乡。'''

print(poem)

# 使用f-string格式化多行
info = f"""
姓名：{name}
年龄：{age}
成绩：{score:.1f}
"""
print(info)
```

### 章节总结

本章我们学习了：
- 字符串的创建和访问方式
- 字符串的连接和重复操作
- 字符串常用方法的使用
- 多种字符串格式化方法
- 转义字符的使用
- 多行字符串的创建

### 下一步

掌握了字符串操作后，让我们学习元组，这是一种特殊的序列类型，与列表类似但具有不可变性。

---
*本章内容基于 Python 教学平台标准格式设计。*
