# 设计方案：客户端登录 localStorage 方案

## 概述

将登录流程从服务端 action 转发改为客户端直连 API，使用 localStorage 存储 JWT token。

## 架构设计

### 当前架构
```
浏览器 → React Router Action (服务端) → Django API
           ↓
      Session Cookie 存储 token
```

### 目标架构
```
浏览器 → Django API (直连，配置 CORS)
           ↓
    localStorage 存储 token
```

## 实现细节

### 1. 客户端 HTTP 工具 (`app/utils/http/client.ts`)

- **Token 存储**: 使用 `localStorage` 存储 `{ access, refresh }` 对象
- **Base URL**: 优先使用 `VITE_API_BASE_URL`，回退到 `/api/v1`
- **Axios 实例**: 创建带拦截器的 axios 实例
  - 请求拦截器：自动添加 `Authorization: Bearer <token>`
  - 响应拦截器：处理 401 自动刷新 token

### 2. Auth 工具 (`clientAuth`)

| 方法 | 说明 |
|-----|------|
| `login(username, password)` | 调用 `/auth/login/` API，存储 token，获取用户信息 |
| `logout()` | 调用 `/auth/logout/` API，清除 localStorage token |
| `getToken()` | 获取当前存储的 token |
| `setToken(token)` | 手动设置 token |
| `clearToken()` | 清除 token |
| `isAuthenticated()` | 检查是否已登录 |

### 3. Token 自动刷新机制

```
请求 → 401 响应 → 检查 refresh token → 调用 /auth/refresh/ 
    → 更新 localStorage → 重试原请求 → 成功继续，失败跳转登录
```

### 4. 登录页面改造 (`app/routes/auth.login.tsx`)

- **移除** 服务端 `action` 函数
- **新增** 客户端 `handleSubmit` 使用 `clientAuth.login()`
- **使用** `useNavigate` 进行页面跳转

## 后端配置

### Django CORS 设置

```python
# settings.py
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite 开发
    "https://yourdomain.com", # 生产
]
```

### 环境变量

| 变量 | 说明 |
|-----|------|
| `API_BASE_URL` | 服务端转发用 (`http://localhost:8000/api/v1`) |
| `VITE_API_BASE_URL` | 客户端直连用 (同上) |

## 安全性考虑

| 风险 | 缓解措施 |
|-----|---------|
| XSS 攻击盗取 token | 配合 CSP 策略，限制脚本来源 |
| CSRF | 使用 Bearer Token 而非 Cookie |

## 待完成任务

1. 后端配置 CORS
2. 测试登录流程
3. 测试 token 刷新机制
4. 登出流程测试
