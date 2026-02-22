---
title: "Pandas 数据筛选方法填空"
type: "fillblank"
difficulty: 2
chapter: 1
content_with_blanks: |
  在 Pandas 中，使用标签选择数据行的正确方法是 [blank1]。
  使用位置索引选择数据行的方法是 [blank2]。

blanks:
  blank1:
    answers: ["loc"]
    case_sensitive: false
  blank2:
    answers: ["iloc"]
    case_sensitive: false
blank_count: 2
---

## 题目描述

在 Pandas 中，使用标签选择数据行的正确方法是什么？

### 题目内容

以下代码使用标签选择 DataFrame 中特定行，请填写正确的方法：

```python
import pandas as pd

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
}, index=['a', 'b', 'c'])

# 使用标签选择名为 'b' 的行
bob_row = df.______['b']

# 使用位置索引选择第一行
first_row = df.______[0]
```

---

*本题基于 Python 教学平台标准格式设计。*
