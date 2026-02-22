---
title: "逻辑回归"
order: 4
unlock_conditions:
  type: "prerequisite"
  prerequisites: [3]
---
## 逻辑回归

### 章节概述

逻辑回归是分类问题的核心算法，虽然名字中有"回归"，但实际上是一种分类算法。它通过 Sigmoid 函数将线性输出映射到 [0, 1] 区间，表示样本属于某一类别的概率。本章将学习二分类问题的解决方法。

### 知识点 1：分类问题与 Sigmoid 函数

**描述：**

分类问题要求预测离散的类别标签，而逻辑回归通过引入 Sigmoid 函数，将线性回归的连续输出转换为概率值。

**Sigmoid 函数：**

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

**性质：**
- 输出范围：(0, 1)
- $\sigma(0) = 0.5$，是决策边界阈值
- 当 $z \to \infty$ 时，$\sigma(z) \to 1$
- 当 $z \to -\infty$ 时，$\sigma(z) \to 0$

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt

def sigmoid(z):
    """
    Sigmoid 激活函数

    Args:
        z: 线性组合结果

    Returns:
        概率值，范围 (0, 1)
    """
    return 1 / (1 + np.exp(-z))

# 可视化 Sigmoid 函数
z = np.linspace(-10, 10, 100)
sigma = sigmoid(z)

plt.figure(figsize=(10, 4))

# Sigmoid 函数曲线
plt.subplot(1, 2, 1)
plt.plot(z, sigma, 'b-', linewidth=2)
plt.axhline(y=0.5, color='r', linestyle='--', label='阈值 0.5')
plt.axvline(x=0, color='g', linestyle='--', label='z=0')
plt.xlabel('z')
plt.ylabel('sigmoid(z)')
plt.title('Sigmoid 函数')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)

# 决策边界示意图
plt.subplot(1, 2, 2)
plt.axhline(y=0.5, color='r', linestyle='-', linewidth=2)
plt.fill_between([-10, 0], 0, 0.5, alpha=0.3, color='blue', label='预测类别 0')
plt.fill_between([0, 10], 0.5, 1, alpha=0.3, color='orange', label='预测类别 1')
plt.xlim(-10, 10)
plt.ylim(0, 1)
plt.xlabel('z')
plt.ylabel('概率')
plt.title('决策边界')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

# 测试 Sigmoid 函数
test_values = [-10, -5, -1, 0, 1, 5, 10]
print("Sigmoid 函数值测试:")
for val in test_values:
    print(f"sigmoid({val:3d}) = {sigmoid(val):.6f}")
```

**解释：**

- Sigmoid 函数将任意实数映射到 (0, 1) 区间
- 输出可以解释为样本属于正类的概率
- 当概率 ≥ 0.5 时，预测为类别 1；否则预测为类别 0
- 决策边界位于 $z = 0$ 处，即 $w \cdot x + b = 0$

### 知识点 2：逻辑回归损失函数

**描述：**

线性回归使用均方误差作为损失函数，但对于分类问题，均方误差是非凸的，会导致梯度下降陷入局部最优。逻辑回归使用交叉熵损失函数，它是凸函数，可以保证找到全局最优解。

**交叉熵损失函数：**

$$J(w,b) = -\frac{1}{m}\sum_{i=1}^{m}[y^{(i)}\log(\hat{y}^{(i)}) + (1-y^{(i)})\log(1-\hat{y}^{(i)})]$$

其中 $\hat{y} = \sigma(w \cdot x + b)$ 是模型预测的概率。

**直观理解：**

- 当 $y = 1$ 时，损失 $= -\log(\hat{y})$，预测越接近 1，损失越小
- 当 $y = 0$ 时，损失 $= -\log(1-\hat{y})$，预测越接近 0，损失越小

**示例代码：**

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def compute_loss(X, y, w, b):
    """
    计算交叉熵损失

    Args:
        X: 特征数据，形状 (m, n)
        y: 标签数据，形状 (m,)，值为 0 或 1
        w: 权重，形状 (n,)
        b: 偏置

    Returns:
        损失值
    """
    m = X.shape[0]

    # 前向传播
    z = np.dot(X, w) + b
    y_pred = sigmoid(z)

    # 计算交叉熵损失
    # 添加小值避免 log(0)
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)

    loss = -(1/m) * np.sum(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))

    return loss

# 测试损失函数
# 简单示例：正确预测时损失小，错误预测时损失大
print("损失函数测试:")
print(f"预测 0.9，真实 1: 损失 = {-np.log(0.9):.4f}")
print(f"预测 0.1，真实 0: 损失 = {-np.log(0.9):.4f}")
print(f"预测 0.1，真实 1: 损失 = {-np.log(0.1):.4f}")
print(f"预测 0.9，真实 0: 损失 = {-np.log(0.1):.4f}")
```

