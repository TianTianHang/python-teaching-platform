## Why

尽管已实施缓存 `enrollment` 和 `completed_chapter_ids`，章节列表 API 仍执行 34 次查询。分析发现剩余的 N+1 查询主要来自：
1. `prerequisite_chapters` 预取未使用 `to_attr`，导致每个章节都查询数据库
2. `CourseModelSerializer` 的 `recent_threads` 字段产生 N+1 查询
3. `EnrollmentSerializer` 在章节列表序列化时被调用，产生独立查询

## What Changes

### 修复代码
- **views.py**: 为 `unlock_condition__prerequisite_chapters` 添加 `to_attr` 预取
- **views.py**: 移除不必要的 `_is_instructor_or_admin()` 检查
- **serializers.py**: 使用预取数据替代 `.all()` 查询

### 优化
- 将查询数从 34 进一步降低到 < 15
- 消除 `prerequisite_chapters` 的 N+1 查询
- 消除 `recent_threads` 的 N+1 查询
- 移除冗余的用户角色检查

### 性能目标
- 目标查询数：< 15（当前 34）
- 响应时间减少 50%+

## Capabilities

### New Capabilities
- None（本次为纯性能优化，不涉及新功能）

### Modified Capabilities
- `chapter-prerequisites`: 优化查询性能，移除 N+1 查询

## Impact

### 受影响代码
- `backend/courses/views.py`:
  - `get_queryset()` 方法（添加 `to_attr`）
  - `_is_instructor_or_admin()` 方法（移除）
- `backend/courses/serializers.py`:
  - `ChapterUnlockConditionSerializer.get_prerequisite_chapters()` 方法
  - `CourseModelSerializer.get_recent_threads()` 方法

### 其他影响
- 无 API 变更
- 无数据模型变更
- 向后兼容，仅优化内部实现