## ADDED Requirements

### Requirement: Frontend Polling Mechanism
前端 SHALL 实现状态轮询机制，实时获取评测结果。

#### Scenario: Initial submission
- **WHEN** 用户提交代码
- **THEN** 显示 "正在排队，前面有 X 人" 的状态
- **AND** 开始每2秒轮询一次状态
- **AND** 显示预估等待时间

#### Scenario: Status update
- **WHEN** 收到状态更新
- **THEN** 根据新状态更新UI：
  - pending: 显示排队位置和等待时间
  - started: 显示 "开始评测..."
  - judging: 显示 "评测中..." 并显示进度条
  - success/failed: 显示结果详情

#### Scenario: Polling timeout
- **WHEN** 轮询超过60次（2分钟）
- **THEN** 停止轮询
- **AND** 显示 "获取结果超时，请刷新重试"
- **AND** 提供刷新按钮

### Requirement: API Error Handling
API 请求 SHALL 正确处理各种错误情况。

#### Scenario: Network error
- **WHEN** 轮询请求失败
- **THEN** 自动重试最多3次
- **AND** 重试间隔使用指数退避（2s, 4s, 8s）
- **AND** 所有重试失败后显示网络错误提示

#### Scenario: Authentication error
- **WHEN** 返回 401 未授权
- **THEN** 自动跳转到登录页面
- **AND** 清除本地存储的认证信息

#### Scenario: Server error
- **WHEN** 返回 5xx 服务器错误
- **THEN** 显示 "服务器繁忙，请稍后重试"
- **AND** 停止轮询并提供重试按钮

### Requirement: Real-time Status Display
UI SHALL 提供友好的实时状态展示。

#### Scenario: Queue position indicator
- **WHEN** 处于等待状态
- **THEN** 显示进度条和文字提示：
  - "前面有 5 人等待"
  - "预计等待 3 分钟"
  - 实时更新的进度动画

#### Scenario: Progress indicators
- **WHEN** 处于评测中
- **THEN** 显示：
  - 旋转的加载动画
  - "正在评测第 1/3 个测试用例"
  - 已用时间计时器

#### Scenario: Result display
- **WHEN** 评测完成
- **THEN** 显示：
  - 通过/失败的图标和文字
  - 执行时间和内存使用情况
  - 测试用例详情（失败时）
  - "查看详情" 链接

### Requirement: User Experience Enhancements
系统 SHALL 提供良好的用户体验。

#### Scenario: Empty state
- **WHEN** 用户首次进入页面
- **THEN** 显示：
  - "系统空闲，可以立即提交"
  - 绿色指示灯
  - 无等待状态

#### Scenario: System busy state
- **WHEN** 系统负载较高
- **THEN** 显示：
  - "系统繁忙，请稍候"
  - 橙色警告图标
  - 预估等待时间

#### Scenario: System full state
- **WHEN** 系统达到容量上限
- **THEN** 显示：
  - "系统已满，请稍后重试"
  - 红色错误图标
  - "预计 5 分钟后重试" 的建议

### Requirement: Browser Compatibility
轮询机制 SHALL 兼容各种浏览器环境。

#### Scenario: SSR compatibility
- **WHEN** 在服务器端渲染时
- **THEN** 不执行轮询逻辑
- **AND** 仅返回初始状态
- **AND** 在客户端激活后才开始轮询

#### Scenario: Tab visibility
- **WHEN** 用户切换到其他标签页
- **THEN** 降低轮询频率（改为每10秒一次）
- **WHEN** 用户切换回当前标签页
- **THEN** 恢复正常轮询频率（每2秒一次）

#### Scenario: Network offline
- **WHEN** 网络连接断开
- **THEN** 显示 "网络已断开" 提示
- **AND** 停止轮询
- **WHEN** 网络恢复
- **THEN** 自动重试轮询

### Requirement: Mobile Optimization
移动端 SHALL 优化轮询体验。

#### Scenario: Touch interactions
- **WHEN** 在移动设备上操作
- **THEN** 按钮和状态显示适合触摸操作
- **AND** 避免过小的点击区域

#### Scenario: Data usage
- **WHEN** 在移动网络环境下
- **THEN** 优化数据传输：
  - 压缩响应数据
  - 减少不必要的字段
  - 使用 HTTP 缓存

#### Scenario: Screen orientation
- **WHEN** 屏幕方向改变
- **THEN** 自适应调整布局
- **AND** 保持轮询状态不丢失