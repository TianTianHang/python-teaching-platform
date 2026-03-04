## Context

当前项目采用 React Router v7 的 SSR 架构，部分页面已迁移到客户端直连模式（如登录页），但首页、课程列表和课程详情仍使用服务端代理模式。

**当前架构（服务端代理）**:
```
浏览器 → SSR Loader → createHttp(request) → 后端 API
```

**目标架构（客户端直连）**:
```
浏览器 → useEffect + clientHttp → 后端 API (CORS)
```

现有 `client-side-backend-migration-guide` 提供了通用迁移规范，本设计针对具体页面进行细化。

## Goals / Non-Goals

**Goals:**
- 将首页、课程列表、课程详情迁移到客户端直连模式
- 保持现有功能不变（显示逻辑、用户体验）
- 遵循 `client-side-backend-migration-guide` 的代码模板

**Non-Goals:**
- 不修改后端 API（仅修改前端调用方式）
- 不添加新功能
- 不修改页面 UI/UX

## Decisions

### D1: 数据获取方式

使用 `useEffect` + `clientHttp` 获取数据，而非 `useLoaderData`。

**替代方案考虑**:
- React Router v7 的 `clientLoader`: 可保留用于 SSR 降级，但会导致数据获取逻辑重复
- **选择**: 直接使用 `useEffect`，简化逻辑，依赖 `clientHttp` 内置的 401 自动刷新

### D2: 分页处理

课程列表使用 `useSearchParams` 管理分页参数。

**替代方案考虑**:
- URL 参数 + `useLoaderData`: 服务端方案
- **选择**: 客户端方案，使用 `useSearchParams` 监听参数变化触发数据重新获取

### D3: 报名功能（课程详情页）

将服务端 `action` 改为客户端 `clientHttp.post()` 调用。

**替代方案考虑**:
- 保留 action + 客户端导航: 混合方案
- **选择**: 完全客户端调用，简化流程

### D4: 错误处理

401 时跳转登录页，其他错误显示错误信息。

**实现**: 使用 `clientHttp` 的响应拦截器已处理 401 自动刷新，刷新失败才跳转登录

## Risks / Trade-offs

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 首屏加载变慢 | 用户需等待 JS 加载后才能看到数据 | 保留 Skeleton 骨架屏组件 |
| SEO 丢失 | 这些页面需要登录，不影响 | 无需处理 |
| CORS 配置 | 需要后端允许前端域名 | 确认现有配置已满足 |
| Token 过期 | 401 时需处理 | clientHttp 内置自动刷新 |