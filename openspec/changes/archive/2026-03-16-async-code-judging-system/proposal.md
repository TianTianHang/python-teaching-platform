## Why

当前代码评测系统采用同步阻塞模式，用户提交代码后需要等待 2-30 秒才能获得结果，导致：
1. 用户体验差：前端长时间等待，无法进行其他操作
2. 系统稳定性风险：高并发时可能造成服务器负载过高
3. 资源利用率低：CPU 资源被长时间占用，无法处理其他任务

将评测改为异步模式，通过队列管理实现更好的用户体验和系统稳定性。

## What Changes

### 核心功能变更
- **SubmissionViewSet.create()**：修改为异步提交，返回任务ID而非直接结果
- **CodeExecutorService.run_all_test_cases()**：重构支持异步调用
- **新增 JudgingCapacityService**：实现队列容量管理和状态监控
- **新增异步评测任务**：通过 Celery 执行异步评测
- **新增前端轮询机制**：实时获取评测状态

### 数据模型变更
- **Submission**：新增 `task_id` 和 `estimated_wait_seconds` 字段
- **新增 JudgingQueueStats**：跟踪每个提交的队列状态、位置和超时信息

### 新增接口
- `GET /api/submissions/queue-status/`：获取队列状态（全局和个人）
- **BREAKING**：提交响应格式变更（返回 task_id 和预估时间）

### 配置和部署
- **新增 Celery 队列**：专用代码评测队列
- **配置 Redis**：作为消息队列和缓存
- **新增 Worker 进程**：专用评测 Worker

## Capabilities

### New Capabilities
- `async-code-judging`：异步代码评测能力，包括队列管理、容量控制和状态轮询
- `queue-monitoring`：队列监控能力，实时显示系统状态和历史统计
- `submission-polling`：提交状态轮询能力，前端实时获取结果

### Modified Capabilities
- `code-execution`：从同步执行改为异步执行，REQUIREMENTS 变更

## Impact

### 受影响代码
- `backend/courses/models.py`：Submission 模型扩展
- `backend/courses/views.py`：SubmissionViewSet.create() 修改
- `backend/courses/services.py`：CodeExecutorService 重构
- `backend/courses/tasks.py`：新增异步评测任务
- `backend/core/settings.py`：配置更新
- `frontend/src/api/`：前端 API 封装更新
- `frontend/src/components/submission/`：新增状态轮询组件

### 系统依赖
- Redis：需要配置消息队列和缓存
- Celery：新增专用队列和 Worker
- Judge0：保持不变，作为评测后端

### 性能影响
- 响应时间从 2-30 秒降至 < 100ms
- 系统并发能力提升 50%
- 需要额外资源：Redis、Celery Worker