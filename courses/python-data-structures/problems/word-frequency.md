---
title: "词频统计"
type: "algorithm"
difficulty: 2
chapter: 3
time_limit: 1000
memory_limit: 256
solution_name:
  python: "word_frequency"
code_template:
  python: |
    def word_frequency(text):
        """
        统计文本中每个单词出现的频率

        Args:
            text: 文本字符串，单词之间用空格分隔

        Returns:
            返回一个字典，键是单词，值是出现次数
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "\"apple banana apple orange banana apple\""
    output: "{\"apple\": 3, \"banana\": 2, \"orange\": 1}"
    is_sample: true
  - input: "\"hello world hello python\""
    output: "{\"hello\": 2, \"world\": 1, \"python\": 1}"
    is_sample: false
  - input: "\"a a a b b c\""
    output: "{\"a\": 3, \"b\": 2, \"c\": 1}"
    is_sample: false
unlock_conditions:
  type: "prerequisite"
  prerequisites: ["list-statistics.md"]
---
## 题目描述

编写一个函数，统计文本中每个单词出现的频率。

### 输入格式

函数接收一个参数：
- `text`：文本字符串，单词之间用空格分隔

### 输出格式

返回一个字典，键是单词，值是出现次数。字典中的单词应该按出现次数降序排列，如果出现次数相同，按单词字母顺序升序排列。

### 示例

**示例1：**
```python
word_frequency("apple banana apple orange banana apple")
# 返回：{"apple": 3, "banana": 2, "orange": 1}
```

**示例2：**
```python
word_frequency("hello world hello python")
# 返回：{"hello": 2, "world": 1, "python": 1}
```

### 提示

1. 使用`text.split()`方法将字符串分割成单词列表
2. 使用字典来统计每个单词出现的次数
3. 处理大小写转换（可以将所有单词转换为小写）
4. 使用`sorted()`函数或`collections.Counter`进行排序

**示例代码：**
```python
def word_frequency(text):
    # 分割单词
    words = text.lower().split()  # 转换为小写并分割

    # 使用字典统计词频
    freq = {}
    for word in words:
        if word in freq:
            freq[word] += 1
        else:
            freq[word] = 1

    # 按频率降序、单词升序排序
    sorted_freq = dict(sorted(freq.items(),
                             key=lambda item: (-item[1], item[0])))

    return sorted_freq

# 更简洁的实现
def word_frequency(text):
    words = text.lower().split()
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return dict(sorted(freq.items(), key=lambda item: (-item[1], item[0])))
```

### 注意事项
- 忽略大小写，将所有单词转换为小写
- 返回的字典要按频率降序排列
- 频率相同时，按单词字母顺序升序排列
- 确保去除了标点符号（本题暂不考虑标点）

### 进阶要求
- 如果你想挑战，可以尝试去除标点符号：
```python
import string
translator = str.maketrans('', '', string.punctuation)
text = text.translate(translator)  # 去除标点符号
```

---
*本题目基于 Python 教学平台标准格式设计。*
