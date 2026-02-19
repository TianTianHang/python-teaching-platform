---
title: "K 近邻算法"
order: 6
unlock_conditions:
  type: "prerequisite"
  prerequisites: [5]
---
## K 近邻算法

### 章节概述

K 近邻（K-Nearest Neighbors，KNN）是一种简单但有效的机器学习算法。它的核心思想是"近朱者赤，近墨者黑"——一个样本的类别由它最近的 K 个邻居的类别决定。KNN 是一种惰性学习算法，不需要显式的训练过程。

### 知识点 1：KNN 算法原理

**描述：**

KNN 是一种基于实例的学习算法。对于新的测试样本，算法会在训练集中找到距离它最近的 K 个样本，根据这 K 个邻居的类别来预测新样本的类别。

**算法步骤：**

1. 计算测试样本与所有训练样本之间的距离
2. 按距离排序，选择最近的 K 个样本
3. 统计这 K 个邻居中各类别的数量
4. 将测试样本归类为数量最多的类别

**分类 vs 回归：**

- **分类问题**：K 个邻居中最多的类别作为预测结果（多数投票）
- **回归问题**：K 个邻居的目标值平均值作为预测结果

**示例代码（手动实现）：**

```python
import numpy as np
from collections import Counter

def euclidean_distance(x1, x2):
    """
    计算欧氏距离

    Args:
        x1, x2: 两个样本点

    Returns:
        欧氏距离
    """
    return np.sqrt(np.sum((x1 - x2) ** 2))

def knn_predict(X_train, y_train, x_test, k=3):
    """
    KNN 分类预测

    Args:
        X_train: 训练集特征，形状 (m, n)
        y_train: 训练集标签，形状 (m,)
        x_test: 测试样本，形状 (n,)
        k: 最近的邻居数量

    Returns:
        预测类别
    """
    # 1. 计算测试样本到所有训练样本的距离
    distances = []
    for i in range(len(X_train)):
        dist = euclidean_distance(x_test, X_train[i])
        distances.append((dist, y_train[i]))

    # 2. 按距离排序
    distances.sort(key=lambda x: x[0])

    # 3. 选择最近的 K 个邻居
    k_nearest = distances[:k]
    k_labels = [label for _, label in k_nearest]

    # 4. 多数投票
    most_common = Counter(k_labels).most_common(1)
    return most_common[0][0]

# 示例使用
if __name__ == "__main__":
    # 创建简单训练数据
    X_train = np.array([
        [1.0, 1.0],
        [1.5, 2.0],
        [2.0, 1.5],
        [6.0, 5.0],
        [7.0, 7.0],
        [8.0, 6.0]
    ])
    y_train = np.array([0, 0, 0, 1, 1, 1])

    # 测试样本
    x_test = np.array([3.0, 3.0])

    # 使用不同的 K 值预测
    for k in [1, 3, 5]:
        prediction = knn_predict(X_train, y_train, x_test, k)
        print(f"K={k} 时，预测类别: {prediction}")
```

**解释：**

- KNN 不需要训练过程，直接在预测时计算距离
- K 的选择对结果影响很大
- 距离度量通常使用欧氏距离，也可以使用曼哈顿距离等

### 知识点 2：距离度量

**描述：**

KNN 的核心是计算样本间的距离。不同的距离度量适合不同类型的数据。

**常用距离度量：**

**1. 欧氏距离（Euclidean Distance）**

$$d(x, y) = \sqrt{\sum_{i=1}^{n}(x_i - y_i)^2}$$

最常见的距离度量，即两点间的直线距离。

**2. 曼哈顿距离（Manhattan Distance）**

$$d(x, y) = \sum_{i=1}^{n}|x_i - y_i|$$

城市街区距离，适合网格状路径。

**示例代码：**

