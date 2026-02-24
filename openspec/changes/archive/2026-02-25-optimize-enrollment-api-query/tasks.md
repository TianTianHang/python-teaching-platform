## 1. 修改 EnrollmentViewSet - 添加 select_related 和 prefetches

- [x] 1.1 添加 `select_related('user', 'course')` 到 `get_queryset()` 方法
- [x] 1.2 添加 `Prefetch` import（如果不存在）
- [x] 1.3 添加 `prefetch_related('chapter_progress')`
- [x] 1.4 添加 `Prefetch('course__chapters', queryset=Chapter.objects.all(), to_attr='all_chapters')`

## 2. 更新序列化器 - 使用预取数据

- [x] 2.1 修改 `EnrollmentSerializer.get_progress_percentage()` 使用 `all_chapters`
- [x] 2.2 修改 `EnrollmentSerializer.get_progress_percentage()` 使用预取的 `chapter_progress`

## 3. 测试验证

- [x] 3.1 运行 `cd backend && uv run python manage.py test courses.tests.test_enrollments --verbosity=2`
- [x] 3.2 使用 Silk 验证查询数降低到 < 7
- [x] 3.3 测试不同场景：
  - 验证 `progress_percentage` 数据正确
  - 验证 `user_username` 数据正确
  - 验证 `course_title` 数据正确

## 4. 性能验证

- [x] 4.1 对比优化前后的查询数量
- [x] 4.2 验证目标：查询数 < 7（当前 14）
- [x] 4.3 确认功能一致性：
  - 所有序列化数据完整
  - 进度百分比计算正确
  - 用户和课程信息正确

## 5. 提交和部署

- [ ] 5.1 提交代码
- [ ] 5.2 创建 PR
- [ ] 5.3 监控生产环境性能
