# 迁移 signals.py 的缓存失效逻辑到统一服务层

## Why

**当前问题**

`courses/signals.py` 中的缓存失效逻辑使用直接 `cache.delete()` 和手动构造 key，存在以下问题：

1. **Key 格式不一致**：
   - signals.py 使用：`f"chapter:global:{chapter_id}"`
   - views.py 迁移后使用：`courses:ChapterViewSet:SEPARATED:GLOBAL:pk={chapter_id}`
   - 导致失效逻辑无法命中新的缓存 key

2. **缺少类型安全**：手动拼接字符串，容易拼写错误
   ```python
   # 旧代码：容易出错
   cache.delete(f"chapter:global:list:{course_id}")
   # 拼写错误示例
   cache.delete(f"chapters:global:list:{course_id}")  # 多了 's'
   ```

3. **缺少统一接口**：每个信号处理器重复实现失效逻辑
   ```python
   # 重复代码
   @receiver(post_save, sender=Chapter)
   def on_chapter_change(...):
       cache.delete(f"chapter:global:{chapter_id}")
       cache.delete(f"chapter:global:list:{course_id}")

   @receiver(post_save, sender=Problem)
   def on_problem_change(...):
       cache.delete(f"problem:global:{problem_id}")
       cache.delete(f"problem:global:list:{chapter_id}")
   ```

4. **缺少 Observability**：无日志记录失效操作，难以排查缓存未失效问题

5. **无法批量失效**：使用 `cache.delete()` 只能失效单个 key，无法使用通配符批量失效

**为什么现在迁移**

- ✅ Phase 1 已完成：`CacheInvalidator` 已实现，提供标准失效 API
- ✅ Phase 2 已完成：views.py 中的缓存 key 已标准化，失效逻辑需要同步更新
- ✅ Phase 3 已完成：services.py 中的缓存 key 已标准化，失效逻辑需要同步更新

## What Changes

**迁移范围**（2 个信号处理器 + 1 个辅助方法）

| 信号处理器 | 当前失效逻辑 | 新失效逻辑 |
|-----------|-------------|-----------|
| `on_chapter_content_change()` | `cache.delete(f"chapter:global:{chapter_id}")`<br>`cache.delete(f"chapter:global:list:{course_id}")` | `CacheInvalidator.invalidate_separated_cache_global(...)` |
| `on_problem_content_change()` | `cache.delete(f"problem:global:{problem_id}")`<br>`cache.delete(f"problem:global:list:{chapter_id}")` | `CacheInvalidator.invalidate_separated_cache_global(...)` |
| `ChapterUnlockService._invalidate_cache()` | `delete_cache_pattern(f"unlock:chapter:{chapter_id}:*")` | `CacheInvalidator.invalidate_viewset_list(...)` |

**代码变更**

### 1. on_chapter_content_change() 重构

**旧代码**：
```python
@receiver(post_save, sender=Chapter)
def on_chapter_content_change(sender, instance, **kwargs):
    """章节内容变化 → 失效全局数据缓存"""
    from django.core.cache import cache

    chapter_id = instance.id
    course_id = instance.course_id

    # 失效单个章节的全局数据缓存
    cache.delete(f"chapter:global:{chapter_id}")

    # 失效课程章节列表的全局数据缓存
    cache.delete(f"chapter:global:list:{course_id}")

    logger.debug(
        f"Invalidated chapter global cache for chapter {chapter_id} and course {course_id}"
    )
```

**新代码**：
```python
from common.utils.cache import CacheInvalidator

@receiver(post_save, sender=Chapter)
def on_chapter_content_change(sender, instance, **kwargs):
    """章节内容变化 → 失效全局数据缓存（使用统一服务层）"""
    chapter_id = instance.id
    course_id = instance.course_id

    # 失效单个章节的全局数据缓存
    CacheInvalidator.invalidate_separated_cache_global(
        prefix="courses",
        view_name="ChapterViewSet",
        pk=chapter_id,
        parent_pks={"course_pk": course_id}
    )

    # 失效课程章节列表的全局数据缓存
    CacheInvalidator.invalidate_separated_cache_global(
        prefix="courses",
        view_name="ChapterViewSet",
        pk=None,  # list view 无 pk
        parent_pks={"course_pk": course_id}
    )

    logger.debug(
        f"Invalidated chapter global cache for chapter {chapter_id} and course {course_id} "
        f"using CacheInvalidator"
    )
```

