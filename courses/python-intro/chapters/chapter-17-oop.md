---
title: "面向对象基础"
order: 17
unlock_conditions:
  type: "prerequisite"
  prerequisites: [16]
---

## 面向对象基础

### 章节概述

面向对象编程（OOP）是一种重要的编程范式。本章将学习类、对象、属性、方法等基本概念，以及面向对象的三大特性：封装、继承和多态。

### 知识点 1：类和对象

**描述：**
类是创建对象的模板，对象是类的实例。类定义了对象的属性和方法。

**创建类和对象：**
```python-exec
# 创建一个简单的类
class Student:
    """学生类"""
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"我是{self.name}，今年{self.age}岁"

# 创建对象
student1 = Student("张三", 20)
student2 = Student("李四", 22)

# 使用对象
print(student1.introduce())
print(student2.introduce())

# 访问属性
print(f"学生1的姓名：{student1.name}")
print(f"学生2的年龄：{student2.age}")
```

### 知识点 2：属性和方法

**描述：**
属性存储对象的数据，方法定义对象的行为。方法分为实例方法、类方法和静态方法。

**属性和方法：**
```python-exec
class Person:
    def __init__(self, name):
        self.name = name
        self._age = 0  # 受保护的属性

    def set_age(self, age):
        """设置年龄"""
        if age > 0:
            self._age = age
        else:
            print("年龄必须大于0")

    def get_age(self):
        """获取年龄"""
        return self._age

    def birthday(self):
        """庆祝生日"""
        self._age += 1
        print(f"生日快乐！{self.name}现在{self._age}岁了")

# 使用
p = Person("王五")
p.set_age(25)
print(f"{p.name}的年龄：{p.get_age()}")
p.birthday()
```

### 知识点 3：继承

**描述：**
继承允许一个类继承另一个类的属性和方法，实现代码复用。

**继承实现：**
```python-exec
# 父类
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "动物会说话"

# 子类
class Dog(Animal):
    def speak(self):
        return f"{self.name}：汪汪！"

    def wag_tail(self):
        return f"{self.name}摇尾巴"

class Cat(Animal):
    def speak(self):
        return f"{self.name}：喵喵！"

# 使用继承
dog = Dog("小黄")
cat = Cat("咪咪")

print(dog.speak())
print(dog.wag_tail())
print(cat.speak())
```

### 知识点 4：封装

**描述：**
封装是指将数据和方法包装在类中，隐藏内部实现细节，只暴露必要的接口。

**封装示例：**
```python-exec
class BankAccount:
    def __init__(self, owner, balance=0):
        self._owner = owner  # 受保护的属性
        self.__balance = balance  # 私有属性

    def deposit(self, amount):
        """存款"""
        if amount > 0:
            self.__balance += amount
            print(f"存款成功：{amount}元")
        else:
            print("存款金额必须大于0")

    def withdraw(self, amount):
        """取款"""
        if amount > 0 and amount <= self.__balance:
            self.__balance -= amount
            print(f"取款成功：{amount}元")
        else:
            print("取款失败：余额不足")

    def get_balance(self):
        """获取余额"""
        return self.__balance

# 使用封装
account = BankAccount("张三", 1000)
print(f"账户所有者：{account._owner}")
print(f"当前余额：{account.get_balance()}")

account.deposit(500)
account.withdraw(200)

# 尝试直接访问私有属性（不推荐）
# print(account.__balance)  # 会报错
print(f"余额：{account.get_balance()}")
```

### 知识点 5：多态

**描述：**
多态是指不同对象对同一消息（方法）有不同的响应。

**多态示例：**
```python-exec
# 形状基类
class Shape:
    def area(self):
        pass

    def perimeter(self):
        pass

# 圆形
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius * self.radius

    def perimeter(self):
        return 2 * 3.14 * self.radius

# 矩形
class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

# 多态函数
def calculate_area(shape):
    return shape.area()

# 使用多态
circle = Circle(5)
rectangle = Rectangle(4, 6)

print(f"圆形面积：{calculate_area(circle)}")
print(f"矩形面积：{calculate_area(rectangle)}")

# 不同形状的响应
shapes = [circle, rectangle]
for shape in shapes:
    print(f"形状面积：{shape.area()}")
```

### 知识点 6：特殊方法

**描述：**
Python类中有很多特殊方法（以__开头和结尾），用于实现对象的特殊行为。

**特殊方法：**
```python-exec
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __str__(self):
        """字符串表示"""
        return f"'{self.title}' by {self.author}"

    def __repr__(self):
        """调试表示"""
        return f"Book('{self.title}', '{self.author}', {self.pages})"

    def __len__(self):
        """长度"""
        return self.pages

    def __eq__(self, other):
        """比较相等"""
        return self.title == other.title and self.author == other.author

# 使用特殊方法
book1 = Book("Python入门", "张三", 300)
book2 = Book("Python入门", "张三", 350)
book3 = Book("Python进阶", "李四", 400)

print(book1)  # 调用__str__
print(f"页数：{len(book1)}")  # 调用__len__

print(f"book1 == book2: {book1 == book2}")  # 调用__eq__
print(f"book1 == book3: {book1 == book3}")  # 调用__eq__
```

### 章节总结

本章我们学习了：
- 类和对象的基本概念
- 属性和方法的定义与使用
- 继承的实现方式
- 封装的概念和应用
- 多态的实现和好处
- 常用的特殊方法

### 下一步

恭喜！你已经完成了Python入门课程的全部内容。现在你已经掌握了Python的基础知识，可以开始编写自己的Python程序了。

---
*本章内容基于 Python 教学平台标准格式设计。*
