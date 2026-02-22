---
title: "KNN 距离计算填空"
type: "fillblank"
difficulty: 2
chapter: 6
content_with_blanks: |
  在 KNN 算法中，计算两个点之间的欧氏距离，使用 NumPy 实现的代码是：dist = [blank1]

blanks:
  blank1:
    answers: ["np.sqrt(np.sum((x_test - X_train[i]) ** 2))"]
    case_sensitive: true
blank_count: 1
---

## 题目描述

在 KNN 算法的实现中，需要计算测试样本到所有训练样本的距离。请填写正确的欧氏距离计算代码。

### 题目内容

以下代码用于计算欧氏距离，请填写正确的表达式：

```python
import numpy as np

def knn_distances(X_train, y_train, x_test, k):
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)

    distances = []

    for i in range(len(X_train)):
        dist = ______  # 计算欧氏距离
        distances.append({
            'distance': dist,
            'label': int(y_train[i])
        })

    distances.sort(key=lambda x: x['distance'])
    return distances[:k]
```

---

*本题基于 Python 教学平台标准格式设计。*
