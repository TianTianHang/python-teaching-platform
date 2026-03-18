## 1. Profile 页面优化

- [x] 1.1 修改 `_layout.profile.tsx`，移除 `clientLoader` 函数和 `clientLoader.hydrate` 声明
- [x] 1.2 在 `_layout.profile.tsx` 中导入 `useUser` hook
- [x] 1.3 修改 `ProfilePage` 组件使用 `useUser()` 获取用户数据，移除 `loaderData` 参数
- [x] 1.4 添加 `user === null` 检查，显示 `SkeletonProfile` 加载状态
- [x] 1.5 简化 `ErrorBoundary` 组件（移除独立的 loader 错误处理）
- [x] 1.6 清理未使用的导入（`clientHttp`、`redirect`、`Route.ClientLoaderArgs` 等）

## 2. 课程数据复用（已取消）

> **取消原因**：该方案与现有的 `useInfiniteScroll` 实现存在兼容性问题。父路由预取的章节列表数据格式（`{ results: [], count: 0 }`）缺少 `next` 字段，导致无限滚动钩子误判 `hasMore` 为 `true`，引发无限加载 bug。保持现有独立请求模式。

- [ ] ~~2.1 修改 `_layout.courses_.$courseId/route.tsx` 的 `clientLoader`，预取章节列表数据~~
- [ ] ~~2.2 在 `exams.tsx` 中移除独立的课程数据请求，改用 `useRouteLoaderData`~~
- [ ] ~~2.3 在 `chapters/route.tsx` 中移除独立的课程数据请求，改用 `useRouteLoaderData`~~
- [ ] ~~2.4 在 `chapters/$chapterId/route.tsx` 中移除 `courseChapters` 请求，改用 `useRouteLoaderData`~~
- [ ] ~~2.5 为各子路由添加 `useRouteLoaderData` 返回值为 `undefined` 的降级处理~~

## 3. 验证与测试

- [ ] 3.1 访问 `/profile` 页面，使用 Chrome DevTools 验证 `auth/me` 请求只有 1 次
- [ ] 3.2 访问 `/courses/:id/exams` 页面，验证 `Course` 数据请求只有 1 次
- [ ] 3.3 访问 `/courses/:id/chapters/:id` 页面，验证 `courseChapters` 请求只有 1 次
- [ ] 3.4 测试直接从 URL 访问子路由（刷新页面）的场景
- [x] 3.5 运行 `pnpm run typecheck` 确保 TypeScript 类型检查通过
