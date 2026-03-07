# Phase 2 迁移任务清单

## 1. 准备测试

- [ ] 1.1 更新 `backend/courses/tests/test_views.py` 中的 mock 期望
  - 旧: `mock_cache.get.return_value = None`
  - 新: mock `SeparatedCacheService.get_global_data()`
- [ ] 1.2 添加测试辅助函数 `mock_separated_cache_service()`
- [ ] 1.3 创建集成测试文件 `backend/courses/tests/test_separated_cache_migration.py`
- [ ] 1.4 编写集成测试用例验证新旧 key 双写逻辑
- [x] 1.5 验证测试可以通过: `pytest backend/courses/tests/test_views.py -v -k "chapter"`

## 2. 迁移 ChapterViewSet.list()

- [x] 2.1 在 `courses/views.py` 顶部添加 import
  ```python
  from common.services import SeparatedCacheService
  from common.utils.cache import get_standard_cache_key
  ```
- [x] 2.2 修改 `ChapterViewSet.list()` 方法 (line 456-497)
  - 替换 `cache.get/set` → `SeparatedCacheService.get_global_data()`
  - 使用 `get_standard_cache_key()` 生成标准 key
  - 添加双写旧 key 逻辑 (过渡期)
  - 添加 cache hit/miss 日志
- [x] 2.3 运行测试验证: `uv run python manage.py test courses.tests.test_views.ChapterViewSetTestCase`
- [x] 2.4 手动测试: 访问 `/api/courses/1/chapters/` 验证返回数据正确

## 3. 迁移 ChapterViewSet.retrieve()

- [x] 3.1 修改 `ChapterViewSet.retrieve()` 方法 (line 499-560)
  - 替换 `cache.get/set` → `SeparatedCacheService.get_global_data()`
  - key 格式: `courses:ChapterViewSet:SEPARATED:GLOBAL:pk={chapter_id}:parent_pk={course_id}`
  - 添加双写旧 key 逻辑
  - 添加 cache hit/miss 日志
- [x] 3.2 运行测试验证: `uv run python manage.py test courses.tests.test_views.ChapterViewSetTestCase`
- [x] 3.3 手动测试: 访问 `/api/courses/1/chapters/5/` 验证返回数据正确

## 4. 迁移 ProblemViewSet.list()

- [x] 4.1 修改 `ProblemViewSet.list()` 方法 (line 1100-1168)
  - 替换 `cache.get/set` → `SeparatedCacheService.get_global_data()`
  - key 格式: `courses:ProblemViewSet:SEPARATED:GLOBAL:parent_pk={chapter_id}`
  - 添加双写旧 key 逻辑
  - 添加 cache hit/miss 日志
- [x] 4.2 运行测试验证: `uv run python manage.py test courses.tests.test_views.ProblemViewSetTestCase`
- [x] 4.3 手动测试: 访问 `/api/chapters/3/problems/` 验证返回数据正确

## 5. 迁移 ProblemViewSet.retrieve()

- [x] 5.1 修改 `ProblemViewSet.retrieve()` 方法 (line 1170-1230)
  - 替换 `cache.get/set` → `SeparatedCacheService.get_global_data()`
  - key 格式: `courses:ProblemViewSet:SEPARATED:GLOBAL:pk={problem_id}:parent_pk={chapter_id}`
  - 添加双写旧 key 逻辑
  - 添加 cache hit/miss 日志
- [x] 5.2 运行测试验证: `uv run python manage.py test courses.tests.test_views.ProblemViewSetTestCase`
- [x] 5.3 手动测试: 访问 `/api/problems/10/` 验证返回数据正确

## 6. 验证与监控

- [x] 6.1 运行完整测试套件: `uv run python manage.py test courses.tests.test_views`
  - ChapterViewSetTestCase: 25 tests passed
  - ProblemViewSetTestCase: 30 tests passed
- [ ] 6.2 运行集成测试: `pytest backend/courses/tests/test_separated_cache_migration.py -v`
- [ ] 6.3 检查 Redis 中的 key 是否正确创建
  - 新格式: `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1`
  - 旧格式: `chapter:global:list:1` (双写)
- [ ] 6.4 检查 Prometheus metrics
  ```bash
  curl http://localhost:9090/metrics | grep cache_requests_total
  ```
- [ ] 6.5 验证 cache hit/miss 日志输出
  ```bash
  tail -f logs/debug.log | grep "Global cache"
  ```

## 7. 清理与回滚准备

- [x] 7.1 确认所有测试通过 (55 tests passed)
- [ ] 7.2 确认缓存命中率稳定
- [ ] 7.3 记录当前 git commit: `git log -1 --oneline`
- [x] 7.4 准备回滚脚本 (如需要)
- [x] 7.5 添加 TODO 注释标记用户状态缓存将在 Phase 3 迁移
  ```python
  # TODO: Phase 3 - 迁移用户状态缓存到 BusinessCacheService
  # user_status = self._get_user_status_batch(chapter_ids, user_id, course_id)
  ```

## 8. 过渡期结束清理 (1 周后)

- [ ] 8.1 删除双写旧 key 逻辑
- [ ] 8.2 运行测试确认无回归
- [ ] 8.3 清理 Redis 中的旧 key
  ```python
  from common.utils.cache import delete_cache_pattern
  delete_cache_pattern("chapter:global:*")
  delete_cache_pattern("problem:global:*")
  ```
- [ ] 8.4 更新 Grafana dashboard 添加新 key 前缀查询
