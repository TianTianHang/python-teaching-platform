---
title: "合并两个列表"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "merge_lists"
code_template:
  python: |
    def merge_lists(list1, list2):
        """
        合并两个列表

        Args:
            list1: 第一个列表
            list2: 第二个列表

        Returns:
            list: 合并后的新列表
        """
        # 请在此实现你的代码
        # 提示：使用 + 运算符或 extend() 方法
        pass
test_cases:
  - input: "[[1,2,3],[4,5,6]]"
    output: "[1,2,3,4,5,6]"
    is_sample: true
  - input: '[["a","b"],["c","d"]]'
    output: '["a","b","c","d"]'
    is_sample: true
  - input: "[[1,2],[]]"
    output: "[1,2]"
    is_sample: false
  - input: "[[],[3,4]]"
    output: "[3,4]"
    is_sample: false
  - input: "[[10],[20]]"
    output: "[10,20]"
    is_sample: false
---
## 题目描述

编写一个函数，将两个列表按顺序合并成一个新列表。

### 输入格式

两个列表 [list1, list2]。

### 输出格式

返回合并后的新列表，先包含 list1 的所有元素，再包含 list2 的所有元素。

### 示例

**输入：**
```
[[1, 2, 3], [4, 5, 6]]
```

**输出：**
```
[1, 2, 3, 4, 5, 6]
```

### 提示

使用 `+` 运算符合并列表：`list1 + list2`

### 注意事项

- 原列表不会被修改
- 空列表与任何列表合并得到另一个列表的内容
- 元素的顺序保持不变（先 list1 的元素，后 list2 的元素）

---
*本题目基于 Python 教学平台标准格式设计。*
