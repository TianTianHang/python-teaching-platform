---
title: "合并元组"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "merge_tuples"
code_template:
  python: |
    def merge_tuples(t1, t2):
        """
        合并两个元组

        Args:
            t1: 第一个元组
            t2: 第二个元组

        Returns:
            tuple: 合并后的新元组
        """
        # 请在此实现你的代码
        # 提示：使用 + 运算符
        pass
test_cases:
  - input: "[(1,2),(3,4)]"
    output: "(1,2,3,4)"
    is_sample: true
  - input: '[("a",),("b",)]'
    output: '("a","b")'
    is_sample: true
  - input: "[(1,2,3),(4,5)]"
    output: "(1,2,3,4,5)"
    is_sample: false
  - input: "[(),(1,2)]"
    output: "(1,2)"
    is_sample: false
  - input: "[(10,),()]"
    output: "(10,)"
    is_sample: false
---
## 题目描述

编写一个函数，将两个元组合并成一个新元组。

### 输入格式

两个元组 [t1, t2]。

### 输出格式

返回合并后的新元组。

### 示例

**输入：**
```
[(1, 2), (3, 4)]
```

**输出：**
```
(1, 2, 3, 4)
```

### 提示

:::tip{title="提示" state="collapsed"}
使用 `+` 运算符合并元组：`t1 + t2`
:::

### 注意事项

- 原元组不会被修改
- 空元组与另一个元组合并得到另一个元组的内容
- 元组是不可变的，所以操作总是返回新元组

---
*本题目基于 Python 教学平台标准格式设计。*
