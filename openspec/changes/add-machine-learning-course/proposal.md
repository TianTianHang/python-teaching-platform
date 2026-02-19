# Proposal: Add 机器学习基础 Course

## Summary

Create an advanced 机器学习基础 (Machine Learning Basics) course for students who have completed Python 入门. The course covers traditional machine learning algorithms starting from Linear Regression, with hands-on practice using NumPy, Pandas, Matplotlib, and scikit-learn libraries.

## Motivation

Machine learning is one of the most in-demand skills in the tech industry. This course bridges the gap between Python programming knowledge and practical ML applications by:
- Building on Python fundamentals learned in python-intro course
- Teaching traditional ML algorithms before deep learning
- Providing hands-on experience with industry-standard ML libraries
- Preparing learners for real-world data science and ML projects

## Proposed Solution

### Course Structure

Create a new course `machine-learning-basics` with 6 focused chapters:

1. **NumPy 与 Pandas 基础** (NumPy and Pandas Basics)
   - NumPy arrays and operations
   - Pandas Series and DataFrame
   - Data manipulation and cleaning
   - Hands-on data preprocessing exercises

2. **数据可视化与 Matplotlib** (Data Visualization with Matplotlib)
   - Basic plots: line, scatter, bar, histogram
   - Figure customization and subplots
   - Visualizing data distributions
   - Practice with real datasets

3. **线性回归** (Linear Regression)
   - Simple linear regression concepts
   - Multiple linear regression
   - Gradient descent optimization
   - scikit-learn implementation
   - Model evaluation metrics (MSE, R²)

4. **逻辑回归** (Logistic Regression)
   - Binary classification concepts
   - Sigmoid function and decision boundaries
   - Cost function for classification
   - scikit-learn implementation
   - Evaluation metrics (accuracy, precision, recall)

5. **支持向量机** (Support Vector Machines)
   - SVM concepts and intuition
   - Kernel functions (linear, RBF, polynomial)
   - Hyperparameter tuning (C, gamma)
   - scikit-learn implementation
   - Multi-class classification

6. **K 近邻算法** (K-Nearest Neighbors)
   - KNN algorithm principles
   - Distance metrics (Euclidean, Manhattan)
   - Choosing K value
   - scikit-learn implementation
   - Pros and cons of KNN

### Exercise Distribution

Given the course nature:
- **Algorithm Problems**: Focus on NumPy/Pandas data manipulation and ML model implementation
- **Choice Questions**: Test ML concepts, algorithm understanding, and theory
- **Fill-blank Questions**: Reinforce key ML terminology and API usage

Each chapter will include 1-2 focused exercises (total ~6-12 exercises for the course).

### Target Audience

- Students who have completed Python 入门 course
- Learners with basic Python programming knowledge
- Those interested in data science and machine learning
- Students preparing for advanced ML or deep learning courses

### Technical Approach

**Library Introduction Strategy**:
- Chapters 1-2 focus on library fundamentals (NumPy, Pandas, Matplotlib)
- Chapters 3-6 introduce ML algorithms with scikit-learn
- Each algorithm chapter includes: theory → manual implementation with NumPy → scikit-learn practice

**Code Examples Strategy**:
- Use ` ```python-exec ` blocks for interactive NumPy/Pandas demonstrations
- Use standard ` ```python ` blocks for longer algorithm implementations
- Include visualization code outputs for data exploration chapters

## Alternatives Considered

### Alternative 1: Deep Learning First Course
Start with neural networks and deep learning.
- **Pros**: Covers trendy topics
- **Cons**: Skips fundamental ML concepts; traditional ML is still widely used

### Alternative 2: Comprehensive ML Course
Include more algorithms (decision trees, random forests, clustering, etc.).
- **Pros**: More complete coverage
- **Cons**: Too long; selected approach focuses on core supervised learning algorithms

### Alternative 3: Theory-Heavy Course
Emphasize mathematical derivations and proofs.
- **Pros**: Deeper theoretical understanding
- **Cons**: May overwhelm students; selected approach balances theory with practice

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Math prerequisites may challenge some students | Medium | Include intuitive explanations before formulas |
| Library versions may change | Low | Focus on stable APIs and common patterns |
| Some students may lack Python basics | Medium | Require python-intro course as prerequisite |
| Dataset availability issues | Low | Use built-in datasets from scikit-learn |

## Dependencies

- **Prerequisite Course**: python-intro (order: 1)
- **Platform Features**: Jupyter notebook integration for data exploration
- **External Libraries**: NumPy, Pandas, Matplotlib, scikit-learn (platform-provided)

## Success Criteria

- [ ] Course metadata created in `courses/machine-learning-basics/course.md`
- [ ] All 6 chapters created with proper YAML frontmatter
- [ ] 6-12 exercises created with NumPy/Pandas focus
- [ ] Sequential chapter unlock conditions configured
- [ ] All content follows project format conventions
- [ ] YAML validation passes without errors

## Open Questions

1. Should we include a chapter on model evaluation and cross-validation?
   - **Decision**: Keep evaluation metrics within each algorithm chapter for 6-chapter focus

2. Should we use real-world datasets or synthetic data?
   - **Decision**: Use scikit-learn's built-in datasets (iris, boston, etc.) for consistency

3. Should we include hyperparameter tuning exercises?
   - **Decision**: Include basic tuning in SVM chapter; advanced tuning to future courses

## Related Changes

- **python-intro-course**: This course builds on the python-intro course as a prerequisite
- **chapter-sequential-unlock**: Will use sequential chapter unlock pattern

## References

- [Project Context](../project.md)
- [Format Specification](../../docs/format-specification.md)
- [Course Authoring Guide](../../docs/course-authoring-guide.md)
- [scikit-learn Documentation](https://scikit-learn.org/stable/) - For API references and examples
- [NumPy Documentation](https://numpy.org/doc/) - For array operations
- [Pandas Documentation](https://pandas.pydata.org/docs/) - For data manipulation
