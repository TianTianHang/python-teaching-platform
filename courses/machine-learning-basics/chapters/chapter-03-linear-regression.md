---
title: "线性回归"
order: 3
unlock_conditions:
  type: "prerequisite"
  prerequisites: [2]
---
## 线性回归

### 章节概述

线性回归是机器学习中最基础也是最重要的算法之一。它通过拟合一条直线（或超平面）来预测连续值，是许多复杂算法的基础。本章将从数学原理出发，学习如何使用 NumPy 手动实现线性回归，以及如何使用 scikit-learn 快速构建模型。

### 知识点 1：线性回归概念

**描述：**

线性回归是一种监督学习算法，用于预测连续值。其核心思想是找到一组参数，使得模型预测值与真实值之间的误差最小。

**数学公式：**

- 简单线性回归（一个特征）：$h(x) = w \cdot x + b$
  - $w$：权重（斜率）
  - $b$：偏置（截距）

- 多元线性回归（多个特征）：$h(x) = w_1x_1 + w_2x_2 + ... + w_nx_n + b$

**损失函数（均方误差 MSE）：**

$$J(w,b) = \frac{1}{m}\sum_{i=1}^{m}(h(x^{(i)}) - y^{(i)})^2$$

**解释：**

- **假设函数 $h(x)$**：模型的预测公式
- **损失函数**：衡量预测值与真实值的差距
- **目标**：找到使损失函数最小的 $w$ 和 $b$

### 知识点 2：梯度下降算法

**描述：**

梯度下降是优化损失函数的常用方法。它通过沿梯度负方向迭代更新参数，逐步找到最小值。

**梯度更新公式：**

$$w := w - \alpha \cdot \frac{\partial J}{\partial w}$$
$$b := b - \alpha \cdot \frac{\partial J}{\partial b}$$

其中 $\alpha$ 是学习率（learning rate），控制每次更新的步长。

**示例代码（NumPy 实现）：**

```python
import numpy as np

def linear_regression_gd(X, y, learning_rate=0.01, epochs=1000):
    """
    使用梯度下降实现线性回归

    Args:
        X: 特征数据，形状 (m, n)，m 为样本数，n 为特征数
        y: 标签数据，形状 (m,)
        learning_rate: 学习率
        epochs: 迭代次数

    Returns:
        w: 权重参数，形状 (n,)
        b: 偏置参数
        costs: 每次迭代的损失值
    """
    m, n = X.shape

    # 初始化参数
    w = np.zeros(n)
    b = 0

    # 记录损失
    costs = []

    for epoch in range(epochs):
        # 前向传播：计算预测值
        y_pred = np.dot(X, w) + b

        # 计算损失
        cost = (1 / (2 * m)) * np.sum((y_pred - y) ** 2)
        costs.append(cost)

        # 反向传播：计算梯度
        dw = (1 / m) * np.dot(X.T, (y_pred - y))
        db = (1 / m) * np.sum(y_pred - y)

        # 更新参数
        w = w - learning_rate * dw
        b = b - learning_rate * db

        # 每 100 次迭代打印一次损失
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Cost: {cost:.4f}")

    return w, b, costs

# 示例使用
if __name__ == "__main__":
    # 创建简单线性数据
    np.random.seed(42)
    X = 2 * np.random.rand(100, 1)
    y = 4 + 3 * X + np.random.randn(100, 1)

    # 训练模型
    w, b, costs = linear_regression_gd(X, y, learning_rate=0.1, epochs=1000)

    print(f"\n训练结果:")
    print(f"权重 w: {w[0]:.4f} (真实值: 3)")
    print(f"偏置 b: {b:.4f} (真实值: 4)")

    # 预测
    X_new = np.array([[0], [2]])
    y_pred = np.dot(X_new, w) + b
    print(f"\n预测结果:")
    print(f"X=0 时预测: {y_pred[0]:.4f}")
    print(f"X=2 时预测: {y_pred[1]:.4f}")
```

**解释：**

- **前向传播**：计算模型预测值
- **计算损失**：使用均方误差衡量误差
- **反向传播**：计算损失对参数的梯度
- **参数更新**：沿梯度负方向更新参数
- **学习率选择**：太大可能震荡，太小收敛慢

