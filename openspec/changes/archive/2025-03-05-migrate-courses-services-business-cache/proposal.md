# 迁移 courses/services.py 的业务逻辑缓存到统一服务层

## Why

**当前问题**

`courses/services.py` 中有多处使用直接 `cache.get/set` 实现业务逻辑缓存，存在以下问题：

1. **缺少类型安全**：手动构造 cache key，容易拼写错误
2. **无统一接口**：`cache.set/get` 调用分散，难以统一调整 TTL
3. **缺少 Observability**：无 Prometheus metrics 记录缓存命中率
4. **无缓存穿透保护**：未使用 `CacheResult.is_null_value`
5. **缓存失效逻辑复杂**：`_invalidate_cache()` 使用通配符删除，但 key 格式不标准

**影响范围**

- `ChapterUnlockService`：章节解锁状态缓存（影响解锁逻辑性能）
- `get_user_chapter_status()`：用户章节状态缓存（影响章节列表响应时间）
- `get_user_problem_status()`：用户问题状态缓存（影响问题列表响应时间）

**为什么现在迁移**

- ✅ Phase 1 已完成：`BusinessCacheService.cache_result()`、`CacheInvalidator` 已实现
- ✅ Phase 2 已完成：全局数据缓存已迁移，遗留用户状态缓存需要统一
- ✅ 后续依赖：Phase 4 需要基于统一的缓存失效机制

## What Changes

**迁移范围**（3 个业务逻辑模块）

| 模块 | 方法 | 当前 Key 格式 | 新 Key 格式 |
|------|------|---------------|-------------|
| `ChapterUnlockService` | `_get_cache_key()` | `unlock:chapter:{chapter_id}:{enrollment_id}` | `courses:ChapterUnlockService:UNLOCK:chapter_pk={chapter_id}:enrollment_pk={enrollment_id}` |
| `ChapterUnlockService` | `_invalidate_cache()` | `unlock:chapter:{chapter_id}:*`（通配符） | `courses:ChapterUnlockService:UNLOCK:chapter_pk={chapter_id}:*` |
| `courses/services.py` | `get_user_chapter_status()` | `chapter:status:{course_id}:{user_id}` | `courses:business:ChapterStatus:course_pk={course_id}:user_id={user_id}` |
| `courses/services.py` | `get_user_problem_status()` | `problem:status:{chapter_id}:{user_id}` | `courses:business:ProblemStatus:chapter_pk={chapter_id}:user_id={user_id}` |

**代码变更**

### 1. ChapterUnlockService 重构

**旧代码**：
```python
class ChapterUnlockService:
    UNLOCK_CACHE_PREFIX = "unlock:chapter"

    @classmethod
    def _get_cache_key(cls, chapter_id, enrollment_id, prefix=None):
        if prefix is None:
            prefix = cls.UNLOCK_CACHE_PREFIX
        return f"{prefix}:{chapter_id}:{enrollment_id}"

    @classmethod
    def _set_cache(cls, key, value):
        cache.set(key, value, cls.CACHE_TIMEOUT)

    @classmethod
    def _get_cache(cls, key):
        return cache.get(key)

    @classmethod
    def is_unlocked(cls, chapter, enrollment):
        cache_key = cls._get_cache_key(chapter.id, enrollment.id)
        cached_result = cls._get_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # 计算解锁状态
        result = compute_unlock_status(chapter, enrollment)
        cls._set_cache(cache_key, result)
        return result
```

**新代码**：
```python
from common.services import BusinessCacheService
from common.utils.cache import get_standard_cache_key, CacheInvalidator

class ChapterUnlockService:
    CACHE_TIMEOUT = 300  # 5分钟

    @classmethod
    def is_unlocked(cls, chapter, enrollment):
        """使用 BusinessCacheService 缓存解锁状态"""
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={"chapter_pk": chapter.id, "enrollment_pk": enrollment.id},
            params={"type": "UNLOCK"}
        )

        result, is_hit = BusinessCacheService.cache_result(
            cache_key=cache_key,
            fetcher=lambda: cls._compute_unlock_status(chapter, enrollment),
            timeout=cls.CACHE_TIMEOUT
        )

        if is_hit:
            logger.debug(f"Unlock cache HIT for chapter {chapter.id}, enrollment {enrollment.id}")
        else:
            logger.debug(f"Unlock cache MISS for chapter {chapter.id}, enrollment {enrollment.id}")

        return result

    @staticmethod
    def _compute_unlock_status(chapter, enrollment):
        """计算解锁状态（纯业务逻辑，无缓存）"""
        # ... 原有的解锁计算逻辑 ...
        pass
```

