## ADDED Requirements

### Requirement: Independent error handling for multiple data sources
当页面加载多个独立的数据源时，系统 SHALL 使用 `Promise.allSettled` 确保一个数据源的失败不会影响其他数据源的显示。

#### Scenario: 课程详情页 - 报名信息 API 失败但课程信息正常显示
- **WHEN** 用户访问课程详情页，且报名信息 API 返回错误（500、超时等）
- **THEN** 系统 SHALL 显示课程基本信息（标题、描述、章节列表等）
- **AND** 报名信息区域 SHALL 显示错误提示或占位符
- **AND** 用户仍然可以查看课程内容

#### Scenario: 课程详情页 - 课程信息 API 失败但报名信息正常显示
- **WHEN** 用户访问课程详情页，且课程信息 API 返回错误
- **THEN** 系统 SHALL 显示友好的错误消息（使用 ErrorCard）
- **AND** 提供"重新加载"按钮允许重试
- **AND** 提供"返回课程列表"按钮

### Requirement: Friendly Chinese error messages
系统 SHALL 根据错误类型（HTTP 状态码、网络错误）提供友好的中文错误消息。

#### Scenario: 显示 404 错误
- **WHEN** API 返回 404 状态码
- **THEN** 系统 SHALL 显示"请求的内容不存在"

#### Scenario: 显示 403 错误
- **WHEN** API 返回 403 状态码
- **THEN** 系统 SHALL 显示"您没有权限查看此内容"

#### Scenario: 显示 500 错误
- **WHEN** API 返回 500 状态码
- **THEN** 系统 SHALL 显示"服务器出错了，我们正在努力修复"

#### Scenario: 显示网络错误
- **WHEN** 网络请求失败（无响应、超时等）
- **THEN** 系统 SHALL 显示"网络连接失败，请检查网络后重试"或"网络连接超时"

#### Scenario: 显示 429 错误
- **WHEN** API 返回 429（Too Many Requests）状态码
- **THEN** 系统 SHALL 显示"请求过于频繁，请稍后再试"

### Requirement: Retry functionality for failed requests
系统 SHALL 为可重试的错误提供"重新加载"按钮，允许用户主动重试失败的操作。

#### Scenario: 重试 5xx 错误
- **WHEN** API 返回 5xx 错误
- **THEN** 系统 SHALL 显示"重新加载"按钮
- **AND** 点击按钮 SHALL 重新发起 API 请求
- **AND** 重试期间按钮 SHALL 显示加载状态并禁用

#### Scenario: 重试网络错误
- **WHEN** 网络请求失败（无网络、超时等）
- **THEN** 系统 SHALL 显示"重新加载"按钮
- **AND** 点击按钮 SHALL 重新发起请求

#### Scenario: 不重试 4xx 错误（除了 429）
- **WHEN** API 返回 4xx 错误（400、403、404 等）
- **THEN** 系统 SHALL **不**显示"重新加载"按钮
- **AND** 显示适当的错误消息（如"您没有权限查看此内容"）
- **AND** 提供"返回首页"或其他导航按钮

### Requirement: ErrorBoundary for all major pages
系统 SHALL 为所有主要页面添加 ErrorBoundary 组件，捕获数据加载错误并显示友好的错误 UI。

#### Scenario: 个人资料页加载失败
- **WHEN** 用户访问个人资料页，且 API 返回错误
- **THEN** 系统 SHALL 显示 ErrorCard 组件，包含错误消息和重试按钮
- **AND** **不**显示空白页面或原始错误堆栈

#### Scenario: 题目列表页加载失败
- **WHEN** 用户访问题目列表页，且 API 返回错误
- **THEN** 系统 SHALL 显示 ErrorCard 组件，替换基础 ErrorBoundary
- **AND** 提供基于状态码的友好中文消息

#### Scenario: 会员页加载失败（SSR）
- **WHEN** 会员页的 loader 抛出错误
- **THEN** 系统 SHALL 捕获错误并返回适当的响应
- **AND** 客户端导航时 SHALL 使用 ErrorBoundary 显示错误

### Requirement: Authentication error handling
当 API 返回 401（未授权）错误时，系统 SHALL 重定向用户到登录页面。

#### Scenario: 401 错误重定向到登录页
- **WHEN** 任何 clientLoader 或 loader 收到 401 响应
- **THEN** 系统 SHALL 重定向用户到 `/auth/login`
- **AND** ErrorBoundary **不**捕获此错误（因为它是重定向，不是显示错误）

### Requirement: Error state isolation
页面的不同部分 SHALL 有独立的错误和数据状态，一个部分的错误 SHALL **不**影响其他部分的显示。

#### Scenario: 题目列表筛选器可用但列表加载失败
- **WHEN** 题目列表 API 失败
- **THEN** 筛选器 SHALL 保持可用（如果已加载）
- **AND** 列表区域 SHALL 显示错误消息

#### Scenario: 用户资料的基本信息加载失败但操作按钮可用
- **WHEN** 个人资料 API 失败
- **THEN** 系统 SHALL 显示错误消息
- **AND** 但如果页面有其他不依赖 API 的内容（如导航），那些内容 SHALL 正常显示

### Requirement: Loading states during retry
系统 SHALL 在重试请求期间显示加载状态，提供视觉反馈。

#### Scenario: 重试期间显示加载状态
- **WHEN** 用户点击"重新加载"按钮
- **THEN** 系统 SHALL 显示加载指示器（如 skeleton 或 spinner）
- **AND** "重新加载"按钮 SHALL 禁用，显示"重新加载中..."
- **AND** 其他操作按钮 SHALL **不**禁用（除非逻辑上需要）

### Requirement: Consistent ErrorCard component usage
系统 SHALL 在所有页面使用统一的 ErrorCard 组件，确保错误 UI 的一致性。

#### Scenario: 所有页面使用相同的错误 UI 样式
- **WHEN** 任何页面显示错误
- **THEN** 错误 UI SHALL 使用 ErrorCard 组件
- **AND** 包含警告图标、错误标题、错误消息和操作按钮
- **AND** 样式（颜色、间距、图标）保持一致
