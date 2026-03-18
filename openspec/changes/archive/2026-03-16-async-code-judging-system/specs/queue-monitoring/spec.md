## ADDED Requirements

### Requirement: Real-time Queue Monitoring
系统 SHALL 提供实时队列监控功能，跟踪系统状态和性能指标。

#### Scenario: Queue length monitoring
- **WHEN** 监控系统检查队列状态
- **THEN** 记录当前等待任务数和执行任务数
- **AND** 计算队列长度随时间的变化趋势

#### Scenario: Worker utilization monitoring
- **WHEN** Worker 执行任务
- **THEN** 记录 Worker 的 CPU 和内存使用情况
- **AND** 计算平均利用率
- **AND** 检测异常资源使用情况

### Requirement: Performance Metrics Collection
系统 SHALL 收集和存储性能指标用于分析。

#### Scenario: Task duration tracking
- **WHEN** 任务从开始到完成
- **THEN** 记录以下指标：
  - 队列等待时间
  - 任务执行时间
  - 总处理时间
- **AND** 按时间段聚合统计数据

#### Scenario: Success rate tracking
- **WHEN** 任务完成
- **THEN** 记录任务结果状态
- **AND** 计算通过率、超时率和失败率
- **AND** 按语言、题目类型等维度分类统计

### Requirement: Alerting System
系统 SHALL 在异常情况下触发告警。

#### Scenario: Queue length alert
- **WHEN** 队列长度超过阈值（50个任务）
- **THEN** 触发队列积压告警
- **AND** 通过日志记录告警信息
- **AND** 通知管理员检查系统状态

#### Scenario: Timeout rate alert
- **WHEN** 超时率超过阈值（10%）
- **THEN** 触发性能告警
- **AND** 检查评测服务是否正常
- **AND** 建议调整超时参数

### Requirement: Admin Dashboard
系统 SHALL 提供管理员查看队列状态的接口。

#### Scenario: Real-time status view
- **WHEN** 管理员访问管理界面
- **THEN** 显示以下信息：
  - 当前队列状态（等待/执行中/完成）
  - 实时任务列表
  - 性能指标图表
- **AND** 数据每10秒自动刷新

#### Scenario: Historical data view
- **WHEN** 管理员查看历史数据
- **THEN** 显示以下图表：
  - 队列长度变化趋势
  - 任务执行时间分布
  - 成功率趋势
- **AND** 支持按时间段筛选

### Requirement: Manual Operations
系统 SHALL 支持管理员手动操作队列。

#### Scenario: Cancel pending task
- **WHEN** 管理员取消等待中的任务
- **THEN** 更新对应 Submission 为 cancelled
- **AND** 更新 JudgingQueueStats 为 cancelled
- **AND** 从队列中移除该任务

#### Scenario: Restart failed task
- **WHEN** 管理员重启失败的任务
- **THEN** 重置 Submission 为 pending 状态
- **AND** 创建新的 Celery 任务
- **AND** 清理旧的失败记录

### Requirement: Performance Thresholds
系统 SHALL 定义性能基准和阈值。

#### Scenario: Performance benchmark
- **WHEN** 系统运行时
- **THEN** 监控以下阈值：
  - 平均排队时间 < 30秒
  - 评测成功率 > 95%
  - 超时率 < 5%
  - Worker 利用率 60-80%
- **AND** 超过阈值时触发告警

#### Scenario: Capacity scaling
- **WHEN** 队列持续高负载
- **THEN** 建议扩容策略：
  - 增加 Worker 数量
  - 优化评测算法
  - 调整超时参数
- **AND** 提供具体的扩容建议