---
title: "创建简单的学生类"
type: "algorithm"
difficulty: 1
chapter: 17
time_limit: 1000
memory_limit: 256
solution_name:
  python: "Student"
code_template:
  python: |
    class Student:
        """
        学生类
        """
        def __init__(self, name, age):
            """
            初始化学生对象
            """
            # 在这里实现构造函数
            pass

        def introduce(self):
            """
            返回学生介绍信息
            返回格式：我是{name}，今年{age}岁
            """
            # 在这里实现方法
            pass
test_cases:
  - input: "[[\"张三\", 20]]"
    output: "[\"我是张三，今年20岁\"]"
    is_sample: true
  - input: "[[\"李四\", 22]]"
    output: "[\"我是李四，今年22岁\"]"
    is_sample: false
  - input: "[[\"王五\", 18]]"
    output: "[\"我是王五，今年18岁\"]"
    is_sample: false
  - input: "[[\"赵六\", 25]]"
    output: "[\"我是赵六，今年25岁\"]"
    is_sample: false
  - input: "[[\"小明\", 21]]"
    output: "[\"我是小明，今年21岁\"]"
    is_sample: false
---

## 题目描述

创建一个简单的学生类（Student），包含以下内容：
1. 构造函数 __init__ 接收 name（姓名）和 age（年龄）两个参数
2. 方法 introduce() 返回介绍信息，格式为"我是{name}，今年{age}岁"

### 输入格式
两个参数：name（字符串）和 age（整数）

### 输出格式
调用 introduce() 方法返回的字符串

### 示例

**输入：**
```
student = Student("张三", 20)
student.introduce()
```

**输出：**
```
"我是张三，今年20岁"
```

### 提示
- 在 __init__ 方法中使用 self.name = name 和 self.age = age 存储属性
- 在 introduce() 方法中返回格式化的字符串

### 注意事项
- 必须正确实现构造函数和方法
- 确保返回的字符串格式正确
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*
