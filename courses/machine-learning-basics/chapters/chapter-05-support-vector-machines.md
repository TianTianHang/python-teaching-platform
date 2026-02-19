---
title: "支持向量机"
order: 5
unlock_conditions:
  type: "prerequisite"
  prerequisites: [4]
---
## 支持向量机

### 章节概述

支持向量机（Support Vector Machine，SVM）是一种强大的分类算法。它的核心思想是找到一个最优的分类超平面，使得不同类别的数据点之间的间隔最大化。本章将学习 SVM 的原理、核函数技巧以及使用 scikit-learn 实践。

### 知识点 1：SVM 基本概念

**描述：**

SVM 的目标是找到一个超平面，将两类数据分开，并且使离超平面最近的那些点（支持向量）到超平面的距离（间隔）最大化。

**核心概念：**

- **超平面**：在二维空间中是一条直线，在三维空间中是一个平面，在高维空间中是超平面
- **支持向量**：离决策边界最近的那些数据点
- **间隔**：支持向量到超平面的距离

**数学表示：**

超平面方程：$w \cdot x + b = 0$

分类决策：
- 如果 $w \cdot x + b \geq 0$，预测为类别 1
- 如果 $w \cdot x + b < 0$，预测为类别 0

**优化目标：**

$$\min_{w,b} \frac{1}{2}\|w\|^2$$

约束条件：
$$y^{(i)}(w \cdot x^{(i)} + b) \geq 1, \quad i = 1, ..., m$$

**直观图示：**

```
       类别 1                 类别 0
    ○  ○  ○               ×  ×  ×
  ○  ○  ○  ○           ×  ×  ×  ×
    ○  ────────           ×
       支持向量
           ↑
      最优超平面
       (最大间隔)
```

**解释：**

- SVM 只关心支持向量，其他点不影响决策边界
- 最大间隔策略使模型具有更好的泛化能力
- 间隔宽度为 $2/\|w\|$，最大化间隔等价于最小化 $\|w\|^2$

### 知识点 2：核函数

**描述：**

当数据不是线性可分时，SVM 通过核函数将数据映射到高维空间，在高维空间中寻找线性可分的超平面。

**常用核函数：**

| 核函数 | 公式 | 适用场景 |
|--------|------|----------|
| 线性核 | $K(x, x') = x \cdot x'$ | 线性可分数据 |
| 多项式核 | $K(x, x') = (x \cdot x' + c)^d$ | 需要非线性边界 |
| RBF 核（高斯核） | $K(x, x') = \exp(-\gamma\|x - x'\|^2)$ | 复杂非线性数据 |

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.datasets import make_circles, make_moons

# 创建非线性可分数据
X_circles, y_circles = make_circles(n_samples=200, factor=0.3, noise=0.1, random_state=42)

# 创建不同的 SVM 模型
models = [
    ('线性核 (Linear)', svm.SVC(kernel='linear', C=1)),
    ('多项式核 (Poly, d=3)', svm.SVC(kernel='poly', degree=3, C=1)),
    ('RBF 核', svm.SVC(kernel='rbf', gamma=2, C=1)),
]

plt.figure(figsize=(15, 4))

for idx, (name, model) in enumerate(models):
    # 训练模型
    model.fit(X_circles, y_circles)

    # 创建子图
    plt.subplot(1, 3, idx + 1)

    # 绘制数据点
    plt.scatter(X_circles[y_circles == 0, 0], X_circles[y_circles == 0, 1],
                c='blue', marker='o', label='类别 0', alpha=0.6)
    plt.scatter(X_circles[y_circles == 1, 0], X_circles[y_circles == 1, 1],
                c='red', marker='s', label='类别 1', alpha=0.6)

    # 绘制决策边界
    x_min, x_max = X_circles[:, 0].min() - 0.5, X_circles[:, 0].max() + 0.5
    y_min, y_max = X_circles[:, 1].min() - 0.5, X_circles[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))
    Z = model.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.contour(xx, yy, Z, levels=[-1, 0, 1], linestyles=['--', '-', '--'],
                colors=['green', 'black', 'green'], linewidths=1.5)
    plt.contourf(xx, yy, Z, levels=[-100, 0, 100], alpha=0.2, colors=['blue', 'red'])

    # 标记支持向量
    plt.scatter(model.support_vectors_[:, 0], model.support_vectors_[:, 1],
                s=100, facecolors='none', edgecolors='yellow', linewidths=2,
                label='支持向量')

    plt.xlabel('特征 1')
    plt.ylabel('特征 2')
    plt.title(f'{name}\n支持向量数量: {len(model.support_vectors_)}')
    plt.legend(loc='upper right', fontsize=8)
    plt.grid(True, linestyle=':', alpha=0.3)

