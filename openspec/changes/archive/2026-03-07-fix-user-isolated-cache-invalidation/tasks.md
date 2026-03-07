## 1. 修改 CacheInvalidator 核心 API

- [x] 1.1 在 `CacheInvalidator.invalidate_viewset()` 方法中添加 `user_id` 可选参数
- [x] 1.2 在 `CacheInvalidator.invalidate_viewset()` 方法调用 `get_standard_cache_key()` 时传递 `user_id` 参数
- [x] 1.3 在 `CacheInvalidator.invalidate_viewset_list()` 方法中添加 `user_id` 可选参数
- [x] 1.4 在 `CacheInvalidator.invalidate_viewset_list()` 方法调用 `get_standard_cache_key()` 时传递 `user_id` 参数
- [x] 1.5 更新两个方法的 docstring，说明 `user_id` 参数的用途和使用场景

## 2. 修复 Enrollment 缓存失效信号

- [x] 2.1 修改 `invalidate_enrollment_cache_on_create` 信号处理器，传递 `instance.user.id` 给 `CacheInvalidator.invalidate_viewset_list()`
- [ ] 2.2 验证修改后的信号处理器在创建 Enrollment 时能正确失效该用户的缓存

## 3. 添加测试用例

- [x] 3.1 添加单元测试：测试 `CacheInvalidator.invalidate_viewset_list()` 带 `user_id` 参数时生成的 pattern 正确
- [x] 3.2 添加单元测试：测试 `CacheInvalidator.invalidate_viewset()` 带 `user_id` 参数时生成的 cache key 正确
- [x] 3.3 添加集成测试：模拟用户调用 enroll 接口后，EnrollmentViewSet 列表缓存被正确失效
- [x] 3.4 添加集成测试：验证不带 `user_id` 参数时仍能正常工作（向后兼容性）
- [x] 3.5 添加测试：验证带 `user_id` 的失效不影响其他用户的缓存

## 4. 代码审查和验证

- [x] 4.1 搜索代码库中所有使用 `CacheInvalidator` 的地方，确认是否需要传递 `user_id`
- [x] 4.2 检查其他用户隔离的 ViewSet（如 ChapterProgress、ProblemProgress）是否需要类似修复
- [x] 4.3 运行测试套件确保所有测试通过：`cd backend && uv run python manage.py test`
- [x] 4.4 运行 lint 检查确保代码质量

## 5. 文档更新

- [x] 5.1 更新 `backend/common/utils/cache.py` 中 `CacheInvalidator` 类的文档字符串
- [x] 5.2 在代码注释中说明何时需要传递 `user_id` 参数
- [x] 5.3 如果存在开发者文档，更新缓存失效的最佳实践
