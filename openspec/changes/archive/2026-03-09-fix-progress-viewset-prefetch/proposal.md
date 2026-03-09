## Why

ChapterProgressViewSet 和 ProblemProgressViewSet 缺少必要的 `select_related` 预取，导致序列化时触发 N+1 查询。ProblemProgressSerializer 访问 `problem.chapter.course.title` 这种3层嵌套关系，每次序列化都会触发额外数据库查询，影响 API 响应性能。

## What Changes

- 修改 `ChapterProgressViewSet.get_queryset()` 添加 `select_related("chapter", "chapter__course")`
- 修改 `ProblemProgressViewSet.get_queryset()` 添加 `select_related("problem", "problem__chapter", "problem__chapter__course")`

## Capabilities

### Modified Capabilities
- `progress-tracking`: 优化进度查询性能，修复 N+1 问题

## Impact

- 代码变更: `backend/courses/views.py` 中的 `ChapterProgressViewSet` 和 `ProblemProgressViewSet`
- 性能影响: 消除 N+1 查询，提升列表接口响应速度