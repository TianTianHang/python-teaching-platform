---
title: "Pandas 数据筛选方法填空"
type: "fillblank"
difficulty: 2
chapter: 1
is_multiple_choice: false
options:
  A: "query"
  B: "filter"
  C: "loc"
  D: "iloc"
correct_answer: "C"
---
## 题目描述

在 Pandas 中，使用标签选择数据行的正确方法是？

### 题目内容

以下代码使用标签选择 DataFrame 中特定行，请选择正确的填空选项：

```python
import pandas as pd

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# 选择名为 'Bob' 的行
bob_row = df[______['name'] == 'Bob']
```

---

*本题基于 Python 教学平台标准格式设计。*