**梯度计算：**

$$\frac{\partial J}{\partial w} = \frac{1}{m}X^T(\hat{y} - y)$$
$$\frac{\partial J}{\partial b} = \frac{1}{m}\sum_{i=1}^{m}(\hat{y}^{(i)} - y^{(i)})$$

### 知识点 3：scikit-learn 逻辑回归

**描述：**

scikit-learn 提供了高效的逻辑回归实现，支持多种优化算法和正则化方法。

**示例代码：**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.datasets import make_classification

# 创建二分类数据集
X, y = make_classification(
    n_samples=200,
    n_features=2,
    n_redundant=0,
    n_informative=2,
    random_state=42,
    n_clusters_per_class=1
)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 创建并训练模型
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# 查看模型参数
print(f"权重 (coef_): {model.coef_}")
print(f"偏置 (intercept_): {model.intercept_}")

# 进行预测
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# 输出预测概率示例
print("\n预测概率示例（前5个样本）:")
print("类别 0 的概率 | 类别 1 的概率 | 预测类别 | 真实类别")
for i in range(5):
    print(f"    {y_pred_proba[i, 0]:.4f}    |    {y_pred_proba[i, 1]:.4f}    |    {y_pred[i]}       |    {y_test[i]}")

# 评估模型
accuracy = accuracy_score(y_test, y_pred)
print(f"\n准确率: {accuracy:.4f}")

print("\n分类报告:")
print(classification_report(y_test, y_pred))

print("混淆矩阵:")
print(confusion_matrix(y_test, y_pred))

# 可视化决策边界
plt.figure(figsize=(12, 5))

# 训练数据
plt.subplot(1, 2, 1)
plt.scatter(X_train[y_train == 0, 0], X_train[y_train == 0, 1],
            c='blue', marker='o', label='类别 0', alpha=0.6)
plt.scatter(X_train[y_train == 1, 0], X_train[y_train == 1, 1],
            c='red', marker='s', label='类别 1', alpha=0.6)

# 绘制决策边界
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                     np.linspace(y_min, y_max, 100))
Z = model.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
Z = Z.reshape(xx.shape)
plt.contour(xx, yy, Z, levels=[0.5], colors='green', linestyles='--', linewidths=2)
plt.contourf(xx, yy, Z, levels=[0, 0.5, 1], alpha=0.2, colors=['blue', 'red'])
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.title('训练数据和决策边界')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)

# 测试数据预测结果
plt.subplot(1, 2, 2)
# 正确预测
correct = y_pred == y_test
plt.scatter(X_test[correct & (y_test == 0), 0], X_test[correct & (y_test == 0), 1],
            c='blue', marker='o', label='正确预测（类别 0）', alpha=0.6)
plt.scatter(X_test[correct & (y_test == 1), 0], X_test[correct & (y_test == 1), 1],
            c='red', marker='s', label='正确预测（类别 1）', alpha=0.6)
# 错误预测
wrong = ~correct
plt.scatter(X_test[wrong & (y_test == 0), 0], X_test[wrong & (y_test == 0), 1],
            c='blue', marker='x', s=100, label='错误预测（实际为 0）', linewidths=2)
plt.scatter(X_test[wrong & (y_test == 1), 0], X_test[wrong & (y_test == 1), 1],
            c='red', marker='x', s=100, label='错误预测（实际为 1）', linewidths=2)

