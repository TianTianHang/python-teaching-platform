---
title: "集合并集"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "set_union"
code_template:
  python: |
    def set_union(set1, set2):
        """
        计算两个集合的并集

        Args:
            set1: 第一个集合（用列表表示）
            set2: 第二个集合（用列表表示）

        Returns:
            list: 两个集合的并集
        """
        # 请在此实现你的代码
        # 提示：使用 | 运算符或 union() 方法
        pass
test_cases:
  - input: "[[1,2,3],[3,4,5]]"
    output: "[1,2,3,4,5]"
    is_sample: true
  - input: '[["a","b"],["b","c"]]'
    output: '["a","b","c"]'
    is_sample: true
  - input: "[[1,2],[3,4]]"
    output: "[1,2,3,4]"
    is_sample: false
  - input: "[[],[1,2]]"
    output: "[1,2]"
    is_sample: false
  - input: "[[5,5],[5]]"
    output: "[5]"
    is_sample: false
---
## 题目描述

编写一个函数，计算两个集合的并集（包含所有出现过的元素）。

### 输入格式

两个集合 [set1, set2]，用列表表示。

### 输出格式

返回两个集合的并集（表示为列表格式）。

### 示例

**输入：**
```
[[1, 2, 3], [3, 4, 5]]
```

**输出：**
```
[1, 2, 3, 4, 5]
```

### 提示

- 方法 1：使用 `|` 运算符：`set(set1) | set(set2)`
- 方法 2：使用 `union()` 方法：`set(set1).union(set2)`

### 注意事项

- 并集包含两个集合中的所有不重复元素
- 空集合与任何集合的并集是另一个集合
- 结果是去重后的元素
- 返回列表格式，元素顺序不重要

---
*本题目基于 Python 教学平台标准格式设计。*
