---
title: "获取字典值"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "get_dict_value"
code_template:
  python: |
    def get_dict_value(d, key):
        """
        获取字典中指定键的值

        Args:
            d: 一个字典
            key: 要查找的键

        Returns:
            键对应的值，如果键不存在返回 None
        """
        # 请在此实现你的代码
        # 提示：使用 d[key] 或 d.get(key) 方法
        pass
test_cases:
  - input: '[{"name":"Tom","age":18},"name"]'
    output: '"Tom"'
    is_sample: true
  - input: '[{"a":1,"b":2},"b"]'
    output: "2"
    is_sample: true
  - input: '[{"x":10,"y":20},"z"]'
    output: "null"
    is_sample: false
  - input: '[{"count":5},"count"]'
    output: "5"
    is_sample: false
  - input: '[{},"any"]'
    output: "null"
    is_sample: false
---
## 题目描述

编写一个函数，获取字典中指定键对应的值。

### 输入格式

[字典 d, 键 key]。

### 输出格式

返回键对应的值。如果键不存在，返回 null。

### 示例

**输入：**
```
[{"name": "Tom", "age": 18}, "name"]
```

**输出：**
```
"Tom"
```

### 提示

- 使用 `d[key]` 访问字典值（键不存在时会报错）
- 使用 `d.get(key)` 访问字典值（键不存在时返回 None）
- 推荐使用 `d.get(key)` 方法

### 注意事项

- Python 的 None 在 JSON 中表示为 null
- 字典的键区分大小写
- 返回 null 的原因是处理键不存在的情况

---
*本题目基于 Python 教学平台标准格式设计。*
