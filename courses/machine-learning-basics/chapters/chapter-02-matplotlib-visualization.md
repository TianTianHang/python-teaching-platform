---
title: "数据可视化与 Matplotlib"
order: 2
unlock_conditions:
  type: "prerequisite"
  prerequisites: [1]
---
## 数据可视化与 Matplotlib

### 章节概述

本章将介绍 Python 中最流行的数据可视化库 Matplotlib。数据可视化是数据科学中不可或缺的技能，它能帮助我们直观地理解数据分布、发现数据规律、展示分析结果。通过学习本章，你将掌握创建各种类型图表的方法。

### 知识点 1：基础图表类型

**描述：**

Matplotlib 提供了多种基础图表类型，每种图表适合展示不同类型的数据。折线图用于展示趋势，散点图用于展示关系，柱状图用于比较类别，直方图用于展示分布。

**示例代码：**

```python-exec
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体（可选，平台可能不支持）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 创建示例数据
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# 折线图
plt.figure(figsize=(10, 3))

plt.subplot(1, 4, 1)
plt.plot(x, y1, label='sin(x)')
plt.plot(x, y2, label='cos(x)')
plt.title('折线图')
plt.legend()

# 散点图
plt.subplot(1, 4, 2)
x_scatter = np.random.randn(100)
y_scatter = np.random.randn(100)
colors = np.random.rand(100)
plt.scatter(x_scatter, y_scatter, c=colors, cmap='viridis')
plt.title('散点图')
plt.colorbar()

# 柱状图
plt.subplot(1, 4, 3)
categories = ['A', 'B', 'C', 'D']
values = [15, 30, 45, 10]
plt.bar(categories, values, color=['red', 'blue', 'green', 'orange'])
plt.title('柱状图')

# 直方图
plt.subplot(1, 4, 4)
data = np.random.randn(1000)
plt.hist(data, bins=30, edgecolor='black')
plt.title('直方图')

plt.tight_layout()
plt.show()
```

**解释：**

- `plt.figure()`：创建新的画布，`figsize` 设置大小（英寸）
- `plt.subplot(rows, cols, index)`：创建子图布局
- `plt.plot()`：绘制折线图，适合展示时间序列或连续变化
- `plt.scatter()`：绘制散点图，适合展示两个变量关系
- `plt.bar()`：绘制柱状图，适合比较不同类别
- `plt.hist()`：绘制直方图，适合展示数据分布
- `plt.tight_layout()`：自动调整子图间距

### 知识点 2：图表自定义

**描述：**

良好的可视化需要清晰的标签、标题和样式设置。Matplotlib 提供了丰富的自定义选项，让图表更加美观和易读。

**示例代码：**

```python-exec
import matplotlib.pyplot as plt
import numpy as np

# 示例数据
months = ['1月', '2月', '3月', '4月', '5月', '6月']
sales = [120, 150, 180, 220, 260, 310]
profits = [30, 45, 55, 70, 85, 100]

# 创建画布
plt.figure(figsize=(10, 6))

# 绘制折线
plt.plot(months, sales, marker='o', linewidth=2, label='销售额')
plt.plot(months, profits, marker='s', linewidth=2, label='利润', linestyle='--')

# 设置标题和标签
plt.title('2024年上半年销售数据', fontsize=16, fontweight='bold')
plt.xlabel('月份', fontsize=12)
plt.ylabel('金额（万元）', fontsize=12)

# 设置网格
plt.grid(True, linestyle=':', alpha=0.6)

# 设置图例
plt.legend(loc='upper left', fontsize=12)

# 设置坐标轴范围
plt.ylim(0, 350)

# 添加注释
plt.annotate('最高销售额', xy=('5月', 310), xytext=('4月', 280),
             arrowprops=dict(arrowstyle='->', color='red'))

plt.show()

# 绘制堆叠柱状图
plt.figure(figsize=(10, 6))
costs = [90, 105, 125, 150, 175, 210]
plt.bar(months, costs, label='成本', color='lightcoral')
plt.bar(months, profits, bottom=costs, label='利润', color='lightblue')

plt.title('成本与利润堆叠图')
plt.xlabel('月份')
plt.ylabel('金额（万元）')
plt.legend()
plt.grid(axis='y', linestyle=':', alpha=0.5)

plt.show()
```

**解释：**

- `marker`：数据点标记样式（'o' 圆形，'s' 方形，'^' 三角形等）
- `linewidth`：线宽
- `linestyle`：线型（'-' 实线，'--' 虚线，':' 点线等）
- `title()` / `xlabel()` / `ylabel()`：设置标题和轴标签
- `grid()`：显示网格
- `legend()`：显示图例
- `annotate()`：添加文字注释
- 堆叠柱状图使用 `bottom` 参数指定起始位置

### 知识点 3：子图与布局

**描述：**

当需要在一个画布上展示多个相关图表时，子图布局非常有用。Matplotlib 提供了灵活的子图创建方式。

**示例代码：**

