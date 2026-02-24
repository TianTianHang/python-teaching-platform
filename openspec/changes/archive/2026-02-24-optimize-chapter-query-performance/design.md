## Context

当前 GET /api/v1/courses/{id}/chapters/ 接口存在严重的 N+1 查询问题：

### 问题分析
1. **prefetch_related 覆盖**: views.py 中两次调用 `prefetch_related`，第二次调用覆盖了第一次的预取配置
2. **Service 层 unaware**: `get_prerequisite_progress()` 调用 `ChapterUnlockService.get_unlock_status()`，这个方法不知道数据已被预取
3. **额外查询**: 每个章节都会产生 3-4 个额外查询（prerequisite_chapters.all(), enrollment, ChapterProgress, COUNT）

### 当前代码结构
- `ChapterViewSet.get_queryset()`: 两次单独的 prefetch_related 调用
- `ChapterSerializer.get_prerequisite_progress()`: 调用 Service 层，不使用预取数据
- `ChapterUnlockService.get_unlock_status()`: 总是查询数据库，无视预取数据

## Goals / Non-Goals

**Goals:**
- 查询数从 63 降低到 < 15
- 保持所有现有功能不变
- 不修改 API 响应结构
- 使用现有的缓存策略

**Non-Goals:**
- 修改数据库结构
- 添加新的 API 端点
- 修改前端代码
- 改变缓存策略

## Decisions

### 1. 合并 prefetch_related 调用

**Decision**: 在 `ChapterViewSet.get_queryset()` 中合并所有 prefetch_related 调用

**Rationale**:
- Django 的 `prefetch_related` 不是累加的，每次调用会覆盖之前的配置
- 通过合并调用确保所有需要的预取都生效
- 使用 `Prefetch` 对象提供更精确的控制

**Alternatives considered**:
- 使用多个 `prefetch_related` 调用 ×（会覆盖）
- 创建自定义 QuerySet ×（增加复杂度）

### 2. 重写 get_prerequisite_progress()

**Decision**: 直接使用预取的数据而不是调用 Service 层

**Rationale**:
- Service 层无法访问 ViewSet 的预取数据
- 序列化器可以直接从预取的数据中计算进度
- 避免额外的数据库查询

**Alternatives considered**:
- 修改 Service 层接受预取参数 ×（破坏封装）
- 使用 annotation 在数据库层计算 ×（逻辑复杂，难以维护）

### 3. 保留现有缓存

**Decision**: 继续使用现有的 ChapterUnlockService 缓存

**Rationale**:
- 缓存仍然适用于其他场景（如详情接口）
- 预取优化比缓存更有效
- 减少缓存失效的复杂性

## Risks / Trade-offs

### [Risk 1] 预取数据可能不完整
- 如果某些章节没有 unlock_condition，预取会跳过
- **Mitigation**: 在序列化器中检查数据是否存在，回退到查询

### [Risk 2] 预取数据可能被覆盖
- 如果序列化器中有其他查询可能触发延迟加载
- **Mitigation**: 仔细检查序列化器的所有字段调用

### [Risk 3] 性能优化不够彻底
- Service 履仍然会在其他地方被调用
- **Mitigation**: 未来可以考虑在其他接口也应用相同的优化

### [Trade-off] 代码复杂度 vs 性能
- 序列化器逻辑变得更复杂
- 但显著提升了性能，值得这个 trade-off