### 2. on_problem_content_change() 重构

**旧代码**：
```python
@receiver(post_save, sender=Problem)
def on_problem_content_change(sender, instance, **kwargs):
    """问题内容变化 → 失效全局数据缓存"""
    from django.core.cache import cache

    problem_id = instance.id
    chapter_id = instance.chapter_id

    # 失效单个问题的全局数据缓存
    cache.delete(f"problem:global:{problem_id}")

    # 失效章节问题列表的全局数据缓存
    if chapter_id:
        cache.delete(f"problem:global:list:{chapter_id}")

    logger.debug(
        f"Invalidated problem global cache for problem {problem_id} and chapter {chapter_id}"
    )
```

**新代码**：
```python
from common.utils.cache import CacheInvalidator

@receiver(post_save, sender=Problem)
def on_problem_content_change(sender, instance, **kwargs):
    """问题内容变化 → 失效全局数据缓存（使用统一服务层）"""
    problem_id = instance.id
    chapter_id = instance.chapter_id

    # 失效单个问题的全局数据缓存
    CacheInvalidator.invalidate_separated_cache_global(
        prefix="courses",
        view_name="ProblemViewSet",
        pk=problem_id,
        parent_pks={"chapter_pk": chapter_id} if chapter_id else None
    )

    # 失效章节问题列表的全局数据缓存
    if chapter_id:
        CacheInvalidator.invalidate_separated_cache_global(
            prefix="courses",
            view_name="ProblemViewSet",
            pk=None,  # list view 无 pk
            parent_pks={"chapter_pk": chapter_id}
        )

    logger.debug(
        f"Invalidated problem global cache for problem {problem_id} and chapter {chapter_id} "
        f"using CacheInvalidator"
    )
```

### 3. ChapterUnlockService._invalidate_cache() 重构

**旧代码**：
```python
@classmethod
def _invalidate_cache(cls, chapter_id, enrollment_id=None):
    """使缓存失效"""
    patterns_to_invalidate = []

    # 使当前章节的缓存失效
    patterns_to_invalidate.append(f"{cls.UNLOCK_CACHE_PREFIX}:{chapter_id}:*")
    patterns_to_invalidate.append(
        f"{cls.PREREQUISITE_PROGRESS_CACHE_PREFIX}:{chapter_id}:*"
    )

    # 如果 enrollment_id 提供了，使其特定的缓存失效
    if enrollment_id:
        patterns_to_invalidate.append(
            f"{cls.UNLOCK_CACHE_PREFIX}:{chapter_id}:{enrollment_id}"
        )
        patterns_to_invalidate.append(
            f"{cls.PREREQUISITE_PROGRESS_CACHE_PREFIX}:{chapter_id}:{enrollment_id}"
        )

    from common.utils.cache import delete_cache_pattern

    for pattern in patterns_to_invalidate:
        delete_cache_pattern(pattern)
```

**新代码**：
```python
from common.utils.cache import CacheInvalidator, get_standard_cache_key

@classmethod
def _invalidate_cache(cls, chapter_id, enrollment_id=None):
    """使缓存失效（使用统一服务层）"""
    # 失效所有章节解锁缓存（通配符）
    CacheInvalidator.invalidate_viewset_list(
        prefix="courses",
        view_name="ChapterUnlockService",
        parent_pks={"chapter_pk": chapter_id},
        query_params={"type": "UNLOCK"}
    )

    # 如果 enrollment_id 提供了，失效特定用户的缓存（精确删除）
    if enrollment_id:
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={"chapter_pk": chapter_id, "enrollment_pk": enrollment_id},
            query_params={"type": "UNLOCK"}
        )
        CacheInvalidator.invalidate_by_key(cache_key)  # 精确删除单个 key
```

