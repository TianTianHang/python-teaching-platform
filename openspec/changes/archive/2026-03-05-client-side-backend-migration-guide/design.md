# Design: 客户端直连后端迁移规范

## 1. 迁移决策矩阵

### 何时使用客户端直连

| 场景 | 推荐方式 | 原因 |
|------|----------|------|
| 登录/注册页面 | 客户端直连 | 用户交互频繁，需要即时反馈 |
| 个人中心/设置 | 客户端直连 | 用户特定数据，私密的 |
| 表单提交页面 | 客户端直连 | 即时验证，提升体验 |
| 动态内容加载 | 客户端直连 | 减少首屏加载时间 |
| 需要 SEO 的页面 | 服务端代理 | 需要服务端渲染 |
| 公开内容列表 | 服务端代理 | 可缓存，减少 API 调用 |

### 决策流程

```
页面是否需要迁移到客户端直连？
│
├─ 是否需要用户登录后访问？ ──── 是 ──▶ 客户端直连
│
├─ 是否需要 SEO？ ────────────── 是 ──▶ 服务端代理
│
├─ 是否有大量即时用户交互？ ─── 是 ──▶ 客户端直连
│
└─ 是否需要服务端预渲染数据？ ─ 是 ──▶ 服务端代理
                                         │
                                         ▼
                              考虑混合方案：首屏 SSR + 客户端更新
```

## 2. 迁移检查清单

### 2.1 环境配置

- [ ] 已配置 `VITE_API_BASE_URL` 在 `.env` 文件
- [ ] 后端 `CORS_ALLOWED_ORIGINS` 已包含前端域名
- [ ] `CORS_ALLOW_CREDENTIALS = True`
- [ ] `CORS_ALLOW_HEADERS` 包含 `authorization`

### 2.2 代码改造

- [ ] 移除 `action`/`loader` 中的服务端 API 调用
- [ ] 引入 `clientHttp` 或 `clientAuth` 工具
- [ ] 使用 `useNavigate` 进行页面跳转
- [ ] 处理错误状态和加载状态

### 2.3 Session 同步（仅登录相关页面）

- [ ] 登录后调用 `/auth/set-session` 设置服务端 session
- [ ] 登出使用 `/auth/logout` 路由清除 session

## 3. 代码模板

### 3.1 客户端页面模板

```tsx
// 改造前 (服务端)
export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const http = createHttp(request);
  const data = await http.post('endpoint', formData);
  
  const session = await getSession(request.headers.get('Cookie'));
  session.set('key', data.value);
  return redirect('/next', { headers: { 'Set-Cookie': await commitSession(session) } });
}

export default function Page() {
  const { data } = useLoaderData<typeof loader>;
  // ...
}
```

```tsx
// 改造后 (客户端)
import { clientHttp } from '~/utils/http/client';
import { useNavigate } from 'react-router';

export default function Page() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await clientHttp.post('endpoint', { key: value });
      navigate('/next');
    } catch (err: any) {
      setError(err.response?.data?.detail || '操作失败');
    } finally {
      setLoading(false);
    }
  };

  // ...
}
```

### 3.2 登录后 Session 同步模板

```tsx
// 登录后同步 session
const handleLogin = async () => {
  const { token, user } = await clientAuth.login(username, password);
  
  // 同步到服务端 session（用于 SSR）
  const formData = new FormData();
  formData.append('accessToken', token.access);
  formData.append('refreshToken', token.refresh);
  formData.append('user', JSON.stringify(user));
  
  await fetch('/auth/set-session', {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });
  
  navigate('/home');
};
```

### 3.3 登出模板

```tsx
// 使用服务端路由登出（自动清除 session）
import { useNavigate } from 'react-router';
import { useSubmit } from 'react-router';

function LogoutButton() {
  const navigate = useNavigate();
  const submit = useSubmit();

  const handleLogout = () => {
    submit({}, { action: '/auth/logout', method: 'POST' });
  };

  return <button onClick={handleLogout}>登出</button>;
}
```

## 4. HTTP 客户端 API 参考

### 4.1 clientHttp

```ts
import { clientHttp } from '~/utils/http/client';

// GET 请求
const data = await clientHttp.get<T>('/endpoint', params, config);

// POST 请求
const result = await clientHttp.post<T>('/endpoint', data, config);

// PUT 请求
await clientHttp.put<T>('/endpoint', data, config);

// DELETE 请求
await clientHttp.delete<T>('/endpoint', params, config);

// PATCH 请求
await clientHttp.patch<T>('/endpoint', data, config);

// 获取原始 axios 实例
const axiosInstance = clientHttp.getInstance();
```

### 4.2 clientAuth

```ts
import { clientAuth } from '~/utils/http/client';

// 获取当前 token
const token = clientAuth.getToken();

// 检查是否已登录
const isLoggedIn = clientAuth.isAuthenticated();

// 登录
const { token, user } = await clientAuth.login(username, password);

// 登出（清除 localStorage）
await clientAuth.logout();

// 清除 token
clientAuth.clearToken();
```

## 5. 错误处理规范

### 5.1 常见错误码处理

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 401 | 未认证 | 清除 token，跳转登录 |
| 403 | 无权限 | 显示错误提示 |
| 404 | 资源不存在 | 显示404页面 |
| 500 | 服务器错误 | 显示错误提示 |
| network | 网络错误 | 显示重试提示 |

### 5.2 错误处理示例

```tsx
try {
  await clientHttp.post('endpoint', data);
} catch (err: any) {
  if (err.response?.status === 401) {
    clientAuth.clearToken();
    navigate('/auth/login');
    return;
  }
  
  const message = err.response?.data?.detail 
    || err.response?.data?.message 
    || '操作失败，请稍后重试';
  setError(message);
}
```

## 6. 迁移优先级建议

### 高优先级

1. **注册页面** (`auth.register.tsx`) - 与登录类似模式
2. **个人资料页面** - 频繁用户交互

### 中优先级

3. **课程评论/讨论区** - 即时互动
4. **作业提交页面** - 实时反馈

### 低优先级

5. **公开课程列表** - 可保持 SSR，需要 SEO
6. **搜索结果页** - 需要 SEO 和缓存

## 7. 注意事项

1. **API 端点一致性**: 后端 URL 不要使用尾部斜杠
2. **CORS 配置**: 确保前端域名在允许列表中
3. **Token 过期处理**: 401 时自动刷新 token
4. **Session 同步**: 登录后必须同步 session，否则 SSR 无法获取用户状态
5. **Loading 状态**: 所有异步操作需要 loading 状态提升用户体验