# 扩展动态字段排除功能到其他 API

## Why

当前 `ProblemViewSet` 已成功实现动态字段排除功能（基于 `openspec/specs/api-dynamic-field-exclusion`），在列表页通过 `?exclude=content,recent_threads` 参数减少了 70-80% 的数据传输，显著提升了页面加载性能。

但其他高优先级 API（Submission、Chapter、DiscussionThread）仍存在严重的数据冗余问题：
- **SubmissionViewSet**: 提交历史列表包含完整代码、输出、错误信息，冗余超过 90%
- **ChapterViewSet**: 章节列表包含完整 `content` 字段（富文本+图片），数据量巨大
- **DiscussionThreadViewSet**: 讨论列表包含完整 `content` 和嵌套 `replies`，列表页不需要

这些冗余导致：
- 移动端和低带宽环境下加载缓慢
- 不必要的网络传输和服务器负载
- 用户体验差，尤其是提交历史和讨论列表页面

## What Changes

将已有的 `DynamicFieldsMixin` 和 `DynamicFieldsSerializerMixin` 扩展应用到以下 ViewSet：

**后端修改**：
- 为 `SubmissionViewSet` 添加 `DynamicFieldsMixin`，为 `SubmissionSerializer` 添加 `DynamicFieldsSerializerMixin`
- 为 `ChapterViewSet` 添加 `DynamicFieldsMixin`，为 `ChapterSerializer` 添加 `DynamicFieldsSerializerMixin`
- 为 `DiscussionThreadViewSet` 添加 `DynamicFieldsMixin`，为 `DiscussionThreadSerializer` 添加 `DynamicFieldsSerializerMixin`
- 为新增功能的 ViewSet 添加集成测试（约 30-40 个测试用例）

**前端集成**：
- 修改 `submission.tsx`：添加 `?exclude=code,output,error` 参数
- 修改 `problems.$problemId.submissions.tsx`：添加 `?exclude=code,output,error` 参数
- 修改 `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`：添加 `?exclude=content,recent_threads,status` 参数
- 修改 `threads.tsx`：添加 `?exclude=content,replies` 参数（可选）

**不修改 spec**：此变更是实现已有的 `api-dynamic-field-exclusion` spec，不涉及新的能力或需求变更。

## Capabilities

### Modified Capabilities
- `api-dynamic-field-exclusion`: 扩展应用到 Submission、Chapter、DiscussionThread 三个 ViewSet

**注意**：不需要创建新的 spec 文件，因为 `openspec/specs/api-dynamic-field-exclusion/spec.md` 已经定义了完整的需求。此变更只是将该 spec 应用到更多的 API 端点。

## Impact

**影响的代码**：
- `backend/courses/views.py`：修改 3 个 ViewSet 的继承链，添加 `DynamicFieldsMixin`
- `backend/courses/serializers.py`：修改 3 个 Serializer 的继承链，添加 `DynamicFieldsSerializerMixin`
- `backend/courses/tests/test_views.py`：添加约 30-40 个集成测试用例
- `frontend/web-student/app/routes/submission.tsx`：添加 `exclude` 参数到 API 请求
- `frontend/web-student/app/routes/problems.$problemId.submissions.tsx`：添加 `exclude` 参数到 API 请求
- `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`：添加 `exclude` 参数到 API 请求
- `frontend/web-student/app/routes/threads.tsx`：添加 `exclude` 参数到 API 请求（可选）

**API 变更**：
- 所有修改的 ViewSet 支持可选的 `exclude` 查询参数
- 例如：`GET /api/submissions/?exclude=code,output,error`
- 向后兼容：不提供 `exclude` 参数时行为不变

**性能影响**：
- ✅ SubmissionViewSet 响应大小减少 ~90%
- ✅ ChapterViewSet 响应大小减少 ~60-70%
- ✅ DiscussionThreadViewSet 响应大小减少 ~50-60%
- ✅ 数据传输时间显著降低
- ⚠️ 缓存变体增加（不同的 exclude 组合生成不同的缓存键）
- ✅ 通过规范化 exclude 字段顺序，最大化缓存命中率

**依赖变更**：无新增依赖

**向后兼容性**：完全向后兼容，所有修改都是增量式的可选功能
