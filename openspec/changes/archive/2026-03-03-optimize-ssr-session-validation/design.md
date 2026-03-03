## Context

### 当前架构问题

```
请求流程（每个页面）:
Browser → Nginx → SSR Node → [连接池] → Django API
                      │
                      ▼
               1. _layout loader 调用 auth/me (阻塞)
               2. 子页面 loader 开始
               3. 渲染页面
```

**瓶颈分析**：
- 每个 SSR 请求都要先调用 `auth/me`（约 50-100ms）
- 连接池有限：2 进程 × 50 连接 = 100 并发上限
- 高峰期请求排队，响应时间显著增加

### 现有认证机制

```
登录流程:
1. 用户提交用户名/密码
2. 后端返回 JWT access token + refresh token
3. 前端将 access token 存入 Session
4. 后续请求从 Session 读取 token，放入 Authorization header

Session 结构（当前）:
{
  accessToken: string,
  refreshToken: string
}
```

## Goals / Non-Goals

**Goals:**
- 减少 SSR 层对后端 API 的调用次数（每个请求节省 1 次 `auth/me` 调用）
- 降低连接池压力，提升并发处理能力
- 减少首屏加载延迟（目标：减少 50-100ms）
- 保持现有认证安全性，不引入新的安全风险

**Non-Goals:**
- 不改变 JWT 认证机制
- 不修改后端 API
- 不实现跨 Session 的用户信息共享（如多标签页同步）
- 不优化客户端（CSR）场景（本次专注于 SSR 层优化）

## Decisions

### 决策 1: Session 缓存用户信息

**方案**: 在 Session 中存储用户基本信息，避免每次都调用 `auth/me`

**Session 结构（优化后）**:
```typescript
{
  accessToken: string,
  refreshToken: string,
  user: {
    id: number,
    username: string,
    email: string,
    // 其他必要字段...
  },
  userCachedAt: number  // 缓存时间戳
}
```

**理由**:
- 简单有效：只需修改前端 Session 逻辑
- 无需后端改动：利用现有 Session 机制
- 性能提升明显：减少每请求的 API 调用

**备选方案**:
1. **Redis 缓存** - 需要后端配合，复杂度高
2. **客户端 localStorage** - 不适用于 SSR 场景
3. **JWT payload 存储用户信息** - 会增加 token 体积，每次请求都要传输

### 决策 2: 惰性验证 + TTL 过期

**方案**:
- 优先从 Session 读取用户信息
- 只在缓存不存在或过期时调用 `auth/me`
- TTL 设置为 15 分钟（与后端缓存策略一致）

**过期策略**:
```typescript
const USER_CACHE_TTL = 15 * 60 * 1000; // 15 分钟

function isUserCacheValid(session: Session): boolean {
  const cachedAt = session.get('userCachedAt');
  if (!cachedAt) return false;
  return Date.now() - cachedAt < USER_CACHE_TTL;
}
```

**理由**:
- 平衡性能和安全性：15 分钟足够长，能减少大量重复请求
- 与后端缓存策略一致，便于理解和维护
- TTL 过期后自动验证，无需担心数据过旧

### 决策 3: Token 过期时的处理

**方案**: 利用现有的 401 refresh 机制

**流程**:
```
请求 → Session 有用户信息? → 是 → 直接使用
                            → 否 → 调用 auth/me
                                     ↓
                              成功 → 缓存用户信息
                              失败 (401) → 尝试 refresh token
                                             ↓
                                      refresh 成功 → 重试 auth/me
                                      refresh 失败 → 重定向到登录页
```

**理由**:
- 不改变现有错误处理逻辑
- 兼容现有的 token 刷新机制
- 对用户透明，无感知

### 决策 4: 清除缓存的时机

**方案**: 在以下场景清除 Session 中的用户缓存：
1. 用户主动退出登录
2. Token refresh 失败
3. 用户修改密码
4. 用户信息更新（如个人资料页保存后）

**实现**:
```typescript
// 退出登录时
export const action = async ({ request }: Route.ActionArgs) => {
  const session = await getSession(request.headers.get('Cookie'));
  session.unset('user');
  session.unset('userCachedAt');
  // ... 其他退出逻辑
}

// 修改密码后
export const action = async ({ request }: Route.ActionArgs) => {
  // ... 修改密码逻辑
  session.unset('user');
  session.unset('userCachedAt');
}
```

**理由**:
- 保证数据一致性
- 避免使用过期的用户信息
- 简单直接，易于维护

## Risks / Trade-offs

### 风险 1: Session 中的用户信息可能过期

**场景**: 用户在其他设备修改了邮箱/密码，但当前设备的 Session 缓存仍是旧数据

**影响**: 中等 - 用户可能在短时间内看到旧的个人资料信息

**缓解措施**:
1. TTL 设置为 15 分钟，最多 15 分钟后会更新
2. 用户主动刷新页面会重新验证
3. 关键操作（如修改密码）后清除缓存

### 风险 2: Session 存储空间增加

**影响**: 低 - 用户信息约 200-500 bytes，对内存影响很小

**缓解措施**: 无需特殊处理，Session 本身已有大小限制

### 风险 3: 并发请求时可能多次调用 auth/me

**场景**: 用户打开多个标签页，同时触发多个 SSR 请求，都发现缓存过期

**影响**: 低 - 只是暂时的性能波动，不会影响正确性

**缓解措施**:
1. TTL 设置足够长（15 分钟），降低过期概率
2. 可在后续版本实现请求去重（使用 Promise 缓存）

### Trade-off: 性能 vs 实时性

**选择**: 优先性能，接受最多 15 分钟的数据延迟

**理由**:
- 用户信息变更频率很低（每天可能只改几次）
- 性能提升显著（每个请求减少 50-100ms）
- 15 分钟的延迟在大多数场景下可接受

## Migration Plan

### 阶段 1: 实现核心功能（不影响现有行为）

1. 修改 `sessions.server.ts`，支持存储用户信息
2. 修改 `_layout.tsx` loader，实现惰性验证逻辑
3. 修改 `auth.login.tsx` 和 `auth.register.tsx`，登录/注册后缓存用户信息

### 阶段 2: 添加缓存清除逻辑

1. 修改 `auth.logout.tsx`，退出时清除缓存
2. 修改 `_layout.profile.tsx`，修改密码后清除缓存

### 阶段 3: 测试和监控

1. 单元测试：Session 缓存逻辑
2. 集成测试：登录 → 访问页面 → 验证不调用 auth/me
3. 性能测试：对比优化前后的请求延迟

### 回滚策略

如果发现问题，可以快速回滚：
1. 移除 Session 中的 `user` 和 `userCachedAt` 字段
2. 恢复 `_layout.tsx` loader 为每次都调用 `auth/me`

由于不涉及后端改动，回滚风险极低。

## Open Questions

1. **TTL 时长是否合适？**
   - 当前选择 15 分钟，是否需要根据实际使用情况调整？
   - 建议：先上线 15 分钟，监控效果后再决定

2. **是否需要在客户端也缓存用户信息？**
   - 当前专注于 SSR 层优化
   - 建议：先完成 SSR 优化，观察效果后再考虑客户端优化

3. **是否需要实现请求去重？**
   - 当前设计下，并发请求可能重复调用 auth/me
   - 建议：作为后续优化，暂不实现