# 绘制决策边界
plt.contour(xx, yy, Z, levels=[0.5], colors='green', linestyles='--', linewidths=2)
plt.contourf(xx, yy, Z, levels=[0, 0.5, 1], alpha=0.2, colors=['blue', 'red'])
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.title('测试数据预测结果')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()
```

**解释：**

- `predict_proba()`：返回每个类别的概率，形状 (n_samples, n_classes)
- `predict()`：返回预测的类别标签
- `coef_`：权重参数，表示每个特征的重要性
- `intercept_`：偏置参数
- 决策边界是概率等于 0.5 的线

### 知识点 4：分类评估指标

**描述：**

对于分类问题，准确率不是唯一的评估指标。当数据不平衡时，还需要关注精确率、召回率和 F1 分数。

**评估指标详解：**

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# 混淆矩阵
#               预测类别 0   预测类别 1
# 实际类别 0      TN            FP
# 实际类别 1      FN            TP
#
# TN: True Negative  正确预测为负例
# FP: False Positive 错误预测为正例（第一类错误）
# FN: False Negative 错误预测为负例（第二类错误）
# TP: True Positive  正确预测为正例

# 假设有预测结果
y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
y_pred = np.array([0, 1, 0, 0, 0, 1, 1, 1, 0, 1])

# 计算各项指标
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print(f"准确率 (Accuracy):  {accuracy:.4f}")
print(f"精确率 (Precision): {precision:.4f}")
print(f"召回率 (Recall):    {recall:.4f}")
print(f"F1 分数:           {f1:.4f}")

# 计算公式
print("\n计算公式:")
print("准确率  = (TP + TN) / (TP + TN + FP + FN)  - 所有预测正确的比例")
print("精确率 = TP / (TP + FP)                     - 预测为正例中真正为正例的比例")
print("召回率 = TP / (TP + FN)                     - 真正正例中被正确预测的比例")
print("F1 分数 = 2 * 精确率 * 召回率 / (精确率 + 召回率)")

# 混淆矩阵可视化
cm = confusion_matrix(y_true, y_pred)
print("\n混淆矩阵:")
print(cm)

# 分类报告（包含每个类别的详细指标）
print("\n分类报告:")
print(classification_report(y_true, y_pred))
```

**指标选择场景：**

| 场景 | 重要指标 | 原因 |
|------|----------|------|
| 垃圾邮件分类 | 精确率 | 不希望误判正常邮件为垃圾邮件 |
| 疾病筛查 | 召回率 | 不希望漏掉真正的病人 |
| 一般分类 | F1 分数 | 平衡精确率和召回率 |
| 平衡数据集 | 准确率 | 各类别数量相近 |

### 本章小结

本章学习了逻辑回归这一核心分类算法：

- **Sigmoid 函数**：将线性输出映射为概率
- **交叉熵损失**：适合分类问题的凸损失函数
- **sklearn 实现**：使用 LogisticRegression 进行二分类
- **评估指标**：准确率、精确率、召回率、F1 分数

逻辑回归是分类算法的起点，虽然简单，但在许多实际场景中效果良好，尤其适合作为基线模型。

### 📓 笔记本练习

完成本章学习后，请通过以下笔记本练习来巩固你的知识：

- **[练习笔记本](https://tiantianhang.github.io/python-teaching-platform/notebooks/index.html?fromURL=https://raw.githubusercontent.com/TianTianHang/python-teaching-platform/refs/heads/course-content-v1/courses/machine-learning-basics/notebooks/chapter-04-logistic-regression-lab.ipynb)** - 逻辑回归实践练习

> 💡 **提示**：完成练习后可以参考答案笔记本来检查你的答案。

- **[答案笔记本](https://tiantianhang.github.io/python-teaching-platform/notebooks/index.html?fromURL=https://raw.githubusercontent.com/TianTianHang/python-teaching-platform/refs/heads/course-content-v1/courses/machine-learning-basics/solutions/chapter-04-logistic-regression-lab-solution.ipynb)** - 练习参考答案

---
*本章内容基于 Python 教学平台标准格式设计。*