### 知识点 3：多元线性回归与特征缩放

**描述：**

当有多个特征时，不同特征的尺度可能差异很大，这会影响梯度下降的收敛速度。特征缩放可以解决这个问题。

**示例代码：**

```python
import numpy as np

def normalize(X):
    """
    标准化特征：使每个特征的均值为 0，标准差为 1

    Args:
        X: 原始特征，形状 (m, n)

    Returns:
        X_normalized: 标准化后的特征
        mean: 每列的均值
        std: 每列的标准差
    """
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    X_normalized = (X - mean) / std
    return X_normalized, mean, std

# 多元线性回归示例
if __name__ == "__main__":
    np.random.seed(42)

    # 创建多元线性数据
    # y = 5 + 2*x1 + 3*x2 + 1*x3 + noise
    m = 100
    X1 = np.random.randn(m, 1) * 10  # 大尺度特征
    X2 = np.random.randn(m, 1) * 0.1  # 小尺度特征
    X3 = np.random.randn(m, 1)
    X = np.hstack([X1, X2, X3])

    true_w = np.array([2, 3, 1])
    true_b = 5
    y = true_b + np.dot(X, true_w) + np.random.randn(m, 1) * 0.5

    # 不使用特征缩放
    print("不使用特征缩放:")
    w1, b1, costs1 = linear_regression_gd(X, y, learning_rate=0.0001, epochs=1000)
    print(f"权重: {w1}")
    print(f"偏置: {b1:.4f}")
    print(f"最终损失: {costs1[-1]:.4f}\n")

    # 使用特征缩放
    print("使用特征缩放:")
    X_normalized, mean, std = normalize(X)
    w2, b2, costs2 = linear_regression_gd(X_normalized, y, learning_rate=0.1, epochs=1000)
    print(f"权重: {w2}")
    print(f"偏置: {b2:.4f}")
    print(f"最终损失: {costs2[-1]:.4f}")
```

**解释：**

- **特征缩放的必要性**：不同尺度特征导致梯度下降在"窄谷"中缓慢前行
- **标准化（Z-score）**：$x' = \frac{x - \mu}{\sigma}$
- **归一化（Min-Max）**：$x' = \frac{x - min}{max - min}$
- 标准化后的特征均值为 0，标准差为 1

### 知识点 4：scikit-learn 线性回归

**描述：**

scikit-learn 提供了简洁的 API，使得使用线性回归变得非常简单。它内部使用了更高效的优化算法（如最小二乘法的解析解）。

**示例代码：**

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 创建示例数据
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 创建并训练模型
model = LinearRegression()
model.fit(X_train, y_train)

# 查看模型参数
print(f"权重 (coef_): {model.coef_[0][0]:.4f}")
print(f"偏置 (intercept_): {model.intercept_[0]:.4f}")

# 进行预测
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# 计算评估指标
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse = mean_squared_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"\n训练集 MSE: {train_mse:.4f}")
print(f"测试集 MSE: {test_mse:.4f}")
print(f"训练集 R²: {train_r2:.4f}")
print(f"测试集 R²: {test_r2:.4f}")

# 可视化结果
plt.figure(figsize=(12, 4))

# 训练数据
plt.subplot(1, 2, 1)
plt.scatter(X_train, y_train, alpha=0.6, label='训练数据')
plt.plot(X_train, y_train_pred, 'r-', linewidth=2, label='拟合直线')
plt.xlabel('X')
plt.ylabel('y')
plt.title('训练集拟合结果')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)

# 测试数据
plt.subplot(1, 2, 2)
plt.scatter(X_test, y_test, alpha=0.6, label='测试数据', color='green')
plt.plot(X_test, y_test_pred, 'r-', linewidth=2, label='拟合直线')
plt.xlabel('X')
plt.ylabel('y')
plt.title('测试集预测结果')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

# 多元线性回归示例
print("\n" + "="*40)
print("多元线性回归示例")
print("="*40)

from sklearn.datasets import make_regression

# 创建多元回归数据
X_multi, y_multi = make_regression(
    n_samples=100, n_features=3, noise=10, random_state=42
)

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X_multi, y_multi, test_size=0.2, random_state=42
)

# 训练模型
model_multi = LinearRegression()
model_multi.fit(X_train, y_train)

