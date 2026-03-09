## Context

在 `courses/views.py` 中，`ChapterProgressViewSet` 和 `ProblemProgressViewSet` 的 `get_queryset()` 方法没有配置 `select_related`，导致序列化时访问外键关系会触发额外的数据库查询。

**当前问题**:
1. `ChapterProgressViewSet` 访问 `chapter.title` 和 `chapter.course.title` 时触发 N+1
2. `ProblemProgressViewSet` 访问 `problem.title`, `problem.chapter.title`, `problem.chapter.course.title` 时触发 N+1（3层嵌套）

## Goals / Non-Goals

**Goals:**
- 在 `ChapterProgressViewSet.get_queryset()` 添加 `select_related("chapter", "chapter__course")`
- 在 `ProblemProgressViewSet.get_queryset()` 添加 `select_related("problem", "problem__chapter", "problem__chapter__course")`

**Non-Goals:**
- 不修改 Serializer 逻辑
- 不添加新的测试用例（仅修复现有性能问题）

## Decisions

使用 `select_related` 而非 `prefetch_related`：外键关系使用 JOIN 效率更高。

## Risks / Trade-offs

[Risk] 查询复杂度增加 → [Mitigation] 只预取必要的字段，避免过度预取导致内存占用增加