plt.tight_layout()
plt.show()
```

**解释：**

- **线性核**：适合线性可分数据，计算快速
- **多项式核**：可以构造复杂的决策边界，degree 控制多项式次数
- **RBF 核**：最常用的核函数，gamma 控制影响范围
  - gamma 小：决策边界平滑，可能欠拟合
  - gamma 大：决策边界复杂，可能过拟合
- 支持向量用黄色圈标记，它们决定了决策边界的位置

### 知识点 3：scikit-learn SVM 实践

**描述：**

scikit-learn 的 `SVC` 类提供了 SVM 分类器的实现。重要的超参数包括 `C`（正则化参数）和 `gamma`（RBF 核参数）。

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
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

# 基础 SVM 模型
model = SVC(kernel='rbf', random_state=42)
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"测试集准确率: {accuracy:.4f}")
print(f"支持向量数量: {len(model.support_vectors_)}")
print(f"支持向量索引: {model.support_[:10]}...")  # 显示前10个

# 超参数调优
print("\n" + "="*50)
print("超参数调优（网格搜索）")
print("="*50)

# 定义参数网格
param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': [0.001, 0.01, 0.1, 1],
    'kernel': ['rbf']
}

# 网格搜索
grid_search = GridSearchCV(
    SVC(random_state=42),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳交叉验证分数: {grid_search.best_score_:.4f}")

# 使用最佳模型
best_model = grid_search.best_estimator_
y_pred_best = best_model.predict(X_test)
print(f"测试集准确率（最佳模型）: {accuracy_score(y_test, y_pred_best):.4f}")

# 可视化不同 C 和 gamma 的影响
print("\n" + "="*50)
print("C 和 gamma 参数的影响")
print("="*50)

C_values = [0.1, 1, 10]
gamma_values = [0.1, 1, 10]

plt.figure(figsize=(12, 9))

plot_idx = 1
for C in C_values:
    for gamma in gamma_values:
        model = SVC(kernel='rbf', C=C, gamma=gamma, random_state=42)
        model.fit(X_train, y_train)

        plt.subplot(3, 3, plot_idx)

        # 绘制数据点
        plt.scatter(X_train[y_train == 0, 0], X_train[y_train == 0, 1],
                    c='blue', marker='o', alpha=0.5)
        plt.scatter(X_train[y_train == 1, 0], X_train[y_train == 1, 1],
                    c='red', marker='s', alpha=0.5)

        # 绘制决策边界
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                             np.linspace(y_min, y_max, 100))
        Z = model.decision_function(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        plt.contourf(xx, yy, Z, levels=[-100, 0, 100], alpha=0.2,
                     colors=['blue', 'red'])
        plt.contour(xx, yy, Z, levels=[0], colors='black', linewidths=1.5)

        # 绘制支持向量
        plt.scatter(model.support_vectors_[:, 0], model.support_vectors_[:, 1],
                    s=80, facecolors='none', edgecolors='yellow', linewidths=1.5)

        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))

        plt.title(f'C={C}, gamma={gamma}\n训练:{train_acc:.2f} 测试:{test_acc:.2f}\nSV:{len(model.support_vectors_)}',
                  fontsize=9)
        plt.xticks([])
        plt.yticks([])

        plot_idx += 1

plt.tight_layout()
plt.show()
```

