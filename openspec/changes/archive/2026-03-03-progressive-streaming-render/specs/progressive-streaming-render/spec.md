## ADDED Requirements

### Requirement: 页面加载器必须支持流式数据传输
系统 SHALL 允许页面 loader 返回 Promise 对象而不阻塞首屏渲染，React Router SHALL 自动将数据流式传输到客户端。

#### Scenario: 章节详情页 loader 返回 Promise
- **WHEN** 用户访问章节详情页（`/courses/:courseId/chapters/:chapterId`）
- **THEN** loader SHALL 在约 50ms 内返回（仅等待 unlockStatus）
- **AND** `chapter`、`problems`、`courseChapters` 数据 SHALL 作为 Promise 返回
- **AND** 首屏 HTML SHALL 在 Promise 解析前开始传输

#### Scenario: 爬虫请求等待所有数据
- **WHEN** 爬虫（user-agent 匹配 isbot）访问章节详情页
- **THEN** loader SHALL 使用 `onAllReady` 策略
- **AND** 所有数据 SHALL 解析完成后才返回 HTML

### Requirement: 必须使用细粒度 Suspense 边界
系统 SHALL 为不同的内容区域使用独立的 `<Suspense>` 边界，允许内容按优先级渐进式渲染。

#### Scenario: 章节标题优先渲染
- **WHEN** 章节详情页加载
- **AND** `chapter` 数据到达（约 100ms）
- **THEN** 章节标题 SHALL 立即显示
- **AND** 章节内容区域 SHALL 继续显示 Skeleton

#### Scenario: 章节内容独立渲染
- **WHEN** 章节详情页加载
- **AND** 章节内容数据到达
- **THEN** Markdown 内容 SHALL 独立渲染
- **AND** 不影响标题区域或题目列表区域

#### Scenario: 题目列表延迟渲染
- **WHEN** 章节详情页加载
- **AND** `problems` 数据尚未到达
- **THEN** 题目列表区域 SHALL 显示 `<ProblemsSkeleton />`
- **AND** 当数据到达后 SHALL 替换为实际内容

#### Scenario: 侧边栏最低优先级渲染
- **WHEN** 章节详情页加载
- **AND** 侧边栏数据最后到达
- **THEN** 侧边栏 SHALL 在主内容渲染完成后才开始渲染
- **AND** 不阻塞用户与主内容的交互

### Requirement: Skeleton 组件必须精确匹配最终内容
系统 SHALL 为每个 Suspense 边界提供精确匹配最终内容尺寸和布局的 Skeleton 组件，减少布局偏移（CLS）。

#### Scenario: Skeleton 使用正确的样式 token
- **WHEN** 创建或修改 Skeleton 组件
- **THEN** Skeleton SHALL 使用设计系统的 spacing token
- **AND** minHeight SHALL 设置为预期内容的近似高度
- **AND** Skeleton 元素 SHALL 使用与实际内容相同的 margin/padding

#### Scenario: Skeleton 减少布局偏移
- **WHEN** 用户访问章节详情页
- **THEN** 页面加载期间的 CLS SHALL 小于 0.1
- **AND** Skeleton 到实际内容的过渡 SHALL 不导致明显的页面跳动

#### Scenario: 多个 Skeleton 并行显示
- **WHEN** 页面有多个 Suspense 边界
- **THEN** 每个 Skeleton SHALL 独立显示
- **AND** Skeleton 之间 SHALL 保持正确的空间关系

### Requirement: 流式渲染必须保持功能完整性
系统 SHALL 在采用流式渲染后保持所有现有功能正常工作，包括重定向、错误处理、用户交互等。

#### Scenario: 锁定章节正常重定向
- **WHEN** 用户访问被锁定的章节
- **AND** unlockStatus 返回 `is_locked: true`
- **THEN** 系统 SHALL 重定向到 `/courses/:courseId/chapters/:chapterId/locked`
- **AND** 重定向 SHALL 在流式渲染前发生

#### Scenario: API 错误正确处理
- **WHEN** `problems` API 返回错误（如 404, 500）
- **THEN** 错误对象 SHALL 通过流式传输到达客户端
- **AND** `<Await>` 组件 SHALL 检测到错误对象
- **AND** 系统 SHALL 显示 `<ResolveError>` 组件

