## ADDED Requirements

### Requirement: Profile 页面复用父路由用户数据

系统应当支持 Profile 页面通过 `useUser()` hook 复用父路由 `_layout.tsx` 提供的用户数据，避免重复请求 `auth/me` 接口。

#### Scenario: Profile 页面成功复用用户数据
- **WHEN** 用户访问 `/profile` 页面
- **WHEN** 父路由 `_layout.tsx` 已成功加载用户数据并通过 `Outlet context` 传递
- **THEN** Profile 页面通过 `useUser()` hook 获取用户数据
- **THEN** 不发起新的 `auth/me` 请求

#### Scenario: 父路由用户数据未加载完成
- **WHEN** 用户直接访问 `/profile` 页面（刷新或直接链接）
- **WHEN** 父路由 `_layout.tsx` 的用户数据尚未加载完成
- **THEN** `useUser()` 返回 `null`
- **THEN** Profile 页面显示 `SkeletonProfile` 加载状态
- **THEN** 等待父路由数据加载完成后重新渲染

#### Scenario: 用户数据为空时重定向
- **WHEN** `useUser()` 返回 `null` 且确认用户未认证
- **THEN** 页面重定向到 `/auth/login`

### Requirement: 课程子路由复用父路由课程数据

系统应当支持课程子路由（exams、chapters、chapter detail）通过 `useRouteLoaderData` 复用父路由 `_layout.courses_.$courseId` 提供的课程数据。

#### Scenario: Exams 页面复用课程数据
- **WHEN** 用户访问 `/courses/:courseId/exams` 页面
- **WHEN** 父路由 `clientLoader` 已加载课程数据
- **THEN** Exams 页面通过 `useRouteLoaderData('routes/_layout.courses_.$courseId')` 获取课程数据
- **THEN** Exams 页面不发起独立的 `GET /courses/:courseId` 请求

#### Scenario: Chapters 页面复用课程数据
- **WHEN** 用户访问 `/courses/:courseId/chapters` 页面
- **WHEN** 父路由 `clientLoader` 已加载课程数据
- **THEN** Chapters 页面通过 `useRouteLoaderData` 获取课程数据
- **THEN** Chapters 页面不发起独立的 `GET /courses/:courseId` 请求

#### Scenario: Chapter Detail 页面复用章节列表
- **WHEN** 用户访问 `/courses/:courseId/chapters/:chapterId` 页面
- **WHEN** 父路由 `clientLoader` 已加载章节列表数据
- **THEN** Chapter Detail 页面通过 `useRouteLoaderData` 获取章节列表用于 sidebar 导航
- **THEN** Chapter Detail 页面不发起独立的 `GET /courses/:courseId/chapters` 请求

#### Scenario: 父路由数据未加载完成
- **WHEN** 用户直接访问子路由页面
- **WHEN** 父路由数据尚未加载完成
- **THEN** `useRouteLoaderData` 返回 `undefined`
- **THEN** 子路由显示加载状态或降级到本地请求

### Requirement: 数据复用 API 使用规范

系统应当提供统一的数据复用 API 使用规范，确保开发者正确使用 `useUser()` 和 `useRouteLoaderData`。

#### Scenario: useUser hook 使用
- **WHEN** 子路由需要获取用户数据
- **THEN** 使用 `import { useUser } from '~/hooks/userUser'`
- **THEN** 调用 `const { user } = useUser()` 获取数据
- **THEN** 处理 `user === null` 的情况

#### Scenario: useRouteLoaderData 使用
- **WHEN** 子路由需要复用父路由数据
- **THEN** 使用正确的 route ID 格式（如 `routes/_layout.courses_.$courseId`）
- **THEN** 处理返回值为 `undefined` 的情况
- **THEN** 使用 TypeScript 类型推导确保类型安全

#### Scenario: 错误处理
- **WHEN** 父路由数据加载失败
- **THEN** 子路由通过 `useRouteLoaderData` 获取的值为 `undefined` 或包含错误信息
- **THEN** 子路由显示适当的错误提示或降级处理