## Capabilities

### New Capabilities
- 无新增 capabilities，本 change 是迁移现有功能到新 API

### Modified Capabilities
- 无修改 capabilities，失效能力已由 Phase 1 提供

## Dependencies

**依赖 Phase 1**（unified-cache-service-layer）
- ✅ `CacheInvalidator.invalidate_separated_cache_global()` 已实现
- ✅ `CacheInvalidator.invalidate_viewset_list()` 已实现
- ✅ `get_standard_cache_key()` 已支持标准化 key 生成

**依赖 Phase 2**（migrate-courses-views-separated-cache）
- ✅ views.py 中的缓存 key 已标准化，失效逻辑需要同步

**依赖 Phase 3**（migrate-courses-services-business-cache）
- ✅ services.py 中的缓存 key 已标准化，失效逻辑需要同步

## Impact

**代码变更**
- `backend/courses/signals.py`：
  - 修改 `on_chapter_content_change()`（约 15 行代码替换）
  - 修改 `on_problem_content_change()`（约 15 行代码替换）

- `backend/courses/services.py`：
  - 修改 `ChapterUnlockService._invalidate_cache()`（约 20 行代码替换）

**测试变更**
- `backend/courses/tests/test_signals.py`：
  - 更新失效相关的 mock 期望
  - 旧：`mock_cache.delete.assert_called_with("chapter:global:123")`
  - 新：`mock_cache_invalidator.invalidate_separated_cache_global.assert_called_once_with(...)`

**兼容性影响**
- ✅ 功能兼容：失效逻辑不变，只是使用新 API
- ⚠️ 监控影响：需要更新 Grafana dashboard 中的失效操作监控
  - 旧：手动解析日志中的 `f"Invalidated chapter global cache"`
  - 新：可以使用 Prometheus metrics：`cache_invalidations_total{key_prefix="courses:ChapterViewSet"}`

**性能影响**
- ✅ 预期性能改善：`CacheInvalidator` 内部使用 `delete_cache_pattern()`，批量失效更高效
- ✅ 失效延迟降低：`CacheInvalidator` 支持异步失效（可选），避免阻塞主流程

## Migration Plan

**步骤 1：准备测试**
1. 更新 `test_signals.py` 中的测试用例，mock `CacheInvalidator`
2. 添加集成测试：验证失效操作真实删除 Redis 中的 key

**步骤 2：迁移 signals.py**
1. 修改 `on_chapter_content_change()`：
   - 替换 `cache.delete()` → `CacheInvalidator.invalidate_separated_cache_global()`
   - 使用标准化 key 生成
   - 添加详细日志
2. 修改 `on_problem_content_change()`：同上

**步骤 3：迁移 services.py**
1. 修改 `ChapterUnlockService._invalidate_cache()`：
   - 替换 `delete_cache_pattern()` → `CacheInvalidator.invalidate_viewset_list()`
   - 使用标准化 key 生成
   - 添加详细日志

**步骤 4：验证**
1. 运行单元测试：`pytest backend/courses/tests/test_signals.py -v`
2. 运行集成测试：`pytest backend/courses/tests/test_cache_integration.py -v`
3. 手动测试：
   - 修改章节内容，检查 Redis 中旧的缓存 key 是否被删除
   - 修改问题内容，检查 Redis 中旧的缓存 key 是否被删除
   - 检查 Prometheus metrics：`curl http://localhost:9090/metrics | grep cache_invalidations_total`

**步骤 5：监控**
1. 观察失效操作数量：`rate(cache_invalidations_total[5m])`
2. 观察缓存命中率：`rate(cache_requests_total{operation="get"}[5m])`
3. 检查日志中的失效消息

