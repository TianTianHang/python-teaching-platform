## 1. Home 页面迁移

- [x] 1.1 添加 clientLoader 到 _layout.home.tsx（获取 enrollments 和 problem-progress）
- [x] 1.2 添加 clientLoader.hydrate = true
- [x] 1.3 添加 errorElement 处理错误
- [x] 1.4 移除 useEffect 和相关 state（enrolledCourses, unfinishedProblems, loading）
- [x] 1.5 使用 useLoaderData() 获取数据

## 2. Courses 列表页迁移

- [x] 2.1 添加 clientLoader 到 _layout.courses/route.tsx（获取课程列表）
- [x] 2.2 添加 clientLoader.hydrate = true
- [x] 2.3 添加 errorElement 处理错误
- [x] 2.4 移除 useEffect 和相关 state（courses, loading）
- [x] 2.5 使用 useLoaderData() 获取数据

## 3. Course Detail 页迁移

- [x] 3.1 添加 clientLoader 到 _layout.courses_.$courseId/route.tsx（获取 course 和 enrollment）
- [x] 3.2 添加 clientLoader.hydrate = true
- [x] 3.3 添加 errorElement 处理错误
- [x] 3.4 移除 useEffect 和相关 state（course, enrollment, loading）
- [x] 3.5 使用 useLoaderData() 获取数据

## 4. 验证

- [x] 4.1 运行 typecheck: pnpm run typecheck（frontend/web-student 目录）
- [x] 4.2 测试 home 页面加载正常
- [x] 4.3 测试 courses 列表页加载正常
- [x] 4.4 测试 course 详情页加载正常
- [x] 4.5 测试登录后页面跳转正常