#### Scenario: 用户交互不受影响
- **WHEN** 页面正在流式加载部分内容
- **AND** 用户点击"标记为已完成"按钮
- **THEN** 表单提交 SHALL 正常工作
- **AND** 不受流式加载状态的影响

### Requirement: 必须建立可复用的流式渲染模式
系统 SHALL 提供可复用的组件、工具和文档，支持团队在其他页面中应用流式渲染模式。

#### Scenario: 流式组件模板
- **WHEN** 开发者需要为新的详情页添加流式渲染
- **THEN** 系统 SHALL 提供 `<StreamedContent>` 等可复用组件
- **AND** 模板 SHALL 包含正确的 Suspense 和 Await 结构

#### Scenario: Skeleton 生成工具
- **WHEN** 开发者需要创建新的 Skeleton 组件
- **THEN** 系统 SHALL 提供代码模板或 CLI 工具
- **AND** 模板 SHALL 包含正确的尺寸和样式配置

#### Scenario: 最佳实践文档
- **WHEN** 团队成员想了解流式渲染的使用场景
- **THEN** 系统 SHALL 提供详细的文档
- **AND** 文档 SHALL 包含何时使用、何时不使用的指导

### Requirement: 流式渲染必须改善核心性能指标
系统 SHALL 通过流式渲染改善核心 Web Vitals 和用户体验指标。

#### Scenario: 首字节时间（TTFB）改善
- **WHEN** 用户访问采用流式渲染的详情页
- **THEN** TTFB SHALL 减少 60% 以上
- **AND** TTFB 目标 SHALL 小于 100ms

#### Scenario: 首次内容绘制（FCP）改善
- **WHEN** 用户访问采用流式渲染的详情页
- **THEN** FCP SHALL 减少 50% 以上
- **AND** FCP 目标 SHALL 小于 150ms

#### Scenario: 最大内容绘制（LCP）改善
- **WHEN** 用户访问采用流式渲染的详情页
- **THEN** LCP SHALL 减少 30% 以上
- **AND** LCP 目标 SHALL 小于 250ms

#### Scenario: 累积布局偏移（CLS）保持良好
- **WHEN** 用户访问采用流式渲染的详情页
- **THEN** CLS SHALL 小于 0.1
- **AND** CLS SHALL 不比改造前更差

### Requirement: 流式渲染必须支持 SSR 环境
系统 SHALL 确保所有流式渲染逻辑在服务器端渲染环境中正常工作。

#### Scenario: Loader 在服务器端执行
- **WHEN** 页面 loader 返回 Promise
- **THEN** 数据获取 SHALL 在服务器端执行
- **AND** SHALL 使用 `createHttp(request)` 而非浏览器 API

#### Scenario: Hydration 正确工作
- **WHEN** 页面在客户端 hydration
- **THEN** `clientLoader.hydrate = true` SHALL 启用
- **AND** `<HydrateFallback>` 组件 SHALL 在 hydration 期间显示
- **AND** 客户端导航 SHALL 重新验证数据

#### Scenario: 环境检测不影响功能
- **WHEN** 代码在 SSR 环境中运行
- **THEN** SHALL 不依赖浏览器专用 API（如 `window`, `document`）
- **AND** SHALL 不抛出 "window is not defined" 错误

### Requirement: 流式渲染必须保持 SEO 友好
系统 SHALL 确保流式渲染不会负面影响搜索引擎对页面内容的抓取和索引。

#### Scenario: 爬虫获得完整内容
- **WHEN** 搜索引擎爬虫访问页面
- **AND** user-agent 被 isbot 识别
- **THEN** 系统 SHALL 使用 `onAllReady` 策略
- **AND** 爬虫 SHALL 获得完整的 HTML 内容

#### Scenario: 元数据正确设置
- **WHEN** 页面使用流式渲染
- **THEN** `<title>` 和其他 meta 标签 SHALL 正确设置
- **AND** meta 标签 SHALL 包含正确的页面信息

#### Scenario: 结构化数据不受影响
- **WHEN** 页面使用流式渲染
- **THEN** JSON-LD 或其他结构化数据 SHALL 正确包含在 HTML 中
- **AND** 搜索引擎 SHALL 能够解析结构化数据
