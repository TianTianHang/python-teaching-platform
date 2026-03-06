## 1. 迁移 ChapterUnlockService 缓存失效逻辑

- [x] 1.1 修改 `_invalidate_cache()` 方法使用 `CacheInvalidator.invalidate_separated_cache_user_status()`
- [x] 1.2 导入 `CacheInvalidator` 到 `services.py`
- [x] 1.3 生成正确的 `parent_pks` 和 `user_id` 参数

## 2. 清理遗留缓存方法

- [x] 2.1 删除 `_get_cache_key()` 方法
- [x] 2.2 删除 `_set_cache()` 方法
- [x] 2.3 删除 `_get_cache()` 方法
- [x] 2.4 删除 `UNLOCK_CACHE_PREFIX` 常量
- [x] 2.5 删除 `PREREQUISITE_PROGRESS_CACHE_PREFIX` 常量

## 3. 清理遗留缓存调用

- [x] 3.1 检查并删除 `unlock_bulk_get_or_create()` 中的旧缓存调用（第 753-755 行）
- [x] 3.2 确保所有缓存操作使用 `BusinessCacheService.cache_result()`
- [x] 3.3 删除 `models.py` 中 `CourseUnlockSnapshot.refresh_unlock_states()` 的旧缓存回填代码

## 4. 更新 signals 缓存失效

- [x] 4.1 检查 `courses/signals.py` 中的缓存失效调用
- [x] 4.2 将直接使用 `cache.delete()` 的调用迁移到 `CacheInvalidator`

## 5. 测试

- [x] 5.1 运行 `cd backend && python manage.py test courses.tests.test_services -v 2` ✅ 45/45 通过
- [x] 5.2 运行 `cd backend && python manage.py test courses.tests.test_signals -v 2` ✅ 23/23 通过
- [x] 5.3 运行 `cd backend && python manage.py test courses.tests.test_cache -v 2` ✅ 12/12 通过
- [x] 5.4 更新 signals.py 使用新的标准缓存 key 格式
- [x] 5.5 更新 `test_cache.py` 和 `test_signals.py` 中的测试以适配新的缓存实现

## 6. 验证

- [x] 6.1 代码审查：验证所有旧缓存方法已删除，使用 CacheInvalidator
- [x] 6.2 代码审查：确认无旧格式 key 的遗留引用
- [ ] 6.3 手动测试：修改章节进度，验证缓存正确失效（需要运行应用）