---
title: "文件操作"
order: 14
unlock_conditions:
  type: "prerequisite"
  prerequisites: [13]
---

## 文件操作

### 章节概述

文件操作是编程中的重要技能。本章将学习如何打开、读取、写入文件，以及使用上下文管理器安全地处理文件。

### 知识点 1：文件的打开和关闭

**描述：**
使用 open() 函数可以打开文件，使用 close() 方法或 with 语句可以关闭文件。

**文件打开：**
```python-exec
# 打开文件读取
with open("example.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(f"文件内容：{content}")

# 写入文件
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello, Python!\n")
    file.write("这是第一行。\n")
    file.write("这是第二行。")

print("文件写入完成！")
```

### 知识点 2：文件的读取方法

**描述：**
Python提供了多种读取文件的方法，可以根据需要选择合适的方式。

**读取方法：**
```python-exec
# 1. 读取全部内容
with open("example.txt", "r", encoding="utf-8") as file:
    all_content = file.read()
    print(f"全部内容：\n{all_content}")

# 2. 逐行读取
with open("example.txt", "r", encoding="utf-8") as file:
    print("\n逐行读取：")
    for line in file:
        print(f"行：{line.strip()}")

# 3. 读取固定字符数
with open("example.txt", "r", encoding="utf-8") as file:
    first_chars = file.read(10)
    print(f"\n前10个字符：{first_chars}")
```

### 知识点 3：文件的写入方法

**描述：**
可以向文件写入字符串，注意写入模式会覆盖原有内容。

**写入方法：**
```python-exec
# 写入字符串
with open("notes.txt", "w", encoding="utf-8") as file:
    file.write("这是第一行笔记\n")
    file.write("这是第二行笔记\n")

# 追加内容
with open("notes.txt", "a", encoding="utf-8") as file:
    file.write("这是追加的第三行\n")

# 写入列表
lines = ["第一条记录", "第二条记录", "第三条记录"]
with open("data.txt", "w", encoding="utf-8") as file:
    file.writelines(f"{line}\n" for line in lines)
```

### 知识点 4：文件的其他操作

**描述：**
除了读写，还可以获取文件信息、移动文件指针等。

**文件操作：**
```python-exec
import os

# 创建文件
with open("temp.txt", "w", encoding="utf-8") as file:
    file.write("临时文件")

# 获取文件信息
if os.path.exists("temp.txt"):
    size = os.path.getsize("temp.txt")
    print(f"文件大小：{size} 字节")

    # 检查是否为文件
    if os.path.isfile("temp.txt"):
        print("这是一个文件")

# 重命名文件
os.rename("temp.txt", "renamed.txt")
print("文件已重命名")

# 删除文件
os.remove("renamed.txt")
print("文件已删除")
```

### 知识点 5：上下文管理器

**描述：**
使用 with 语句可以自动管理文件资源，避免忘记关闭文件的问题。

**with 语句：**
```python-exec
# 自动关闭文件
with open("demo.txt", "w", encoding="utf-8") as file:
    file.write("使用with语句\n")
    file.write("自动关闭文件\n")
    # 即使出错也会关闭文件

print("文件已自动关闭")

# 多文件操作
with open("input.txt", "r", encoding="utf-8") as infile, \
     open("output.txt", "w", encoding="utf-8") as outfile:
    content = infile.read()
    processed = content.upper()
    outfile.write(processed)
```

### 知识点 6：CSV文件处理

**描述：**
CSV是常用的数据格式，Python内置了csv模块来处理CSV文件。

**CSV处理：**
```python-exec
import csv

# 写入CSV
with open("students.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["姓名", "年龄", "成绩"])
    writer.writerow(["张三", "20", "95"])
    writer.writerow(["李四", "22", "88"])
    writer.writerow(["王五", "21", "92"])

# 读取CSV
with open("students.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    print("学生数据：")
    for row in reader:
        print(f"{row[0]}: {row[1]}岁, 成绩{row[2]}")
```

### 章节总结

本章我们学习了：
- 文件的打开和关闭方法
- 多种文件读取方式
- 文件的写入方法
- 文件信息获取和操作
- 上下文管理器的使用
- CSV文件的处理方法

### 下一步

掌握了文件操作后，让我们学习异常处理，了解如何处理程序运行中的错误。

---
*本章内容基于 Python 教学平台标准格式设计。*
