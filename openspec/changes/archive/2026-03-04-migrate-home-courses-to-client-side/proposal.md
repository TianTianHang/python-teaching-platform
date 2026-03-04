## Why

当前项目首页、课程列表和课程详情页面使用服务端代理模式（SSR loader）调用后端 API。根据之前的 `client-side-backend-migration-guide` 规范，需要将这些页面迁移到客户端直连模式，以提升用户体验并减少服务端负担。

登录页面已完成迁移，本迁移是规范化工作的延续。

## What Changes

- **首页** (`_layout.home.tsx`): 移除服务端 loader，改为 `useEffect` + `clientHttp` 获取 enrollments 和未完成题目
- **课程列表** (`_layout.courses/route.tsx`): 移除服务端 loader，改为客户端获取课程列表数据
- **课程详情** (`_layout.courses_.$courseId/route.tsx`): 移除服务端 loader 和 action，改为客户端获取课程详情 + 报名功能

## Capabilities

### New Capabilities
（无新功能引入，属于现有功能的实现方式迁移）

### Modified Capabilities
（无需求变更，仅实现方式改变）

## Impact

**受影响代码**:
- `frontend/web-student/app/routes/_layout.home.tsx`
- `frontend/web-student/app/routes/_layout.courses/route.tsx`
- `frontend/web-student/app/routes/_layout.courses_.$courseId/route.tsx`

**依赖变更**:
- 移除: `createHttp` (服务端), `withAuth` (服务端认证封装)
- 新增: `clientHttp` (客户端 HTTP 客户端)

**环境要求**:
- `.env` 已配置 `VITE_API_BASE_URL`
- 后端 CORS 已允许前端域名