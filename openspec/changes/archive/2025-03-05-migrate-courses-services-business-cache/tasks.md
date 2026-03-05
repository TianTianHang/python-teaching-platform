## 1. 准备测试

- [x] 1.1 更新 `test_services.py` 中的测试用例，mock `BusinessCacheService.cache_result`
- [x] 1.2 添加集成测试：验证新旧 key 格式都能正常工作（过渡期）

## 2. 迁移 ChapterUnlockService

- [x] 2.1 重构 `_get_cache_key()` → 使用 `get_standard_cache_key()`
- [x] 2.2 重构 `_set_cache()` / `_get_cache()` → 使用 `BusinessCacheService.cache_result()`
- [x] 2.3 提取纯业务逻辑到 `_compute_unlock_status()`
- [x] 2.4 添加 cache hit/miss 日志

## 3. 迁移 get_user_chapter_status()

- [x] 3.1 替换 cache.get/set → BusinessCacheService.cache_result
- [x] 3.2 使用 `get_standard_cache_key()` 生成标准 key
- [x] 3.3 添加 cache hit/miss 日志

## 4. 迁移 get_user_problem_status()

- [x] 4.1 替换 cache.get/set → BusinessCacheService.cache_result
- [x] 4.2 使用 `get_standard_cache_key()` 生成标准 key
- [x] 4.3 添加 cache hit/miss 日志

## 5. 验证

- [x] 5.1 运行单元测试：`pytest backend/courses/tests/test_services.py -v`
- [x] 5.2 运行集成测试：`pytest backend/courses/tests/test_cache_integration.py -v`
- [ ] 5.3 手动测试：访问章节列表，验证解锁状态正确
- [ ] 5.4 手动测试：访问问题列表，验证用户状态正确
- [ ] 5.5 检查 Prometheus metrics：`curl http://localhost:9090/metrics | grep cache_requests_total`

## 6. 监控

- [ ] 6.1 观察缓存命中率：`rate(cache_requests_total{operation="get"}[5m])`
- [ ] 6.2 观察业务响应时间：`rate(http_request_duration_seconds{path=~"/api/courses/.*"}[5m])`
- [ ] 6.3 检查日志中的 cache hit/miss 消息

## 7. 回滚（如需要）

- [ ] 7.1 如果缓存命中率下降 > 10%，执行 `git revert <commit>` 回滚
- [ ] 7.2 如果解锁状态计算错误（用户投诉），执行 `git revert <commit>` 回滚