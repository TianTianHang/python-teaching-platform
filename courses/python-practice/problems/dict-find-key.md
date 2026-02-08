---
title: "检查键是否存在"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "has_key"
code_template:
  python: |
    def has_key(d, key):
        """
        检查字典中是否存在指定的键

        Args:
            d: 一个字典
            key: 要检查的键

        Returns:
            bool: 如果键存在返回 True，否则返回 False
        """
        # 请在此实现你的代码
        # 提示：使用 `in` 运算符
        pass
test_cases:
  - input: '[{"name":"Tom","age":18},"name"]'
    output: "true"
    is_sample: true
  - input: '[{"a":1,"b":2},"c"]'
    output: "false"
    is_sample: true
  - input: '[{},"any"]'
    output: "false"
    is_sample: false
  - input: '[{"x":10},"x"]'
    output: "true"
    is_sample: false
  - input: '[{"count":5},"COUNT"]'
    output: "false"
    is_sample: false
---
## 题目描述

编写一个函数，检查字典中是否存在指定的键。

### 输入格式

[字典 d, 键 key]。

### 输出格式

返回布尔值，键存在返回 true，不存在返回 false。

### 示例

**输入：**
```
[{"name": "Tom", "age": 18}, "name"]
```

**输出：**
```
true
```

### 提示

使用 `in` 运算符检查键是否存在：`key in d`

### 注意事项

- 字典的键区分大小写
- 空字典中不包含任何键
- 布尔值返回格式为小写：true/false

---
*本题目基于 Python 教学平台标准格式设计。*