```python-exec
import matplotlib.pyplot as plt
import numpy as np

# 创建示例数据
x = np.linspace(0, 2*np.pi, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = x**2

# 方式一：使用 subplot
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(x, y1)
plt.title('sin(x)')

plt.subplot(2, 2, 2)
plt.plot(x, y2)
plt.title('cos(x)')

plt.subplot(2, 2, 3)
plt.plot(x, y3)
plt.title('tan(x)')
plt.ylim(-5, 5)

plt.subplot(2, 2, 4)
plt.plot(x, y4)
plt.title('x^2')

plt.suptitle('三角函数与多项式', fontsize=16)
plt.tight_layout()
plt.show()

# 方式二：使用 subplots（返回数组和画布）
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

axes[0, 0].plot(x, y1, 'r-')
axes[0, 0].set_title('sin(x)')
axes[0, 0].grid(True)

axes[0, 1].plot(x, y2, 'g-')
axes[0, 1].set_title('cos(x)')
axes[0, 1].grid(True)

axes[1, 0].plot(x, y3, 'b-')
axes[1, 0].set_title('tan(x)')
axes[1, 0].set_ylim(-5, 5)
axes[1, 0].grid(True)

axes[1, 1].plot(x, y4, 'm-')
axes[1, 1].set_title('x^2')
axes[1, 1].grid(True)

fig.suptitle('使用 subplots 创建', fontsize=16)
plt.tight_layout()
plt.show()

# 方式三：不规则的子图布局
fig = plt.figure(figsize=(12, 6))

# 大图占据左侧
ax1 = fig.add_subplot(1, 2, 1)
ax1.plot(x, y1)
ax1.set_title('大图')

# 右侧两个小图
ax2 = fig.add_subplot(2, 2, 2)
ax2.plot(x, y2)
ax2.set_title('小图1')

ax3 = fig.add_subplot(2, 2, 4)
ax3.plot(x, y4)
ax3.set_title('小图2')

plt.tight_layout()
plt.show()
```

**解释：**

- `plt.subplot(rows, cols, index)`：按顺序创建子图
- `plt.subplots(rows, cols)`：一次性创建所有子图，返回画布和子图数组
- `fig.add_subplot()`：灵活添加子图，适合不规则布局
- `set_title()`：为子图设置标题（面向对象 API）
- `tight_layout()`：自动调整子图间距，避免重叠

### 知识点 4：数据分布可视化

**描述：**

理解数据分布是机器学习的重要环节。箱线图可以展示数据的分位数和异常值，热力图可以展示变量间的相关性。

**示例代码：**

```python-exec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 创建示例数据
np.random.seed(42)
data1 = np.random.normal(0, 1, 200)
data2 = np.random.normal(2, 1.5, 200)
data3 = np.random.normal(-1, 0.5, 200)

# 箱线图
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.boxplot([data1, data2, data3], labels=['组1', '组2', '组3'])
plt.title('箱线图')
plt.ylabel('值')
plt.grid(axis='y', linestyle=':', alpha=0.5)

# 小提琴图
plt.subplot(1, 3, 2)
plt.violinplot([data1, data2, data3], showmeans=True)
plt.xticks([1, 2, 3], ['组1', '组2', '组3'])
plt.title('小提琴图')
plt.grid(axis='y', linestyle=':', alpha=0.5)

# 热力图（相关性矩阵）
plt.subplot(1, 3, 3)
df = pd.DataFrame({
    'A': np.random.randn(100),
    'B': np.random.randn(100) * 2,
    'C': np.random.randn(100) + 1,
    'D': np.random.randn(100) - 1
})
correlation = df.corr()
im = plt.imshow(correlation, cmap='coolwarm', vmin=-1, vmax=1)
plt.xticks(range(4), ['A', 'B', 'C', 'D'])
plt.yticks(range(4), ['A', 'B', 'C', 'D'])
plt.colorbar(im, label='相关系数')
plt.title('相关性热力图')

# 在热力图上添加数值标签
for i in range(4):
    for j in range(4):
        plt.text(j, i, f'{correlation.iloc[i, j]:.2f}',
                 ha='center', va='center', fontsize=8)

plt.tight_layout()
plt.show()

# 分布对比：直方图 + 密度曲线
plt.figure(figsize=(10, 5))

# 绘制三个分布的直方图
plt.hist(data1, bins=30, alpha=0.5, label='组1', density=True)
plt.hist(data2, bins=30, alpha=0.5, label='组2', density=True)
plt.hist(data3, bins=30, alpha=0.5, label='组3', density=True)

# 添加核密度估计曲线
from scipy import stats
kde1 = stats.gaussian_kde(data1)
kde2 = stats.gaussian_kde(data2)
kde3 = stats.gaussian_kde(data3)
x_range = np.linspace(-5, 7, 200)
plt.plot(x_range, kde1(x_range), 'r-', linewidth=2)
plt.plot(x_range, kde2(x_range), 'g-', linewidth=2)
plt.plot(x_range, kde3(x_range), 'b-', linewidth=2)

plt.title('数据分布对比')
plt.xlabel('值')
plt.ylabel('密度')
plt.legend()
plt.grid(linestyle=':', alpha=0.5)
plt.show()
```

**解释：**

- **箱线图**：展示最小值、Q1、中位数、Q3、最大值和异常值
- **小提琴图**：结合箱线图和核密度估计，更直观展示分布形状
- **热力图**：用颜色编码展示矩阵数值，常用于相关性分析
- `imshow()`：绘制图像/热力图，`cmap` 指定颜色映射
- 核密度估计（KDE）：平滑的概率密度曲线

### 本章小结

本章介绍了 Matplotlib 的核心功能：

- **基础图表**：折线图、散点图、柱状图、直方图
- **图表美化**：标题、标签、图例、网格、注释
- **子图布局**：规则布局和不规则布局
- **分布可视化**：箱线图、小提琴图、热力图

掌握这些可视化技能后，我们就可以开始学习机器学习算法，并用图表直观地展示模型结果了。

---
*本章内容基于 Python 教学平台标准格式设计。*
