---
title: "模块与文件"
order: 3
---
## 模块与文件

### 章节概述

模块是Python组织代码的基本方式，通过模块可以重用代码、组织功能。文件操作则是程序与外部数据交互的重要手段。本章将学习模块的导入使用、Python标准库以及文件读写操作。

### 知识点 1：模块的导入与使用

**描述：**

模块是包含Python定义和语句的文件，通过导入模块可以使用其他文件中的代码。Python提供了多种导入方式，并且拥有丰富的标准库。

**示例代码：**
```python
# 导入整个模块
import math

print(math.pi)        # 3.141592653589793
print(math.sqrt(16))  # 4.0
print(math.pow(2, 3)) # 8.0

# 导入模块并使用别名
import math as m

print(m.pi)           # 3.141592653589793
print(m.sqrt(25))     # 5.0

# 从模块中导入特定函数
from math import sqrt, pi

print(pi)             # 3.141592653589793
print(sqrt(36))       # 6.0

# 导入模块中的所有内容（不推荐）
from math import *

# 导入自定义模块
# 假设有文件 mymodule.py
# 内容：
# def greet(name):
#     return f"Hello, {name}!"
#
# VERSION = "1.0"

# 导入方式
# import mymodule
# print(mymodule.greet("World"))
# print(mymodule.VERSION)

# 实际应用：使用 random 模块
import random

# 生成随机整数
print(random.randint(1, 10))  # 1到10之间的随机整数

# 生成随机浮点数
print(random.random())        # 0.0到1.0之间的随机浮点数

# 从序列中随机选择
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
print(random.choice(fruits))  # 随机选择一个水果

# 随机打乱列表
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)  # 打乱后的列表

# 实际应用：使用 datetime 模块
from datetime import datetime, date, timedelta

# 获取当前日期和时间
now = datetime.now()
print(f"现在: {now}")
print(f"年份: {now.year}")
print(f"月份: {now.month}")
print(f"日期: {now.day}")

# 创建特定日期
birthday = date(2000, 1, 1)
print(f"生日: {birthday}")

# 计算日期差
today = date.today()
days_since_birthday = (today - birthday).days
print(f"出生天数: {days_since_birthday}")

# 日期加减
tomorrow = today + timedelta(days=1)
print(f"明天: {tomorrow}")

# 实际应用：使用 pathlib 处理路径
from pathlib import Path

# 创建路径对象
current_dir = Path(".")
print(f"当前目录: {current_dir}")

# 构建路径
file_path = Path("documents") / "python" / "lesson.md"
print(f"文件路径: {file_path}")

# 检查路径是否存在
print(f"路径存在: {file_path.exists()}")

# 获取文件信息
if current_dir.exists():
    print(f"是目录: {current_dir.is_dir()}")
```

**解释：**

**模块导入方式：**

1. **import module**
   - 导入整个模块
   - 使用时需要加模块名前缀
   - 优点：命名清晰，避免冲突
   - 示例：`import math`, `math.sqrt(16)`

2. **import module as alias**
   - 导入模块并使用别名
   - 常用于长模块名
   - 示例：`import numpy as np`

3. **from module import name**
   - 导入模块中的特定函数或类
   - 使用时不需要模块名前缀
   - 示例：`from math import sqrt`

4. **from module import ***
   - 导入模块中的所有内容
   - **不推荐**：可能导致命名冲突
   - 示例：`from math import *`

**常用标准库模块：**

```python
# 数学运算
import math
math.pi, math.sqrt(), math.sin()

# 随机数
import random
random.randint(), random.choice(), random.shuffle()

# 日期时间
from datetime import datetime, date, timedelta
datetime.now(), date.today()

# 路径操作
from pathlib import Path
Path(), Path.exists(), Path.is_dir()

# 系统操作
import os
os.getcwd(), os.listdir(), os.mkdir()

# JSON处理
import json
json.loads(), json.dumps()

# 正则表达式
import re
re.match(), re.search(), re.findall()
```

