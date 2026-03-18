## ADDED Requirements

### Requirement: Queue Stats API Error Handling
系统 SHALL 在查询队列统计信息时正确处理异常情况，返回适当的 HTTP 状态码。

#### Scenario: Queue stats not found
- **WHEN** 调用 GET /api/submissions/{id}/queue_stats/ 但该提交没有队列统计信息
- **THEN** 返回 404 Not Found 状态码
- **AND** 返回 JSON 格式的错误信息：{"error": "该提交没有队列统计信息"}
- **AND** 正确捕获 ObjectDoesNotExist 异常（不是 AttributeError）

#### Scenario: Queue stats access success
- **WHEN** 调用 GET /api/submissions/{id}/queue_stats/ 且队列统计信息存在
- **THEN** 返回 200 OK 状态码
- **AND** 返回完整的队列统计信息，包括：
  - status: 队列状态
  - queue_position: 队列位置
  - estimated_start_time: 预估开始时间
  - started_at: 实际开始时间
  - completed_at: 完成时间
  - queue_wait_seconds: 等待时长
  - execution_seconds: 执行时长
  - worker_name: Worker 名称
  - retry_count: 重试次数
  - error_message: 错误信息

#### Scenario: Unauthorized access
- **WHEN** 未授权用户尝试访问 queue_stats 端点
- **THEN** 返回 401 Unauthorized 状态码
- **AND** 不暴露任何队列信息

#### Scenario: Access another user's queue stats
- **WHEN** 用户尝试访问其他用户的提交队列统计
- **THEN** 返回 403 Forbidden 状态码
- **AND** 记录安全日志

### Requirement: Queue Status API Error Handling
系统 SHALL 在查询全局队列状态时正确处理各种错误情况。

#### Scenario: Database connection error
- **WHEN** 查询队列状态时数据库连接失败
- **THEN** 返回 503 Service Unavailable 状态码
- **AND** 返回友好的错误信息
- **AND** 记录详细的错误日志

#### Scenario: Redis cache unavailable
- **WHEN** Redis 缓存服务不可用
- **THEN** 降级为直接查询数据库
- **AND** 仍能返回正确的队列状态
- **AND** 记录降级日志但不影响用户体验

### Requirement: API Response Consistency
所有队列相关的 API 端点 SHALL 返回一致的错误响应格式。

#### Scenario: Consistent error format
- **WHEN** 任何队列 API 端点返回错误
- **THEN** 使用统一的错误格式：
  ```json
  {
    "error": "错误描述",
    "detail": "详细信息（可选）"
  }
  ```
- **AND** 使用正确的 HTTP 状态码：
  - 404: 资源不存在
  - 401: 未授权
  - 403: 无权限
  - 429: 请求过多
  - 500: 服务器内部错误
  - 503: 服务不可用

#### Scenario: Chinese error messages
- **WHEN** 返回错误响应
- **THEN** 所有错误信息使用中文
- **AND** 错误信息清晰、友好、可理解
- **AND** 不暴露技术细节给普通用户