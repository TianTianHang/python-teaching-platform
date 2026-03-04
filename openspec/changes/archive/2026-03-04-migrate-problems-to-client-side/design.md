## Context

Problems 模块当前使用 SSR (Server-Side Rendering) 模式，通过 loader 在服务器端获取数据并渲染页面。这与已迁移的 Home、Courses 模块不一致。

**当前架构**:
- `loader` → 服务器端使用 session 验证 + `createHttp(request)` 调用后端 API
- 页面内容在服务器端渲染完成

**目标架构**:
- 移除 loader，使用 `useEffect` + `clientHttp` 在客户端获取数据
- 客户端使用 localStorage 中的 JWT token 进行认证

## Goals / Non-Goals

**Goals:**
- 将 Problems 模块所有页面迁移到客户端渲染模式
- 保持现有 UI 和功能不变
- 与 Home、Courses 模块保持架构一致性

**Non-Goals:**
- 不添加新功能
- 不修改后端 API
- 不迁移其他模块（如 threads, exams）

## Decisions

### 1. 迁移模式: Full Client-Side (useEffect)

**选择**: 完全使用客户端 useEffect 获取数据（与 Home、Courses 相同）

**备选方案**:
- Hybrid 模式 (loader + clientLoader): 已用于 profile, problems 列表页
- 纯客户端 (skip loader): 最简单但无 SSR 优势

**理由**: 
- 与已完成的 Home/Courses 模块保持一致
- 避免服务器端 session 验证开销
- 复用已有的 `clientHttp` 工具（处理 JWT token 和 401 自动刷新）

### 2. 错误处理策略

使用与 Home 页面相同的错误处理模式：
- 401 错误 → 跳转到登录页
- 其他错误 → 显示错误状态，保留重试能力

### 3. 加载状态

- 初始显示 Skeleton 组件（与 SSR 的 HydrateFallback 一致）
- 数据加载完成后替换为实际内容

## Risks / Trade-offs

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 首屏加载时间增加 | 用户需等待 JS 执行 + API 请求 | 数据量小，影响有限 |
| 无 SEO | 题目内容不包含在初始 HTML | Problems 页面需要登录，无 SEO 需求 |
| 首次访问闪烁 | 先显示 Skeleton 再显示内容 | 与当前 SSR+HydrateFallback 行为一致 |

## Migration Plan

1. 按顺序迁移各页面：
   - `_layout.problems.tsx` (题目列表)
   - `problems.$problemId/route.tsx` (题目详情)
   - 其他子页面
2. 每迁移一个页面，运行 `pnpm run typecheck` 验证
3. 手动验证功能正常

## Open Questions

- 是否需要为每个子页面（如 submissions, check）单独创建 Skeleton 组件？
  - 初步判断：可以复用现有的或创建简单的占位组件