```python
import numpy as np

def euclidean_distance(x1, x2):
    """欧氏距离"""
    return np.sqrt(np.sum((x1 - x2) ** 2))

def manhattan_distance(x1, x2):
    """曼哈顿距离"""
    return np.sum(np.abs(x1 - x2))

def minkowski_distance(x1, x2, p=3):
    """
    闵可夫斯基距离（Minkowski Distance）
    p=1: 曼哈顿距离
    p=2: 欧氏距离
    """
    return np.sum(np.abs(x1 - x2) ** p) ** (1 / p)

# 测试不同距离
point_a = np.array([1, 2, 3])
point_b = np.array([4, 5, 6])

print(f"欧氏距离: {euclidean_distance(point_a, point_b):.4f}")
print(f"曼哈顿距离: {manhattan_distance(point_a, point_b):.4f}")
print(f"闵可夫斯基距离 (p=3): {minkowski_distance(point_a, point_b, p=3):.4f}")
```

**距离度量选择：**

| 度量 | 特点 | 适用场景 |
|------|------|----------|
| 欧氏距离 | 考虑绝对差异，对异常值敏感 | 连续数值特征 |
| 曼哈顿距离 | 对异常值较鲁棒 | 高维稀疏数据 |
| 闵可夫斯基距离 | 通用形式，p 可调 | 需要灵活调整 |

### 知识点 3：scikit-learn KNN 分类

**描述：**

scikit-learn 提供了高效的 KNN 实现，使用 `KNeighborsClassifier` 进行分类。

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import make_classification

# 创建示例数据
X, y = make_classification(
    n_samples=300,
    n_features=2,
    n_redundant=0,
    n_informative=2,
    random_state=42,
    n_clusters_per_class=1,
    class_sep=1.5
)

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 测试不同 K 值的效果
k_values = [1, 3, 5, 11, 21, 51]

plt.figure(figsize=(12, 8))

for idx, k in enumerate(k_values):
    # 创建并训练模型
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)

    # 预测
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # 创建子图
    plt.subplot(2, 3, idx + 1)

    # 绘制训练数据
    plt.scatter(X_train[y_train == 0, 0], X_train[y_train == 0, 1],
                c='blue', marker='o', label='类别 0', alpha=0.5)
    plt.scatter(X_train[y_train == 1, 0], X_train[y_train == 1, 1],
                c='red', marker='s', label='类别 1', alpha=0.5)

    # 绘制决策边界
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.contourf(xx, yy, Z, alpha=0.3, levels=[-1, 0, 1, 2], colors=['blue', 'red'])
    plt.contour(xx, yy, Z, colors='black', linewidths=0.5)

    plt.xlabel('特征 1')
    plt.ylabel('特征 2')
    plt.title(f'K={k}\n准确率: {accuracy:.4f}')
    plt.grid(True, linestyle=':', alpha=0.3)

    if idx == 0:
        plt.legend()

plt.tight_layout()
plt.show()

# 寻找最佳 K 值
print("\n寻找最佳 K 值:")
k_range = range(1, 51)
train_scores = []
test_scores = []

for k in k_range:
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)
    train_scores.append(model.score(X_train, y_train))
    test_scores.append(model.score(X_test, y_test))

best_k = k_range[np.argmax(test_scores)]
best_score = max(test_scores)
print(f"最佳 K 值: {best_k}")
print(f"最佳测试集准确率: {best_score:.4f}")