**模块搜索路径：**

Python按以下顺序搜索模块：
1. 当前目录
2. PYTHONPATH环境变量
3. Python安装目录

```python
# 查看模块搜索路径
import sys
print(sys.path)

# 查看已导入的模块
print(sys.modules)
```

**模块的最佳实践：**
1. **导入顺序**：标准库 → 第三方库 → 本地模块
2. **避免循环导入**：模块A导入B，B又导入A
3. **使用有意义的别名**：`import numpy as np` 而非 `import numpy as n`
4. **按需导入**：只导入需要的内容

---

### 知识点 2：Python标准库简介

**描述：**

Python标准库是随Python安装的一组模块，提供了丰富的功能，从文本处理到网络编程，几乎涵盖所有常见任务。

**示例代码：**
```python
# 1. os 模块 - 操作系统接口
import os

# 获取当前工作目录
print(f"当前目录: {os.getcwd()}")

# 列出目录内容
items = os.listdir(".")
print(f"目录内容: {items[:5]}")  # 显示前5个

# 创建目录
if not os.path.exists("test_dir"):
    os.mkdir("test_dir")
    print("目录创建成功")

# 路径操作
print(f"文件是否存在: {os.path.exists('chapter-03-modules-files.md')}")
print(f"是否为文件: {os.path.isfile('chapter-03-modules-files.md')}")
print(f"是否为目录: {os.path.isdir('.')}")

# 2. json 模块 - JSON数据处理
import json

# Python对象转JSON字符串
data = {
    "name": "张三",
    "age": 25,
    "scores": [85, 92, 78]
}

json_string = json.dumps(data, ensure_ascii=False)
print(f"JSON字符串: {json_string}")

# JSON字符串转Python对象
parsed_data = json.loads(json_string)
print(f"解析后: {parsed_data}")

# 读写JSON文件
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("data.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    print(f"从文件加载: {loaded_data}")

# 3. re 模块 - 正则表达式
import re

text = "我的电话号码是 138-1234-5678，备用电话 010-12345678"

# 查找所有电话号码
phones = re.findall(r"\d{3,4}-?\d{7,8}", text)
print(f"找到的电话: {phones}")

# 替换文本
new_text = re.sub(r"\d{3,4}-?\d{7,8}", "[电话号码]", text)
print(f"替换后: {new_text}")

# 验证邮箱格式
email = "user@example.com"
if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
    print("邮箱格式正确")

# 4. collections 模块 - 特殊容器
from collections import Counter, defaultdict

# Counter - 计数器
words = ["apple", "banana", "apple", "orange", "banana", "apple"]
word_count = Counter(words)
print(f"词频统计: {word_count}")
print(f"最常见的单词: {word_count.most_common(2)}")

# defaultdict - 带默认值的字典
grades = defaultdict(list)
grades["张三"].append(85)
grades["张三"].append(92)
grades["李四"].append(78)
print(f"成绩: {dict(grades)}")

# 5. itertools 模块 - 迭代器工具
from itertools import count, cycle, chain

# count - 无限计数器
# for i in count(10):
#     print(i)
#     if i > 15:
#         break

# chain - 连接多个序列
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined = list(chain(list1, list2))
print(f"连接后: {combined}")

# 实际应用：数据验证
def validate_user_data(user_data):
    """验证用户数据"""
    errors = []

    # 检查必需字段
    required_fields = ["name", "email", "age"]
    for field in required_fields:
        if field not in user_data:
            errors.append(f"缺少字段: {field}")

    # 验证邮箱格式
    if "email" in user_data:
        email = user_data["email"]
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            errors.append("邮箱格式不正确")

    # 验证年龄范围
    if "age" in user_data:
        age = user_data["age"]
        if not isinstance(age, int) or age < 0 or age > 150:
            errors.append("年龄必须是0-150之间的整数")

    return errors

user = {"name": "张三", "email": "invalid-email", "age": 200}
errors = validate_user_data(user)
print(f"验证错误: {errors}")

# 实际应用：日志记录
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 记录不同级别的日志
logging.info("程序开始执行")
logging.warning("这是一个警告")
logging.error("这是一个错误")
```

