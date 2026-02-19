---
title: "集合交集"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "set_intersection"
code_template:
  python: |
    def set_intersection(set1, set2):
        """
        计算两个集合的交集

        Args:
            set1: 第一个集合（用列表表示）
            set2: 第二个集合（用列表表示）

        Returns:
            list: 两个集合的交集
        """
        # 请在此实现你的代码
        # 提示：使用 & 运算符或 intersection() 方法
        pass
test_cases:
  - input: "[[1,2,3],[3,4,5]]"
    output: "[3]"
    is_sample: true
  - input: '[["a","b","c"],["b","c","d"]]'
    output: '["b","c"]'
    is_sample: true
  - input: "[[1,2],[3,4]]"
    output: "[]"
    is_sample: false
  - input: "[[1,2,3],[]]"
    output: "[]"
    is_sample: false
  - input: "[[5,5,5],[5]]"
    output: "[5]"
    is_sample: false
---
## 题目描述

编写一个函数，计算两个集合的交集（同时存在于两个集合中的元素）。

### 输入格式

两个集合 [set1, set2]，用列表表示。

### 输出格式

返回两个集合的交集（表示为列表格式）。如果没有交集，返回空列表。

### 示例

**输入：**
```
[[1, 2, 3], [3, 4, 5]]
```

**输出：**
```
[3]
```

### 提示

:::tip{title="方法一" state="collapsed"}
使用 `&` 运算符：`set(set1) & set(set2)`
:::

:::tip{title="方法二" state="collapsed"}
使用 `intersection()` 方法：`set(set1).intersection(set2)`
:::

### 注意事项

- 交集只包含同时存在于两个集合中的元素
- 如果没有共同元素，返回空列表
- 空集合与任何集合的交集是空集合
- 返回列表格式，元素顺序不重要

---
*本题目基于 Python 教学平台标准格式设计。*
