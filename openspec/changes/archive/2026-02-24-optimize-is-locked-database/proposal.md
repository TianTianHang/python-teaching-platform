## Why

当前章节查询列表接口存在性能瓶颈，主要问题是 `ChapterSerializer.get_is_locked()` 方法在每个章节序列化时都调用 `ChapterUnlockService.is_unlocked()`，导致 N+1 查询问题：

- 每个章节调用一次 `condition.prerequisite_chapters.exists()`
- 每个章节调用一次 `ChapterProgress` 查询
- 列表接口中 10 个章节可能产生 30+ 次数据库查询

虽然项目已有缓存机制，但缓存未命中时仍会导致严重性能问题。

## What Changes

- **将 `is_locked` 计算移到数据库层**：使用 `annotate()` 在查询阶段计算章节锁定状态
- **修改 `ChapterViewSet.get_queryset()`**：为学生用户添加 `is_locked_db` 注解
- **修改 `ChapterSerializer.get_is_locked()`**：优先使用数据库注解，回退到 Service 层（用于详情接口）
- **移除不必要的数据预取**：优化 `prefetch_related` 配置
- **保持缓存机制**：`get_unlock_status()` 的缓存继续用于详情接口

**不需要修改**：
- `prerequisite_progress` 字段（保留原有逻辑和缓存）
- `unlock_status` action（继续使用 Service 层）
- 讲师/管理员的行为（始终看到所有章节）

## Capabilities

### New Capabilities
- `database-is-locked-calculation`: 实现数据库层章节锁定状态计算，避免列表查询的 N+1 问题

### Modified Capabilities
- `chapter-list-api`: 列表接口性能优化，使用数据库注解减少查询次数
- `chapter-serialization`: 序列化器逻辑更新，支持从数据库注解读取锁定状态

## Impact

- **Backend**：修改 `courses/views.py` 和 `courses/serializers.py`
- **Performance**：列表查询从 30+ 次查询减少到 2-3 次
- **API 兼容性**：无 breaking changes，所有返回字段保持不变
- **缓存**：Service 层缓存继续工作，仅影响未命中时的性能
- **测试**：需要更新章节列表的性能测试用例