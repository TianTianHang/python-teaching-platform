## Context

Phase 3 已完成 `courses/services.py` 中业务逻辑缓存的迁移，使用 `BusinessCacheService.cache_result()` 实现标准 key 格式。但遗留的缓存失效逻辑仍使用旧的通配符模式：

**当前问题代码**（`ChapterUnlockService._invalidate_cache()`）：
```python
patterns_to_invalidate = []
patterns_to_invalidate.append(f"{cls.UNLOCK_CACHE_PREFIX}:{chapter_id}:*")
patterns_to_invalidate.append(f"{cls.PREREQUISITE_PROGRESS_CACHE_PREFIX}:{chapter_id}:*")
# ...
for pattern in patterns_to_invalidate:
    delete_cache_pattern(pattern)
```

**遗留方法**：
- `_get_cache_key()` - 生成旧格式 key (`chapter_unlock:{id}:{id}`)
- `_set_cache()` / `_get_cache()` - 直接调用 `cache.get/set`
- `UNLOCK_CACHE_PREFIX` / `PREREQUISITE_PROGRESS_CACHE_PREFIX` 常量

## Goals / Non-Goals

**Goals:**
- 将 `ChapterUnlockService._invalidate_cache()` 迁移到使用 `CacheInvalidator`
- 删除遗留的缓存方法和常量
- 确保所有缓存失效使用标准 key 格式

**Non-Goals:**
- 不修改 `CacheInvalidator` 本身（已在 Phase 1 实现）
- 不修改其他模块的缓存失效逻辑（如 feature_flags, throttling）

## Decisions

### Decision 1: 使用 CacheInvalidator 替换通配符删除

**Options Considered:**
- A. 继续使用通配符删除 `delete_cache_pattern()`
- B. 使用 `CacheInvalidator.invalidate_viewset()` 或 `invalidate_separated_cache_user_status()`

**Chosen:** B

**Rationale:**
- 统一 key 格式，确保只删除新格式的缓存
- 类型安全，API 明确
- 便于监控和调试

### Decision 2: 删除遗留方法而非保留向后兼容

**Options Considered:**
- A. 保留旧方法用于向后兼容
- B. 完全删除旧方法

**Chosen:** B

**Rationale:**
- Phase 3 已完成迁移，旧 key 已不再使用
- 减少代码复杂度
- 避免未来的维护负担

## Risks / Trade-offs

**Risk 1:** 过渡期间旧缓存未被清除
- **Mitigation:** 旧 key 有 TTL，过期后自动失效

**Risk 2:** 缓存失效不完整导致数据不一致
- **Mitigation:** 测试验证新旧缓存都能被正确失效