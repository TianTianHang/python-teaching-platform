## Why

当用户调用 `/api/v1/courses/{id}/enroll/` 接口加入课程后，EnrollmentViewSet 的缓存没有正确失效，导致前端仍显示空的课程列表。这是因为 CacheInvalidator.invalidate_viewset_list() 方法没有考虑用户隔离缓存的场景，导致生成的 pattern 无法匹配实际的缓存键。

## What Changes

- 扩展 `CacheInvalidator.invalidate_viewset_list()` 方法，添加 `user_id` 可选参数以支持用户隔离缓存
- 扩展 `CacheInvalidator.invalidate_viewset()` 方法，添加 `user_id` 可选参数以保持一致性
- 修改 `invalidate_enrollment_cache_on_create` 信号处理器，在调用 CacheInvalidator 时传递 user_id
- 确保所有用户隔离的 ViewSet 在创建/更新/删除操作时能正确失效缓存

## Capabilities

### New Capabilities

无新增功能特性。这是对现有缓存失效机制的修复和增强。

### Modified Capabilities

- `cache-invalidation`: 修复用户隔离缓存失效逻辑，确保 CacheInvalidator 能正确处理带 user_id 的缓存键

## Impact

**受影响的代码：**
- `backend/common/utils/cache.py` - CacheInvalidator 类的 invalidate_viewset_list() 和 invalidate_viewset() 方法
- `backend/courses/signals.py` - invalidate_enrollment_cache_on_create 信号处理器
- 其他使用 CacheInvalidator 失效用户隔离缓存的信号和业务逻辑

**不兼容性变更：**
无破坏性变更。user_id 参数为可选，向后兼容现有代码。

**测试影响：**
需要添加测试用例验证用户隔离缓存的失效行为。
