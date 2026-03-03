## Why

章节详情页当前使用 React Router 的流式渲染（Streaming SSR），但 Sidebar 组件中嵌套了 `<Await resolve={chapter}>`，导致 Sidebar 必须等待 chapter 数据加载完成后才能渲染。这破坏了流式渲染的并行优势，Sidebar 应该只需要章节列表（courseChapters）即可立即渲染。

## What Changes

- 修改 `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
- 移除 Sidebar 中嵌套的 `<Await resolve={chapter}>`
- 使用 `params.chapterId` 直接传递当前章节 ID 给 ChapterSidebar
- 验证 ChapterSidebar 组件能够正确地从 `initialData` 中找到当前章节高亮

## Capabilities

### New Capabilities
- 无新功能

### Modified Capabilities
- 无 spec-level 变更（仅 UI 渲染优化）

## Impact

- 前端文件：`frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
- 需验证 `ChapterSidebar` 组件的 `currentChapterId` prop 用法
- 性能提升：Sidebar 不再等待 chapter 数据，实现真正的并行流式渲染