### 2. get_user_chapter_status() 重构

**旧代码**：
```python
def get_user_chapter_status(course_id, user_id, chapter_ids):
    cache_key = f"chapter:status:{course_id}:{user_id}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    # 从数据库获取用户状态
    result = compute_user_status_from_db(...)
    cache.set(cache_key, result, timeout=300)
    return result
```

**新代码**：
```python
from common.services import BusinessCacheService
from common.utils.cache import get_standard_cache_key

def get_user_chapter_status(course_id, user_id, chapter_ids):
    cache_key = get_standard_cache_key(
        prefix="courses",
        view_name="business:ChapterStatus",
        parent_pks={"course_pk": course_id},
        query_params={"user_id": user_id}
    )

    result, is_hit = BusinessCacheService.cache_result(
        cache_key=cache_key,
        fetcher=lambda: _compute_user_chapter_status_from_db(course_id, user_id, chapter_ids),
        timeout=300
    )

    if is_hit:
        logger.debug(f"Chapter status cache HIT for user {user_id}, course {course_id}")
    else:
        logger.debug(f"Chapter status cache MISS for user {user_id}, course {course_id}")

    return result
```

### 3. get_user_problem_status() 重构

**类似模式，使用 BusinessCacheService.cache_result()**

### 4. 缓存失效逻辑迁移到 Phase 4

**本 change 不包含**：`_invalidate_cache()` 的迁移（将在 Phase 4 中使用 `CacheInvalidator` 重构）

## Capabilities

### New Capabilities
- 无新增 capabilities，本 change 是迁移现有功能到新 API

### Modified Capabilities
- 无修改 capabilities，缓存能力已由 Phase 1 提供

## Dependencies

**依赖 Phase 1**（unified-cache-service-layer）
- ✅ `BusinessCacheService.cache_result()` 已实现
- ✅ `get_standard_cache_key()` 已支持标准化 key 生成
- ✅ `CacheResult` 已支持穿透保护

**依赖 Phase 2**（migrate-courses-views-separated-cache）
- ✅ 全局数据缓存已迁移，遗留用户状态缓存需要统一

**依赖现有基础设施**
- ✅ 业务逻辑函数（`_compute_unlock_status`、`_compute_user_chapter_status_from_db`）已存在
- ✅ Prometheus metrics（`cache_requests_total`, `cache_operation_duration_seconds`）已配置

## Impact

**代码变更**
- `backend/courses/services.py`：
  - 修改 `ChapterUnlockService` 类（约 50 行代码替换）
  - 修改 `get_user_chapter_status()`（约 20 行代码替换）
  - 修改 `get_user_problem_status()`（约 20 行代码替换）
  - 移除 `_get_cache_key()`、`_set_cache()`、`_get_cache()` 辅助方法

**测试变更**
- `backend/courses/tests/test_services.py`：
  - 更新缓存相关的 mock 期望
  - 旧：`mock_cache.get.return_value = None`
  - 新：`mock_business_cache.cache_result.return_value = (result, False)`

**性能影响**
- ✅ 预期性能改善：服务层开销 < 1μs（Phase 1 已验证）
- ✅ 缓存命中率保持：业务逻辑不变，缓存行为一致
- ✅ Observability 增强：自动记录 Prometheus metrics

**兼容性影响**
- ✅ API 兼容：函数签名和返回值不变
- ✅ 缓存兼容：旧缓存 key 在 TTL 过期前仍然有效，但新代码使用新 key
- ⚠️ 监控影响：需要更新 Grafana dashboard 中的缓存 key 过滤器
  - 旧：`key_prefix="unlock:chapter"`
  - 新：`key_prefix="courses:ChapterUnlockService:UNLOCK"`

## Migration Plan

**步骤 1：准备测试**
1. 更新 `test_services.py` 中的测试用例，mock `BusinessCacheService.cache_result`
2. 添加集成测试：验证新旧 key 格式都能正常工作（过渡期）

**步骤 2：迁移 ChapterUnlockService**
1. 重构 `_get_cache_key()` → 使用 `get_standard_cache_key()`
2. 重构 `_set_cache()` / `_get_cache()` → 使用 `BusinessCacheService.cache_result()`
3. 提取纯业务逻辑到 `_compute_unlock_status()`
4. 添加 cache hit/miss 日志

