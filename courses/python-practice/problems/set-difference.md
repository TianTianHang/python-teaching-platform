---
title: "集合差集"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "set_difference"
code_template:
  python: |
    def set_difference(set1, set2):
        """
        计算两个集合的差集（在 set1 但不在 set2 中的元素）

        Args:
            set1: 第一个集合（用列表表示）
            set2: 第二个集合（用列表表示）

        Returns:
            list: set1 减去 set2 后的差集
        """
        # 请在此实现你的代码
        # 提示：使用 - 运算符或 difference() 方法
        pass
test_cases:
  - input: "[[1,2,3,4,5],[3,4,5]]"
    output: "[1,2]"
    is_sample: true
  - input: '[["a","b","c"],["b"]]'
    output: '["a","c"]'
    is_sample: true
  - input: "[[1,2],[1,2]]"
    output: "[]"
    is_sample: false
  - input: "[[1,2,3],[]]"
    output: "[1,2,3]"
    is_sample: false
  - input: "[[],[1,2]]"
    output: "[]"
    is_sample: false
---
## 题目描述

编写一个函数，计算两个集合的差集（在第一个集合中但不在第二个集合中的元素）。

### 输入格式

两个集合 [set1, set2]，用列表表示。

### 输出格式

返回 set1 减去 set2 后的差集（表示为列表格式）。如果没有差集，返回空列表。

### 示例

**输入：**
```
[[1, 2, 3, 4, 5], [3, 4, 5]]
```

**输出：**
```
[1, 2]
```

### 提示

- 方法 1：使用 `-` 运算符：`set(set1) - set(set2)`
- 方法 2：使用 `difference()` 方法：`set(set1).difference(set2)`

### 注意事项

- 差集只存在于 set1 但不存在于 set2 中的元素
- 如果两个集合相同，返回空列表
- 空集合减去任何集合都是空集合
- 任何集合减去空集合得到原集合
- 返回列表格式，元素顺序不重要

---
*本题目基于 Python 教学平台标准格式设计。*