**参数说明：**

- **C 参数**：正则化强度的倒数
  - C 小：更大的正则化，决策边界平滑，可能欠拟合
  - C 大：更小的正则化，决策边界复杂，可能过拟合

- **gamma 参数**（RBF 核）：单个训练样本的影响范围
  - gamma 小：影响范围大，决策边界平滑
  - gamma 大：影响范围小，决策边界围绕单个点

### 知识点 4：SVM 多分类

**描述：**

SVM 本质上是二分类算法。对于多分类问题，scikit-learn 提供了两种策略：

1. **一对一（One-vs-One）**：为每两类创建一个分类器
   - n 类需要 n(n-1)/2 个分类器
   - 投票决定最终类别

2. **一对多（One-vs-Rest）**：为每类创建一个分类器
   - n 类需要 n 个分类器
   - 选择输出分数最高的类别

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 创建三分类数据
X, y = make_blobs(
    n_samples=300,
    centers=3,
    n_features=2,
    random_state=42,
    cluster_std=1.5
)

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 训练多分类 SVM（默认使用 one-vs-one 策略）
model_ovo = SVC(kernel='rbf', decision_function_shape='ovo', random_state=42)
model_ovo.fit(X_train, y_train)

y_pred_ovo = model_ovo.predict(X_test)
print("One-vs-One 策略:")
print(f"准确率: {accuracy_score(y_test, y_pred_ovo):.4f}")
print(f"决策函数形状: {model_ovo.decision_function(X_test).shape}")

# 使用 one-vs-rest 策略
model_ovr = SVC(kernel='rbf', decision_function_shape='ovr', random_state=42)
model_ovr.fit(X_train, y_train)

y_pred_ovr = model_ovr.predict(X_test)
print("\nOne-vs-Rest 策略:")
print(f"准确率: {accuracy_score(y_test, y_pred_ovr):.4f}")
print(f"决策函数形状: {model_ovr.decision_function(X_test).shape}")

# 可视化决策边界
plt.figure(figsize=(12, 5))

for idx, (model, title) in enumerate([(model_ovo, 'One-vs-One'),
                                        (model_ovr, 'One-vs-Rest')]):
    plt.subplot(1, 2, idx + 1)

    # 绘制数据点
    colors = ['blue', 'red', 'green']
    markers = ['o', 's', '^']
    for i in range(3):
        plt.scatter(X_test[y_test == i, 0], X_test[y_test == i, 1],
                    c=colors[i], marker=markers[i], label=f'类别 {i}', alpha=0.6)

    # 绘制决策边界
    x_min, x_max = X[:, 0].min() - 2, X[:, 0].max() + 2
    y_min, y_max = X[:, 1].min() - 2, X[:, 1].max() + 2
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.contourf(xx, yy, Z, alpha=0.3, levels=2)
    plt.contour(xx, yy, Z, colors='black', linewidths=1)

    plt.xlabel('特征 1')
    plt.ylabel('特征 2')
    plt.title(f'{title}\n准确率: {accuracy_score(y_test, model.predict(X_test)):.4f}')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

# 详细分类报告
print("\n分类报告 (One-vs-One):")
print(classification_report(y_test, y_pred_ovo))
```

**解释：**

- `decision_function_shape='ovo'`：一对一策略，默认选项
- `decision_function_shape='ovr'`：一对多策略
- 对于少量类别，两种策略差异不大
- 对于大量类别，ovr 通常更高效

### 本章小结

本章学习了支持向量机（SVM）这一强大的分类算法：

- **基本原理**：最大间隔分类，支持向量决定决策边界
- **核函数**：线性核、多项式核、RBF 核处理非线性数据
- **超参数**：C 控制正则化，gamma 控制 RBF 核的影响范围
- **多分类**：通过一对一或一对多策略实现

SVM 在中小型数据集上表现优异，特别适合高维数据和分类边界复杂的情况。

---
*本章内容基于 Python 教学平台标准格式设计。*
