# session-cached-auth Specification

## Purpose
TBD - created by archiving change optimize-ssr-session-validation. Update Purpose after archive.
## Requirements
### Requirement: Session 存储用户信息

系统 SHALL 在用户登录或注册成功后，将用户基本信息存储在 Session 中，包括用户 ID、用户名、邮箱等必要字段，以及缓存时间戳。

#### Scenario: 登录成功后存储用户信息

- **WHEN** 用户成功登录
- **THEN** 系统 SHALL 将用户信息存入 Session
- **AND** Session 中 SHALL 包含 `user` 字段（用户基本信息）
- **AND** Session 中 SHALL 包含 `userCachedAt` 字段（缓存时间戳）

#### Scenario: 注册成功后存储用户信息

- **WHEN** 用户成功注册并自动登录
- **THEN** 系统 SHALL 将用户信息存入 Session
- **AND** Session 中 SHALL 包含 `user` 字段（用户基本信息）
- **AND** Session 中 SHALL 包含 `userCachedAt` 字段（缓存时间戳）

### Requirement: 惰性验证用户身份

系统 SHALL 在处理 SSR 请求时，优先从 Session 读取用户信息，只在缓存不存在或过期时才调用后端 `auth/me` API。

#### Scenario: Session 缓存有效时不调用后端 API

- **GIVEN** Session 中存在有效的用户缓存（未过期）
- **WHEN** SSR loader 处理页面请求
- **THEN** 系统 SHALL 直接从 Session 读取用户信息
- **AND** 系统 SHALL NOT 调用 `auth/me` API

#### Scenario: Session 缓存过期时调用后端 API

- **GIVEN** Session 中的用户缓存已过期（超过 15 分钟）
- **WHEN** SSR loader 处理页面请求
- **THEN** 系统 SHALL 调用 `auth/me` API 获取最新用户信息
- **AND** 系统 SHALL 更新 Session 中的用户缓存
- **AND** 系统 SHALL 更新 `userCachedAt` 时间戳

#### Scenario: Session 中无用户缓存时调用后端 API

- **GIVEN** Session 中不存在用户缓存
- **WHEN** SSR loader 处理页面请求
- **THEN** 系统 SHALL 调用 `auth/me` API 获取用户信息
- **AND** 系统 SHALL 将用户信息存入 Session

### Requirement: 用户缓存 TTL 过期策略

系统 SHALL 设置用户缓存的有效期为 15 分钟，超过此时间后缓存自动失效，需要重新验证。

#### Scenario: 缓存在 15 分钟内有效

- **GIVEN** 用户缓存在 14 分钟前创建
- **WHEN** SSR loader 检查缓存有效性
- **THEN** 系统 SHALL 认为缓存有效
- **AND** 系统 SHALL NOT 调用 `auth/me` API

#### Scenario: 缓存超过 15 分钟失效

- **GIVEN** 用户缓存在 16 分钟前创建
- **WHEN** SSR loader 检查缓存有效性
- **THEN** 系统 SHALL 认为缓存已失效
- **AND** 系统 SHALL 调用 `auth/me` API 重新验证

### Requirement: Token 过期时的处理

系统 SHALL 在 `auth/me` API 返回 401 错误时，使用现有的 refresh token 机制尝试刷新，刷新成功后更新 Session 缓存。

#### Scenario: Token 过期但 refresh 成功

- **GIVEN** Session 中的 access token 已过期
- **WHEN** 调用 `auth/me` API 返回 401 错误
- **THEN** 系统 SHALL 使用 refresh token 刷新
- **AND** 刷新成功后 SHALL 重试 `auth/me` API
- **AND** 系统 SHALL 更新 Session 中的用户缓存和 access token

#### Scenario: Token 和 refresh token 都过期

- **GIVEN** Session 中的 access token 和 refresh token 都已过期
- **WHEN** 尝试 refresh token 失败
- **THEN** 系统 SHALL 清除 Session 中的用户缓存
- **AND** 系统 SHALL 重定向用户到登录页面

### Requirement: 清除用户缓存的时机

系统 SHALL 在特定场景下清除 Session 中的用户缓存，确保数据一致性。

#### Scenario: 用户退出登录时清除缓存

- **WHEN** 用户主动退出登录
- **THEN** 系统 SHALL 清除 Session 中的 `user` 字段
- **AND** 系统 SHALL 清除 Session 中的 `userCachedAt` 字段

#### Scenario: 用户修改密码后清除缓存

- **WHEN** 用户成功修改密码
- **THEN** 系统 SHALL 清除 Session 中的 `user` 字段
- **AND** 系统 SHALL 清除 Session 中的 `userCachedAt` 字段

#### Scenario: 用户更新个人信息后清除缓存

- **WHEN** 用户成功更新个人信息（如邮箱、用户名）
- **THEN** 系统 SHALL 清除 Session 中的 `user` 字段
- **AND** 系统 SHALL 清除 Session 中的 `userCachedAt` 字段
- **AND** 下次请求时 SHALL 重新获取最新的用户信息

### Requirement: Session 数据结构

系统 SHALL 使用以下数据结构存储用户缓存：

```typescript
{
  accessToken: string,           // JWT access token
  refreshToken: string,          // JWT refresh token
  user: {                        // 用户信息缓存
    id: number,
    username: string,
    email: string,
    // 其他必要字段...
  },
  userCachedAt: number          // 缓存时间戳（毫秒）
}
```

#### Scenario: Session 数据结构正确

- **WHEN** 用户登录成功后
- **THEN** Session SHALL 包含 `accessToken` 字段
- **AND** Session SHALL 包含 `refreshToken` 字段
- **AND** Session SHALL 包含 `user` 字段（对象）
- **AND** Session SHALL 包含 `userCachedAt` 字段（数字）

### Requirement: 性能提升目标

系统 SHALL 通过 Session 缓存机制，显著减少 SSR 层对后端 API 的调用次数和请求延迟。

#### Scenario: 减少 API 调用次数

- **GIVEN** 用户已登录且 Session 缓存有效
- **WHEN** 用户访问任意页面
- **THEN** 系统 SHALL NOT 调用 `auth/me` API
- **AND** 每个页面请求 SHALL 比优化前减少至少 1 次 API 调用

#### Scenario: 减少请求延迟

- **GIVEN** 用户已登录且 Session 缓存有效
- **WHEN** 测量 SSR 请求的总延迟
- **THEN** 请求延迟 SHALL 比优化前减少 50-100ms
- **AND** 连接池压力 SHALL 显著降低

