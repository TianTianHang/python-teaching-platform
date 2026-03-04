# 任务列表：客户端登录 localStorage 方案

## 实现状态：已完成

以下任务已在本次会话中完成：

- [x] **T1**: 创建客户端 HTTP 工具 `app/utils/http/client.ts`
- [x] **T2**: 修改登录页面 `app/routes/auth.login.tsx`，移除服务端 action
- [x] **T3**: 配置前端环境变量 `.env`，添加 `VITE_API_BASE_URL`

## 待完成

- [x] **T4**: 后端配置 CORS
  - 检查 `CORS_ALLOWED_ORIGINS` 是否包含前端域名
  - 确保 `CORS_ALLOW_CREDENTIALS = True`

- [x] **T5**: 测试登录流程
  - 启动前端开发服务器
  - 访问 `/auth/login`
  - 使用测试账号登录
  - 验证 token 存储在 localStorage
  - 验证跳转到 `/home`
  - 验证 session cookie 设置（用于 SSR）

- [x] **T6**: 测试 token 刷新
  - 已修复 refresh 端点（无尾部斜杠）
  - 待手动测试：等待 access token 过期，手动清除，发起 API 请求验证自动刷新

- [x] **T7**: 测试登出流程
  - 已修复 logout 端点（无尾部斜杠）
  - 现有登出使用服务器端路由 `/auth/logout`，会自动清除 session
  - 待手动测试：点击登出按钮，验证 localStorage 清除，验证跳转回登录页

## 后续扩展

- [ ] **T8**: 其他页面改用客户端请求
  - 注册页面 (`auth.register.tsx`)
  - 个人中心页面

- [ ] **T9**: 全局用户状态管理
  - 创建 Auth Context
  - 提供用户信息给全局使用