**解释：**

**常用标准库分类：**

1. **文本处理**
   - `re`: 正则表达式
   - `string`: 字符串操作
   - `textwrap`: 文本格式化

2. **数据结构**
   - `collections`: 特殊容器（Counter, defaultdict等）
   - `heapq`: 堆队列算法
   - `bisect`: 数组二分查找

3. **文件和目录**
   - `os`: 操作系统接口
   - `pathlib`: 面向对象的路径操作
   - `shutil`: 高级文件操作

4. **数据序列化**
   - `json`: JSON数据处理
   - `pickle`: Python对象序列化
   - `csv`: CSV文件读写

5. **日期和时间**
   - `datetime`: 日期时间处理
   - `time`: 时间相关函数
   - `calendar`: 日历相关函数

6. **数学和统计**
   - `math`: 数学函数
   - `statistics`: 统计函数
   - `random`: 随机数生成

7. **网络和互联网**
   - `urllib`: URL处理
   - `http`: HTTP客户端
   - `socket`: 底层网络接口

8. **开发工具**
   - `logging`: 日志记录
   - `unittest`: 单元测试
   - `pdb`: 调试器

**collections 模块详解：**

```python
from collections import Counter, defaultdict, OrderedDict, namedtuple

# Counter - 计数器
Counter(['a', 'b', 'a', 'c', 'b', 'a'])
# Counter({'a': 3, 'b': 2, 'c': 1})

# defaultdict - 默认字典
dd = defaultdict(int)
dd['key'] += 1  # 不会报错

# namedtuple - 命名元组
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
```

