---
title: "统计单词频率"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "count_words"
code_template:
  python: |
    def count_words(words):
        """
        统计单词列表中每个单词出现的频率

        Args:
            words: 一个字符串列表（单词列表）

        Returns:
            dict: 单词到出现次数的映射
        """
        # 请在此实现你的代码
        # 提示：使用字典和 for 循环统计
        pass
test_cases:
  - input: '["apple","banana","apple","orange","banana","apple"]'
    output: '{"apple":3,"banana":2,"orange":1}'
    is_sample: true
  - input: '["a","b","c"]'
    output: '{"a":1,"b":1,"c":1}'
    is_sample: true
  - input: '["hello","hello","hello"]'
    output: '{"hello":3}'
    is_sample: false
  - input: '["x"]'
    output: '{"x":1}'
    is_sample: false
  - input: '[]'
    output: '{}'
    is_sample: false
---
## 题目描述

编写一个函数，统计单词列表中每个单词出现的次数。

### 输入格式

一个字符串列表 words（单词列表）。

### 输出格式

返回一个字典，键是单词，值是该单词在列表中出现的次数。

### 示例

**输入：**
```
["apple", "banana", "apple", "orange", "banana", "apple"]
```

**输出：**
```
{"apple": 3, "banana": 2, "orange": 1}
```

### 提示

使用字典和 for 循环：
```python
result = {}
for word in words:
    if word in result:
        result[word] += 1
    else:
        result[word] = 1
return result
```

或者使用 get() 方法：
```python
result = {}
for word in words:
    result[word] = result.get(word, 0) + 1
return result
```

### 注意事项

- 空列表返回空字典
- 单词区分大小写
- 每个单词至少出现一次（如果在列表中存在）

---
*本题目基于 Python 教学平台标准格式设计。*
