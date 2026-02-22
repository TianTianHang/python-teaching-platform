---
title: "线性回归正规方程填空"
type: "fillblank"
difficulty: 2
chapter: 3
content_with_blanks: |
  对于线性回归模型 y = Xw + b，权重 w 的正规方程是：w = [blank1]
  其中 X 是设计矩阵，y 是目标值向量。

blanks:
  blank1:
    answers: ["(X^T X)^(-1) X^T y", "(X.T @ X).I @ X.T @ y", "inv(X^T X) X^T y"]
    case_sensitive: false
blank_count: 1
---

## 题目描述

在线性回归中，正规方程用于求解权重参数。请填写正确的正规方程形式。

### 题目内容

对于线性回归模型 $y = Xw + b$，权重 $w$ 的正规方程是：

$$w = ______$$

其中 $X$ 是设计矩阵，$y$ 是目标值向量。

---

*本题基于 Python 教学平台标准格式设计。*