# 绘制 K 值与准确率的关系
plt.figure(figsize=(10, 5))
plt.plot(k_range, train_scores, 'o-', label='训练集准确率')
plt.plot(k_range, test_scores, 's-', label='测试集准确率')
plt.axvline(x=best_k, color='green', linestyle='--', label=f'最佳 K={best_k}')
plt.xlabel('K 值')
plt.ylabel('准确率')
plt.title('K 值对模型性能的影响')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)
plt.show()
```

**解释：**

- `n_neighbors`：指定邻居数量 K
- K 较小：模型复杂，可能过拟合，决策边界不规则
- K 较大：模型简单，可能欠拟合，决策边界平滑
- 通常选择 K 为奇数，避免投票平局
- 经验法则：K ≈ √n（n 为样本数）

### 知识点 4：KNN 回归

**描述：**

KNN 也可以用于回归问题，预测值为 K 个最近邻目标值的平均值（或加权平均）。

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 创建回归数据
np.random.seed(42)
X = np.random.rand(200, 1) * 10
y = np.sin(X).ravel() + np.random.randn(200) * 0.2

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 测试不同 K 值
k_values = [1, 5, 10, 20]

plt.figure(figsize=(12, 3))

for idx, k in enumerate(k_values):
    # 创建并训练模型
    model = KNeighborsRegressor(n_neighbors=k)
    model.fit(X_train, y_train)

    # 预测
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # 绘制结果
    plt.subplot(1, 4, idx + 1)

    # 绘制训练数据
    plt.scatter(X_train, y_train, c='blue', alpha=0.5, s=20, label='训练数据')

    # 绘制测试数据
    plt.scatter(X_test, y_test, c='green', alpha=0.5, s=20, label='测试数据')

    # 绘制预测曲线
    X_plot = np.linspace(0, 10, 200).reshape(-1, 1)
    y_plot = model.predict(X_plot)
    plt.plot(X_plot, y_plot, 'r-', linewidth=2, label='KNN 预测')

    plt.xlabel('X')
    plt.ylabel('y')
    plt.title(f'K={k}\nMSE: {mse:.4f}, R²: {r2:.4f}')
    plt.grid(True, linestyle=':', alpha=0.5)

    if idx == 0:
        plt.legend(fontsize=8)

plt.tight_layout()
plt.show()
```

**KNN 回归特点：**

- 预测值是邻居目标值的平均值
- 加权 KNN 回归：距离越近的邻居权重越大
- `weights='distance'` 参数可启用加权模式

### 知识点 5：KNN 优缺点

**描述：**

了解 KNN 的优缺点有助于在实际项目中做出合适的选择。

**优点：**

1. **简单直观**：易于理解和实现
2. **无需训练**：是一种惰性学习算法
3. **适用性广**：可用于分类和回归
4. **对异常值不敏感**（K > 1 时）
5. **多分类友好**：天然支持多分类问题

**缺点：**

1. **计算成本高**：预测时需要计算与所有训练样本的距离
2. **存储需求大**：需要存储所有训练数据
3. **对维度敏感**：高维数据容易出现"维度灾难"
4. **需要选择合适的 K 值**：K 值对结果影响大
5. **对数据不平衡敏感**：多数类可能主导预测

**优化建议：**

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 1. 特征缩放：KNN 对特征尺度敏感
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 2. 降维：缓解维度灾难
pca = PCA(n_components=0.95)  # 保留 95% 方差
X_reduced = pca.fit_transform(X_scaled)

# 3. 使用 KD 树或 Ball 树加速（scikit-learn 自动选择）
model = KNeighborsClassifier(
    n_neighbors=5,
    algorithm='auto',  # 自动选择最优算法
    # algorithm='kd_tree'  # 也可以指定
)

# 4. 加权 KNN：距离近的邻居权重更大
model_weighted = KNeighborsClassifier(
    n_neighbors=5,
    weights='distance'  # 默认是 'uniform'
)
```

**KD 树 vs Ball 树：**

| 算法 | 特点 | 适用场景 |
|------|------|----------|
| Brute Force | 暴力搜索，计算所有距离 | 小数据集 |
| KD Tree | 二叉树结构，快速搜索 | 低维数据（< 20 维） |
| Ball Tree | 超球体划分，更适合高维 | 中高维数据 |

### 本章小结

本章学习了 K 近邻算法：

- **算法原理**：基于最近邻居的多数投票
- **距离度量**：欧氏距离、曼哈顿距离、闵可夫斯基距离
- **K 值选择**：影响模型复杂度和泛化能力
- **分类与回归**：KNN 可用于两类问题
- **优缺点**：简单但计算成本高

KNN 是机器学习入门的重要算法，虽然简单，但在许多实际场景中效果良好。理解 KNN 的工作原理有助于理解更复杂的算法。

---
*本章内容基于 Python 教学平台标准格式设计。*
