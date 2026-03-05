## Context

当前 `courses/services.py` 中存在多处直接使用 `cache.get/set` 实现业务逻辑缓存，这种方式存在以下问题：

1. **缺少类型安全**：手动构造 cache key，容易拼写错误
2. **无统一接口**：缓存调用分散，难以统一调整 TTL
3. **缺少 Observability**：无 Prometheus metrics 记录缓存命中率
4. **无缓存穿透保护**：未使用 `CacheResult.is_null_value`
5. **缓存失效逻辑复杂**：`_invalidate_cache()` 使用通配符删除

**目标模块**：
- `ChapterUnlockService`：章节解锁状态缓存
- `get_user_chapter_status()`：用户章节状态缓存
- `get_user_problem_status()`：用户问题状态缓存

## Goals / Non-Goals

**Goals:**
- 将 `ChapterUnlockService`、`get_user_chapter_status()`、`get_user_problem_status()` 迁移到使用 `BusinessCacheService.cache_result()`
- 保持现有缓存行为不变
- 添加缓存 hit/miss 日志记录

**Non-Goals:**
- 不修改缓存失效逻辑（将在 Phase 4 处理）
- 不修改业务逻辑计算方式

## Decisions

### Decision 1: 使用 BusinessCacheService.cache_result() 替换直接 cache.get/set

**Options Considered:**
- A. 直接使用 `cache.get/set` + 手动 key 生成
- B. 使用 `BusinessCacheService.cache_result()` + 标准 key 生成

**Chosen:** B

**Rationale:**
- 自动类型安全的标准 key 生成
- 内置 Prometheus metrics 记录
- 内置缓存穿透保护
- 统一 TTL 管理

### Decision 2: 缓存 key 格式标准化

**Options Considered:**
- A. 保持现有 key 格式
- B. 使用 `get_standard_cache_key()` 生成标准 key

**Chosen:** B

**Rationale:**
- 统一格式便于缓存管理和失效
- 便于监控和分析

### Decision 3: 保留原有 TTL 设置

**Options Considered:**
- A. 统一使用 BusinessCacheService 默认 TTL
- B. 保留原有 TTL 设置

**Chosen:** B

**Rationale:**
- 避免改变缓存行为

## Risks / Trade-offs

**Risk 1:** 新旧 key 格式不兼容
- **Mitigation:** 旧 key 在 TTL 过期前仍然有效，过渡期间两个 key 会同时存在

**Risk 2:** 缓存命中率暂时下降
- **Mitigation:** 监控缓存命中率，如有下降 > 10% 则回滚

**Risk 3:** 缓存失效逻辑变化
- **Mitigation:** 缓存失效逻辑在 Phase 4 迁移，当前保持原有失效逻辑