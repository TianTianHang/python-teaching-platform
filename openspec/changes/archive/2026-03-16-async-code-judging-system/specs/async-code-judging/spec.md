## ADDED Requirements

### Requirement: Asynchronous Code Submission
系统 SHALL 支持异步代码提交，用户提交代码后立即返回任务ID而非等待结果。

#### Scenario: Successful submission
- **WHEN** 用户提交代码到算法题
- **THEN** 系统立即响应 202 Accepted 状态
- **AND** 返回数据包含 task_id、estimated_wait_seconds 和 status=pending
- **AND** 在数据库中创建 Submission 和 JudgingQueueStats 记录

#### Scenario: Queue capacity check
- **WHEN** 系统负载达到容量上限（18个任务）
- **THEN** 返回 429 Too Many Requests 状态
- **AND** 错误信息为 "系统繁忙，请稍后再试"
- **AND** 不创建任何新的提交记录

#### Scenario: Queue busy state
- **WHEN** 系统负载在警告阈值（10个任务）但未达到上限
- **THEN** 允许提交
- **AND** estimated_wait_seconds 反映预估等待时间

### Requirement: Queue Management
系统 SHALL 实现队列容量管理，包括状态计算和缓存。

#### Scenario: Capacity calculation
- **WHEN** 调用 JudgingCapacityService.get_current_capacity()
- **THEN** 返回包含以下信息的字典：
  - pending_count: 等待中的任务数
  - running_count: 执行中的任务数
  - total_capacity: 总容量（18）
  - available_slots: 剩余槽位数
  - status: available/busy/full

#### Scenario: Cache management
- **WHEN** 获取容量信息
- **THEN** 优先返回 Redis 缓存数据（30秒过期）
- **AND** 缓存不存在时计算并缓存结果
- **AND** 每次计算都使用最新数据库数据

### Requirement: Task Execution
系统 SHALL 通过 Celery 异步执行代码评测任务。

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

### Requirement: Queue Status API
系统 SHALL 提供队列状态查询接口。

#### Scenario: Global queue status
- **WHEN** 调用 GET /api/submissions/queue-status/
- **THEN** 返回全局队列容量信息
- **AND** 包含当前排队人数、执行人数和系统状态

#### Scenario: Personal queue status
- **WHEN** 用户查询个人队列状态
- **THEN** 返回该用户的当前提交状态
- **AND** 显示队列位置（如果有）和预估等待时间

### Requirement: Submission Status Update
系统 SHALL 在任务执行过程中更新提交状态。

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

## MODIFIED Requirements

### Requirement: Code execution
**FROM**: CodeExecutorService.run_all_test_cases() 同步执行所有测试用例
**TO**: 支持同步和异步两种调用模式

**系统 SHALL** 支持同步和异步两种调用模式。

#### Scenario: Synchronous execution (backward compatibility)
- **WHEN** 调用 run_all_test_cases() 保持原有参数
- **THEN** 同步执行并返回完整的 Submission 对象
- **AND** 状态直接更新为最终结果

#### Scenario: Asynchronous execution
- **WHEN** 通过 Celery 任务调用 run_all_test_cases()
- **THEN** 返回结果但不阻塞当前流程
- **AND** 通过队列状态跟踪进度