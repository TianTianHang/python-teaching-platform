# SSR Loader 并行请求规范

## ADDED Requirements

### Requirement: 独立 API 请求并行执行

SSR loader 函数 SHALL 使用 `Promise.all` 并行执行独立的 API 请求，以最小化总等待时间。

#### Scenario: 并行请求总耗时取最慢者

- **WHEN** loader 函数需要获取多个独立的 API 资源
- **THEN** 系统 SHALL 使用 `Promise.all` 同时发起所有请求
- **AND** 总耗时 SHALL 等于最慢请求的耗时（而非所有请求之和）

#### Scenario: 并行请求失败隔离

- **WHEN** `Promise.all` 中的某个请求失败
- **THEN** 系统 SHALL 使用 `.catch()` 捕获该请求的错误
- **AND** 该请求 SHALL 返回包含 `status` 和 `message` 字段的错误对象
- **AND** 其他并行请求 SHALL 继续执行并正常返回数据

#### Scenario: 并行请求类型安全

- **WHEN** 使用 `Promise.all` 并行化多个类型不同的请求
- **THEN** 系统 SHALL 使用 TypeScript 泛型明确标注返回类型
- **AND** 返回值 SHALL 保持正确的类型推断

### Requirement: 快速失败机制优化

对于需要前置验证的场景，loader SHALL 保持串行的验证检查，避免不必要的 API 调用。

#### Scenario: 锁定资源快速失败

- **WHEN** loader 需要检查资源是否被锁定（如章节解锁状态）
- **THEN** 系统 SHALL 先执行验证检查（串行）
- **AND** 如果验证失败，系统 SHALL 立即返回 redirect，不执行后续请求
- **AND** 如果验证通过，系统 SHALL 使用 `Promise.all` 并行获取所有后续数据

#### Scenario: 验证检查失败不影响并发能力

- **WHEN** 验证检查通过后执行并行请求
- **THEN** 系统 SHALL 确保 `Promise.all` 包含所有独立请求
- **AND** 总耗时 SHALL 不包含验证检查的耗时（验证 + 并行，而非 验证 + 串行）

### Requirement: 非关键操作异步执行

对于不影响页面渲染的非关键操作（如学习进度记录），loader SHALL 异步执行，避免阻塞响应。

#### Scenario: POST 请求不阻塞 loader 响应

- **WHEN** loader 需要执行非关键的 POST 请求（如 `mark_as_completed`）
- **THEN** 系统 SHALL 发起 POST 请求但不使用 `await` 等待其完成
- **AND** loader SHALL 立即返回数据给组件，不等待 POST 完成
- **AND** POST 请求 SHALL 在后台异步执行

#### Scenario: 异步 POST 失败静默处理

- **WHEN** 异步 POST 请求失败
- **THEN** 系统 SHALL 使用 `.catch()` 捕获错误
- **AND** 错误 SHALL 被静默处理，不影响用户体验
- **AND** 系统 MAY 记录日志用于后续分析

### Requirement: 保持现有错误处理语义

并行化优化 SHALL 保持现有的错误处理逻辑和组件层的错误展示方式。

#### Scenario: 错误对象格式一致

- **WHEN** 请求失败并通过 `.catch()` 返回错误对象
- **THEN** 错误对象 SHALL 包含 `status` 字段（HTTP 状态码）
- **AND** 错误对象 SHALL 包含 `message` 字段（错误描述）
- **AND** 组件层 SHALL 根据 `status` 字段判断是否显示 `ResolveError` 组件

#### Scenario: 非关键数据失败不影响主流程

- **WHEN** 非关键数据（如侧边栏列表）请求失败
- **THEN** 页面 SHALL 正常渲染主内容
- **AND** 系统 SHALL 在失败区域显示 `ResolveError` 组件
- **AND** 用户 SHALL 能够继续使用页面其他功能

### Requirement: 向后兼容性

并行化优化 SHALL 完全向后兼容，不破坏任何现有功能或 API。

#### Scenario: 组件层数据格式不变

- **WHEN** loader 经过并行化优化后
- **THEN** 组件接收的 `loaderData` 对象结构 SHALL 保持不变
- **AND** 组件代码 SHALL 无需修改即可正常工作

#### Scenario: JWT 认证流程不受影响

- **WHEN** loader 执行并行请求时
- **THEN** 每个请求 SHALL 自动携带 JWT token（通过 `createHttp` 拦截器）
- **AND** 如果任何请求返回 401，系统 SHALL 触发 token 刷新流程
- **AND** token 刷新成功后，系统 SHALL 自动重试失败的请求
