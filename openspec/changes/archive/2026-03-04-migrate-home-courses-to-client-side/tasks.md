## 1. 首页迁移 (_layout.home.tsx)

- [x] 1.1 移除 `loader` 函数和 `withAuth` 装饰器
- [x] 1.2 删除服务端导入: `createHttp`, `withAuth`, `AxiosError`
- [x] 1.3 添加客户端导入: `clientHttp`, `useState`, `useEffect`, `useNavigate`
- [x] 1.4 实现 `useEffect` 数据获取（enrollments + unfinished_problems）
- [x] 1.5 添加 loading 和 error 状态处理
- [x] 1.6 处理 401 跳转登录
- [x] 1.7 运行 `pnpm run typecheck` 验证类型

## 2. 课程列表迁移 (_layout.courses/route.tsx)

- [x] 2.1 移除 `loader` 函数和 `withAuth` 装饰器
- [x] 2.2 删除服务端导入
- [x] 2.3 添加客户端导入: `clientHttp`, `useSearchParams`
- [x] 2.4 实现 `useEffect` 数据获取，监听分页参数变化
- [x] 2.5 添加 loading 和 error 状态处理
- [x] 2.6 运行 `pnpm run typecheck` 验证类型

## 3. 课程详情迁移 (_layout.courses_.$courseId/route.tsx)

- [x] 3.1 移除 `loader` 函数
- [x] 3.2 移除 `action` 函数（报名功能）
- [x] 3.3 删除服务端导入
- [x] 3.4 添加客户端导入: `clientHttp`, `useState`, `useEffect`, `useNavigate`, `useParams`
- [x] 3.5 实现 `useEffect` 数据获取（course + enrollment）
- [x] 3.6 改造报名按钮：从 `useSubmit` 改为 `clientHttp.post()` + 状态更新
- [x] 3.7 添加 loading、enrolling 和 error 状态处理
- [x] 3.8 运行 `pnpm run typecheck` 验证类型

## 4. 验证测试

- [ ] 4.1 登录后访问首页，验证数据加载正常
- [ ] 4.2 登录后访问课程列表，验证分页正常
- [ ] 4.3 登录后访问课程详情，验证课程信息显示正常
- [ ] 4.4 测试课程报名功能
- [ ] 4.5 测试 Token 过期自动刷新
- [ ] 4.6 登出功能验证（使用 `/auth/logout`）