**步骤 3：迁移 get_user_chapter_status()**
1. 替换 cache.get/set → BusinessCacheService.cache_result
2. 使用 `get_standard_cache_key()` 生成标准 key
3. 添加 cache hit/miss 日志

**步骤 4：迁移 get_user_problem_status()**
1. 同步骤 3

**步骤 5：验证**
1. 运行单元测试：`pytest backend/courses/tests/test_services.py -v`
2. 运行集成测试：`pytest backend/courses/tests/test_cache_integration.py -v`
3. 手动测试：
   - 访问章节列表，验证解锁状态正确
   - 访问问题列表，验证用户状态正确
   - 检查 Prometheus metrics：`curl http://localhost:9090/metrics | grep cache_requests_total`

**步骤 6：监控**
1. 观察缓存命中率：`rate(cache_requests_total{operation="get"}[5m])`
2. 观察业务响应时间：`rate(http_request_duration_seconds{path=~"/api/courses/.*"}[5m])`
3. 检查日志中的 cache hit/miss 消息

**回滚计划**
- 如果缓存命中率下降 > 10%，回滚到旧实现
- 如果解锁状态计算错误（用户投诉），回滚到旧实现
- 回滚方式：`git revert <commit>`

## Risks / Trade-offs

### Risk 1: 业务逻辑复杂度高，缓存逻辑容易出错

**风险**：解锁状态计算涉及前置章节、解锁日期等多个条件，迁移时可能引入 bug

**缓解**：
- **提取纯函数**：将解锁计算逻辑提取到 `_compute_unlock_status()`，无缓存依赖
- **测试覆盖**：添加单元测试，覆盖所有解锁条件类型（prerequisite、date、all）
- **灰度验证**：先在测试环境验证解锁逻辑正确性，再发布到生产

### Risk 2: 用户状态缓存 key 包含 user_id，可能被误删除

**风险**：如果 `CacheInvalidator` 使用通配符失效，可能误删其他用户的缓存

**缓解**：
- **Scope 明确**：本 change 不迁移缓存失效逻辑（Phase 4 负责）
- **Key 设计**：使用 `user_id` 作为 query_param，避免被通配符误删
- **监控告警**：如果缓存命中率突然下降，检查是否有误删除

### Risk 3: 缓存 TTL 不一致导致数据新鲜度问题

**风险**：不同业务逻辑的 TTL 不同（解锁状态 5 分钟，用户状态 5 分钟），可能过期导致性能下降

**缓解**：
- **保持 TTL 不变**：迁移时保持原有 TTL 值（`CACHE_TIMEOUT=300`）
- **自适应 TTL**：Phase 1 已实现 `AdaptiveTTLCalculator`，根据命中率自动调整 TTL
- **监控指标**：观察缓存命中率，如果下降 > 5%，考虑延长 TTL

## Open Questions

### Q1: 是否需要保持旧缓存 key 的兼容性？

**问题**：迁移后是否需要继续支持旧的缓存 key 格式？

**选项**：
- **A**：双写新旧 key，完全兼容（过渡期 1 周）
- **B**：只写新 key，旧 key 自然过期（TTL 5 分钟后失效）

**倾向**：选择 B，理由：
- TTL 较短（5 分钟），旧 key 快速过期
- 用户状态缓存相对独立，不会影响全局数据缓存
- 双写增加复杂度，收益有限

**决策**：只写新 key，不保持旧 key 兼容

### Q2: 是否需要迁移缓存失效逻辑？

**问题**：本 change 是否包含 `_invalidate_cache()` 的迁移？

**选项**：
- **A**：一起迁移（完整性强）
- **B**：延后到 Phase 4（职责分离）

**倾向**：选择 B，理由：
- `_invalidate_cache()` 依赖 `CacheInvalidator`，属于失效逻辑的范畴
- Phase 4 会统一迁移所有失效逻辑（包括 signals.py）
- 避免本 change 范围过大

**决策**：不迁移 `_invalidate_cache()`，保留旧实现，Phase 4 统一重构

### Q3: 是否需要添加缓存预热逻辑？

**问题**：是否需要在服务层添加 `warm_unlock_cache()` 方法？

**选项**：
- **A**：添加预热方法（主动预热热门课程）
- **B**：依赖 on-demand 缓存（按需缓存）

**倾向**：选择 B，理由：
- 当前已有 `cache_warming/tasks.py`，按需预热机制已存在
- 解锁状态是用户特定的，无法提前预知哪些用户会访问
- 添加预热方法增加复杂度，收益有限

**决策**：不添加预热方法，依赖现有 on-demand 机制
