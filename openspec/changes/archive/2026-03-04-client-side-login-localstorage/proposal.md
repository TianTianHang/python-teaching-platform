## Why

当前登录流程经过 React Router 服务端 action，增加了不必要的延迟和网络跳转。采用客户端直连后端 API 的方式可以简化架构、降低服务端负载，同时让用户获得更快的登录响应体验。

## What Changes

- **移除服务端登录 action**：登录页面不再使用 `export const action`，改为浏览器端直接调用 Django API
- **localStorage Token 存储**：登录成功后，access token 和 refresh token 都存储在 localStorage
- **客户端 Auth 工具**：创建 `app/utils/auth/client.ts` 封装 token 管理和 API 请求
- **Django CORS 配置**：后端需要允许跨域请求并支持 credentials
- **登录页面重构**：改用 `axios` 直接调用 `/api/v1/auth/login/`，处理响应并存储 token

**BREAKING**: 登录流程完全改为客户端实现，原有的服务端 session 机制不再用于登录态管理

## Capabilities

### New Capabilities
- `client-auth`: 客户端认证管理，包括 token 存储、刷新、API 请求封装

### Modified Capabilities
- `auth-login`: 登录功能从服务端 action 改为客户端直连 API

## Impact

- **前端**: `app/routes/auth.login.tsx` 重构，`app/utils/auth/client.ts` 新增
- **后端**: Django 需要配置 CORS 允许跨域携带 credentials
- **安全**: Token 存储在 localStorage 存在 XSS 风险，需要配合 CSP 策略
- **用户体验**: 登录响应更快，但需要处理 token 过期和刷新逻辑
