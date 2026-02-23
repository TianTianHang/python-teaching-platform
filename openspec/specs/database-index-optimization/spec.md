## ADDED Requirements

### Requirement: ChapterProgress Query Optimization
系统 SHALL 在 ChapterProgress 模型上添加数据库索引以优化章节进度查询性能。

#### Scenario: Query Progress by Enrollment Status
- **WHEN** 系统查询特定用户的已完成章节列表
- **THEN** 查询应使用 (enrollment, completed) 复合索引
- **AND** 查询时间复杂度应从 O(n) 降低到 O(log n)

#### Scenario: Count Completed Prerequisites
- **WHEN** 章节解锁服务检查前置章节完成数量（ChapterUnlockService.is_unlocked）
- **THEN** ChapterProgress.objects.filter(enrollment=X, chapter_id__in=Y, completed=True).count() 应使用索引
- **AND** 该查询不应产生 N+1 问题

### Requirement: Submission Query Optimization
系统 SHALL 在 Submission 模型上添加数据库索引以优化用户提交记录查询。

#### Scenario: Check Accepted Submission
- **WHEN** 系统检查用户是否已通过特定问题的提交记录
- **THEN** Submission.objects.filter(user=X, problem=Y, status='accepted').exists() 应使用索引
- **AND** 查询响应时间应小于 10ms（即使在大数据量下）

#### Scenario: List User Submissions by Problem
- **WHEN** 获取用户在某问题上的所有提交记录
- **THEN** 查应使用 (user, problem, status) 复合索引
- **AND** 结果应按创建时间倒序排列

### Requirement: ProblemProgress Query Optimization
系统 SHALL 在 ProblemProgress 模型上添加数据库索引以优化问题进度查询。

#### Scenario: Get Problem Progress Status
- **WHEN** 序列化器获取用户对特定问题的解决状态
- **THEN** ProblemProgress.objects.get(enrollment__user=X, problem=Y) 应高效执行
- **AND** 支持 enrollment__user 的跨表 JOIN 查询

#### Scenario: Filter by Progress Status
- **WHEN** 获取用户所有已解决的问题列表
- **THEN** ProblemProgress.objects.filter(enrollment__user=X, status='solved') 应使用索引
- **AND** 该操作应能在 100ms 内完成（即使在 10K+ 进度记录下）

### Requirement: Problem Query Optimization
系统 SHALL 在 Problem 模型上添加数据库索引以优化问题相关查询。

#### Scenario: Filter Problems by Chapter
- **WHEN** 获取某章节下的所有问题
- **THEN** Problem.objects.filter(chapter=X) 应使用 chapter 索引
- **AND** 避免 Seq Scan 使用全表扫描

#### Scenario: Get Next Problem of Same Type
- **WHEN** 查找同类型问题中下一题（ProblemViewSet.n_next）
- **THEN** 查询应使用 (type, -created_at, id) 复合索引
- **AND** 排序操作应高效执行

### Requirement: ChapterUnlockCondition Date Query Optimization
系统 SHALL 在 ChapterUnlockCondition 模型上添加日期索引以优化解锁时间查询。

#### Scenario: Check Unlock Date Range
- **WHEN** 检查章节是否已到解锁时间
- **THEN** unlock_date 字段的范围查询应使用索引
- **AND** ChapterUnlockService.get_unlock_status 的时间检查应高效

### Requirement: Course Title Sort Optimization
系统 SHALL 在 Course 模型上添加标题索引以优化排序操作。

#### Scenario: Sort Courses by Title
- **WHEN** 课程列表按标题排序
- **THEN** ORDER BY title 操作应使用索引
- **AND** 排序结果应在 50ms 内返回（即使课程数 > 1K）

### Requirement: ExamSubmission Index Cleanup
系统 SHALL 移除 ExamSubmission 中冗余的索引以避免存储浪费。

#### Scenario: Unique Constraint Enforcement
- **WHEN** 确保用户对同一测验只能提交一次
- **THEN** unique_together=('exam', 'user') 已提供足够的索引约束
- **AND** 不需要额外的 (exam, user) 索引