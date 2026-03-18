## Context

当前前端架构采用 React Router v7 的路由系统，支持 SSR 和客户端 hydration 混合模式。父路由 `_layout.tsx` 已通过 `Outlet context` 传递用户数据，并提供了 `useUser()` hook 供子路由使用。然而，部分子路由（如 Profile 页面、课程子页面）仍独立发起 API 请求获取数据，导致重复请求问题。

**当前请求模式**：
```
/profile 访问：_layout.tsx (auth/me) + _layout.profile.tsx (auth/me) = 2 次请求
```

> **注**：课程详情页的数据复用方案已取消，原因是与现有的 `useInfiniteScroll` 实现存在兼容性问题。

**可用机制**：
- `useOutletContext` / `useUser()` hook：复用父路由通过 `Outlet context` 传递的数据
- `useRouteLoaderData(routeId)`：通过 route ID 访问任意路由的 loader 数据

## Goals / Non-Goals

**Goals:**
- 消除 Profile 页面对 `auth/me` 的重复请求
- 建立前端数据复用的最佳实践
- 保持 SSR 兼容性和现有错误处理机制

**Non-Goals:**
- 不修改后端 API
- 不引入全局状态管理（如 Redux、Zustand）
- 不修改现有的 HTTP 客户端核心逻辑
- 不修改用户认证和 token 刷新机制

## Decisions

### 决策 1：Profile 页面使用 `useUser()` hook 复用用户数据

**选择**：移除 `clientLoader`，使用 `useUser()` hook

**理由**：
- `_layout.tsx` 已通过 `Outlet context={{ user }}` 传递用户数据
- `useUser()` hook 已封装好类型安全的访问方式
- 无需额外改动，复用现有机制

**替代方案**：
- 使用 `useRouteLoaderData('routes/_layout')`：类型推导不如 `useUser()` 方便

### 决策 2：课程数据复用方案（已取消）

**原方案**：在 `_layout.courses_.$courseId/route.tsx` 的 `clientLoader` 中预取章节列表，子路由通过 `useRouteLoaderData` 复用。

**取消原因**：
- 预取的章节列表数据格式（`{ results: [], count: 0 }`）缺少 `next` 字段
- `useInfiniteScroll` 钩子通过 `pageData.next !== null` 判断 `hasMore`
- 当 `next` 字段缺失时，`undefined !== null` 返回 `true`，导致无限加载 bug
- 修复此问题需要修改 `useInfiniteScroll` 或调整数据格式，增加复杂度

**决定**：保持现有的独立请求模式。

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Profile 页面移除 `clientLoader` 后首次访问可能无数据 | 保留 `HydrateFallback` 显示 SkeletonProfile |

## Migration Plan

**Phase 1**：Profile 页面优化
1. 修改 `_layout.profile.tsx` 移除 `clientLoader`
2. 使用 `useUser()` 获取用户数据
3. 验证请求数量减少

> **注**：原计划的 Phase 2（课程数据复用）已取消。

**回滚策略**：
- 恢复 `clientLoader` 代码

## Open Questions

无