**标准库使用技巧：**
1. **阅读官方文档**：[docs.python.org](https://docs.python.org/)
2. **探索式学习**：使用 `help()` 和 `dir()`
3. **代码复用**：优先使用标准库而非自己实现
4. **性能考虑**：标准库通常经过优化，性能更好

```python
# 探索模块
import math
help(math)      # 查看帮助文档
dir(math)       # 查看所有属性和方法
```

---

### 知识点 3：文件读写基础

**描述：**

文件操作是程序持久化数据的基本方式。Python提供了简单易用的文件读写接口，支持文本文件和二进制文件的处理。

**示例代码：**
```python
# 1. 读取文本文件
# 方法1：使用 open() 和 read()
with open("example.txt", "r", encoding="utf-8") as f:
    content = f.read()  # 读取全部内容
    print(f"全部内容:\n{content}")

# 方法2：逐行读取
with open("example.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(f"行: {line.strip()}")

# 方法3：读取所有行到列表
with open("example.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(f"行数: {len(lines)}")

# 2. 写入文本文件
# 方法1：覆盖写入
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")

# 方法2：追加写入
with open("output.txt", "a", encoding="utf-8") as f:
    f.write("追加的行\n")

# 方法3：写入多行
lines = ["行1\n", "行2\n", "行3\n"]
with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)

# 实际应用：处理CSV文件
# 读取CSV
with open("data.csv", "r", encoding="utf-8") as f:
    for line in f:
        fields = line.strip().split(",")
        print(f"字段: {fields}")

# 写入CSV
data = [
    ["姓名", "年龄", "成绩"],
    ["张三", "25", "85"],
    ["李四", "24", "92"]
]

with open("output.csv", "w", encoding="utf-8") as f:
    for row in data:
        f.write(",".join(map(str, row)) + "\n")

# 实际应用：配置文件读写
def read_config(filename):
    """读取配置文件"""
    config = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue
            # 解析 key=value
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config

def write_config(filename, config):
    """写入配置文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 配置文件\n")
        f.write("# 生成时间: 2024\n\n")
        for key, value in config.items():
            f.write(f"{key} = {value}\n")

# 使用示例
config = {
    "debug": "True",
    "database_url": "localhost:5432",
    "max_connections": "100"
}

write_config("config.ini", config)
loaded_config = read_config("config.ini")
print(f"配置: {loaded_config}")

# 实际应用：统计文件信息
def analyze_file(filename):
    """分析文件信息"""
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)
    non_empty_lines = len([line for line in lines if line.strip()])
    total_chars = sum(len(line) for line in lines)
    total_words = sum(len(line.split()) for line in lines)

    return {
        "总行数": total_lines,
        "非空行数": non_empty_lines,
        "总字符数": total_chars,
        "总单词数": total_words
    }

# 统计当前文件
stats = analyze_file("chapter-03-modules-files.md")
for key, value in stats.items():
    print(f"{key}: {value}")

# 实际应用：文件备份
import shutil
from datetime import datetime

def backup_file(filename):
    """备份文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filename}.backup_{timestamp}"

    try:
        shutil.copy2(filename, backup_name)
        print(f"备份成功: {backup_name}")
        return True
    except Exception as e:
        print(f"备份失败: {e}")
        return False

# 使用示例
# backup_file("example.txt")
```

**解释：**

**文件打开模式：**

| 模式 | 描述 | 文件不存在时 |
|------|------|--------------|
| `'r'` | 只读 | 报错 |
| `'w'` | 写入（覆盖） | 创建新文件 |
| `'a'` | 追加 | 创建新文件 |
| `'r+'` | 读写 | 报错 |
| `'w+'` | 读写（覆盖） | 创建新文件 |
| `'a+'` | 读写（追加） | 创建新文件 |
| `'b'` | 二进制模式 | - |
| `'t'` | 文本模式（默认） | - |

**with 语句的优势：**
```python
# 不使用 with（不推荐）
f = open("file.txt", "r")
content = f.read()
f.close()  # 需要手动关闭

# 使用 with（推荐）
with open("file.txt", "r") as f:
    content = f.read()
# 自动关闭文件，即使发生异常
```

**文件读取方法：**

```python
with open("file.txt", "r") as f:
    # read() - 读取全部内容
    content = f.read()

    # read(size) - 读取指定字节数
    first_100 = f.read(100)

    # readline() - 读取一行
    line = f.readline()

    # readlines() - 读取所有行到列表
    lines = f.readlines()

    # for循环 - 逐行读取（推荐）
    for line in f:
        print(line.strip())
```

**文件写入方法：**

```python
with open("file.txt", "w") as f:
    # write(string) - 写入字符串
    f.write("Hello\n")

    # writelines(list) - 写入字符串列表
    lines = ["Line1\n", "Line2\n"]
    f.writelines(lines)
```

**编码处理：**
- 使用 `encoding="utf-8"` 参数指定编码
- Windows可能使用 `encoding="gbk"`
- 统一使用UTF-8是最安全的做法

**文件操作的异常处理：**
```python
try:
    with open("file.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("文件不存在")
except PermissionError:
    print("没有权限访问文件")
except Exception as e:
    print(f"发生错误: {e}")
```

**文件操作的最佳实践：**
1. **始终使用 with 语句**：自动管理文件关闭
2. **指定编码**：使用 UTF-8 编码
3. **处理异常**：捕获文件操作可能出现的错误
4. **路径处理**：使用 `pathlib.Path` 或 `os.path` 处理路径
5. **及时关闭**：使用 with 后无需手动关闭

**实际应用场景：**
- **日志处理**：读取和分析日志文件
- **数据导入导出**：CSV、JSON等格式的数据交换
- **配置管理**：读写配置文件
- **数据持久化**：保存程序状态
- **批处理**：批量处理文件

---
*本章内容基于 Python 教学平台标准格式设计。*
