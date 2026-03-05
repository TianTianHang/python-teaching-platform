## Context

当前题目模块的 4 个页面使用 `useEffect` 在客户端获取数据，这是项目早期采用的实现模式。在之前的迁移中，Home 页面（`_layout.home.tsx`）、课程列表页（`_layout.courses/route.tsx`）和课程详情页（`_layout.courses_.$courseId/route.tsx`）已成功迁移到 `clientLoader` 模式。

`clientLoader` 是 React Router v7 推荐的数据加载模式，支持：
- 服务端渲染时预加载数据
- 客户端导航时数据预取
- 统一的加载和错误状态处理
- 更好的类型安全（通过 `useLoaderData<typeof clientLoader>()`）

**当前状态**：
- 已迁移 3 个页面（home, courses, course-detail）
- 待迁移 4 个题目相关页面（problems list, problem detail, description, submissions）
- 剩余页面使用 SSR loader（21个页面）或特殊场景（如 payment pay 轮询）

**约束**：
- 必须保持 SSR 兼容性（虽然这些是 clientLoader，但可能被 SSR 页面嵌套）
- 必须保持现有的缓存策略（`_layout.problems.tsx` 的 `Cache-Control` 头）
- 必须保持所有功能不变（无行为变更）
- JWT 认证和 401 重定向逻辑必须一致

## Goals / Non-Goals

**Goals:**
- 将 4 个题目页面从 `useEffect` 迁移到 `clientLoader`
- 统一数据加载模式，提升代码一致性
- 改善首屏加载性能和用户体验
- 添加统一的错误处理（`ErrorBoundary`）

**Non-Goals:**
- 不修改 API 接口或后端逻辑
- 不改变用户可见的行为或功能
- 不迁移其他未使用 `useEffect` 的页面（如 performance, payment pay 等）
- 不实现 API 服务层封装（留待后续优化）

## Decisions

### 1. 使用 clientLoader 而非 serverLoader

**决策**: 使用 `clientLoader` 而非 `serverLoader` 进行数据获取。

**理由**:
- 这些页面已使用 `clientHttp` 客户端 HTTP 工具，包含完整的认证和错误处理逻辑
- `clientLoader` 支持 SSR/Hydration，可以获得与 `serverLoader` 类似的性能优势
- 迁移成本更低，不需要重写 HTTP 客户端逻辑
- 与已迁移的 Home/Courses 页面保持一致

**替代方案考虑**:
- `serverLoader`: 需要在服务端重建认证逻辑，迁移成本高，且这些页面主要是客户端导航场景

### 2. 错误处理策略

**决策**: 使用 `ErrorBoundary` 组件统一处理错误，移除各组件内的内联错误状态。

**模式**:
```tsx
// 在 clientLoader 中
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  try {
    const data = await clientHttp.get('/problems/');
    return data;
  } catch (error: any) {
    if (error?.response?.status === 401) {
      throw redirect('/auth/login');
    }
    throw new Response('Error', { status: error?.response?.status || 500 });
  }
}

// 在组件中添加 ErrorBoundary
export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  // 错误处理 UI
}
```

**理由**:
- React Router 7 推荐的错误处理模式
- 与已迁移页面保持一致
- 减少组件内部状态管理复杂度

### 3. Hydration Fallback 策略

**决策**: 为每个页面添加 `HydrateFallback` 组件，显示加载骨架屏。

**理由**:
- 提升用户体验，避免内容闪烁
- 遵循 React Router 7 最佳实践
- 复用现有的骨架屏组件（如 `SkeletonProblems`）

### 4. 并行请求处理（submissions.tsx）

**决策**: 在 `clientLoader` 中使用 `Promise.all` 保持并行请求逻辑。

```tsx
const [submissionsData, problemData] = await Promise.all([
  clientHttp.get<Page<Submission>>(`/submissions/?...`),
  clientHttp.get<Problem>(`/problems/${problemId}`)
]);
```

