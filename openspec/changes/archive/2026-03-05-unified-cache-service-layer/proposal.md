# 统一Cache服务层

## Why

当前系统中存在多种cache使用方式，导致代码不一致、缺少observability、难以维护。courses/views.py直接使用`django.core.cache.cache`绕过了CacheResult、metrics和穿透保护机制，而file_management使用了CacheMixin。这种混合实现方式使得缓存行为不可预测，难以调试和监控性能。

本change通过创建统一的服务层API，为所有cache操作提供标准接口，封装最佳实践（metrics、穿透保护、自适应TTL），为后续迁移现有代码奠定基础。

## What Changes

- **新增 SeparatedCacheService**：为分离缓存场景（全局数据+用户状态）提供统一API，封装两层缓存的获取、合并和失效逻辑
- **新增 BusinessCacheService**：为业务逻辑层缓存（如services.py中的快照、执行结果）提供标准接口
- **新增 CacheInvalidator**：统一的缓存失效API，提供类型安全的方法来失效ViewSet和分离缓存
- **增强 get_standard_cache_key()**：标准化cache key命名规范，支持分离缓存标记，确保所有key格式一致
- **保持向后兼容**：新增服务层，不修改现有代码，后续change可以逐步迁移

## Capabilities

### New Capabilities
- `separated-cache-service`: 提供全局数据和用户状态的分离缓存服务，支持自动合并和独立失效
- `business-cache-service`: 为业务逻辑层提供标准缓存接口，封装metrics和穿透保护
- `cache-invalidation-api`: 统一的缓存失效API，支持ViewSet和分离缓存的类型安全失效

### Modified Capabilities
无（本change只添加新服务层，不修改现有能力的行为要求）

## Impact

- **新增代码**：
  - `backend/common/services/separated_cache.py`：SeparatedCacheService实现
  - `backend/common/services/business_cache.py`：BusinessCacheService实现
  - `backend/common/utils/cache.py`：增强get_standard_cache_key()，新增CacheInvalidator类

- **不影响的代码**：
  - 现有views.py、services.py、signals.py保持不变
  - 不影响现有的CacheMixin工作方式

- **后续影响**：
  - 为下一步迁移（courses/views.py、services.py等）提供基础
  - 新功能应优先使用这些服务层API而非直接使用cache

- **无性能影响**：纯新增代码，不影响现有路径
- **无依赖变更**：使用现有的django-redis和Prometheus基础设施
