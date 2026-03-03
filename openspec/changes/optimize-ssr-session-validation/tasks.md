## 1. Session 存储扩展

- [x] 1.1 修改 `app/sessions.server.ts`，扩展 Session 数据结构，支持 `user` 和 `userCachedAt` 字段
- [x] 1.2 添加 Session 类型定义，确保 TypeScript 类型安全
- [x] 1.3 实现 `setUserCache(session, user)` 辅助函数，用于存储用户缓存
- [x] 1.4 实现 `getUserCache(session)` 辅助函数，用于读取用户缓存
- [x] 1.5 实现 `isUserCacheValid(session)` 辅助函数，检查缓存是否在 15 分钟 TTL 内

## 2. 登录和注册流程修改

- [x] 2.1 修改 `app/routes/auth.login.tsx`，登录成功后调用 `setUserCache` 存储用户信息
- [x] 2.2 修改 `app/routes/auth.register.tsx`，注册成功后调用 `setUserCache` 存储用户信息
- [x] 2.3 验证登录和注册后的 Session 数据结构正确

## 3. _layout loader 惰性验证实现

- [x] 3.1 修改 `app/routes/_layout.tsx` loader，优先从 Session 读取用户信息
- [x] 3.2 实现缓存过期逻辑：如果 `!isUserCacheValid(session)`，调用 `auth/me` API
- [x] 3.3 调用 `auth/me` 成功后，更新 Session 缓存（`setUserCache`）
- [x] 3.4 处理 `auth/me` 返回 401 的情况：尝试 refresh token
- [x] 3.5 refresh token 成功后，重试 `auth/me` 并更新缓存
- [x] 3.6 refresh token 失败后，清除缓存并重定向到登录页

## 4. 缓存清除逻辑

- [x] 4.1 修改 `app/routes/auth.logout.tsx` action，退出时调用 `clearUserCache(session)`
- [x] 4.2 修改 `app/routes/_layout.profile.tsx` action，修改密码成功后清除用户缓存
- [x] 4.3 修改 `app/routes/_layout.profile.tsx` action，更新个人信息成功后清除用户缓存
- [x] 4.4 实现 `clearUserCache(session)` 辅助函数，清除 `user` 和 `userCachedAt` 字段

## 5. 类型定义和辅助函数

- [x] 5.1 在 `app/types/user.ts` 中定义 `CachedUser` 类型（包含 id, username, email 等字段）
- [x] 5.2 在 `app/sessions.server.ts` 中导出所有辅助函数
- [x] 5.3 确保所有辅助函数有完整的 TypeScript 类型注解

## 6. 测试

- [ ] 6.1 编写单元测试：`setUserCache` 和 `getUserCache` 函数
- [ ] 6.2 编写单元测试：`isUserCacheValid` 函数（测试 TTL 过期逻辑）
- [ ] 6.3 编写集成测试：登录后访问页面，验证不调用 `auth/me` API
- [ ] 6.4 编写集成测试：缓存过期后访问页面，验证调用 `auth/me` API
- [ ] 6.5 编写集成测试：退出登录后访问页面，验证需要重新验证
- [x] 6.6 运行所有前端类型检查：`pnpm run typecheck`

## 7. 性能验证

- [ ] 7.1 使用 Chrome DevTools 测量优化前后的首屏加载时间（需要在生产/测试环境手动验证）
- [ ] 7.2 监控 SSR 层连接池使用率变化（需要在生产/测试环境手动验证）
- [ ] 7.3 验证每个请求减少 1 次 `auth/me` API 调用（需要在生产/测试环境手动验证）
- [ ] 7.4 确认请求延迟减少 50-100ms（需要在生产/测试环境手动验证）

## 8. 文档和清理

- [x] 8.1 更新 `app/sessions.server.ts` 顶部注释，说明新增的用户缓存功能
- [x] 8.2 清理调试代码和 console.log
- [ ] 8.3 确保 ESLint 检查通过：`pnpm run lint`（注：ESLint 配置有问题，需要单独修复）