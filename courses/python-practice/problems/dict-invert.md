---
title: "字典键值互换"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "invert_dict"
code_template:
  python: |
    def invert_dict(d):
        """
        将字典的键和值互换

        Args:
            d: 一个字典

        Returns:
            dict: 键值互换后的新字典
        """
        # 请在此实现你的代码
        # 提示：使用字典推导式 {v: k for k, v in d.items()}
        pass
test_cases:
  - input: '{"a":1,"b":2,"c":3}'
    output: '{1:"a",2:"b",3:"c"}'
    is_sample: true
  - input: '{"name":"Tom","age":18}'
    output: '{"Tom":"name",18:"age"}'
    is_sample: true
  - input: '{}'
    output: '{}'
    is_sample: false
  - input: '{"x":10}'
    output: '{10:"x"}'
    is_sample: false
  - input: '{"first":1,"second":2}'
    output: '{1:"first",2:"second"}'
    is_sample: false
---
## 题目描述

编写一个函数，将字典的键和值互换，原来的键变成值，原来的值变成键。

### 输入格式

一个字典 d。

### 输出格式

返回键值互换后的新字典。

### 示例

**输入：**
```
{"a": 1, "b": 2, "c": 3}
```

**输出：**
```
{1: "a", 2: "b", 3: "c"}
```

### 提示

使用字典推导式：
```python
{v: k for k, v in d.items()}
```

### 注意事项

- 空字典互换后仍是空字典
- 如果原字典的值不唯一（有重复），互换后的字典会丢失部分数据（因为键必须唯一）
- 本题目测试用例保证原字典的值都是唯一的

---
*本题目基于 Python 教学平台标准格式设计。*
