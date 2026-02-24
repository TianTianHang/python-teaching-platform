## Why

上一轮优化已将章节列表查询数从 63 降低到 34，但分析显示仍有重复查询和数据传递问题：
- `_annotate_is_locked` 中重复查询已缓存的 `completed_chapter_ids`
- `enrollment` 对象在 views.py 中已获取但未传递给 serializer context，导致回退逻辑重复查询

**注意**：系统只有学生用户，无讲师角色，管理员也不需要特殊处理。

## What Changes

### 修复代码
- **views.py**: `_annotate_is_locked` 复用 `self._completed_chapter_ids` 缓存
- **views.py**: `get_serializer_context` 将 `enrollment` 添加到 context

### 优化
- 查询数从 34 进一步降低
- 消除重复的 `completed_chapter_ids` 查询
- 消除 serializer 回退逻辑中的 `enrollment` 查询

### 性能目标
- 目标查询数：< 25（当前 34）
- 消除可避免的重复查询

## Capabilities

### New Capabilities
- None（本次为纯性能优化，不涉及新功能）

### Modified Capabilities
- `chapter-listing`: 现有章节列表功能的性能优化，不改变功能需求

## Impact

### 受影响代码
- `backend/courses/views.py`:
  - `_annotate_is_locked()` 方法
  - `get_serializer_context()` 方法
  - `get_queryset()` 方法（缓存 enrollment）

### 其他影响
- 无 API 变更
- 无数据模型变更
- 向后兼容，仅优化内部实现
