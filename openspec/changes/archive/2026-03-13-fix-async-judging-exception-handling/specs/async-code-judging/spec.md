## MODIFIED Requirements

### Requirement: Task Execution
系统 SHALL 通过 Celery 异步执行代码评测任务，并正确处理所有异常情况。

#### Scenario: Task creation
- **WHEN** 创建新的评测任务
- **THEN** 使用 Celery 任务路由到 code_judging 队列
- **AND** 设置正确的超时限制（软270秒，硬300秒）
- **AND** 任务绑定到特定的 Submission

#### Scenario: Task timeout handling
- **WHEN** 任务执行超过软超时时间
- **THEN** 抛出 SoftTimeLimitExceeded 异常
- **AND** 标记 Submission 为 timeout 状态
- **AND** 更新 JudgingQueueStats 为 timeout 状态

#### Scenario: Task failure handling
- **WHEN** 任务执行失败
- **THEN** 标记 Submission 为 internal_error 状态
- **AND** 更新 JudgingQueueStats 为 failed 状态
- **AND** 记录详细的错误信息

#### Scenario: Queue stats access error handling
- **WHEN** 任务尝试访问 submission.queue_stats 但记录不存在
- **THEN** 捕获 RelatedObjectDoesNotExist 异常
- **AND** 记录错误日志（包含 submission_id）
- **AND** 抛出清晰的 ValueError 异常："Submission 没有对应的队列统计信息"

#### Scenario: Task retry failure handling
- **WHEN** 任务达到最大重试次数且仍失败
- **THEN** 使用 get_or_create 获取或创建 JudgingQueueStats
- **AND** 避免违反 OneToOne 约束导致的 IntegrityError
- **AND** 更新 queue_stats 状态为 failed
- **AND** 更新 submission 状态为 internal_error
- **AND** 记录错误信息包含重试次数

### Requirement: Submission Status Update
系统 SHALL 在任务执行过程中更新提交状态，确保所有状态转换都能正确执行。

#### Scenario: Status transition from pending to started
- **WHEN** Worker 开始处理任务
- **THEN** 更新 Submission status 为 judging
- **AND** 更新 JudgingQueueStats status 为 started
- **AND** 记录 started_at 时间戳

#### Scenario: Status transition from started to completed
- **WHEN** 任务执行完成
- **THEN** 更新 Submission 为最终状态（accepted/wrong_answer等）
- **AND** 更新 JudgingQueueStats 为 success
- **AND** 记录 completed_at 时间戳

#### Scenario: Status update with missing queue_stats
- **WHEN** 尝试更新状态但 queue_stats 不存在
- **THEN** 在任务开始前捕获异常并记录
- **AND** 不会导致任务崩溃或 500 错误
- **AND** 提供清晰的错误信息用于调试