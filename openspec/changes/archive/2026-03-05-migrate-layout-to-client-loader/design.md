## Context

当前 `_layout.tsx` 使用服务端 `loader` 获取用户信息：
1. 检查 session.isAuthenticated
2. 检查 session 缓存有效性 (getUserCache + isUserCacheValid)
3. 缓存无效时调用 auth/me API
4. 返回用户信息

问题：即使页面已迁移到 clientLoader，SSR 阶段仍会执行 loader，导致服务端需要等待 API 响应。

## Goals / Non-Goals

**Goals:**
- 将用户信息获取从服务端移到客户端
- 保留 session 缓存机制减少 API 调用
- 减少 SSR 阶段的阻塞时间

**Non-Goals:**
- 不修改 auth.set-session.tsx 的现有逻辑
- 不修改其他使用 withAuth 的路由

## Decisions

### 方案：分离服务端和客户端职责

**决定：服务端 loader 只做 session 检查，不调用 API**

| 组件 | 职责 |
|------|------|
| 服务端 loader | 检查 session.isAuthenticated，返回缓存用户信息或标记 needsRefresh |
| 客户端 clientLoader | 检查服务端返回，若 needsRefresh=true，调用 auth/me 并 set-session |

**替代方案考虑：**
- 方案 A：完全移除服务端 loader → 但会导致未认证用户看到短暂的白屏
- 方案 B：服务端仍调用 API，但返回更快 → 没有解决核心问题

### 数据结构设计

```
服务端返回:
{
  user: User | null,           // session 缓存中的用户
  hasUser: boolean,            // 是否有用户信息
  needsRefresh: boolean        // 缓存是否过期需要刷新
}

客户端行为:
- hasUser=true → 直接使用
- needsRefresh=true → 背景调用 auth/me → auth.set-session → 更新
```

## Risks / Trade-offs

- [风险] 客户端首次加载时会多一次 API 调用 → 收益：服务端渲染更快
- [风险] 用户信息延迟加载可能导致闪烁 → 已有 HydrateFallback 处理