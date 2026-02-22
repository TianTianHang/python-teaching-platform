---
title: "Pandas 方法填空"
type: "fillblank"
difficulty: 2
chapter: 1
content_with_blanks: |
  Pandas 中，如果 DataFrame 包含缺失值（NaN），想要删除所有包含缺失值的行，应该使用 [blank1] 方法。

blanks:
  blank1:
    answers: ["dropna"]
    case_sensitive: false
blank_count: 1
---

## 题目描述

Pandas 中，如果 DataFrame 包含缺失值（NaN），想要删除所有包含缺失值的行，应该使用哪个方法？

### 题目内容

Pandas 中，如果 DataFrame 包含缺失值（NaN），想要删除所有包含缺失值的行，应该使用哪个方法？

```python
import pandas as pd

df = pd.DataFrame({
    'A': [1, 2, None],
    'B': [4, None, 6]
})

df = df.______()  # 删除包含缺失值的行
```

---

*本题基于 Python 教学平台标准格式设计。*
