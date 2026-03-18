## Why

前端页面在访问后端数据时存在重复请求问题，导致不必要的网络开销和加载延迟。例如访问 `/profile` 页面时会发起两次 `auth/me` 请求，访问课程子页面时会重复请求课程详情数据。本变更旨在通过复用已加载数据减少重复请求，提升用户体验。

## What Changes

- 移除 `_layout.profile.tsx` 中独立的 `clientLoader`，改用 `useUser()` hook 复用父路由用户数据
- 减少页面加载时的重复 API 请求，提升性能

> **注意**：课程详情页的数据复用方案（Phase 2）由于与现有的无限滚动实现存在兼容性问题，已取消。保持现有的独立请求模式。

## Capabilities

### New Capabilities

- `data-request-reuse`: 定义前端路由间数据复用机制，包括 `useOutletContext` 的使用规范

### Modified Capabilities

- 无

## Impact

- **Affected Files**:
  - `frontend/web-student/app/routes/_layout.profile.tsx` - 移除独立请求，复用父路由用户数据
- **Dependencies**: React Router v7 (`useOutletContext`)
- **Performance**: 预计减少 `auth/me` 重复请求
