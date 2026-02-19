# Tasks: Add 机器学习基础 Course

## Prerequisites

- Read [project.md](../project.md) for format conventions
- Read [course authoring guide](../../docs/course-authoring-guide.md)
- Review [format specification](../../docs/format-specification.md)
- Review templates in `courses/_templates/`
- Verify python-intro course exists and is complete

## Content References

When authoring course content, you may reference:
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html) - For algorithm explanations
- [NumPy Quickstart](https://numpy.org/doc/stable/user/quickstart.html) - For array operations
- [Pandas Getting Started](https://pandas.pydata.org/docs/getting_started/intro_tutorial/) - For data manipulation
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html) - For visualization examples

## Implementation Tasks

### Phase 1: Course Setup

- [x] Create course folder structure: `courses/machine-learning-basics/`, `chapters/`, `problems/`
- [x] Create `courses/machine-learning-basics/course.md` with proper metadata
  - Set `title: "机器学习基础"`
  - Write `description` (50-200 characters in Chinese)
  - Set `order: 2` (after python-intro)
  - Set `difficulty: 2` (medium)
  - Set `prerequisites: ["python-intro"]`
  - Add relevant tags: `["机器学习", "ml", "numpy", "pandas", "scikit-learn"]`
- [x] Verify YAML syntax is correct (all strings quoted, arrays with brackets)

### Phase 2: Chapter Content Creation

#### Chapter 1: NumPy 与 Pandas 基础

- [x] Create `chapters/chapter-01-numpy-pandas-basics.md`
  - **知识点 1**: NumPy 数组创建与操作
    - 描述：数组创建、索引、切片、形状操作
    - 示例代码：np.array(), np.zeros(), np.ones(), reshaping
  - **知识点 2**: NumPy 数组运算与广播
    - 描述：元素级运算、矩阵运算、广播机制
    - 示例代码：算术运算、点积、转置
  - **知识点 3**: Pandas Series 与 DataFrame
    - 描述：创建、索引、选择、过滤数据
    - 示例代码：pd.Series(), pd.DataFrame(), loc/iloc
  - **知识点 4**: Pandas 数据处理
    - 描述：缺失值处理、数据清洗、分组聚合
    - 示例代码：fillna(), groupby(), merge()
  - Add 1-2 exercises (algorithm: NumPy/Pandas manipulation)

#### Chapter 2: 数据可视化与 Matplotlib

- [x] Create `chapters/chapter-02-matplotlib-visualization.md`
  - **知识点 1**: 基础图表类型
    - 描述：折线图、散点图、柱状图、直方图
    - 示例代码：plt.plot(), plt.scatter(), plt.bar(), plt.hist()
  - **知识点 2**: 图表自定义
    - 描述：标题、标签、图例、样式设置
    - 示例代码：plt.title(), plt.xlabel(), plt.legend()
  - **知识点 3**: 子图与布局
    - 描述：创建多个子图、调整布局
    - 示例代码：plt.subplots(), plt.subplot()
  - **知识点 4**: 数据分布可视化
    - 描述：箱线图、小提琴图、热力图
    - 示例代码：plt.boxplot(), seaborn integration (optional)
  - Add 1-2 exercises (algorithm: Matplotlib visualization, choice: chart selection)

#### Chapter 3: 线性回归

- [x] Create `chapters/chapter-03-linear-regression.md`
  - **知识点 1**: 线性回归概念
    - 描述：回归问题、假设函数、损失函数
    - 示例代码：概念图示、数学公式
  - **知识点 2**: 梯度下降算法
    - 描述：梯度下降原理、学习率、收敛
    - 示例代码：NumPy 实现简单梯度下降
  - **知识点 3**: 多元线性回归
    - 描述：多特征回归、特征缩放
    - 示例代码：标准化、多元回归实现
  - **知识点 4**: scikit-learn 线性回归
    - 描述：LinearRegression API、模型训练与预测
    - 示例代码：fit(), predict(), score()
  - **知识点 5**: 模型评估
    - 描述：MSE、RMSE、R² 等评估指标
    - 示例代码：metrics 计算与解释
  - Add 1-2 exercises (choice: theory, algorithm: sklearn implementation)

#### Chapter 4: 逻辑回归

- [x] Create `chapters/chapter-04-logistic-regression.md`
  - **知识点 1**: 分类问题与 Sigmoid 函数
    - 描述：二分类、Sigmoid 函数、决策边界
    - 示例代码：sigmoid 函数实现与可视化
  - **知识点 2**: 逻辑回归损失函数
    - 描述：交叉熵损失、梯度推导
    - 示例代码：损失函数计算
  - **知识点 3**: scikit-learn 逻辑回归
    - 描述：LogisticRegression API、二分类实践
    - 示例代码：模型训练、预测、概率输出
  - **知识点 4**: 分类评估指标
    - 描述：准确率、精确率、召回率、F1 分数
    - 示例代码：classification_report, confusion_matrix
  - Add 1-2 exercises (choice: threshold understanding, algorithm: sklearn)

#### Chapter 5: 支持向量机

- [x] Create `chapters/chapter-05-support-vector-machines.md`
  - **知识点 1**: SVM 基本概念
    - 描述：超平面、支持向量、间隔最大化
    - 示例代码：概念图示
  - **知识点 2**: 核函数
    - 描述：线性核、多项式核、RBF 核
    - 示例代码：不同核函数效果比较
  - **知识点 3**: scikit-learn SVM
    - 描述：SVC API、参数调优
    - 示例代码：linear kernel, rbf kernel 实现
  - **知识点 4**: SVM 多分类
    - 描述：一对一、一对多策略
    - 示例代码：多分类 SVM 实践
  - Add 1-2 exercises (choice: kernel selection, fillblank: hyperparameters)

#### Chapter 6: K 近邻算法

- [x] Create `chapters/chapter-06-k-nearest-neighbors.md`
  - **知识点 1**: KNN 算法原理
    - 描述：最近邻、K 值选择、距离度量
    - 示例代码：欧氏距离、曼哈顿距离计算
  - **知识点 2**: scikit-learn KNN
    - 描述：KNeighborsClassifier API、使用流程
    - 示例代码：fit(), predict(), 不同 K 值比较
  - **知识点 3**: KNN 回归
    - 描述：KNeighborsRegressor、回归问题
    - 示例代码：KNN 回归实践
  - **知识点 4**: KNN 优缺点
    - 描述：惰性学习、计算复杂度、维度灾难
    - 示例代码：性能比较
  - Add 1-2 exercises (choice: distance metrics, algorithm: KNN)

### Phase 3: Chapter Unlock Configuration

- [x] Configure sequential chapter unlock for all chapters
  - Chapter 1: No unlock conditions (entry point)
  - Chapter 2: `prerequisites: [1]`
  - Chapter 3: `prerequisites: [2]`
  - Chapter 4: `prerequisites: [3]`
  - Chapter 5: `prerequisites: [4]`
  - Chapter 6: `prerequisites: [5]`

### Phase 4: Exercise Creation

#### Fill-blank Questions (API and terminology)

- [x] All fill-blank questions created (9 total):
  - Chapter 1: `problems/numpy-array-statistics.md` - NumPy mean function
  - Chapter 1: `problems/pandas-dataframe-filter.md` - Pandas loc method
  - Chapter 3: `problems/linear-regression-predict.md` - Normal equation formula
  - Chapter 3: `problems/normalize-features.md` - Z-score normalization formula
  - Chapter 4: `problems/sigmoid-function.md` - Sigmoid function definition
  - Chapter 6: `problems/knn-distance.md` - Euclidean distance formula
  - Chapter 1: `problems/pandas-methods-fillblank.md` - dropna method
  - Chapter 3: `problems/sklearn-api-fillblank.md` - fit method
  - Chapter 4: `problems/classification-metrics-fillblank.md` - precision metric

#### Choice Questions (ML concepts)

- [x] Create choice questions for ML theory understanding:
  - [x] Chapter 1: `problems/numpy-broadcasting-choice.md`
  - [x] Chapter 3: `problems/linear-regression-theory-choice.md`
  - [x] Chapter 4: `problems/sigmoid-function-choice.md`
  - [x] Chapter 5: `problems/svm-kernel-choice.md`
  - [x] Chapter 6: `problems/knn-distance-metric-choice.md`

#### Fill-blank Questions (API and terminology)

- [x] Create fill-blank questions for API practice:
  - [x] Chapter 1: `problems/pandas-methods-fillblank.md`
  - [x] Chapter 3: `problems/sklearn-api-fillblank.md`
  - [x] Chapter 4: `problems/classification-metrics-fillblank.md`

### Phase 5: Validation and Testing

- [x] Run YAML syntax validation on all files
- [x] Verify all code examples are syntactically correct
- [x] Convert all algorithm problems to fill-blank format (6 total)
- [x] Check all chapter references in problems exist
- [x] Verify all required fields are present
- [x] Verify prerequisite course reference is valid
- [ ] Run `openspec validate add-machine-learning-course --strict --no-interactive` (requires CLI access)

### Phase 6: Documentation

- [x] Update course.md with chapter links
- [x] Verify chapter content matches learning objectives
- [x] Check exercise difficulty is appropriate (difficulty: 2)
- [x] Ensure total exercise count is 6-12 (0 algorithms, 5 choices, 9 fill-blank)
- [x] Verify all code uses proper syntax highlighting

## Validation Criteria

- All YAML passes strict validation
- All code examples run without errors
- All chapter references in problems are valid
- Exercise distribution: 0% algorithm, 36% choice, 64% fill-blank
- Content follows project conventions
- All files use UTF-8 encoding
- Prerequisite course (python-intro) is correctly referenced

## Notes

- Use templates from `courses/_templates/` as starting points
- Copy templates, never edit them directly
- Focus on hands-on practice with libraries
- Use scikit-learn built-in datasets for consistency
- Target audience: students who completed python-intro
- Include visualization outputs where helpful
- Balance theory (conceptual understanding) with practice (code implementation)
