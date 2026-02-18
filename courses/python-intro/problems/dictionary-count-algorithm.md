---
title: "单词频率统计"
type: "algorithm"
difficulty: 1
chapter: 9
time_limit: 1000
memory_limit: 256
solution_name:
  python: "count_word_frequency"
code_template:
  python: |
    def count_word_frequency(words):
        """
        统计单词列表中每个单词的出现频率

        Args:
            words: 单词列表

        Returns:
            一个字典，键是单词，值是出现次数
        """
        # 在这里实现你的代码
        pass
test_cases:
  - input: "[['hello', 'world', 'hello', 'python', 'world']]"
    output: "[{'hello': 2, 'world': 2, 'python': 1}]"
    is_sample: true
  - input: "[['apple', 'banana', 'apple', 'orange', 'apple']]"
    output: "[{'apple': 3, 'banana': 1, 'orange': 1}]"
    is_sample: false
  - input: "[[]]"
    output: "[{}]"
    is_sample: false
  - input: "[['a', 'b', 'c']]"
    output: "[{'a': 1, 'b': 1, 'c': 1}]"
    is_sample: false
  - input: "[['a', 'a', 'a', 'a', 'a']]"
    output: "[{'a': 5}]"
    is_sample: false
---

## 题目描述

编写一个函数，统计给定单词列表中每个单词的出现频率。

### 输入格式
一个单词列表，如 ['hello', 'world', 'hello', 'python', 'world']

### 输出格式
一个字典，键是单词，值是该单词的出现次数

### 示例

**输入：**
```
['hello', 'world', 'hello', 'python', 'world']
```

**输出：**
```
{'hello': 2, 'world': 2, 'python': 1}
```

### 提示
- 可以使用字典来存储每个单词的计数
- 遍历列表，对每个单词进行计数
- 如果单词不存在于字典中，则初始化为1，否则增加1

### 注意事项
- 确保代码的正确性和效率
- 处理空列表的情况
- 代码风格要符合 Python PEP 8 规范
*本题目基于 Python 教学平台标准格式设计。*
