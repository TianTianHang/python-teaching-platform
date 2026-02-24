## Why

`/api/v1/enrollments/` 端点当前执行 14 次数据库查询。Silk 分析显示主要的 N+1 查询来自 `EnrollmentSerializer`：
- `user_username` 字段 - 每条记录都查询 user 表
- `course_title` 字段 - 每条记录都查询 course 表
- `get_progress_percentage()` 方法 - 每条记录都查询 chapters 和 chapter_progress

## What Changes

### 修复代码
- **views.py**: 为 `user` 和 `course` 添加 `select_related`，为 `chapter_progress` 和 `course__chapters` 添加 `prefetch_related`
- **serializers.py**: 更新 `get_progress_percentage()` 方法使用预取数据

### 优化
- 将查询数从 14 降低到约 5-7
- 消除 `user`、`course`、`chapters`、`chapter_progress` 的 N+1 查询
- 提升响应速度约 40%

### 性能目标
- 目标查询数：< 7（当前 14）
- 响应时间减少 40%+
- 保持 API 响应结构不变

### 不包含
- `get_next_chapter()` 方法的优化（逻辑复杂，需要单独处理）

## Capabilities

### New Capabilities
- None（本次为纯性能优化，不涉及新功能）

### Modified Capabilities
- None（本次优化仅改变实现细节，不改变规范级行为）

## Impact

### 受影响代码
- `backend/courses/views.py`:
  - `EnrollmentViewSet.get_queryset()` 方法（添加 select_related 和 prefetch_related）
- `backend/courses/serializers.py`:
  - `EnrollmentSerializer.get_progress_percentage()` 方法（使用预取数据）

### 其他影响
- 无 API 变更
- 无数据模型变更
- 向后兼容，仅优化内部实现
