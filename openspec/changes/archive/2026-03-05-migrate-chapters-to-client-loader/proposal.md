## Why

章节相关页面（列表、详情、locked 页）目前仍使用服务端 loader，导致：
- **客户端导航较慢**：每次导航都需要服务器渲染，无法利用客户端路由优势
- **服务器负担重**：SSR 计算成本高，尤其是高访问量的章节页面
- **缓存策略受限**：服务端缓存无法利用浏览器本地缓存
- **架构不一致**：其他高频页面（首页、题目列表、课程列表）已迁移到客户端，章节页面成为架构短板

同时，这些页面的认证逻辑依赖 `withAuth` 包装器和服务端 session，阻碍了完全客户端化的实现。

**现在进行迁移的时机已经成熟**：其他核心页面已完成客户端化，积累了成熟的经验和模式。

## What Changes

将所有章节相关页面从服务端 loader 迁移到客户端 loader + hydrate：

### 页面迁移
- **章节列表页** (`_layout.courses_.$courseId_.chapters/route.tsx`)
  - 移除 `withAuth` 包装器
  - 替换 `loader` → `clientLoader` + `hydrate = true`
  - 使用 `clientHttp` 替代 `createHttp(request)`
  - 添加 `HydrateFallback` 和 `ErrorBoundary`

- **章节详情页** (`_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`)
  - 保持现有的 `clientAction`（已是客户端）
  - 替换 `loader` → `clientLoader` + `hydrate = true`
  - 在 clientLoader 中检查 `unlock_status`，返回状态信息
  - 在组件中根据状态进行客户端重定向到 locked 页
  - 移除服务端条件重定向逻辑
  - 使用 `clientHttp` 替代 `createHttp(request)`
  - 保留副作用逻辑（标记章节为进行中）

- **章节 locked 页** (`_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx`)
  - 迁移到 `clientLoader` + `hydrate = true`
  - 使用 `clientHttp` 进行 API 调用

### 认证机制重构
- **移除 `withAuth` 包装器依赖**：章节页面不再依赖服务端认证
- **完全客户端认证**：使用 `clientHttp` + JWT token（从 localStorage 或 cookie 获取）
- **认证失败处理**：在 clientLoader 中捕获 401 错误，使用 `redirect()` 重定向到登录页

### 保留服务端的场景
- **session 设置**：登录/注册时的 `/auth/set-session` 端点保持服务端（需要设置 HTTP-only cookies）
- **其他认证相关**：auth.register.tsx, auth.set-session.tsx 等保持服务端

## Capabilities

### New Capabilities
- **client-side-chapter-auth**: 客户端章节认证和权限检查能力，包括：
  - 使用 JWT token 进行客户端认证
  - 在 clientLoader 中检查章节解锁状态
  - 客户端重定向逻辑（基于权限状态）
  - 错误处理和认证失败重定向

### Modified Capabilities
无（现有功能的行为保持不变，只是实现从服务端迁移到客户端）

## Impact

### Affected Code
- **Frontend Routes**:
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters/route.tsx`
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx`

- **Utilities**:
  - 可能需要增强 `~/utils/http/client.ts` 以支持更多错误处理场景
  - 可能需要添加客户端认证辅助函数（从 localStorage/cookie 获取 token）

### API Changes
- **无 API 变更**：后端 API 保持不变，只是调用方从服务端改为客户端

### Dependencies
- **无新增依赖**：使用现有的 `clientHttp` 和 React Router v7 的客户端特性

### Performance Impact
- **正向影响**：
  - 客户端导航速度提升（无需 SSR）
  - 服务器负载降低
  - 更好的缓存利用

- **潜在风险**：
  - 首次访问可能稍慢（需要客户端渲染）
  - 通过 `hydrate = true` 缓解（SSR 首次，客户端导航后续）

### Testing Requirements
- 章节列表页的认证和未认证状态
- 章节详情页的解锁/锁定状态重定向
- 客户端导航的性能测试
- 错误处理（401、403、404 等）
