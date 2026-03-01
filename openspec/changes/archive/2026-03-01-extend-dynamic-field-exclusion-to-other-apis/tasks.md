# 实施任务清单

> **注意**：本阶段专注于扩展动态字段排除功能到 Submission、Chapter、DiscussionThread 三个 ViewSet，并在前端集成 exclude 参数。

## 1. 后端迁移 - SubmissionViewSet

- [x] 1.1 为 `SubmissionViewSet` 添加 `DynamicFieldsMixin`
  - 在 `backend/courses/views.py` 中导入 `DynamicFieldsMixin`
  - 修改 `SubmissionViewSet` 继承链：`class SubmissionViewSet(DynamicFieldsMixin, viewsets.ModelViewSet)`
  - 确保 Mixin 放在继承链最前面

- [x] 1.2 为 `SubmissionSerializer` 添加 `DynamicFieldsSerializerMixin`
  - 在 `backend/courses/serializers.py` 中导入 `DynamicFieldsSerializerMixin`
  - 修改 `SubmissionSerializer` 继承链：`class SubmissionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer)`
  - 确保在 `ModelSerializer` 前面

- [x] 1.3 添加 `SubmissionViewSet` 集成测试
  - 在 `backend/courses/tests/test_views.py` 中创建 `SubmissionViewSetExcludeTestCase` 类
  - 添加测试：`test_exclude_single_field`（排除 code 字段）
  - 添加测试：`test_exclude_multiple_fields`（排除 code,output,error）
  - 添加测试：`test_exclude_invalid_field`（验证无效字段返回 400）
  - 添加测试：`test_exclude_empty_parameter`（空参数返回所有字段）
  - 添加测试：`test_exclude_with_pagination`（分页支持）
  - 添加测试：`test_exclude_with_filtering`（过滤支持）

- [x] 1.4 运行 SubmissionViewSet 测试
  - 运行：`cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_views.SubmissionViewSetExcludeTestCase`
  - 确保所有测试通过

## 2. 后端迁移 - ChapterViewSet

- [x] 2.1 为 `ChapterViewSet` 添加 `DynamicFieldsMixin`
  - 在 `backend/courses/views.py` 中导入 `DynamicFieldsMixin`（已完成）
  - 修改 `ChapterViewSet` 继承链：将 `DynamicFieldsMixin` 添加到最前面
  - 确保 `get_serializer_context()` 调用链正确

- [x] 2.2 为 `ChapterSerializer` 添加 `DynamicFieldsSerializerMixin`
  - 在 `backend/courses/serializers.py` 中导入 `DynamicFieldsSerializerMixin`（已完成）
  - 修改 `ChapterSerializer` 继承链：将 `DynamicFieldsSerializerMixin` 添加到 `ModelViewSet` 前面

- [x] 2.3 优化 `ChapterSerializer` 的 `SerializerMethodField`
  - 为 `get_status()` 方法添加提前返回优化（检查 `exclude_fields`）
  - 为 `get_prerequisite_progress()` 方法添加提前返回优化
  - 为 `get_is_locked()` 方法添加提前返回优化
  - 仅在字段被排除时返回 `None`，避免不必要的计算

- [x] 2.4 添加 `ChapterViewSet` 集成测试
  - 在 `backend/courses/tests/test_views.py` 中创建 `ChapterViewSetExcludeTestCase` 类
  - 添加测试：`test_exclude_single_field`（排除 content 字段）
  - 添加测试：`test_exclude_multiple_fields`（排除 content,status）
  - 添加测试：`test_exclude_invalid_field`（验证无效字段返回 400）
  - 添加测试：`test_exclude_with_filters`（与过滤参数配合）
  - 添加测试：`test_exclude_with_ordering`（与排序参数配合）

- [x] 2.5 运行 ChapterViewSet 测试
  - 运行：`cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_views.ChapterViewSetExcludeTestCase`
  - 确保所有测试通过

## 3. 后端迁移 - DiscussionThreadViewSet

- [x] 3.1 为 `DiscussionThreadViewSet` 添加 `DynamicFieldsMixin`
  - 在 `backend/courses/views.py` 中修改 `DiscussionThreadViewSet` 继承链
  - 添加 `DynamicFieldsMixin` 到继承链最前面

- [x] 3.2 为 `DiscussionThreadSerializer` 添加 `DynamicFieldsSerializerMixin`
  - 在 `backend/courses/serializers.py` 中修改 `DiscussionThreadSerializer` 继承链
  - 添加 `DynamicFieldsSerializerMixin` 到 `ModelViewSet` 前面

- [x] 3.3 优化 `DiscussionThreadSerializer` 的 `get_replies()` 方法
  - 添加提前返回优化：检查 `replies` 是否在 `exclude_fields` 中
  - 如果被排除，直接返回 `None`，避免查询嵌套回复

