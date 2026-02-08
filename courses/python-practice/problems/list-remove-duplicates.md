---
title: "去除列表重复元素"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "remove_duplicates"
code_template:
  python: |
    def remove_duplicates(items):
        """
        去除列表中的重复元素

        Args:
            items: 一个列表

        Returns:
            list: 去除重复后的新列表
        """
        # 请在此实现你的代码
        # 提示：先转为 set() 去重，再转回 list()
        pass
test_cases:
  - input: "[1,2,2,3,3,3,4]"
    output: "[1,2,3,4]"
    is_sample: true
  - input: '["a","b","a","c","b"]'
    output: '["a","b","c"]'
    is_sample: true
  - input: "[1,2,3]"
    output: "[1,2,3]"
    is_sample: false
  - input: "[5,5,5,5]"
    output: "[5]"
    is_sample: false
  - input: "[]"
    output: "[]"
    is_sample: false
---
## 题目描述

编写一个函数，去除列表中的重复元素，返回一个新列表。

### 输入格式

一个列表 items。

### 输出格式

返回去除重复后的新列表，保持首次出现的顺序。

### 示例

**输入：**
```
[1, 2, 2, 3, 3, 3, 4]
```

**输出：**
```
[1, 2, 3, 4]
```

### 提示

将列表转为集合可以自动去重，然后转回列表：
```python
list(set(items))
```

注意：使用 set 会改变原始顺序。如果需要保持顺序，可以：
```python
seen = set()
result = []
for x in items:
    if x not in seen:
        seen.add(x)
        result.append(x)
return result
```

### 注意事项

- 空列表去重后仍是空列表
- 返回的是新列表，原列表不会被修改
- 测试用例可能检查顺序，建议使用保持顺序的方法

---
*本题目基于 Python 教学平台标准格式设计。*
