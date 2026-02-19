---
title: "NumPy 与 Pandas 基础"
order: 1
---
## NumPy 与 Pandas 基础

### 章节概述

本章将介绍数据科学领域最重要的两个 Python 库：NumPy 和 Pandas。NumPy 提供了高效的数组运算能力，是机器学习的数学基础；Pandas 则提供了强大的数据处理和分析功能，是数据清洗和预处理的利器。通过学习本章，你将掌握数据科学的基本工具集。

### 知识点 1：NumPy 数组创建与操作

**描述：**

NumPy（Numerical Python）是 Python 中用于科学计算的核心库。它的核心是 `ndarray`（N 维数组）对象，提供了高效的数组存储和运算能力。相比 Python 原生列表，NumPy 数组的运算速度快 10-100 倍，且支持向量化运算。

**示例代码：**

```python-exec
import numpy as np

# 创建数组的多种方式
# 从列表创建
arr1 = np.array([1, 2, 3, 4, 5])
print("从列表创建:", arr1)

# 创建全零数组
zeros = np.zeros((2, 3))
print("全零数组:\n", zeros)

# 创建全一数组
ones = np.ones((2, 3))
print("全一数组:\n", ones)

# 创建等差数列
arange = np.arange(0, 10, 2)
print("等差数列:", arange)

# 创建指定范围的数组
linspace = np.linspace(0, 1, 5)
print("线性空间:", linspace)

# 数组索引和切片
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print("原始数组:\n", arr)
print("第一行:", arr[0])
print("第一列:", arr[:, 0])
print("子数组[1:3, 1:3]:\n", arr[1:3, 1:3])

# 数组形状操作
arr = np.arange(12)
print("原始形状:", arr.shape)
reshaped = arr.reshape(3, 4)
print("重塑后:\n", reshaped)
transposed = reshaped.T
print("转置:\n", transposed)
```

**解释：**

- `np.array()`：从 Python 列表或元组创建数组
- `np.zeros()` / `np.ones()`：创建指定形状的全零/全一数组
- `np.arange()`：创建等差数列，类似于 Python 的 `range()`
- `np.linspace()`：在指定范围内创建指定数量的等间距点
- 数组切片使用 `arr[start:stop:step]` 语法，多维数组用逗号分隔各维度
- `.reshape()` 可以改变数组形状而不改变数据
- `.T` 属性返回数组的转置

### 知识点 2：NumPy 数组运算与广播

**描述：**

NumPy 数组支持元素级运算和线性代数运算，这被称为向量化运算。广播机制允许不同形状的数组进行运算，是 NumPy 的强大特性之一。

**示例代码：**

```python-exec
import numpy as np

# 元素级运算
arr1 = np.array([1, 2, 3, 4])
arr2 = np.array([5, 6, 7, 8])

print("数组加法:", arr1 + arr2)
print("数组减法:", arr1 - arr2)
print("数组乘法:", arr1 * arr2)
print("数组除法:", arr1 / arr2)
print("幂运算:", arr1 ** 2)

# 标量运算（广播）
arr = np.array([1, 2, 3, 4])
print("数组 + 10:", arr + 10)
print("数组 * 2:", arr * 2)

# 矩阵运算
matrix1 = np.array([[1, 2], [3, 4]])
matrix2 = np.array([[5, 6], [7, 8]])

# 矩阵乘法
print("矩阵乘法:\n", np.dot(matrix1, matrix2))
print("或使用 @ 运算符:\n", matrix1 @ matrix2)

# 统计运算
arr = np.array([[1, 2, 3], [4, 5, 6]])
print("数组:\n", arr)
print("求和:", np.sum(arr))
print "按行求和:", np.sum(arr, axis=1)
print("按列求和:", np.sum(arr, axis=0))
print("平均值:", np.mean(arr))
print("标准差:", np.std(arr))
print("最大值:", np.max(arr))
print("最小值:", np.min(arr))

# 广播机制示例
arr = np.array([[1, 2, 3], [4, 5, 6]])
row_mean = np.mean(arr, axis=1, keepdims=True)
print("行均值:\n", row_mean)
print("减去行均值（数据中心化）:\n", arr - row_mean)
```

**解释：**

- 元素级运算：对数组中每个元素执行相同的运算
- 标量广播：标量会自动扩展以匹配数组形状
- 矩阵乘法：使用 `np.dot()` 或 `@` 运算符
- 轴参数 `axis`：0 表示列方向（垂直），1 表示行方向（水平）
- `keepdims=True`：保持维度，便于后续广播运算
- 广播规则：从右向左比较维度，如果相同或其中一个为 1，则可以广播

