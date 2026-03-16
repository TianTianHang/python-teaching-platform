## Why

异步代码评测系统存在三个严重的异常处理缺陷，导致系统在边缘情况下返回错误的 HTTP 状态码（500 而非 404）、在重试失败时可能崩溃（IntegrityError）、以及存在误导性的错误处理代码。这些问题影响用户体验和系统稳定性，需要立即修复。

## What Changes

- 修复 `views.py` 中 `queue_stats` 端点的异常捕获：使用正确的 `ObjectDoesNotExist` 或 `RelatedObjectDoesNotExist` 替代 `AttributeError`
- 修复 `tasks.py` 中任务重试失败时的重复创建问题：使用 `get_or_create` 避免 IntegrityError
- 改进 `tasks.py` 中的队列统计检查逻辑：正确处理 `RelatedObjectDoesNotExist` 异常
- 添加缺失的测试用例，确保异常处理路径得到验证

## Capabilities

### New Capabilities

无新增 capability。

### Modified Capabilities

- **async-code-judging**: 修改任务执行异常处理要求
  - 任务执行前访问 queue_stats 时必须正确处理 RelatedObjectDoesNotExist 异常
  - 任务重试失败时必须使用 get_or_create 防止 IntegrityError
  - 确保异常处理路径清晰且可测试

- **queue-monitoring**: 修改队列状态查询端点的错误处理要求
  - queue_stats 端点必须正确捕获 RelatedObjectDoesNotExist 异常
  - 返回 404 状态码而非 500 状态码

## Impact

### 后端代码变更
- `backend/courses/views.py`: SubmissionViewSet.queue_stats 方法的异常处理
- `backend/courses/tasks.py`: judge_submission_async 任务的异常处理和重试逻辑

### API 变更
- 无 API 接口变更，仅修复错误响应状态码（从 500 改为 404）

### 测试变更
- `backend/courses/tests/test_views.py`: 新增 queue_stats 端点的测试用例
- `backend/courses/tests/test_tasks.py`: 新增异常处理路径的测试用例

### 依赖和系统影响
- 无数据库迁移
- 无第三方依赖变更
- 不影响现有的异步代码评测流程