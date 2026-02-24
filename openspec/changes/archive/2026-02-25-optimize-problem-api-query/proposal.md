## Why

`/api/v1/problems/` 端点当前执行 37 次数据库查询，其中 27 次是 N+1 查询。Silk 日志显示查询来自 `discussion_threads`（12 次）、`chapter`（12 次）、`test_cases`（13 次）。尽管已存在缓存机制，缓存未命中时性能仍然很差，需要优化查询结构。

## What Changes

### 修复代码
- **views.py**: 为 `chapter` 添加 `select_related`，为 `discussion_threads` 和 `test_cases` 添加带 `to_attr` 的 `prefetch_related`
- **views.py**: 为 `prerequisite_problems` 添加 `to_attr`
- **serializers.py**: 更新序列化器方法使用预取数据而非直接查询

### 优化
- 将查询数从 37 降低到 < 15
- 消除 `discussion_threads`、`chapter`、`test_cases` 的 N+1 查询
- 提升响应速度 50%+

### 性能目标
- 目标查询数：< 15（当前 37）
- 响应时间减少 50%+
- 保持 API 响应结构不变

## Capabilities

### New Capabilities
- None（本次为纯性能优化，不涉及新功能）

### Modified Capabilities
- None（本次优化仅改变实现细节，不改变规范级行为）

## Impact

### 受影响代码
- `backend/courses/views.py`:
  - `ProblemViewSet.get_queryset()` 方法（添加 `select_related('chapter')` 和新的 prefetch）
- `backend/courses/serializers.py`:
  - `ProblemSerializer.get_recent_threads()` 方法
  - `AlgorithmProblemSerializer.get_sample_cases()` 方法
  - `ProblemSerializer.get_unlock_condition_description()` 方法

### 其他影响
- 无 API 变更
- 无数据模型变更
- 向后兼容，仅优化内部实现
