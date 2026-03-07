## Context

**当前状态：**

系统使用 Django + DRF，并实现了多层缓存机制：
- `StandardCacheListMixin` 和 `StandardCacheRetrieveMixin` - 提供统一的缓存键生成逻辑
- `CacheInvalidator` - 统一的缓存失效 API
- 用户隔离缓存 - 当 ViewSet 的 `get_queryset()` 过滤 `user` 时，缓存键自动注入 `user_id`

缓存键格式（通过 `get_standard_cache_key()` 生成）：
```
{prefix}:{view_name}[:parent_keys][:pk][:params][:user_id]
```

例如：`api:EnrollmentViewSet:user_id=1:page=1`

**问题：**

当 `CacheInvalidator.invalidate_viewset_list()` 生成失效 pattern 时，没有考虑 `user_id` 参数：

```python
# 当前实现
pattern = f"{cache_key}:*"  # 例如：api:EnrollmentViewSet:*

# 实际缓存键
# api:EnrollmentViewSet:user_id=1:page=1

# 结果：pattern 无法匹配实际缓存键
```

这导致用户隔离的缓存（如 EnrollmentViewSet）在创建对象后无法正确失效。

## Goals / Non-Goals

**Goals:**
1. 修复 CacheInvalidator 以支持用户隔离缓存的失效
2. 保持向后兼容性 - user_id 参数应为可选
3. 确保 EnrollmentViewSet 在 enroll 操作后能正确失效缓存
4. 为其他用户隔离的 ViewSet 提供可复用的解决方案

**Non-Goals:**
1. 不修改缓存键生成逻辑（`get_standard_cache_key`）
2. 不改变 StandardCacheListMixin 的行为
3. 不重构整个缓存系统（仅修复失效逻辑）

## Decisions

### 1. 扩展 CacheInvalidator API 而非创建新的 API

**决策：** 在现有的 `CacheInvalidator` 方法中添加可选的 `user_id` 参数

**理由：**
- 保持 API 一致性，开发者熟悉现有的失效方法
- 最小化代码变更
- 向后兼容 - 现有调用不需要修改

**替代方案考虑：**
- 创建新的 `invalidate_viewset_list_for_user()` 方法
  - ❌ 增加API复杂度，开发者需要记住两套方法
  - ❌ 代码重复

### 2. 修改信号处理器传递 user_id

**决策：** 在 `invalidate_enrollment_cache_on_create` 信号处理器中传递 `instance.user.id`

**理由：**
- Enrollment 对象包含 user 信息，可以直接获取
- 确保 enrollment 创建时只失效该用户的缓存（而非所有用户）
- 符合最小权限原则 - 只清除必要的缓存

**实现细节：**
```python
# 修改前
CacheInvalidator.invalidate_viewset_list(
    prefix=EnrollmentViewSet.cache_prefix,
    view_name=EnrollmentViewSet.__name__
)

# 修改后
CacheInvalidator.invalidate_viewset_list(
    prefix=EnrollmentViewSet.cache_prefix,
    view_name=EnrollmentViewSet.__name__,
    user_id=instance.user.id  # 新增参数
)
```

### 3. Pattern 生成策略

**决策：** 当提供 user_id 时，将其包含在基础缓存键中

**实现：**
```python
def invalidate_viewset_list(prefix, view_name, parent_pks=None, user_id=None):
    cache_key = get_standard_cache_key(
        prefix=prefix,
        view_name=view_name,
        parent_pks=parent_pks,
        user_id=user_id,  # 新增参数
    )
    pattern = f"{cache_key}:*"
    delete_cache_pattern(pattern)
```

**Pattern 匹配示例：**
```
# 不带 user_id
生成：api:EnrollmentViewSet:*
匹配：api:EnrollmentViewSet:page=1  (如果有全局缓存)

# 带 user_id=1
生成：api:EnrollmentViewSet:user_id=1:*
匹配：api:EnrollmentViewSet:user_id=1:page=1
不匹配：api:EnrollmentViewSet:user_id=2:page=1  (正确！其他用户缓存不受影响)
```

### 4. 同时更新 invalidate_viewset() 方法

**决策：** 为保持一致性，也给 `invalidate_viewset()` 添加 `user_id` 参数

**理由：**
- 如果 ViewSet 详情缓存也使用用户隔离，需要能失效特定用户的缓存
- API 一致性 - 两个失效方法都支持相同参数

## Risks / Trade-offs

### Risk 1: 现有代码可能未传递 user_id 导致缓存泄漏

**描述：** 如果其他地方使用 CacheInvalidator 失效用户隔离缓存，但没有传递 user_id，缓存将无法正确失效。

**缓解措施：**
- 代码审查：检查所有 CacheInvalidator 的调用点
- 添加日志：记录缓存失效操作，便于调试
- 文档更新：明确说明何时需要传递 user_id

### Risk 2: 性能影响 - 需要多次调用 delete_cache_pattern

**描述：** 如果需要失效多个用户的缓存（例如管理员操作），可能需要循环调用。

**缓解措施：**
- 这种场景很少见 - 大多数操作只影响单个用户的缓存
- 如果确实需要，可以在调用层循环
- 优化 Redis SCAN 操作，减少性能影响

### Trade-off: 灵活性 vs 简单性

**当前选择：** 显式传递 user_id

**优点：**
- 精确控制 - 只失效必要的缓存
- 避免意外清除其他用户的缓存

**缺点：**
- 需要调用者记得传递 user_id
- 增加少量代码复杂度

**替代方案（未采用）：**
- 失效所有用户的缓存（pattern: `api:EnrollmentViewSet:*:*`）
  - ❌ 过于激进，影响其他用户
  - ❌ 缓存命中率下降

## Migration Plan

### 部署步骤

1. **修改 CacheInvalidator** (`backend/common/utils/cache.py`)
   - 在 `invalidate_viewset_list()` 添加 `user_id` 参数
   - 在 `invalidate_viewset()` 添加 `user_id` 参数
   - 更新方法文档字符串

2. **修改信号处理器** (`backend/courses/signals.py`)
   - 更新 `invalidate_enrollment_cache_on_create` 传递 `user_id`
   - 验证其他信号处理器是否需要类似修改

3. **添加测试用例**
   - 测试用户隔离缓存的失效行为
   - 测试不带 user_id 的向后兼容性
   - 测试 enroll 接口后缓存正确失效

4. **代码审查**
   - 检查所有 CacheInvalidator 调用点
   - 确认用户隔离的 ViewSet 都有正确的缓存失效

5. **部署**
   - 先部署后端变更
   - 验证生产环境缓存失效日志
   - 监控缓存命中率和错误率

### 回滚策略

- 如果发现严重问题，可以快速回滚到之前版本
- user_id 是可选参数，回滚后现有代码仍能工作（只是缓存失效不够精确）
- 没有数据库迁移，回滚风险低

## Open Questions

1. **其他用户隔离的 ViewSet 是否也需要修复？**
   - 需要审查所有使用 `filter(user=...)` 的 ViewSet
   - 确认它们的缓存失效逻辑是否正确

2. **是否需要添加自动检测机制？**
   - 考虑在 InvalidateCacheMixin 中自动检测用户隔离并传递 user_id
   - 但这可能增加复杂度，优先手动修复

3. **如何验证修复效果？**
   - 添加集成测试模拟 enroll 操作
   - 在测试环境验证缓存失效日志
   - 考虑添加缓存失效的监控指标
