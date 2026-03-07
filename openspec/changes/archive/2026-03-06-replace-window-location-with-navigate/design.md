## Context

当前前端 web-student 项目中存在多处使用 `window.location` 进行导航和页面刷新：

1. 内部导航：`window.location.href = '/courses'`
2. 页面刷新：`window.location.reload()`
3. 外部跳转：支付回调等

项目已使用 React Router v7，大部分组件已使用 `useNavigate` hook 进行导航。

## Goals / Non-Goals

**Goals:**
- 将组件内的 `window.location.href` 内部导航改为 `useNavigate()`
- 将页面刷新的 `window.location.reload()` 改为 `router.revalidate()` (SPA 刷新)
- 保持外部 URL 跳转不变（如支付回调）

**Non-Goals:**
- 修改 HTTP 拦截器 `client.ts` 中的 `window.location.href`（非组件上下文）
- 修改支付回调等外部 URL 跳转

## Decisions

### D1: 组件内导航使用 useNavigate
- **决定**: 将组件内的 `window.location.href = '/xxx'` 改为 `navigate('/xxx')`
- **理由**: React Router v7 的标准做法，支持 SPA 无刷新导航
- **替代方案**: 保持 window.location（简单但不 SPA）

### D2: 页面刷新使用 router.revalidate()
- **决定**: 将 `window.location.reload()` 改为调用 `useRevalidator()` 的 `revalidate()`
- **理由**: React Router v7 提供的数据重新加载方式，保持 SPA 体验
- **替代方案**: 
  - 保持 `window.location.reload()`（简单但非 SPA）
  - 手动重新调用 loader 函数

### D3: HTTP 拦截器保持 window.location
- **决定**: HTTP 拦截器中跳转到登录页保持 `window.location.href`
- **理由**: 拦截器在 axios 层面运行，不在 React 组件上下文，无法使用 useNavigate
- **替代方案**: 
  - 使用自定义事件 + 监听器（过度设计）
  - 在路由层面统一处理 401（改动过大）

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| router.revalidate() 在 SSR 环境 | 可能 SSR 时行为不同 | 检查环境，仅在客户端调用 |
| 支付回调需要外部 URL | 无法使用 navigate | 保持 window.location.href |