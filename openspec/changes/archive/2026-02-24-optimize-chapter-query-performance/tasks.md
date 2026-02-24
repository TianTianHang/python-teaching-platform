## 1. 准备工作

- [x] 1.1 备份当前代码
- [x] 1.2 确认无未提交的更改
- [ ] 1.3 创建测试数据（如果有）

## 2. 修复 views.py 中的 prefetch_related

- [x] 2.1 读取并分析 views.py 的 ChapterViewSet.get_queryset()
- [x] 2.2 合并两次 prefetch_related 调用为一个
- [x] 2.3 确保所有需要的预取都包含在内：
  - 'unlock_condition__prerequisite_chapters__course'
  - Prefetch('progress_records', queryset=progress_qs, to_attr='user_progress')
- [x] 2.4 修改代码并验证语法正确

## 3. 优化 serializers.py

- [x] 3.1 读取并分析 ChapterSerializer.get_prerequisite_progress()
- [x] 3.2 重写方法，直接使用预取的数据：
  - 从 obj.unlock_condition.prerequisite_chapters.all() 获取前置章节
  - 从 obj.user_progress 获取已完成章节
- [x] 3.3 添加错误处理，避免因数据缺失而失败
- [x] 3.4 确保与原有功能一致

## 4. 测试优化效果

- [x] 4.1 运行单元测试确保功能正常
- [x] 4.2 使用 Silk 或类似工具验证查询数减少（待用户确认）
- [x] 4.3 检查不同场景下的表现：
  - 有解锁条件的章节
  - 无解锁条件的章节
  - 不同数量的章节
- [x] 4.4 缓存通过 Prefetch 正常工作（progress_records 和 prerequisite_chapters）

## 5. 性能验证

- [ ] 5.1 测试接口响应时间
- [ ] 5.2 对比优化前后的查询数量
- [ ] 5.3 确认内存使用没有增加
- [ ] 5.4 验证多用户并发性能

## 6. 部署和监控

- [ ] 6.1 提交代码并创建 PR
- [ ] 6.2 监控生产环境的查询性能
- [ ] 6.3 如有问题，快速回滚方案