- [x] 3.4 添加 `DiscussionThreadViewSet` 集成测试
  - 在 `backend/courses/tests/test_views.py` 中创建 `DiscussionThreadViewSetExcludeTestCase` 类
  - 添加测试：`test_exclude_single_field`（排除 content 字段）
  - 添加测试：`test_exclude_multiple_fields`（排除 content,replies）
  - 添加测试：`test_exclude_invalid_field`（验证无效字段返回 400）
  - 添加测试：`test_exclude_with_search`（与搜索参数配合）

- [x] 3.5 运行 DiscussionThreadViewSet 测试
  - 运行：`cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_views.DiscussionThreadViewSetExcludeTestCase`
  - 确保所有测试通过

## 4. 后端集成测试

- [x] 4.1 运行所有 courses 应用测试
  - 运行：`cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_views`
  - 确保所有现有测试仍然通过
  - 确保新增测试全部通过

- [ ] 4.2 手动测试 API 端点
  - 测试：`GET /api/v1/submissions/?exclude=code,output,error`
  - 测试：`GET /api/v1/courses/1/chapters/?exclude=content`
  - 测试：`GET /api/v1/threads/?exclude=content,replies`
  - 验证响应中不包含排除的字段
  - 验证无效字段返回 400 错误

## 5. 前端集成 - Submission API

- [x] 5.1 修改 `submission.tsx`
  - 在 loader 中添加 `exclude` 参数：`code,output,error`
  - 修改 API 请求 URL：`/problems/${problemId}/submissions/?exclude=code,output,error`
  - 保持其他逻辑不变

- [x] 5.2 修改 `problems.$problemId.submissions.tsx`
  - 在 loader 中添加 `exclude` 参数：`code,output,error`
  - 修改 API 请求 URL：`/submissions/?exclude=code,output,error`
  - 保持其他逻辑不变

- [ ] 5.3 测试提交记录页面
  - 启动前端：`cd frontend/web-student && pnpm run dev`
  - 访问提交记录页面
  - 打开浏览器 DevTools Network 面板
  - 验证 API 请求包含 `exclude` 参数
  - 验证响应大小显著减少
  - 验证页面功能正常

## 6. 前端集成 - Chapter API

- [x] 6.1 修改 `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
  - 在 loader 中添加 `exclude` 参数：`content,recent_threads,status`
  - 修改 API 请求 URL：`/courses/${courseId}/chapters/${chapterId}/problems?exclude=content,recent_threads,status`
  - 保持其他逻辑不变

- [ ] 6.2 测试章节题目列表页
  - 访问章节题目列表页
  - 打开浏览器 DevTools Network 面板
  - 验证 API 请求包含 `exclude` 参数
  - 验证响应大小显著减少
  - 验证页面功能正常

## 7. 前端集成 - DiscussionThread API（可选）

- [x] 7.1 修改 `threads.tsx`
  - 在 loader 中添加 `exclude` 参数：`content,replies`
  - 修改 API 请求 URL：`/threads/?exclude=content,replies`
  - 保持其他逻辑不变

- [ ] 7.2 测试讨论列表页
  - 访问讨论列表页
  - 打开浏览器 DevTools Network 面板
  - 验证 API 请求包含 `exclude` 参数
  - 验证响应大小显著减少
  - 验证页面功能正常

## 8. 前端类型检查

- [x] 8.1 运行前端类型检查
  - 运行：`cd frontend/web-student && pnpm run typecheck`
  - 确保没有类型错误

## 9. 性能验证

- [ ] 9.1 测量优化前后的响应大小
  - 使用浏览器 DevTools 记录优化前的响应大小
  - 实施优化后记录响应大小
  - 验证数据量减少符合预期：
    - SubmissionViewSet: ~90% 减少
    - ChapterViewSet: ~60-70% 减少
    - DiscussionThreadViewSet: ~50-60% 减少

- [ ] 9.2 验证缓存命中率
  - 使用 Django Debug Toolbar 查看缓存命中率
  - 确保不同的 exclude 组合生成不同的缓存键
  - 确保相同字段组合（不同顺序）生成相同的缓存键

## 10. 文档更新

- [x] 10.1 更新 `SubmissionViewSet` 文档
  - 在 docstring 中添加 `exclude` 参数说明
  - 添加可排除字段列表
  - 添加使用示例

- [x] 10.2 更新 `ChapterViewSet` 文档
  - 在 docstring 中添加 `exclude` 参数说明
  - 添加可排除字段列表
  - 添加使用示例

- [x] 10.3 更新 `DiscussionThreadViewSet` 文档
  - 在 docstring 中添加 `exclude` 参数说明
  - 添加可排除字段列表
  - 添加使用示例

## 11. 清理和收尾

- [x] 11.1 代码格式化
  - 运行：`cd /home/tiantian/project/python-teaching-platform/backend && uv run ruff check backend/courses/views.py backend/courses/serializers.py backend/courses/tests/test_views.py --fix`
  - 确保代码符合格式规范

- [x] 11.2 最终测试
  - 运行完整的后端测试套件
  - 运行前端类型检查
  - 手动测试所有修改的页面
  - 确保所有功能正常

- [ ] 11.3 提交代码
  - 提交后端修改
  - 提交前端修改
  - 创建 pull request（如需要）