### 知识点 3：Pandas Series 与 DataFrame

**描述：**

Pandas 构建在 NumPy 之上，提供了两种核心数据结构：Series（一维）和 DataFrame（二维）。它们类似于 NumPy 数组，但带有行标签和列标签，使数据操作更加直观。

**示例代码：**

```python-exec
import pandas as pd
import numpy as np

# 创建 Series
s = pd.Series([1, 3, 5, np.nan, 7, 9])
print("Series:\n", s)

# 带索引的 Series
s_with_index = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
print("带索引的 Series:\n", s_with_index)

# 创建 DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['Beijing', 'Shanghai', 'Shenzhen']
}
df = pd.DataFrame(data)
print("DataFrame:\n", df)

# 从 NumPy 数组创建
dates = pd.date_range('20240101', periods=6)
df2 = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=['A', 'B', 'C', 'D'])
print("带日期索引的 DataFrame:\n", df2)

# 查看数据基本信息
print("前 3 行:\n", df.head(3))
print("数据形状:", df.shape)
print("数据类型:\n", df.dtypes)
print("数据描述:\n", df.describe())
print("列名:", df.columns.tolist())
print("索引:", df.index.tolist())
```

**解释：**

- `Series`：带标签的一维数组，可以理解为增强版的列表或字典
- `DataFrame`：带标签的二维表格，类似于 Excel 表格或 SQL 表
- 可以从字典、NumPy 数组、CSV 文件等多种来源创建 DataFrame
- `head(n)`：查看前 n 行数据
- `describe()`：生成描述性统计（均值、标准差、最小值、最大值等）

### 知识点 4：Pandas 数据处理

**描述：**

Pandas 提供了丰富的数据操作方法，包括数据选择、过滤、分组聚合、缺失值处理等。这些操作是数据清洗和预处理的核心技能。

**示例代码：**

```python-exec
import pandas as pd
import numpy as np

# 创建示例 DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, np.nan, 28],
    'city': ['Beijing', 'Shanghai', 'Shenzhen', 'Beijing', 'Guangzhou'],
    'salary': [10000, 15000, 20000, 12000, np.nan]
})
print("原始数据:\n", df)

# 数据选择
print("\n选择列:\n", df['name'])
print("\n使用 loc 选择:\n", df.loc[0:2, ['name', 'age']])
print("\n使用 iloc 选择:\n", df.iloc[0:2, 0:2])

# 数据过滤
print("\n年龄大于 25 的人:\n", df[df['age'] > 25])
print("\n城市是 Beijing 或 Shanghai:\n", df[df['city'].isin(['Beijing', 'Shanghai'])])

# 缺失值处理
print("\n缺失值统计:\n", df.isnull().sum())
print("\n删除包含缺失值的行:\n", df.dropna())
print("\n用均值填充年龄缺失值:\n", df['age'].fillna(df['age'].mean()))

# 数据排序
print("\n按年龄排序:\n", df.sort_values('age', ascending=False))

# 分组聚合
df2 = pd.DataFrame({
    'department': ['HR', 'IT', 'IT', 'HR', 'Finance'],
    'employee': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'salary': [5000, 8000, 9000, 5500, 7000]
})
print("\n分组数据:\n", df2)
print("\n按部门分组统计平均薪资:\n", df2.groupby('department')['salary'].mean())

# 数据合并
df1 = pd.DataFrame({'key': ['A', 'B'], 'value1': [1, 2]})
df2 = pd.DataFrame({'key': ['A', 'B'], 'value2': [3, 4]})
print("\n合并数据:\n", pd.merge(df1, df2, on='key'))

# 应用函数
df['salary_rank'] = df['salary'].rank(ascending=False)
print("\n薪资排名:\n", df[['name', 'salary', 'salary_rank']])
```

**解释：**

- `loc`：基于标签的索引，`df.loc[row_labels, col_labels]`
- `iloc`：基于位置的索引，`df.iloc[row_positions, col_positions]`
- `isnull()` / `notnull()`：检测缺失值
- `dropna()`：删除缺失值
- `fillna()`：填充缺失值
- `groupby()`：按列值分组，常配合聚合函数使用
- `merge()`：类似 SQL JOIN 的数据合并操作
- `apply()`：对数据应用自定义函数

### 本章小结

本章介绍了 NumPy 和 Pandas 的基础操作，这些是机器学习数据处理的基础：

- **NumPy**：高效数组运算，向量化操作，广播机制
- **Pandas**：数据清洗，选择过滤，分组聚合，缺失值处理

掌握这些工具后，我们就可以进行数据预处理和可视化了。

---
*本章内容基于 Python 教学平台标准格式设计。*
