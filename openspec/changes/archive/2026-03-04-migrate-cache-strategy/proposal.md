## Why

当前缓存系统存在两套策略并存的问题，导致信号处理器重复执行、缓存失效范围过大、Redis 中存在冗余数据。具体问题：

1. **信号处理器重复注册**：`ChapterProgress` 和 `ProblemProgress` 模型各注册了两套信号处理器，新策略的精细失效被旧策略的粗粒度清除覆盖
2. **ViewSet 继承混乱**：ChapterViewSet/ProblemViewSet 继承了 `CacheListMixin` 但重写了 list/retrieve 方法，代码意图不清
3. **缓存 Key 空间分裂**：旧策略 `api:*` 和新策略 `chapter:global:*`/`chapter:status:*` 并存

现在是迁移的合适时机，因为新策略已部分实现并验证可行。

## What Changes

- **移除旧缓存策略**：
  - 从 ChapterViewSet 和 ProblemViewSet 移除 `CacheListMixin`、`CacheRetrieveMixin`、`InvalidateCacheMixin` 继承
  - 删除旧的信号处理器：`invalidate_problem_progress_cache`、`invalidate_chapter_progress_cache`
  - 清理 `delete_cache_pattern("api:*")` 相关调用

- **统一到新策略**：
  - 全局数据缓存：`{resource}:global:{id}` 或 `{resource}:global:list:{parent_id}`
  - 用户状态缓存：`{resource}:status:{parent_id}:{user_id}`
  - 细粒度失效：仅清除受影响用户的缓存

- **BREAKING**：移除旧缓存 Key 空间后，升级期间可能有短暂的缓存未命中（可接受）

## Capabilities

### New Capabilities

- `separated-cache`: 分离缓存策略，将全局数据缓存与用户状态缓存分离，实现跨用户共享全局数据、按用户隔离状态数据

### Modified Capabilities

（无 - 本次变更属于实现层面的迁移，不改变外部行为规格）