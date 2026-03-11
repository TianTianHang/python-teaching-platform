## Why

当前首页使用 `Promise.all` 并行获取已报名课程和未完成题目两个数据源。当任一请求失败时，整个页面加载失败，用户看不到任何内容。这种"全有或全无"的体验导致：
- 一个API故障会影响整个页面的可用性
- 用户无法区分是哪个请求失败，也无法独立重试
- 错误提示简陋，缺乏友好的视觉引导和操作建议

本变更通过独立错误处理和细粒度重试，提升首页容错能力和用户体验。

## What Changes

### 数据获取层（Loader）
- 将 `Promise.all` 改为 `Promise.allSettled`，使两个请求独立
- 返回包含数据和错误状态的结构化对象
- 保留 ErrorBoundary 处理 401 等全局错误

### UI 组件层
- 创建 `ErrorCard` 通用组件，提供统一的错误展示和重试界面
- 创建 `CoursesSection` 和 `ProblemsSection` 独立区块组件
- 每个区块独立管理自己的数据、加载、错误状态
- 支持区块级别的独立重试功能

### 错误体验
- 根据错误码提供友好的中文错误提示
- 错误UI包含图标、消息、重试按钮和返回首页按钮
- 区分可重试错误（5xx、网络错误）和不可重试错误（4xx）
- 保持空状态（无数据）和错误状态的视觉区分

## Capabilities

### New Capabilities
- `data-section-error-handling`: 定义数据区块的错误处理UI模式，包括错误展示、重试逻辑、按钮策略

### Modified Capabilities
（无 - 现有功能的需求未改变，仅改进实现）

## Impact

### 受影响的代码
- `frontend/web-student/app/routes/_layout.home.tsx` - 首页路由文件
- 新增 `frontend/web-student/app/components/ErrorCard.tsx` - 错误展示组件
- 新增 `frontend/web-student/app/components/CoursesSection.tsx` - 课程区块组件
- 新增 `frontend/web-student/app/components/ProblemsSection.tsx` - 题目区块组件

### API 兼容性
- 无 API 变更，仅改进前端错误处理逻辑
- 后端接口和响应格式保持不变

### 依赖变更
- 新增对 MUI 组件的依赖（ErrorOutline、Refresh、Home、Warning 等 Icon）
- 复用现有的 http client、SectionContainer 等基础设施

### 潜在推广
- 本变更的模式可推广至其他多数据请求页面（如课程详情页、章节列表页）
- `ErrorCard` 组件可作为全局通用组件使用