**理由**:
- 保持原有的性能优化（并行请求）
- 在 clientLoader 中处理比 useEffect 更清晰
- 错误处理可以在 Promise.all 外层统一处理

### 5. 分页和筛选逻辑（problems.tsx）

**决策**: 使用 `useSearchParams` 获取查询参数，传递给 `clientLoader`。

```tsx
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  const url = new URL(request.url);
  const page = url.searchParams.get('page') || '1';
  const type = url.searchParams.get('type');
  // ...
  const data = await clientHttp.get(`/problems/?page=${page}&type=${type}&...`);
  return data;
}
```

**理由**:
- clientLoader 的 `request` 参数包含完整 URL
- 查询参数在服务端和客户端都可访问
- 分页导航通过 URL 参数管理，更符合 RESTful 风格

## Risks / Trade-offs

### Risk: 复杂的筛选逻辑可能导致迁移遗漏

**现状**: `_layout.problems.tsx` 有复杂的筛选逻辑（type, difficulty, ordering）和缓存头。

**缓解措施**:
- 迁移时仔细复制所有查询参数逻辑
- 保留现有的 `headers()` 导出函数（缓存策略）
- 测试所有筛选组合

### Risk: "下一题"导航逻辑需要特别处理

**现状**: `problems.$problemId/route.tsx` 支持两种模式：
- 直接访问: `GET /problems/:id`
- 下一题导航: `GET /problems/next/?type=...&id=...`

**缓解措施**:
- 在 clientLoader 中检查 URL 参数决定使用哪个 API
- 保留现有的条件逻辑
- 确保 has_next 状态正确传递

### Risk: 并行请求的错误处理

**现状**: `submissions.tsx` 使用 `Promise.all` 并行请求两个 API。

**缓解措施**:
- 在 clientLoader 中使用 try-catch 包裹 Promise.all
- 如果任一请求失败，抛出 Response 错误
- ErrorBoundary 会捕获并显示错误

### Trade-off: clientLoader vs serverLoader

**选择**: 使用 clientLoader 而非 serverLoader。

**权衡**:
- ✅ 优势: 迁移成本低，复用现有认证逻辑，与已迁移页面一致
- ❌ 劣势: 首次 SSR 时数据仍在客户端加载（但 Hydration 可以弥补）
- **结论**: 对于题目页面这种主要依赖客户端导航的场景，clientLoader 是更合适的选择

## Migration Plan

### 迁移步骤（按优先级）

1. **Phase 1: 高优先级页面**
   - 迁移 `_layout.problems.tsx`（题目列表，高流量）
   - 迁移 `problems.$problemId/route.tsx`（题目详情，核心功能）

2. **Phase 2: 中优先级页面**
   - 迁移 `problems.$problemId.description.tsx`（题目描述）
   - 迁移 `problems.$problemId.submissions.tsx`（提交记录）

### 每个页面的迁移清单

- [ ] 添加 `clientLoader` 函数
- [ ] 添加 `clientLoader.hydrate = true`
- [ ] 添加 `HydrateFallback` 组件
- [ ] 添加 `ErrorBoundary` 组件
- [ ] 移除 `useEffect` 数据获取逻辑
- [ ] 移除相关的 `useState`（loading, error, data）
- [ ] 将组件改为使用 `useLoaderData()` 获取数据
- [ ] 移除 `ResolveError` 组件（改用 ErrorBoundary）
- [ ] 更新类型定义（使用 `useLoaderData<typeof clientLoader>()`）
- [ ] 保留现有功能（分页、筛选、导航等）

### 验证步骤

每个页面迁移后：
1. 运行 typecheck: `pnpm run typecheck`
2. 手动测试所有功能（筛选、分页、导航等）
3. 测试错误场景（401、404、500）
4. 测试加载状态（骨架屏显示正确）

### Rollback 策略

如果迁移出现问题：
- 可以通过 Git 快速回滚到迁移前的代码
- 无需修改后端或数据库
- 无数据迁移风险

## Open Questions

无。这是一个相对直接的迁移，遵循已验证的模式（home/courses 页面迁移）。
