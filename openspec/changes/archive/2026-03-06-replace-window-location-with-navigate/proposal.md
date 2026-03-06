## Why

前端代码中存在多处使用 `window.location` 进行导航，这会导致页面整体刷新而非 SPA 导航，影响用户体验并违背 React Router v7 的设计理念。项目中已经大量使用 `useNavigate` hook (42处)，需要统一内部导航方式。

## What Changes

- 将组件内的 `window.location.href = '/courses'` 改为 `navigate('/courses')`
- 将 `window.location.href = '/auth/login'` (HTTP 拦截器) 保持不变（非组件上下文）
- 将 5 处 `window.location.reload()` 改为 `router.revalidate()` 实现 SPA 刷新
- 支付回调等外部 URL 跳转保持 `window.location.href`

## Capabilities

### New Capabilities
- 前端导航统一: 前端路由导航统一使用 React Router 的 useNavigate，实现真正的 SPA 体验

### Modified Capabilities
- (无需求变更，仅实现层面修改)

## Impact

- 影响文件:
  - `frontend/web-student/app/routes/_layout.courses_.$courseId/route.tsx`
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters/route.tsx`
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
  - `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx`
  - `frontend/web-student/app/routes/_layout.problems.tsx`
  - `frontend/web-student/app/routes/payment.pay.tsx`
  - `frontend/web-student/app/components/CheckoutModal.tsx`
- 无 API 变更
- 无数据库变更