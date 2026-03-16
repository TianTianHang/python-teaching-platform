## 1. Backend Exception Handling Fixes

- [x] 1.1 修复 `backend/courses/views.py` 中 `SubmissionViewSet.queue_stats` 方法的异常处理
  - 导入 `django.core.exceptions.ObjectDoesNotExist`
  - 将 `except AttributeError` 改为 `except ObjectDoesNotExist`
  - 确保返回 404 状态码而非 500

- [x] 1.2 修复 `backend/courses/tasks.py` 中 `judge_submission_async` 任务的 queue_stats 访问异常处理
  - 在访问 `submission.queue_stats` 前添加 try-except 块
  - 捕获 `Submission.queue_stats.RelatedObjectDoesNotExist` 异常
  - 记录错误日志并抛出清晰的 ValueError

- [x] 1.3 修复 `backend/courses/tasks.py` 中任务重试失败时的 IntegrityError 风险
  - 将 `JudgingQueueStats.objects.create()` 改为 `get_or_create()`
  - 处理 `created` 返回值，更新已存在的记录
  - 确保不会违反 OneToOne 约束

## 2. Backend Testing

- [x] 2.1 添加 `backend/courses/tests/test_views.py` 中 `queue_stats` 端点的测试用例
  - 测试正常情况：queue_stats 存在时返回 200
  - 测试异常情况：queue_stats 不存在时返回 404
  - 测试未授权访问返回 401
  - 测试访问其他用户提交返回 403

- [x] 2.2 添加 `backend/courses/tests/test_tasks.py` 中异常处理路径的测试用例
  - 测试 queue_stats 不存在时的异常处理
  - 测试任务重试失败时的 get_or_create 逻辑
  - 测试 IntegrityError 不会发生
  - 验证错误日志记录

- [x] 2.3 运行所有后端测试验证修复效果
  - 进入 backend 目录：`cd /home/tiantian/project/python-teaching-platform/backend`
  - 运行测试：`uv run python manage.py test courses.tests.test_views.SubmissionViewSetTestCase`
  - 运行测试：`uv run python manage.py test courses.tests.test_tasks.JudgeSubmissionAsyncTaskTestCase`

## 3. Code Quality and Documentation

- [x] 3.1 添加代码注释说明异常处理逻辑
  - 在 `views.py` 中注释说明为什么捕获 ObjectDoesNotExist
  - 在 `tasks.py` 中注释说明 get_or_create 的必要性
  - 添加中文注释说明业务逻辑

- [x] 3.2 验证日志记录完整性
  - 确认所有异常处理路径都有日志记录
  - 确认日志包含关键信息（submission_id, error_type）
  - 确认日志级别正确（error 级别用于异常）

## 4. Integration Testing

- [ ] 4.1 手动测试异常场景
  - 创建 Submission 但不创建 JudgingQueueStats
  - 访问 queue_stats 端点验证返回 404
  - 检查日志确认异常被正确记录

- [ ] 4.2 测试任务重试失败场景
  - 模拟任务失败并达到最大重试次数
  - 验证 JudgingQueueStats 状态正确更新
  - 验证没有 IntegrityError

- [ ] 4.3 验证整体流程正常工作
  - 提交代码并等待评测完成
  - 查询队列状态
  - 验证所有状态转换正常