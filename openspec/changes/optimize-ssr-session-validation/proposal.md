## Why

当前 SSR 架构存在严重的并发瓶颈：每个页面请求都要先调用 `auth/me` API 验证用户身份，这不仅阻塞了后续请求，还占用了宝贵的连接池资源。高峰期请求在 SSR 层排队，导致响应变慢，用户体验下降。

**核心问题**：
- 2 个 PM2 实例 × 50 连接池 = 100 并发上限
- 每个请求都要调用 `auth/me`，增加约 50-100ms 延迟
- 高峰期请求排队，连接池耗尽

## What Changes

- **Session 缓存用户信息**：登录成功后，将用户基本信息存入 Session，后续请求直接从 Session 读取，避免每次都调用后端 API
- **惰性验证**：只在 Session 中没有用户信息时才调用 `auth/me`
- **Token 过期处理**：通过现有的 401 refresh 机制处理 token 过期场景
- **Session 过期策略**：设置合理的 Session TTL，平衡安全性和性能

## Capabilities

### New Capabilities

- `session-cached-auth`: Session 级别的用户信息缓存，减少 SSR 层对后端 API 的调用次数，提升并发处理能力

### Modified Capabilities

（无 - 这是一个性能优化，不改变现有的认证行为，只是减少了重复验证）

## Impact

**前端代码**：
- `app/routes/_layout.tsx` - 修改 loader，优先从 Session 读取用户信息
- `app/sessions.server.ts` - 扩展 Session 存储，支持用户信息缓存
- `app/routes/auth.login.tsx` - 登录成功后存储用户信息到 Session
- `app/routes/auth.register.tsx` - 注册成功后存储用户信息到 Session

**后端代码**：
- 无需修改（现有 `auth/me` API 保持不变）

**性能影响**：
- 每个 SSR 请求减少 1 次 API 调用
- 连接池压力降低约 30-50%（取决于页面复杂度）
- 首屏加载时间减少 50-100ms

**安全考虑**：
- Session 过期时间应与 JWT refresh token 一致
- 用户修改密码/退出登录时需要清除 Session 缓存