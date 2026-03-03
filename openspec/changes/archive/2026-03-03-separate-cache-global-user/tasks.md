# Implementation Tasks

## 1. 准备阶段 - 序列化器和辅助函数

- [x] 1.1 创建 `ChapterGlobalSerializer` 序列化器，包含全局字段（id, course, title, content, order等）
- [x] 1.2 创建 `ProblemGlobalSerializer` 序列化器，包含全局字段（id, chapter, type, title, content, difficulty等）
- [x] 1.3 创建 `get_chapter_user_status()` 辅助函数，批量获取章节用户状态
- [x] 1.4 创建 `get_problem_user_status()` 辅助函数，批量获取问题用户状态
- [x] 1.5 编写单元测试验证序列化器和辅助函数的正确性

## 2. 准备阶段 - 快照扩展

- [x] 2.1 扩展 `CourseUnlockSnapshot.unlock_states` 字段，增加 `status` 子字段
- [x] 2.2 扩展 `ProblemUnlockSnapshot.unlock_states` 字段，增加 `status` 子字段
- [x] 2.3 创建数据迁移脚本，为现有快照添加 `status` 字段
- [x] 2.4 更新快照生成逻辑，在创建/更新快照时填充 `status` 字段
- [x] 2.5 编写单元测试验证快照扩展的正确性和向后兼容性

## 3. 准备阶段 - 缓存失效信号

- [x] 3.1 创建 `on_chapter_progress_change()` 信号处理器，失效用户状态缓存
- [x] 3.2 创建 `on_problem_progress_change()` 信号处理器，失效用户状态缓存
- [x] 3.3 创建 `on_chapter_content_change()` 信号处理器，失效全局数据缓存
- [x] 3.4 创建 `on_problem_content_change()` 信号处理器，失效全局数据缓存
- [x] 3.5 编写单元测试验证缓存失效的正确性

## 4. 核心实现 - ChapterViewSet 分离缓存

- [x] 4.1 在 `ChapterViewSet.list()` 中实现全局数据缓存查询逻辑
- [x] 4.2 在 `ChapterViewSet.list()` 中实现用户状态缓存查询逻辑
- [x] 4.3 在 `ChapterViewSet.list()` 中实现缓存合并逻辑
- [x] 4.4 在 `ChapterViewSet.retrieve()` 中实现分离缓存查询和合并逻辑
- [x] 4.5 实现 `_get_user_status_batch()` 方法，批量获取用户状态
- [x] 4.6 实现 `_merge_global_and_user_status()` 方法，合并全局数据和用户状态
- [x] 4.7 编写集成测试验证 ChapterViewSet 的分离缓存功能

## 5. 核心实现 - ProblemViewSet 分离缓存

- [x] 5.1 在 `ProblemViewSet.list()` 中实现全局数据缓存查询逻辑
- [x] 5.2 在 `ProblemViewSet.list()` 中实现用户状态缓存查询逻辑
- [x] 5.3 在 `ProblemViewSet.list()` 中实现缓存合并逻辑
- [x] 5.4 在 `ProblemViewSet.retrieve()` 中实现分离缓存查询和合并逻辑
- [x] 5.5 实现 `_get_user_status_batch()` 方法，批量获取用户状态
- [x] 5.6 实现 `_merge_global_and_user_status()` 方法，合并全局数据和用户状态
- [x] 5.7 编写集成测试验证 ProblemViewSet 的分离缓存功能

## 6. 测试和验证

- [x] 6.1 编写性能测试，对比分离缓存前后的缓存命中率
- [x] 6.2 编写内存占用测试，验证缓存条目数量减少
- [x] 6.3 编写并发测试，验证多用户场景下的数据隔离性
- [x] 6.4 编写降级测试，验证缓存未命中时的回退逻辑
- [x] 6.5 编写一致性测试，验证缓存失效后的数据一致性

## 7. 监控和指标

- [ ] 7.1 添加全局数据缓存的命中率指标记录
- [ ] 7.2 添加用户状态缓存的命中率指标记录
- [ ] 7.3 添加缓存合并延迟指标记录
- [ ] 7.4 添加缓存失效事件日志
- [ ] 7.5 验证指标正确记录到监控系统

## 8. 文档和清理

- [x] 8.1 更新 API 文档，说明分离缓存机制
- [x] 8.2 更新缓存策略文档，说明新的缓存键格式
- [x] 8.3 编写运维文档，说明缓存监控和故障排查
- [x] 8.4 清理旧的缓存键（可选，可等待自动过期）
- [x] 8.5 归档变更文档