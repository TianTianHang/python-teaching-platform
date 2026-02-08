---
title: "添加字典键值对"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "add_key_value"
code_template:
  python: |
    def add_key_value(d, key, value):
        """
        向字典中添加一个键值对

        Args:
            d: 一个字典
            key: 要添加的键
            value: 要添加的值

        Returns:
            dict: 添加后的字典
        """
        # 请在此实现你的代码
        # 提示：使用 d[key] = value 语法
        pass
test_cases:
  - input: '[{"name":"Tom"},"age",18]'
    output: '{"name":"Tom","age":18}'
    is_sample: true
  - input: '[{}],"x",10]'
    output: '{"x":10}'
    is_sample: true
  - input: '[{"a":1},"b",2]'
    output: '{"a":1,"b":2}'
    is_sample: false
  - input: '[{"count":0},"count",1]'
    output: '{"count":1}'
    is_sample: false
  - input: '[{"list":[1,2]},"item",3]'
    output: '{"list":[1,2],"item":3}'
    is_sample: false
---
## 题目描述

编写一个函数，向字典中添加一个键值对。

### 输入格式

[字典 d, 键 key, 值 value]。

### 输出格式

返回添加键值对后的字典。如果键已存在，会覆盖原有值。

### 示例

**输入：**
```
[{"name": "Tom"}, "age", 18]
```

**输出：**
```
{"name": "Tom", "age": 18}
```

### 提示

使用字典赋值语法添加或更新键值对：`d[key] = value`

### 注意事项

- 如果键已存在，会覆盖原有的值
- 可以添加任意类型的值（整数、字符串、列表等）
- 直接修改原字典并返回它即可

---
*本题目基于 Python 教学平台标准格式设计。*
