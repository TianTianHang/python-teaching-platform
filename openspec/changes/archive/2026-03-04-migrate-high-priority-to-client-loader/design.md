## Context

当前三个高优先级页面使用 `useEffect + clientHttp.get()` 在组件内部获取数据：

1. `_layout.home.tsx` - 获取 enrollments 和 problem-progress
2. `_layout.courses/route.tsx` - 获取课程列表
3. `_layout.courses_.$courseId/route.tsx` - 获取课程详情和 enrollment

这些页面已迁移到客户端渲染，但未使用 React Router 7 的原生 clientLoader 模式。

## Goals / Non-Goals

**Goals:**
- 将三个页面从 useEffect 迁移到 clientLoader
- 保持现有的错误处理和 401 重定向逻辑
- 支持 SSR 水合（hydrate = true）
- 简化组件代码，移除重复的 loading/error state

**Non-Goals:**
- 不修改 API 接口
- 不添加新功能
- 不迁移其他页面（低优先级）

## Decisions

### D1: 使用 clientLoader 而非 useEffect

**选择：** 使用 `clientLoader` 获取数据

**理由：**
- 支持 SSR + Hydration，首屏渲染更快
- React Router 7 官方推荐模式
- 数据获取与组件分离，代码更清晰
- 可复用 serverLoader 的错误处理模式

**备选考虑：**
- useEffect：实现简单，但不利用 SSR 能力
- React Query/TanStack Query：功能强大，但引入新依赖

### D2: clientLoader 实现策略

**选择：** 每个路由独立实现 clientLoader

```tsx
export async function clientLoader({ request, serverLoader }: Route.ClientLoaderArgs) {
  // 直接在客户端获取数据
  const url = new URL(request.url);
  const data = await clientHttp.get(...);
  return data;
}
clientLoader.hydrate = true;
```

**不使用 serverLoader 的原因：**
- 当前 serverLoader 使用 `createHttp(request)`（服务端 HTTP），需要在 node 环境运行
- 迁移目标是客户端加载，所以直接用 `clientHttp`
- 数据格式相同，可以复用

### D3: 错误处理方式

**选择：** 使用 React Router 的错误处理机制

```tsx
// 在 loader 中抛出错误
throw new Response(JSON.stringify({ message: '加载失败' }), { status: 500 });

// 使用 errorElement 显示错误
export function ErrorBoundary() {
  return <ResolveError />;
}
```

**理由：**
- React Router 原生支持
- 可以全局处理，也可以按路由处理

### D4: 401 处理

**选择：** 在 clientLoader 中检测 401 并重定向

```tsx
export async function clientLoader({ request }: Route.ClientLoaderArgs) {
  try {
    const data = await clientHttp.get(...);
    return data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw redirect('/auth/login');
    }
    throw error;
  }
}
```

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| 首屏加载时序 | SSR 渲染后 clientLoader 可能再次请求 | 使用 hydrate = true 减少闪烁 |
| 重复请求 | 初始 SSR 数据被忽略 | 当前项目可接受，后续可优化 |
| 类型定义 | clientLoader 返回类型与原 useEffect 可能不同 | 保持相同的数据结构 |

## Migration Plan

1. 为每个页面创建 clientLoader
2. 添加 `clientLoader.hydrate = true`
3. 移除组件内的 useEffect 和相关 state
4. 使用 `useLoaderData()` 获取数据
5. 添加 errorElement 处理错误
6. 运行 typecheck 验证
7. 手动测试验证功能正常