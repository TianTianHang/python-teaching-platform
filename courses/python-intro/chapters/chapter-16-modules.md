---
title: "模块与包"
order: 16
unlock_conditions:
  type: "prerequisite"
  prerequisites: [15]
---

## 模块与包

### 章节概述

模块是Python代码的文件组织方式，包是模块的集合。本章将学习如何导入和使用模块，创建自己的模块，以及了解标准库中的常用模块。

### 知识点 1：import语句

**描述：**
import语句用于导入模块，可以使用不同的导入方式来访问模块中的功能。

**导入方式：**
```python-exec
# 导入整个模块
import math
print(f"圆周率：{math.pi}")
print(f"平方根：{math.sqrt(16)}")

# 导入特定功能
from math import pi, sqrt
print(f"导入的圆周率：{pi}")
print(f"平方根：{sqrt(25)}")

# 使用别名导入
import math as m
print(f"别名：圆周率 = {m.pi}")

# 导入所有内容（不推荐）
from math import *
print(f"导入所有：cos(0) = {cos(0)}")
```

### 知识点 2：模块搜索路径

**描述：**
Python按特定顺序搜索模块，包括当前目录和sys.path中的路径。

**模块路径：**
```python-exec
import sys
import os

# 查看模块搜索路径
print("Python搜索路径：")
for path in sys.path:
    print(f"  {path}")

# 检查模块是否存在
import random
print(f"\n'random'模块路径：{random.__file__}")

# 检查模块信息
print(f"模块名称：{random.__name__}")
print(f"模块文档：{random.__doc__[:50]}...")
```

### 知识点 3：创建自己的模块

**描述：**
任何Python文件都可以作为模块导入，只需import语句即可使用。

**创建模块：**
```python-exec
# 假设有一个工具模块 utils.py
"""
utils.py 示例模块
"""
def greet(name):
    """问候函数"""
    return f"你好，{name}！"

def add(a, b):
    """加法函数"""
    return a + b

# 导入并使用
import utils

print(f"问候：{utils.greet('张三')}")
print(f"加法：{utils.add(10, 20)}")
```

### 知识点 4：常用标准库

**描述：**
Python内置了许多标准库模块，可以完成各种常见任务。

**标准库模块：**
```python-exec
# os - 操作系统相关
import os
print(f"当前工作目录：{os.getcwd()}")
print(f"系统名称：{os.name}")

# sys - 系统信息
import sys
print(f"Python版本：{sys.version}")
print(f"命令行参数：{sys.argv}")

# datetime - 日期时间
from datetime import datetime
print(f"当前时间：{datetime.now()}")

# json - JSON处理
import json
data = {"name": "张三", "age": 25}
json_str = json.dumps(data)
print(f"JSON字符串：{json_str}")

# collections - 容器工具
from collections import Counter
text = "hello world"
counts = Counter(text)
print(f"字符计数：{counts}")
```

### 知识点 5：包的使用

**描述：**
包是包含__init__.py文件的目录，可以组织多个模块。

**包的概念：**
```python-exec
# 假设有一个mypkg包
# mypkg/
# ├── __init__.py
# ├── mod1.py
# └── mod2.py

# 从包导入
import mypkg.mod1 as m1
import mypkg.mod2 as m2

# 使用包中的模块
print(f"模块1功能：{m1.function1()}")
print(f"模块2功能：{m2.function2()}")

# 使用相对导入（在包内部）
# from . import mod1
# from .. import otherpkg
```

### 知识点 6：安装第三方包

**描述：**
使用pip可以安装第三方包，扩展Python的功能。

**使用pip：**
```python-exec
# 查看已安装的包
import pkg_resources

# 安装包（在命令行中运行）
# pip install requests
# pip install numpy
# pip install pandas

# 导入安装的包
try:
    import requests
    print(f"requests版本：{requests.__version__}")

    # 简单示例
    response = requests.get("https://httpbin.org/json")
    print(f"状态码：{response.status_code}")

except ImportError:
    print("requests包未安装")

# 查看包信息
try:
    import numpy as np
    print(f"numpy版本：{np.__version__}")
    print(f"数组：{np.array([1, 2, 3])}")
except ImportError:
    print("numpy包未安装")
```

### 章节总结

本章我们学习了：
- 不同import语句的使用方式
- Python模块的搜索路径
- 如何创建自己的模块
- 常用标准库模块的功能
- 包的概念和使用
- 使用pip安装第三方包

### 下一步

掌握了模块与包后，让我们学习面向对象基础，这是Python中重要的编程范式。

---
*本章内容基于 Python 教学平台标准格式设计。*
