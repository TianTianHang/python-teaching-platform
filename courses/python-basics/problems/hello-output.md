---
title: "格式化输出"
type: "algorithm"
difficulty: 1
chapter: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "print_formatted"
code_template:
  python: |
    def print_formatted(name, age):
        """
        格式化输出个人信息

        Args:
            name: 人名（字符串）
            age: 年龄（整数）

        Returns:
            格式化的字符串，格式为："你好，我是[name]，今年[age]岁。"
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "[\"小明\", 18]"
    output: "\"你好，我是小明，今年18岁。\""
    is_sample: true
  - input: "[\"张三\", 25]"
    output: "\"你好，我是张三，今年25岁。\""
    is_sample: false
  - input: "[\"李四\", 30]"
    output: "\"你好，我是李四，今年30岁。\""
    is_sample: false
---
## 题目描述

编写一个函数，实现格式化输出个人信息。

### 输入格式

函数接收两个参数：
- `name`：人名（字符串类型）
- `age`：年龄（整数类型）

### 输出格式

返回一个格式化的字符串，格式为：`"你好，我是[name]，今年[age]岁。"`

其中`[name]`和`[age]`需要替换为实际传入的参数值。

### 示例

**输入：**
```python
print_formatted("小明", 18)
```

**输出：**
```
"你好，我是小明，今年18岁。"
```

**输入：**
```python
print_formatted("张三", 25)
```

**输出：**
```
"你好，我是张三，今年25岁。"
```

### 提示

1. 使用字符串拼接或f-string来实现格式化
2. f-string是Python 3.6+推荐的字符串格式化方式，语法清晰简洁
3. f-string的语法：`f"文字{变量}更多文字"`

**示例代码：**
```python
# 方法1：使用f-string（推荐）
def print_formatted(name, age):
    return f"你好，我是{name}，今年{age}岁。"

# 方法2：使用字符串拼接
def print_formatted(name, age):
    return "你好，我是" + name + "，今年" + str(age) + "岁。"

# 方法3：使用format()方法
def print_formatted(name, age):
    return "你好，我是{}，今年{}岁。".format(name, age)
```

### 注意事项
- 确保函数返回字符串类型，而不是直接打印
- 注意输出格式中的标点符号（中文字符的句号）
- 不要添加额外的空格或换行符

---
*本题目基于 Python 教学平台标准格式设计。*