# 评估
y_pred = model_multi.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"各特征的权重: {model_multi.coef_}")
print(f"偏置: {model_multi.intercept_:.4f}")
print(f"测试集 MSE: {mse:.4f}")
print(f"测试集 R²: {r2:.4f}")
```

**解释：**

- `LinearRegression()`：创建线性回归模型
- `fit(X, y)`：训练模型
- `predict(X)`：进行预测
- `coef_`：存储权重参数
- `intercept_`：存储偏置参数
- `train_test_split()`：划分训练集和测试集

### 知识点 5：模型评估

**描述：**

评估回归模型的性能需要使用合适的指标。常用的指标包括均方误差（MSE）、均方根误差（RMSE）、平均绝对误差（MAE）和决定系数（R²）。

**评估指标详解：**

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# 假设有真实值和预测值
y_true = np.array([3.0, -0.5, 2.0, 7.0])
y_pred = np.array([2.5, 0.0, 2.1, 7.8])

# 1. 均方误差 MSE (Mean Squared Error)
# 对大误差敏感
mse = mean_squared_error(y_true, y_pred)
print(f"MSE: {mse:.4f}")

# 2. 均方根误差 RMSE (Root Mean Squared Error)
# 与原始数据同单位
rmse = np.sqrt(mse)
print(f"RMSE: {rmse:.4f}")

# 3. 平均绝对误差 MAE (Mean Absolute Error)
# 对异常值不敏感
mae = mean_absolute_error(y_true, y_pred)
print(f"MAE: {mae:.4f}")

# 4. 决定系数 R² (R-squared)
# 范围 [0, 1]，越接近 1 拟合越好
# 1 表示完美预测，0 表示和用均值预测一样
r2 = r2_score(y_true, y_pred)
print(f"R²: {r2:.4f}")

# R² 的详细解释
# R² = 1 - (SS_res / SS_tot)
# SS_res = sum((y_true - y_pred)^2)  残差平方和
# SS_tot = sum((y_true - y_mean)^2)   总平方和

y_mean = np.mean(y_true)
ss_res = np.sum((y_true - y_pred) ** 2)
ss_tot = np.sum((y_true - y_mean) ** 2)
r2_manual = 1 - (ss_res / ss_tot)
print(f"R² (手动计算): {r2_manual:.4f}")
```

**指标选择建议：**

| 指标 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| MSE | 数学性质好，可导 | 对异常值敏感 | 大样本，关注大误差 |
| RMSE | 与目标同单位，直观 | 对异常值敏感 | 需要直观解释误差大小时 |
| MAE | 对异常值鲁棒 | 不可导 | 有异常值的场景 |
| R² | 相对指标，可比较 | 可能误导 | 需要评估模型整体解释力 |

### 本章小结

本章学习了线性回归的完整流程：

- **理论基础**：假设函数、损失函数、梯度下降
- **手动实现**：使用 NumPy 从零实现线性回归
- **特征工程**：特征缩放对模型训练的影响
- **sklearn 实践**：使用 scikit-learn 快速构建模型
- **模型评估**：MSE、RMSE、MAE、R² 等评估指标

线性回归是机器学习的起点，掌握它的原理和实现将为学习更复杂的算法打下坚实基础。

### 📓 笔记本练习

完成本章学习后，请通过以下笔记本练习来巩固你的知识：

- **[练习笔记本](https://tiantianhang.github.io/python-teaching-platform/notebooks/index.html?fromURL=https://raw.githubusercontent.com/TianTianHang/python-teaching-platform/refs/heads/course-content-v1/courses/machine-learning-basics/notebooks/chapter-03-linear-regression-lab.ipynb)** - 线性回归实践练习

> 💡 **提示**：完成练习后可以参考答案笔记本来检查你的答案。

- **[答案笔记本](https://tiantianhang.github.io/python-teaching-platform/notebooks/index.html?fromURL=https://raw.githubusercontent.com/TianTianHang/python-teaching-platform/refs/heads/course-content-v1/courses/machine-learning-basics/solutions/chapter-03-linear-regression-lab-solution.ipynb)** - 练习参考答案

---
*本章内容基于 Python 教学平台标准格式设计。*