**回滚计划**
- 如果缓存未失效导致数据不一致（用户投诉），回滚到旧实现
- 如果失效操作性能下降（响应时间增加 > 20%），回滚到旧实现
- 回滚方式：`git revert <commit>`

## Risks / Trade-offs

### Risk 1: 失效逻辑错误导致缓存未删除

**风险**：新 API 参数错误，导致缓存 key 未匹配，旧缓存仍然有效

**缓解**：
- **集成测试**：添加端到端测试，验证失效操作真实删除 Redis 中的 key
  ```python
  def test_invalidation_removes_keys():
      # 1. 写入缓存
      SeparatedCacheService.get_global_data(...)
      # 2. 触发失效
      on_chapter_content_change(sender=Chapter, instance=chapter)
      # 3. 验证缓存已删除
      assert cache.get("courses:ChapterViewSet:SEPARATED:GLOBAL:...") is None
  ```
- **监控告警**：添加 Prometheus 告警，如果失效操作数量为 0，发送告警
- **灰度发布**：先在测试环境验证失效逻辑正确性，再发布到生产

### Risk 2: 批量失效导致性能问题

**风险**：`CacheInvalidator.invalidate_viewset_list()` 使用通配符删除，可能影响 Redis 性能

**缓解**：
- **KEYS 命令限制**：`delete_cache_pattern()` 内部使用 `scan()` + `delete()`，避免 `KEYS *` 阻塞
- **监控 Redis 性能**：观察 Redis 的 `used_memory` 和 `instantaneous_ops_per_sec`
- **限制批量失效数量**：如果匹配的 key 数量 > 1000，发送告警

### Risk 3: 信号处理器异常导致业务逻辑失败

**风险**：如果 `CacheInvalidator` 抛出异常，可能阻断模型保存操作

**缓解**：
- **静默失败**：`CacheInvalidator` 内部已实现异常捕获，失效操作失败不影响主流程
  ```python
  # CacheInvalidator 内部实现
  try:
      cache.delete(cache_key)
  except Exception as e:
      logger.debug(f"Failed to delete cache {cache_key}: {e}")
      # 不抛出异常，避免影响业务逻辑
  ```
- **日志记录**：所有失效失败都会记录 debug 日志，便于排查
- **监控告警**：如果失效失败率 > 1%，发送告警

## Open Questions

### Q1: 是否需要支持失效用户状态缓存？

**问题**：章节/问题内容变化时，是否需要失效用户状态缓存？

**选项**：
- **A**：失效用户状态缓存（彻底）
- **B**：只失效全局数据缓存（当前行为）

**倾向**：选择 B，理由：
- **业务逻辑**：用户状态（解锁状态、进度）独立于内容变化
- **性能考虑**：失效用户状态缓存会导致大量 cache miss，增加数据库压力
- **当前行为**：signals.py 只失效全局数据缓存，不失效用户状态缓存

**决策**：保持当前行为，只失效全局数据缓存，不失效用户状态缓存

### Q2: 是否需要支持异步失效？

**问题**：失效操作是否应该异步执行（使用 Celery task）？

**选项**：
- **A**：同步失效（简单）
- **B**：异步失效（性能）

**倾向**：选择 A，理由：
- **当前行为**：signals.py 中失效操作是同步的
- **失效速度快**：`cache.delete()` 操作通常 < 1ms，异步收益有限
- **复杂度低**：无需引入 Celery task

**决策**：保持同步失效，不引入异步机制

### Q3: 是否需要添加失效 metrics？

**问题**：是否需要记录失效操作的 Prometheus metrics？

**选项**：
- **A**：添加 metrics（可观测性）
- **B**：依赖日志（简单）

**倾向**：选择 A，理由：
- **可观测性**：metrics 可以在 Grafana 中可视化，更直观
- **告警支持**：可以基于 metrics 设置告警（失效失败率 > 1%）
- **成本低**：只需在 `CacheInvalidator` 中添加 `cache_invalidations_total` 计数器

**决策**：在 `CacheInvalidator` 中添加失效 metrics，记录失效操作的次数和状态
