## 1. 通用组件开发

- [x] 1.1 创建 ErrorCard 组件
  - 文件：`frontend/web-student/app/components/ErrorCard.tsx`
  - 功能：接收 status、message、onRetry、title props
  - UI：包含错误图标、友好消息、重试按钮、返回首页按钮
  - 逻辑：根据错误类型决定是否显示重试按钮
  - 样式：使用 MUI Paper、Stack、Typography 组件

- [x] 1.2 实现友好错误消息映射函数
  - 在 ErrorCard 组件中创建 `getFriendlyErrorMessage` 函数
  - 映射常见 HTTP 状态码到中文消息（400-504）
  - 处理网络超时和连接失败的特殊情况
  - 提供默认错误消息作为兜底

- [x] 1.3 实现可重试性判断函数
  - 在 ErrorCard 组件中创建 `isRetriableError` 函数
  - 5xx、网络错误、429 返回 true
  - 4xx（除429外）返回 false

- [x] 1.4 ErrorCard 组件加载状态处理
  - 接收 isLoading prop
  - 加载时禁用重试按钮
  - 可选：显示骨架屏或加载指示器

## 2. 首页数据获取层改造

- [x] 2.1 修改 clientLoader 使用 Promise.allSettled
  - 文件：`frontend/web-student/app/routes/_layout.home.tsx`
  - 将 `Promise.all([req1, req2])` 改为 `Promise.allSettled([req1, req2])`
  - 处理每个 PromiseSettledResult，提取数据和错误

- [x] 2.2 定义错误信息类型
  - 在 home route 文件中定义 `ErrorInfo` 类型接口
  - 包含 status: number 和 message: string

- [x] 2.3 返回结构化数据对象
  - 返回 `{ enrolledCourses: { data, error }, unfinishedProblems: { data, error } }`
  - 成功时 data 包含数据，error 为 null
  - 失败时 data 为 null，error 包含 ErrorInfo

- [x] 2.4 保留 ErrorBoundary 处理 401
  - 保持 401 错误重定向到登录的逻辑
  - 更新错误消息以反映新的错误处理模式

## 3. 课程区块组件开发

- [x] 3.1 创建 CoursesSection 组件
  - 文件：`frontend/web-student/app/components/CoursesSection.tsx`
  - Props：initialData, initialError
  - 内部状态管理：data、error、isLoading

- [x] 3.2 实现 CoursesSection 重试逻辑
  - 创建 handleRetry 函数
  - 使用 clientHttp 重新请求数据
  - 更新组件状态（data/error/isLoading）

- [x] 3.3 CoursesSection 加载状态
  - 使用 `CourseCardsSkeleton` 作为加载指示器
  - 从现有 SkeletonHome 组件复用骨架屏

- [x] 3.4 CoursesSection 错误状态
  - 条件渲染 ErrorCard 组件
  - 传递错误信息、重试函数和区块标题

- [x] 3.5 CoursesSection 正常状态
  - 复用现有的课程列表渲染逻辑
  - 保持现有的卡片样式和交互

## 4. 题目区块组件开发

- [x] 4.1 创建 ProblemsSection 组件
  - 文件：`frontend/web-student/app/components/ProblemsSection.tsx`
  - Props：initialData, initialError
  - 内部状态管理：data、error、isLoading

- [x] 4.2 实现 ProblemsSection 重试逻辑
  - 创建 handleRetry 函数
  - 请求 `problem-progress/?status_not=solved` 接口
  - 更新组件状态

- [x] 4.3 ProblemsSection 加载状态
  - 使用题目列表骨架屏
  - 复用 SkeletonHome 中的 ProblemListItemSkeleton

- [x] 4.4 ProblemsSection 错误状态
  - 条件渲染 ErrorCard
  - 传递 "待解决问题" 作为区块标题

- [x] 4.5 ProblemsSection 正常状态
  - 复用现有的题目列表渲染逻辑
  - 保持列表项的图标、标签、按钮样式

## 5. 首页组件集成

- [x] 5.1 替换课程列表渲染为 CoursesSection
  - 移除直接的 enrolledCourses 渲染代码
  - 使用 `<CoursesSection initialData={...} initialError={...} />`

- [x] 5.2 替换题目列表渲染为 ProblemsSection
  - 移除直接的 unfinishedProblems 渲染代码
  - 使用 `<ProblemsSection initialData={...} initialError={...} />`

- [x] 5.3 更新 Home 组件类型定义
  - 调整 loaderData 类型以匹配新的数据结构
  - 确保类型安全

- [x] 5.4 移除不必要的 SectionContainer 包装
  - CoursesSection 和 ProblemsSection 内部已有容器
  - 避免重复嵌套

## 6. 错误边界优化

- [x] 6.1 更新 ErrorBoundary UI
  - 添加友好的错误图标
  - 提供更清晰的错误消息
  - 添加"返回首页"按钮

- [x] 6.2 ErrorBoundary 重试功能
  - 添加重试按钮（Link to="." 重新加载 loader）
  - 区分可重试和不可重试错误

## 7. 测试和验证

- [x] 7.1 手动测试单一区块失败场景
  - 模拟课程列表API失败
  - 验证题目列表正常显示
  - 验证错误区块可独立重试

- [x] 7.2 手动测试双重失败场景
  - 模拟两个API都失败
  - 验证两个区块都显示错误UI
  - 验证可独立重试

- [x] 7.3 测试不同错误类型
  - 4xx 错误：验证无重试按钮
  - 5xx 错误：验证有重试按钮
  - 网络错误：验证正确提示

- [x] 7.4 测试重试功能
  - 点击重试按钮
  - 验证加载状态正确显示
  - 验证重试成功后内容恢复
  - 验证重试失败后错误保持

- [x] 7.5 测试空状态 vs 错误状态
  - 验证 "暂无课程" 空状态显示
  - 验证错误状态与空状态视觉区分

- [x] 7.6 TypeScript 类型检查
  - 运行 `pnpm run typecheck` 确保无类型错误

- [x] 7.7 响应式设计验证
  - 移动端视图测试
  - 平板端视图测试
  - 桌面端视图测试
