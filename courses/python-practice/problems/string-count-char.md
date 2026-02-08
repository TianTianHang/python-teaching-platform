---
title: "统计字符出现次数"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "count_char"
code_template:
  python: |
    def count_char(s, char):
        """
        统计字符在字符串中出现的次数

        Args:
            s: 一个字符串
            char: 要统计的字符（单字符字符串）

        Returns:
            int: char 在 s 中出现的次数
        """
        # 请在此实现你的代码
        # 提示：使用 count() 方法
        pass
test_cases:
  - input: '["hello","l"]'
    output: "2"
    is_sample: true
  - input: '["banana","a"]'
    output: "3"
    is_sample: true
  - input: '["hello","x"]'
    output: "0"
    is_sample: false
  - input: '["mississippi","s"]'
    output: "4"
    is_sample: false
  - input: '["aaaaa","a"]'
    output: "5"
    is_sample: false
---
## 题目描述

编写一个函数，统计某个字符在字符串中出现的次数。

### 输入格式

[字符串 s, 字符 char]，char 是单字符字符串。

### 输出格式

返回 char 在 s 中出现的次数（整数）。

### 示例

**输入：**
```
["hello", "l"]
```

**输出：**
```
2
```

### 提示

使用字符串的 `count()` 方法：`s.count(char)`

### 注意事项

- count() 方法区分大小写
- 如果字符不存在，返回 0
- char 参数始终是单字符字符串

---
*本题目基于 Python 教学平台标准格式设计。*
