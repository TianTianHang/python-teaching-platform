## Why

GET /api/v1/courses/{id}/chapters/ 接口当前产生 63 个查询，严重影响页面加载性能。主要问题是 `get_prerequisite_progress()` 字段和 prefetch_related 配置不当导致的 N+1 查询问题。

## What Changes

### 修复代码
- **views.py**: 合并两次 `prefetch_related` 调用，避免 `unlock_condition__prerequisite_chapters__course` 预取被覆盖
- **serializers.py**: 重写 `get_prerequisite_progress()` 方法，直接使用预取的数据而不是调用 Service 层

### 优化
- 查询数从 63 降低到约 10-15 个
- 保持所有现有功能不变
- 不修改 API 响应结构

### 性能目标
- 接口响应时间：23ms (queries) → 5ms (queries)
- 总查询数：63 → < 15

## Capabilities

### New Capabilities
- **efficient-chapter-listing**: 优化章节列表查询性能，减少数据库查询次数

### Modified Capabilities
- None (仅优化实现，不改变功能需求)

## Impact

### 受影响代码
- `backend/courses/views.py`: ChapterViewSet.get_queryset()
- `backend/courses/serializers.py`: ChapterSerializer.get_prerequisite_progress()

### 其他影响
- 无 API 变更
- 无数据模型变更
- 向后兼容