---
title: "从列表创建集合"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "create_set"
code_template:
  python: |
    def create_set(items):
        """
        从列表创建集合

        Args:
            items: 一个列表

        Returns:
            set: 包含列表元素（去重后）的集合
        """
        # 请在此实现你的代码
        # 提示：使用 set() 函数
        pass
test_cases:
  - input: "[1,2,2,3,3,3]"
    output: "[1,2,3]"
    is_sample: true
  - input: '["a","b","a","c"]'
    output: '["a","b","c"]'
    is_sample: true
  - input: "[1,2,3]"
    output: "[1,2,3]"
    is_sample: false
  - input: "[]"
    output: "[]"
    is_sample: false
  - input: "[5,5,5,5]"
    output: "[5]"
    is_sample: false
---
## 题目描述

编写一个函数，从列表创建集合，自动去除重复元素。

### 输入格式

一个列表 items。

### 输出格式

返回一个包含列表元素（去重后）的集合（表示为列表格式，因为 JSON 不支持集合）。

### 示例

**输入：**
```
[1, 2, 2, 3, 3, 3]
```

**输出：**
```
[1, 2, 3]
```

### 提示

使用 `set()` 函数从列表创建集合：`set(items)`

### 注意事项

- 集合会自动去除重复元素
- 集合中的元素是无序的，但测试用例会接受任意顺序
- 空列表创建空集合
- 集合中的元素必须是可哈希的（不可变类型）

---
*本题目基于 Python 教学平台标准格式设计。*
