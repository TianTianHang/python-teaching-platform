---
title: "元组转列表"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "tuple_to_list"
code_template:
  python: |
    def tuple_to_list(t):
        """
        将元组转换为列表

        Args:
            t: 一个元组

        Returns:
            list: 包含相同元素的列表
        """
        # 请在此实现你的代码
        # 提示：使用 list() 函数
        pass
test_cases:
  - input: "(1,2,3)"
    output: "[1,2,3]"
    is_sample: true
  - input: "('a','b','c')"
    output: '["a","b","c"]'
    is_sample: true
  - input: "()"
    output: "[]"
    is_sample: false
  - input: "(42,)"
    output: "[42]"
    is_sample: false
  - input: "(1,2,3,4,5)"
    output: "[1,2,3,4,5]"
    is_sample: false
---
## 题目描述

编写一个函数，将元组转换为列表。

### 输入格式

一个元组 t。

### 输出格式

返回包含相同元素的列表。

### 示例

**输入：**
```
(1, 2, 3)
```

**输出：**
```
[1, 2, 3]
```

### 提示

使用 `list()` 函数将元组转换为列表：`list(t)`

### 注意事项

- 空元组转换为空列表
- 元素的顺序保持不变
- 列表是可变的，元组是不可变的

---
*本题目基于 Python 教学平台标准格式设计。*
