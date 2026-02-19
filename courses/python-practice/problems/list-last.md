---
title: "获取列表最后一个元素"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "get_last_element"
code_template:
  python: |
    def get_last_element(items):
        """
        获取列表的最后一个元素

        Args:
            items: 一个列表

        Returns:
            最后一个元素
        """
        # 请在此实现你的代码
        # 提示：使用负索引 [-1]
        pass
test_cases:
  - input: "[1,2,3,4,5]"
    output: "5"
    is_sample: true
  - input: '["a","b","c"]'
    output: '"c"'
    is_sample: true
  - input: "[42]"
    output: "42"
    is_sample: false
  - input: '["hello","world"]'
    output: '"world"'
    is_sample: false
  - input: "[10,20,30]"
    output: "30"
    is_sample: false
---
## 题目描述

编写一个函数，获取列表的最后一个元素。

### 输入格式

一个列表 items。

### 输出格式

返回列表的最后一个元素。

### 示例

**输入：**
```
[1, 2, 3, 4, 5]
```

**输出：**
```
5
```

### 提示

:::tip{title="提示" state="collapsed"}
使用负索引 `[-1]` 获取最后一个元素：`items[-1]`
:::

### 注意事项

- `-1` 表示最后一个元素
- `-2` 表示倒数第二个元素，以此类推
- 列表至少包含一个元素

---
*本题目基于 Python 教学平台标准格式设计。*
