## 1. 修改 ChapterViewSet - 添加 to_attr 预取

- [x] 1.1 修改 get_queryset 方法，为 unlock_condition__prerequisite_chapters 添加 to_attr
- [x] 1.2 添加 select_related('course') 到 prerequisite_chapters 预取
- [x] 1.3 移除 _is_instructor_or_admin() 方法及相关调用
- [x] 1.4 确保预取查询正确执行

## 2. 更新序列化器 - 使用预取数据

- [x] 2.1 修改 ChapterUnlockConditionSerializer.get_prerequisite_chapters
- [x] 2.2 使用 obj.prerequisite_chapters_all 替代 obj.prerequisite_chapters.all()
- [x] 2.3 更新 get_prerequisite_titles 方法使用预取数据
- [x] 2.4 确保所有相关序列化器使用 to_attr 数据

## 3. 优化 CourseViewSet（如需要）

- [x] 3.1 检查章节列表是否会调用 recent_threads
- [x] 3.2 如需要，添加 discussion_threads 的 to_attr 预取
- [x] 3.3 确保预取不会影响其他功能

## 4. 测试验证

- [x] 4.1 运行单元测试确保功能正常
- [ ] 4.2 使用 Silk 验证查询数降低到 < 15
- [ ] 4.3 测试不同场景：
  - 有解锁条件的章节
  - 无解锁条件的章节
  - 不同数量的章节
  - 课程和章节序列化

## 5. 性能验证

- [ ] 5.1 对比优化前后的查询数量
- [ ] 5.2 验证目标：查询数 < 15（当前 34）
- [ ] 5.3 确认功能一致性：
  - is_locked 值正确
  - prerequisite_progress 正确
  - status 字段正确
  - 所有序列化数据完整

## 6. 提交和部署

- [ ] 6.1 提交代码
- [ ] 6.2 创建 PR
- [ ] 6.3 监控生产环境性能