## Why

当前 `/problems` 页面（及所有需要认证的页面）的服务端渲染时间过长（~692ms）。原因是在 SSR 阶段，`_layout.tsx` 的 loader 会调用后端 `auth/me` API 获取用户信息，即使页面已经迁移到 clientLoader，服务端仍会执行数据获取逻辑。迁移 `_layout.tsx` 到 clientLoader 可以将用户信息获取移到客户端 hydration 后执行，减少服务端渲染时的阻塞等待。

## What Changes

- 将 `_layout.tsx` 的服务端 `loader` 改为仅做 session 检查
- 添加 `clientLoader` 处理用户信息获取和缓存逻辑
- 保留 session 缓存机制：在服务端检查缓存有效性，返回给客户端
- 客户端检测到需要刷新时，调用 `auth/me` 并通过 `auth.set-session` 写入 session
- 效果：服务端不再调用 `auth/me` API，减少 SSR 阶段的 API 等待时间

## Capabilities

### New Capabilities
- `client-auth-refresh`: 客户端负责在 hydration 时检查用户缓存有效性，必要时调用 auth/me 并刷新 session

### Modified Capabilities
- (无需求变更)

## Impact

- **代码影响**: `frontend/web-student/app/routes/_layout.tsx`
- **依赖**: `auth.set-session.tsx` action 保持不变
- **行为变化**: 服务端渲染时不再调用后端 API，仅检查 session