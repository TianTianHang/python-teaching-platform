## 1. 修改 ProblemViewSet - 添加 select_related 和 prefetches

- [x] 1.1 添加 `select_related('chapter')` 到 `get_queryset()` 方法
- [x] 1.2 添加 `DiscussionThread` 和 `TestCase` import
- [x] 1.3 为 `discussion_threads` 添加带 `to_attr` 的 `Prefetch`
- [x] 1.4 为 `test_cases` 添加带 `to_attr` 的嵌套 `Prefetch`（算法题）
- [x] 1.5 为 `prerequisite_problems` 添加 `to_attr`

## 2. 更新序列化器 - 使用预取数据

- [x] 2.1 修改 `ProblemSerializer.get_recent_threads()` 使用 `recent_threads_list`
- [x] 2.2 修改 `AlgorithmProblemSerializer.get_sample_cases()` 使用 `sample_test_cases`
- [x] 2.3 修改 `ProblemSerializer.get_unlock_condition_description()` 使用 `prerequisite_problems_all`

## 3. 测试验证

- [x] 3.1 运行 `cd backend && uv run python manage.py test courses.tests.test_problems --verbosity=2`
- [x] 3.2 功能测试通过：所有 306 个测试用例通过
- [x] 3.3 添加查询数优化测试用例到 test_views.py
- [x] 3.4 测试不同场景：
  - 无类型过滤的问题列表
  - 只有算法题的问题列表
  - 包含各种类型的问题列表
  - 验证 `recent_threads` 数据正确
  - 验证 `chapter_title` 数据正确
  - 验证 `sample_cases` 数据正确

## 4. 性能验证

- [ ] 4.1 对比优化前后的查询数量
- [ ] 4.2 验证目标：查询数 < 15（当前 37）
- [ ] 4.3 确认功能一致性：
  - 所有序列化数据完整
  - 讨论帖子数据正确
  - 测试用例数据正确
  - 解锁条件描述正确

## 5. 提交和部署

- [ ] 5.1 提交代码
- [ ] 5.2 创建 PR
- [ ] 5.3 监控生产环境性能