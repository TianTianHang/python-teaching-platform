# Separate Cache for Global and User Data

## Why

当前章节和问题的缓存策略将全局数据（章节内容、问题内容）与用户状态（是否解锁、完成状态）混合存储，导致缓存键包含 `user_id`，全局数据无法跨用户共享，造成内存浪费和缓存命中率低的问题。在100章节×1000用户的场景下，缓存条目达到10万条，其中98%是重复的全局数据。

**核心问题**：
- 缓存键包含 `user_id` → 每个用户独立缓存副本
- 全局数据重复存储 → "第一章：变量"的内容存储了N次
- 缓存失效粒度粗 → 用户状态更新，整个缓存失效
- 内存利用率低 → 无法跨用户共享静态内容

## What Changes

- **新增缓存分离机制**：将章节、问题等混合数据拆分为全局数据缓存和用户状态缓存
- **优化序列化器结构**：创建独立的 `ChapterGlobalSerializer` 和 `ChapterUserStatusSerializer`
- **改进缓存键策略**：全局数据使用 `chapter:global:{id}` 格式，用户状态使用 `chapter:status:{course}:{user}` 格式
- **精细化缓存失效**：用户进度变化仅失效用户状态缓存，章节内容变化仅失效全局数据缓存
- **扩展快照字段**：在 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot` 中增加 `status` 字段
- **内存节省**：在100章节×1000用户场景下，缓存条目从10万条降至1100条，节省98.9%内存

## Capabilities

### New Capabilities

- **global-data-cache**: 全局数据缓存能力，实现章节、问题等静态内容的跨用户共享缓存，支持独立的缓存键策略和失效机制
- **user-state-cache**: 用户状态缓存能力，实现用户进度、解锁状态等动态数据的按用户隔离缓存，支持高频更新场景
- **cache-merge-layer**: 缓存合并层，负责在API响应时合并全局数据和用户状态，支持降级策略

### Modified Capabilities

- **progress-cache**: 修改缓存失效策略，用户进度变化时仅失效用户状态缓存，不影响全局数据缓存
- **route-caching**: 调整前端路由缓存策略，支持分离的全局数据和用户状态缓存

## Impact

**后端影响**：
- `backend/courses/serializers.py` - 拆分序列化器，新增 `ChapterGlobalSerializer`、`ProblemGlobalSerializer`
- `backend/courses/views.py` - 修改 `ChapterViewSet`、`ProblemViewSet` 的 `list` 和 `retrieve` 方法，实现分离缓存查询和合并
- `backend/courses/signals.py` - 新增信号处理器，精细化缓存失效
- `backend/courses/models.py` - 扩展 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot`，增加 `status` 字段
- `backend/common/mixins/cache_mixin.py` - 新增 `SeparateCacheMixin`，支持分离缓存策略

**前端影响**：
- 无需前端改动，API响应格式保持不变

**缓存影响**：
- 缓存键结构变化：从 `api:ChapterViewSet:{params}:user_id={id}` 拆分为 `chapter:global:{id}` 和 `chapter:status:{course}:{user}`
- 缓存命中率提升：全局数据可跨用户共享
- 内存占用降低：避免全局数据重复存储

**性能影响**：
- API响应延迟：增加缓存合并步骤（<5ms），但整体响应时间降低（缓存命中率高）
- 缓存查询次数：增加一次查询（全局+用户状态），但总体查询效率提升