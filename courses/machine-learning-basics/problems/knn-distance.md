---
title: "KNN 距离计算填空"
type: "fill-blank"
difficulty: 2
chapter: 6
is_multiple_choice: false
options:
  A: "np.sum(x_test - X_train[i])"
  B: "np.sqrt(np.sum((x_test - X_train[i]) ** 2))"
  C: "np.linalg.norm(x_test - X_train[i])"
  D: "np.abs(x_test - X_train[i]).sum()"
correct_answer: "B"
---
## 题目描述

在 KNN 算法的实现中，需要计算测试样本到所有训练样本的距离。请选择正确的欧氏距离计算公式。

### 题目内容

以下代码用于计算欧氏距离，请选择正确的填空选项：

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
test_cases:
  - input: "[[[1, 1], [2, 2], [3, 3], [4, 4]], [0, 0, 1, 1], [2.5, 2.5], 3]"
    output: "[{\"distance\": 0.7071067811865476, \"label\": 0}, {\"distance\": 0.7071067811865476, \"label\": 1}, {\"distance\": 2.1213203435596424, \"label\": 1}]"
    is_sample: true
  - input: "[[[0, 0], [1, 0], [0, 1]], [0, 1, 1], [0.2, 0.2], 2]"
    output: "[{\"distance\": 0.282842712474619, \"label\": 0}, {\"distance\": 0.8246211251235321, \"label\": 1}]"
    is_sample: false
  - input: "[[[1], [2], [3], [4], [5]], [0, 0, 1, 1, 1], [3.5], 3]"
    output: "[{\"distance\": 0.5, \"label\": 1}, {\"distance\": 1.5, \"label\": 1}, {\"distance\": 2.5, \"label\": 0}]"
    is_sample: false
---
## 题目描述

实现 KNN 算法的距离计算部分，找到测试样本的 K 个最近邻居。

### 输入格式

- `X_train`：训练集特征，二维列表
- `y_train`：训练集标签，列表（0 或 1）
- `x_test`：测试样本，列表
- `k`：需要返回的邻居数量

### 输出格式

返回 K 个最近邻居的列表，每个元素包含：
- `distance`：欧氏距离
- `label`：训练样本的标签

按距离从小到大排序。

### 示例

**输入：**
```
X_train = [[1, 1], [2, 2], [3, 3], [4, 4]]
y_train = [0, 0, 1, 1]
x_test = [2.5, 2.5]
k = 3
```

**计算过程：**
- 到 [1, 1] 的距离: √2.25 + √2.25 ≈ 2.12
- 到 [2, 2] 的距离: √0.25 + √0.25 ≈ 0.707
- 到 [3, 3] 的距离: √0.25 + √0.25 ≈ 0.707
- 到 [4, 4] 的距离: √2.25 + √2.25 ≈ 2.12

**输出：**
```json
[
  {"distance": 0.707, "label": 0},
  {"distance": 0.707, "label": 1},
  {"distance": 2.121, "label": 1}
]
```

### 提示

欧氏距离计算：
```python
dist = np.sqrt(np.sum((x_test - X_train[i]) ** 2))
```

使用 lambda 函数排序：
```python
distances.sort(key=lambda x: x['distance'])
```

### 注意事项

- 距离应为浮点数
- 标签应为整数
- 确保结果按距离升序排列
*本题目基于 Python 教学平台标准格式设计。*
