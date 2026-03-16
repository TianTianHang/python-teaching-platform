## MODIFIED Requirements

### Requirement: Code execution backend
**FROM**: CodeExecutorService.run_all_test_cases() 同步执行所有测试用例，阻塞直到完成
**TO**: 支持同步和异步两种执行模式，保持向后兼容性

**系统 SHALL** 支持同步和异步两种执行模式。

#### Scenario: Synchronous execution (existing behavior)
- **WHEN** 直接调用 CodeExecutorService.run_all_test_cases()
- **THEN** 立即执行所有测试用例
- **AND** 返回包含完整结果的 Submission 对象
- **AND** 更新数据库中的状态和结果

#### Scenario: Asynchronous execution via Celery
- **WHEN** 通过 Celery 任务调用 run_all_test_cases()
- **THEN** 不阻塞当前流程
- **AND** 更新 Submission status 为 judging
- **AND** 创建 JudgingQueueStats 记录
- **AND** 返回任务控制权

### Requirement: Execution timeout handling
**FROM**: 仅依赖 Judge0 的超时机制
**TO**: 增加三层超时保护机制

**系统 SHALL** 实现三层超时保护机制。

#### Scenario: Queue timeout check
- **WHEN** 任务在队列中等待超过120秒
- **THEN** 标记为 timeout 状态
- **AND** 不执行实际评测代码
- **AND** 返回排队超时错误

#### Scenario: Soft timeout during execution
- **WHEN** 任务执行超过270秒（4.5分钟）
- **THEN** 抛出 SoftTimeLimitExceeded 异常
- **AND** 保存已执行的部分结果
- **AND** 标记为 "time_limit_exceeded" 状态

#### Scenario: Hard timeout during execution
- **WHEN** 任务执行超过300秒（5分钟）
- **THEN** Worker 强制终止任务
- **AND** 标记为 "internal_error" 状态
- **AND** 记录任务被强制终止的信息

### Requirement: Error handling and recovery
**FROM**: 简单的异常捕获和错误标记
**TO**: 增强的错误分类和恢复机制

**系统 SHALL** 实现增强的错误分类和恢复机制。

#### Scenario: Judge0 API error
- **WHEN** Judge0 API 返回错误
- **THEN** 根据错误类型分类处理：
  - 5xx 错误：重试最多3次
  - 4xx 错误：标记为 "internal_error"
  - 网络错误：重试机制
- **AND** 记录详细的错误日志

#### Scenario: Database error
- **WHEN** 更新数据库时发生错误
- **THEN** 回滚事务
- **AND** 标记任务为 "failed"
- **AND** 触发告警通知

#### Scenario: Task retry logic
- **WHEN** Celery 任务失败
- **THEN** 根据错误类型决定：
  - 临时错误：自动重试（最多3次）
  - 永久错误：不重试，标记失败
  - 资源错误：等待后重试

### Requirement: Resource management
**FROM**: 无限制的资源使用
**TO**: 增加资源限制和监控

**系统 SHALL** 实现资源限制和监控机制。

#### Scenario: Memory limit enforcement
- **WHEN** 任务内存使用超过限制
- **THEN** Judge0 返回内存超限
- **AND** 标记为 "memory_limit_exceeded"
- **AND** 记录实际内存使用量

#### Scenario: CPU time limit enforcement
- **WHEN** 任务 CPU 时间超过限制
- **THEN** Judge0 返回超时
- **AND** 标记为 "time_limit_exceeded"
- **AND** 记录实际执行时间

#### Scenario: Resource cleanup
- **WHEN** 任务完成（无论成功失败）
- **THEN** 清理临时文件
- **AND** 释放数据库连接
- **AND** 更新资源使用统计

### Requirement: Logging and monitoring
**FROM**: 基础的日志记录
**TO**: 增强的结构化日志和监控指标

**系统 SHALL** 实现增强的结构化日志和监控指标。

#### Scenario: Task lifecycle logging
- **WHEN** 任务状态变化时
- **THEN** 记录结构化日志：
  - 任务开始时间、结束时间
  - 执行状态
  - 错误信息（如果有）
  - 资源使用情况
- **AND** 包含 task_id 和 user_id 用于追踪

#### Scenario: Performance metrics collection
- **WHEN** 任务完成时
- **THEN** 收集以下指标：
  - 队列等待时间
  - 任务执行时间
  - 总处理时间
  - 成功率统计
- **AND** 发送到监控系统

#### Scenario: Performance threshold monitoring
- **WHEN** 执行时间超过阈值
- **THEN** 触发性能告警
- **AND** 记录慢查询日志
- **AND** 分析性能瓶颈