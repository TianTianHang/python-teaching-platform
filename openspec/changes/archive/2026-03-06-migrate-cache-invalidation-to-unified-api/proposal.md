## Why

Phase 3 已将 `courses/services.py` 中的业务逻辑缓存迁移到 `BusinessCacheService.cache_result()`，但遗留的缓存失效逻辑仍使用旧的通配符模式。这导致：
- 缓存失效不完整（可能遗漏新格式的 key）
- 无统一的失效 API，难以维护和监控
- 旧的 `_get_cache_key()`、`_set_cache()`、`_get_cache()` 方法仍存在，增加代码复杂度

## What Changes

1. **迁移 ChapterUnlockService 缓存失效逻辑** - 将 `_invalidate_cache()` 迁移到使用 `CacheInvalidator.invalidate_viewset()` 或 `CacheInvalidator.invalidate_separated_cache_user_status()`

2. **清理遗留缓存方法** - 删除 `ChapterUnlockService` 中的 `_get_cache_key()`、`_set_cache()`、`_get_cache()` 旧方法

3. **清理遗留缓存常量** - 删除 `UNLOCK_CACHE_PREFIX`、`PREREQUISITE_PROGRESS_CACHE_PREFIX` 常量

4. **迁移 signals 中的缓存失效调用** - 将 signals 中直接使用 `cache.delete()` 或通配符删除的调用迁移到 `CacheInvalidator`

## Capabilities

### New Capabilities
- `cache-invalidation-unified`: 统一的缓存失效 API，确保所有缓存失效操作使用标准 key 格式

### Modified Capabilities
- `business-cache-service`: 更新需求，说明缓存失效应使用 `CacheInvalidator`

## Impact

- `backend/courses/services.py`：
  - 修改 `ChapterUnlockService._invalidate_cache()` 使用 `CacheInvalidator`
  - 删除 `_get_cache_key()`、`_set_cache()`、`_get_cache()` 方法
  - 删除 `UNLOCK_CACHE_PREFIX`、`PREREQUISITE_PROGRESS_CACHE_PREFIX` 常量

- `backend/courses/signals.py`：
  - 更新缓存失效调用使用 `CacheInvalidator`

- 测试：
  - 更新 `test_services.py` 中的缓存失效测试
  - 更新 `test_signals.py` 中的失效验证