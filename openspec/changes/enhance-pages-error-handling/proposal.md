## Why

当前平台各页面的错误处理机制不一致，部分页面完全缺少 ErrorBoundary，导致 API 失败时用户体验很差。例如：
- 课程详情页使用 `Promise.all`，如果报名信息 API 失败，用户连课程基本信息都看不到
- 个人资料页完全没有 ErrorBoundary，API 失败时显示空白或原始错误
- 题目列表页的错误 UI 很基础，缺少友好的中文提示和重试功能
- 会员页使用 SSR 但没有错误处理

这些问题影响用户体验和平台的专业性。现在首页已经实现了良好的错误处理模式，应该推广到其他页面。

## What Changes

- **课程详情页** (`_layout.courses_.$courseId/route.tsx`)
  - 将 `Promise.all` 改为 `Promise.allSettled`，实现课程信息和报名信息的独立错误处理
  - 添加 ErrorCard 组件用于显示错误
  - 允许用户在报名信息加载失败时仍能看到课程详情

- **题目列表页** (`_layout.problems.tsx`)
  - 将基础 ErrorBoundary 替换为 ErrorCard 组件
  - 添加基于状态码的友好中文错误消息
  - 添加重试功能

- **个人资料页** (`_layout.profile.tsx`)
  - 添加 ErrorBoundary（当前缺失）
  - 使用 ErrorCard 显示加载失败
  - 保持现有的操作级错误通知（密码修改、资料更新）

- **会员页** (`_layout.membership.tsx`)
  - 添加 ErrorBoundary 用于处理客户端导航错误
  - 改进 loader 的错误处理

- **可复用组件**
  - 考虑提取通用的错误处理模式或 wrapper 组件
  - 统一错误处理 API

## Capabilities

### New Capabilities
- `graceful-error-handling`: 为页面级数据加载提供优雅的错误处理，包括独立错误状态、友好提示和重试功能

### Modified Capabilities
- 无（仅改进错误处理 UI 和用户体验，不改变功能需求）

## Impact

**影响的页面：**
- `frontend/web-student/app/routes/_layout.courses_.$courseId/route.tsx`
- `frontend/web-student/app/routes/_layout.problems.tsx`
- `frontend/web-student/app/routes/_layout.profile.tsx`
- `frontend/web-student/app/routes/_layout.membership.tsx`

**复用的组件：**
- `frontend/web-student/app/components/ErrorCard.tsx`（已存在）

**技术影响：**
- 不涉及后端 API 变更
- 不涉及数据库变更
- 纯前端 UX 改进
- 保持与现有错误处理模式一致（基于首页优化的经验）

**用户体验改进：**
- 减少因部分 API 失败导致的完全不可用情况
- 提供更友好的错误提示（中文、基于状态码）
- 支持用户主动重试失败的操作
