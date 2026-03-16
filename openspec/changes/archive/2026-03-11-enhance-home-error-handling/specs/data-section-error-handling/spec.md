## ADDED Requirements

### Requirement: 独立错误状态
系统 SHALL 为每个数据区块维护独立的错误状态，当一个区块的数据请求失败时，不影响其他区块的显示。

#### Scenario: 单一区块加载失败
- **WHEN** 页面有多个数据区块，其中一个区块的请求失败
- **THEN** 失败的区块显示错误UI，其他区块正常显示内容

#### Scenario: 所有区块加载失败
- **WHEN** 页面有多个数据区块，所有请求都失败
- **THEN** 每个区块都显示各自的错误UI，用户可以独立重试

#### Scenario: 区块状态独立管理
- **WHEN** 用户重试一个失败的区块
- **THEN** 只有该区块显示加载状态，其他区块保持当前状态不变

### Requirement: 友好的错误展示
系统 SHALL 在数据区块失败时显示包含图标、错误消息和操作按钮的友好错误UI。

#### Scenario: 错误UI基本结构
- **WHEN** 数据区块加载失败
- **THEN** 错误UI SHALL 包含：
  - 错误图标（视觉引导）
  - 区块特定的错误标题（如"课程列表加载失败"）
  - 友好的中文错误消息
  - 操作按钮（重试和/或返回）

#### Scenario: 错误视觉区分
- **WHEN** 用户浏览页面
- **THEN** 错误状态 SHALL 使用警告图标和警告色，与空状态（无数据）明确区分

#### Scenario: 错误状态不隐藏区块
- **WHEN** 数据区块加载失败
- **THEN** 区块容器 SHALL 保持可见，不折叠或隐藏

### Requirement: 智能错误消息映射
系统 SHALL 根据HTTP状态码和错误类型提供特定的中文错误消息。

#### Scenario: 4xx客户端错误消息
- **WHEN** 请求返回4xx错误（400, 403, 404等）
- **THEN** 显示对应的友好中文消息：
  - 400: "请求参数不正确，请刷新页面重试"
  - 403: "您没有权限查看此内容"
  - 404: "请求的内容不存在"

#### Scenario: 5xx服务器错误消息
- **WHEN** 请求返回5xx错误（500, 502, 503等）
- **THEN** 显示服务器错误消息：
  - 500: "服务器出错了，我们正在努力修复"
  - 502: "网关错误，请稍后重试"
  - 503: "服务暂时不可用，请稍后重试"
  - 504: "请求超时，请检查网络连接"

#### Scenario: 网络错误消息
- **WHEN** 请求因网络问题失败
- **THEN** 显示网络相关提示：
  - 超时: "网络连接超时，请检查您的网络设置"
  - 连接失败: "网络连接失败，请检查网络后重试"

### Requirement: 条件性重试按钮
系统 SHALL 根据错误类型决定是否显示重试按钮，只有可重试的错误才显示重试选项。

#### Scenario: 可重试错误显示重试按钮
- **WHEN** 错误是5xx、网络超时或连接失败
- **THEN** 显示"重新加载"按钮，用户点击后重新请求该区块数据

#### Scenario: 不可重试错误隐藏重试按钮
- **WHEN** 错误是4xx（除429外）
- **THEN** 不显示重试按钮，只显示返回按钮或建议操作

#### Scenario: 429限流错误可重试
- **WHEN** 错误是429 Too Many Requests
- **THEN** 显示重试按钮，提示用户稍后重试

### Requirement: 重试加载状态
系统 SHALL 在用户点击重试后显示加载状态，防止重复点击并提供视觉反馈。

#### Scenario: 重试时显示加载状态
- **WHEN** 用户点击重试按钮
- **THEN** 区块显示骨架屏或加载指示器，隐藏错误UI

#### Scenario: 重试期间禁用按钮
- **WHEN** 重试请求正在进行
- **THEN** 重试按钮处于禁用状态，防止重复点击

#### Scenario: 重试成功恢复内容
- **WHEN** 重试请求成功返回数据
- **THEN** 隐藏加载状态，显示数据内容，清除错误状态

#### Scenario: 重试失败保持错误
- **WHEN** 重试请求再次失败
- **THEN** 重新显示错误UI，保持可重试状态

### Requirement: 返回导航选项
系统 SHALL 在错误UI中提供返回首页或返回上一页的导航选项。

#### Scenario: 返回首页按钮
- **WHEN** 数据区块显示错误UI
- **THEN** 提供返回首页按钮，点击后导航到 /home

#### Scenario: 401错误特殊处理
- **WHEN** 错误是401未授权
- **THEN** 不显示重试按钮，系统自动重定向到登录页面

### Requirement: Promise.allSettled 数据处理
系统 SHALL 使用 Promise.allSettled 并行处理多个独立请求，使每个请求的成功或失败状态独立。

#### Scenario: 并行请求独立处理
- **WHEN** Loader发起多个并行请求
- **THEN** 使用 Promise.allSettled 而非 Promise.all，每个请求的失败不影响其他请求

#### Scenario: 结构化返回数据
- **WHEN** Loader完成数据获取
- **THEN** 返回结构化对象，包含每个请求的数据或错误信息：
  ```typescript
  {
    enrolledCourses: { data: Enrollment[] | null, error: ErrorInfo | null },
    unfinishedProblems: { data: ProblemProgress[] | null, error: ErrorInfo | null }
  }
  ```

#### Scenario: 错误信息提取
- **WHEN** Promise.allSettled 中的请求失败
- **THEN** 从 reason 中提取错误状态码和消息，转换为 ErrorInfo 对象

### Requirement: 区块组件独立性
每个数据区块组件 SHALL 独立管理自己的状态、重试逻辑和UI渲染。

#### Scenario: 组件接收初始状态
- **WHEN** 数据区块组件挂载
- **THEN** 从 loader data 接收初始数据或错误状态

#### Scenario: 组件内部状态管理
- **WHEN** 用户在区块内执行操作（如重试）
- **THEN** 组件使用内部 useState 管理加载、数据和错误状态

#### Scenario: 组件可复用性
- **WHEN** 创建多个数据区块组件（如 CoursesSection、ProblemsSection）
- **THEN** 每个组件独立工作，可单独替换或移除而不影响其他区块
