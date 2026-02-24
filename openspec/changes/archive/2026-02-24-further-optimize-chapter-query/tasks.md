## 1. 准备工作

- [x] 1.1 确认当前代码状态
- [x] 1.2 备份当前实现（如需要）

## 2. 修改 get_queryset - 缓存 enrollment

- [x] 2.1 在 `get_queryset()` 中添加 `self._enrollment = enrollment` 缓存
- [x] 2.2 确认 enrollment 查询成功后设置缓存

## 3. 修改 _annotate_is_locked - 复用缓存

- [x] 3.1 读取并分析 `_annotate_is_locked()` 方法中的 `completed_chapter_ids` 查询
- [x] 3.2 移除重复的 `ChapterProgress.objects.filter(...)` 查询
- [x] 3.3 使用 `self._completed_chapter_ids` 缓存替代
- [x] 3.4 添加回退逻辑：如果缓存不存在，使用原查询方式


## 4. 修改 get_serializer_context - 传递 enrollment

- [x] 5.1 在 `get_serializer_context()` 中添加 `enrollment` 到 context
- [x] 5.2 确认使用 `self._enrollment` 缓存
- [x] 5.3 添加检查：只有当 `enrollment` 存在时才传递

## 5. 更新 serializer（可选优化）

- [x] 6.1 检查 serializer 中是否需要使用 context 中的 enrollment
- [x] 6.2 如果回退逻辑使用 enrollment，确保从 context 获取

## 6. 测试验证

- [x] 6.1 运行单元测试确保功能正常
- [ ] 6.2 使用 Silk 或类似工具验证查询数降低
- [ ] 6.3 测试用户功能（所有用户都是学生角色）
- [ ] 6.4 测试不同场景：
  - 有解锁条件的章节
  - 无解锁条件的章节
  - 不同数量的章节

## 7. 性能验证

- [ ] 7.1 对比优化前后的查询数量
- [ ] 7.2 验证目标：查询数 < 25（当前 34）
- [ ] 7.3 确认功能一致性：
  - is_locked 值正确
  - prerequisite_progress 正确
  - status 字段正确

## 8. 提交和部署

- [ ] 9.1 提交代码
- [ ] 9.2 创建 PR
- [ ] 9.3 监控生产环境性能
