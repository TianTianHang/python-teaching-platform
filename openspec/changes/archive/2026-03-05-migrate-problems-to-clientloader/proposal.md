## Why

题目模块的 4 个核心页面目前使用 `useEffect` 在客户端获取数据，导致首次渲染延迟、无法利用 SSR/Hydration 优化，且与已迁移的 Home 和 Courses 页面的数据加载模式不一致。这次迁移将统一数据获取模式，提升首屏性能和用户体验。

## What Changes

将以下 4 个页面从 `useEffect + clientHttp` 模式迁移到 `clientLoader` 模式：

- **`_layout.problems.tsx`** (题目列表页)
  - 添加 `clientLoader` 处理筛选、分页逻辑
  - 添加 `HydrateFallback` 和 `ErrorBoundary`
  - 移除 `useEffect`、`useState`、`useSearchParams` 的数据获取逻辑
  - 保留现有的缓存头优化 (`Cache-Control: public, max-age=300`)

- **`problems.$problemId/route.tsx`** (题目详情页)
  - 添加 `clientLoader` 处理"下一题"导航逻辑
  - 添加 `HydrateFallback` 和 `ErrorBoundary`
  - 移除 `useEffect` 数据获取逻辑
  - 保留条件路由逻辑（`GET /problems/:id` 或 `GET /problems/next/`）

- **`problems.$problemId.description.tsx`** (题目描述子路由)
  - 添加 `clientLoader` 获取题目描述
  - 添加 `HydrateFallback` 和 `ErrorBoundary`
  - 移除 `useEffect` 数据获取逻辑

- **`problems.$problemId.submissions.tsx`** (提交记录子路由)
  - 添加 `clientLoader` 处理并行请求 (`Promise.all`)
  - 添加 `HydrateFallback` 和 `ErrorBoundary`
  - 移除 `useEffect` 数据获取逻辑
  - 保留分页逻辑

## Capabilities

### New Capabilities

无新增功能能力。这是纯技术迁移，不改变任何用户可见的行为或需求。

### Modified Capabilities

无需求变更。所有功能保持不变，只是实现方式从 `useEffect` 迁移到 `clientLoader`。

## Impact

- **前端代码**: 修改 4 个路由文件，迁移约 300-400 行代码
- **API**: 无变化，继续使用现有 REST API
- **依赖**: 无新增依赖
- **性能**: 
  - 首屏渲染更快（数据预加载）
  - 支持 Hydration，减少页面闪烁
  - 可以实现导航预加载（prefetch）
- **一致性**: 与已迁移的 Home、Courses 页面保持一致的代码模式
