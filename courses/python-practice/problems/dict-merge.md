---
title: "合并两个字典"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "merge_dicts"
code_template:
  python: |
    def merge_dicts(dict1, dict2):
        """
        合并两个字典

        Args:
            dict1: 第一个字典
            dict2: 第二个字典

        Returns:
            dict: 合并后的新字典
        """
        # 请在此实现你的代码
        # 提示：使用 update() 方法或 | 运算符（Python 3.9+）
        pass
test_cases:
  - input: '[{"a":1},{"b":2}]'
    output: '{"a":1,"b":2}'
    is_sample: true
  - input: '[{"name":"Tom"},{"age":18}]'
    output: '{"name":"Tom","age":18}'
    is_sample: true
  - input: '[{"x":10},{"x":20}]'
    output: '{"x":20}'
    is_sample: false
  - input: '[{},{}]'
    output: '{}'
    is_sample: false
  - input: '[{"a":1,"b":2},{"c":3,"d":4}]'
    output: '{"a":1,"b":2,"c":3,"d":4}'
    is_sample: false
---
## 题目描述

编写一个函数，合并两个字典。

### 输入格式

两个字典 [dict1, dict2]。

### 输出格式

返回合并后的新字典。如果有重复的键，dict2 的值会覆盖 dict1 的值。

### 示例

**输入：**
```
[{"a": 1}, {"b": 2}]
```

**输出：**
```
{"a": 1, "b": 2}
```

### 提示

:::tip{title="方法一（Python 3.9+）" state="collapsed"}
使用 `|` 运算符：`dict1 | dict2`
:::

:::tip{title="方法二" state="collapsed"}
使用 `update()` 方法：
```python
result = dict1.copy()
result.update(dict2)
return result
```
:::

### 注意事项

- 如果有重复的键，dict2 的值会覆盖 dict1 的值
- 空字典与另一个字典合并得到另一个字典
- 原字典不会被修改

---
*本题目基于 Python 教学平台标准格式设计。*
