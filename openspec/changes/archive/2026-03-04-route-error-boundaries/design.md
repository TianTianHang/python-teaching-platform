# 设计文档：路由级错误边界改进

## 架构概述

本文档描述如何为4个关键路由页面添加健壮的错误处理机制，确保 API 请求失败时页面不会崩溃。

## 核心原则

1. **防御性编程**：所有外部 API 请求都必须有错误捕获
2. **渐进式降级**：错误发生时显示友好提示，而不是白屏
3. **一致性**：统一错误处理模式，便于维护

## 技术方案

### 方案 1: Loader 级别错误处理（服务端）

#### 模式 A: 直接 `.catch()` 包装

适用于：单个 API 请求

```typescript
// ❌ 错误示例
const data = await http.get('/api/endpoint');
return { data };

// ✅ 正确示例
const data = await http.get('/api/endpoint')
  .catch((e: AxiosError) => ({
    status: e.status || 500,
    message: e.message || '加载失败',
  }));
return { data };
```

#### 模式 B: Promise.all 独立错误处理

适用于：多个并行请求，任何一个失败不应影响其他请求

```typescript
// ❌ 错误示例：任何一个失败都会导致整个 Promise.all 失败
const [data1, data2] = await Promise.all([
  http.get('/api/1'),
  http.get('/api/2'),
]);

// ✅ 方案 1: 使用 Promise.allSettled（推荐）
const results = await Promise.allSettled([
  http.get('/api/1'),
  http.get('/api/2'),
]);
const data1 = results[0].status === 'fulfilled' ? results[0].value : { status: 500, message: '加载失败' };
const data2 = results[1].status === 'fulfilled' ? results[1].value : { status: 500, message: '加载失败' };

// ✅ 方案 2: 单独 .catch() 包装
const data1 = await http.get('/api/1')
  .catch((e: AxiosError) => ({ status: e.status || 500, message: e.message }));
const data2 = await http.get('/api/2')
  .catch((e: AxiosError) => ({ status: e.status || 500, message: e.message }));
```

#### 模式 C: 依赖关系请求

适用于：第二个请求依赖第一个请求的结果

```typescript
// 第一个请求必须成功，否则 redirect
const unlockStatus = await http.get<ChapterUnlockStatus>(`/api/unlock`)
  .catch((e: AxiosError) => {
    // 404 或 403 时重定向到锁定页面
    if (e.status === 404 || e.status === 403) {
      return redirect(`/courses/${courseId}/chapters/${chapterId}/locked`);
    }
    // 其他错误返回错误对象
    return { status: e.status || 500, message: e.message || '无法访问此章节' };
  });

if (unlockStatus instanceof Response) {
  return unlockStatus; // redirect
}

if (unlockStatus.is_locked) {
  return redirect(`/courses/${courseId}/chapters/${chapterId}/locked`);
}

// 第二个请求
const chapter = await http.get<Chapter>(`/api/chapter`)
  .catch((e: AxiosError) => ({ status: e.status || 500, message: e.message }));
```

### 方案 2: 客户端 Await 错误处理

#### 模式 A: `<Await>` 错误边界

```typescript
// ❌ 错误示例：没有错误处理
<Await resolve={data}>
  {(resolved) => <Component data={resolved} />}
</Await>

// ✅ 正确示例：使用 errorFn 或单独的错误处理 children
<Await resolve={data}>
  {(resolved) => <Component data={resolved} />}
  {(error) => (
    <ResolveError status={error.status} message={error.message}>
      <Typography>加载失败，请重试</Typography>
    </ResolveError>
  )}
</Await>

// 或者使用 children 函数的第二个参数
<Await resolve={data}>
  {(resolved) => {
    if ('status' in resolved) {
      return (
        <ResolveError status={resolved.status} message={resolved.message}>
          <Typography>加载失败，请重试</Typography>
        </ResolveError>
      );
    }
    return <Component data={resolved} />;
  }}
</Await>
```

## 具体实现

### 1. 章节详情页 (`_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`)

#### 问题分析
```typescript
// 当前代码（line 46）
const unlockStatus = await http.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`)
if (unlockStatus.is_locked) {
  return redirect(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`)
}
```

**问题**：如果请求失败（网络错误、500错误等），会抛出未捕获异常。

#### 解决方案

```typescript
export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);

  // 修改 1: unlockStatus 添加错误处理
  const unlockStatus = await http.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`)
    .catch((e: AxiosError) => {
      // 403/404 表示章节锁定或不存在，重定向
      if (e.status === 403 || e.status === 404) {
        return redirect(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`);
      }
      // 其他错误返回错误对象
      return {
        status: e.status || 500,
        message: e.message || '无法检查章节状态',
        is_locked: true, // 默认锁定，防止用户看到未授权内容
      };
    });

  // 如果是 redirect 对象，直接返回
  if (unlockStatus instanceof Response) {
    return unlockStatus;
  }

  // 如果 unlockStatus 包含错误字段，仍然返回但标记为锁定
  if ('status' in unlockStatus) {
    return redirect(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`);
  }

  if (unlockStatus.is_locked) {
    return redirect(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`);
  }

  // 剩余代码保持不变...
  const chapter = http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
  const problems = http.get<Page<Problem>>(`/courses/${params.courseId}/chapters/${params.chapterId}/problems?exclude=recent_threads`)
    .catch((e: AxiosError) => ({
      status: e.status || 500,
      message: e.message || '无法加载题目',
    }));
  const courseChapters = http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters?exclude=content`)
    .catch((e: AxiosError) => ({
      status: e.status || 500,
      message: e.message || '无法加载章节列表',
    }));

  return { chapter, problems, courseChapters, unlockStatus };
});
```

### 2. 章节列表页 (`_layout.courses_.$courseId_.chapters/route.tsx`)

#### 问题分析
```typescript
// 当前代码（line 43-44）
const [course, chapters] = await Promise.all([
  http.get<Course>(`/courses/${params.courseId}`),
  http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters/?${queryParams.toString()}`),
]);
```

**问题**：任何一个请求失败都会导致整个 loader 失败。

#### 解决方案

```typescript
export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const url = new URL(request.url);
  const searchParams = url.searchParams;
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10);

  const queryParams = new URLSearchParams();
  queryParams.set("page", page.toString());
  queryParams.set("page_size", pageSize.toString());
  queryParams.set("exclude", "content");

  const http = createHttp(request);

  // 修改: 使用 Promise.allSettled 或单独 .catch()
  const results = await Promise.allSettled([
    http.get<Course>(`/courses/${params.courseId}`),
    http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters/?${queryParams.toString()}`),
  ]);

  const course = results[0].status === 'fulfilled'
    ? results[0].value
    : { status: 500, message: '无法加载课程信息' };

  const chapters = results[1].status === 'fulfilled'
    ? results[1].value
    : { results: [], count: 0, next: null, previous: null, page_size: pageSize };

  return { chapters, course };
});
```

**注意**：如果 `course` 加载失败，可以显示错误，但 `chapters` 仍然可以正常显示（假设课程 ID 有效）。

### 3. 课程详情页 (`_layout.courses_.$courseId/route.tsx`)

#### 问题分析
```typescript
// 当前代码（line 43-44）
const enrollmentPromise = http.get<Page<Enrollment>>(`/enrollments/?course=${params.courseId}`)
  .then(result => result.results.length > 0 ? result.results[0] : null);
```

这个 Promise 已经有 `.then()`，但没有 `.catch()`。在客户端 `<Await>` 中使用时，如果失败会导致错误。

#### 解决方案

**服务端修改**：
```typescript
export const loader = withAuth(async ({ request, params }: Route.LoaderArgs) => {
  const http = createHttp(request);

  // 修改: enrollmentPromise 添加 .catch()
  const enrollmentPromise = http.get<Page<Enrollment>>(`/enrollments/?course=${params.courseId}`)
    .then(result => result.results.length > 0 ? result.results[0] : null)
    .catch((e: AxiosError) => {
      // 返回 null 表示未报名，但记录错误（可选：记录到日志）
      console.error('Failed to load enrollment:', e.message);
      return null;
    });

  const course = http.get<Course>(`/courses/${params.courseId}`)
    .catch((e: AxiosError) => ({
      status: e.status || 500,
      message: e.message,
    }));

  return { course, enrollment: enrollmentPromise };
});
```

**客户端修改**：
```typescript
// 修改: enrollmentPromise 的 Await 添加错误处理
<React.Suspense fallback={<Skeleton variant="rounded" height={100} />}>
  <Await resolve={enrollmentPromise} error={<EnrollmentError />}>
    {(enrollment) => (
      <>
        {enrollment ? (
          // 显示报名信息
        ) : (
          // 显示"未报名"状态
        )}
      </>
    )}
  </Await>
</React.Suspense>
```

创建 `EnrollmentError` 组件：
```typescript
function EnrollmentError() {
  return (
    <Box sx={{ mt: 2 }}>
      <Alert severity="warning">
        无法加载报名状态，请刷新页面重试
      </Alert>
    </Box>
  );
}
```

### 4. 题目详情页 (`problems.$problemId/route.tsx`)

#### 问题分析
```typescript
// 当前代码（line 40-44）
if(problem===undefined){
  return <Box p={4}>
    <title>{formatTitle(PAGE_TITLES.problem("题目加载失败"))}</title>
    <Typography variant="h6" color="error">题目加载失败，请重试。</Typography>
  </Box>
}
```

**问题**：
1. 只检查 `undefined`，不处理 API 错误响应对象
2. 如果 API 返回错误对象（如 `{ status: 404, message: 'Not Found' }`），会被当作正常数据

#### 解决方案

**服务端修改**：
```typescript
export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
  const searchParams = new URL(request.url).searchParams;
  const next_type = searchParams.get('type');
  const next_id = searchParams.get('id');

  // 修改: 添加错误处理
  let problem: Problem;
  let hasNext = true;
  let error: { status: number; message: string } | null = null;

  try {
    if (next_id && next_type) {
      const search = new URLSearchParams();
      search.append('type', next_type);
      search.append('id', next_id);
      const result = await http.get<{problem:Problem,has_next:boolean}>(`/problems/next/?${search.toString()}`);
      problem = result.problem;
      hasNext = result.has_next;
    } else {
      problem = await http.get<Problem>(`/problems/${params.problemId}`);
    }
  } catch (e) {
    const axiosError = e as AxiosError;
    error = {
      status: axiosError.status || 500,
      message: axiosError.message || '题目加载失败',
    };
  }

  return { problem, hasNext, error };
});
```

**客户端修改**：
```typescript
export default function ProblemPage({ loaderData }: Route.ComponentProps) {
  const navigate = useNavigate();
  const problem = loaderData.problem;
  const error = loaderData.error;
  const hasNext = loaderData.hasNext;

  // 修改: 优先检查错误
  if (error) {
    return (
      <Box p={4}>
        <title>{formatTitle(PAGE_TITLES.problem("题目加载失败"))}</title>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error.message}
        </Alert>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" onClick={() => navigate('/problems')}>
            返回题目列表
          </Button>
          <Button variant="contained" onClick={() => window.location.reload()}>
            重新加载
          </Button>
        </Box>
      </Box>
    );
  }

  // 原有的 undefined 检查（保留）
  if (problem === undefined) {
    return (
      <Box p={4}>
        <title>{formatTitle(PAGE_TITLES.problem("题目加载失败"))}</title>
        <Typography variant="h6" color="error">题目加载失败，请重试。</Typography>
      </Box>
    );
  }

  // 剩余代码保持不变...
}
```

## 错误类型定义

创建统一的错误类型：

```typescript
// app/types/error.ts
export interface ApiError {
  status: number;
  message: string;
}

export function isApiError(obj: unknown): obj is ApiError {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'status' in obj &&
    'message' in obj
  );
}
```

## 测试策略

### 单元测试
- 测试 loader 在 API 失败时的返回值
- 测试错误对象的结构

### 集成测试
- 测试完整的错误流程（API 失败 → 显示错误提示）
- 测试重试机制

### 手动测试场景
1. **网络断开**：断开网络，访问页面，应显示友好错误提示
2. **服务器 500**：Mock 500 错误，验证错误处理
3. **404 错误**：访问不存在的资源，验证降级处理
4. **慢网络**：使用 Chrome DevTools 模拟慢网络，验证加载状态

## 性能考虑

- 错误处理不应增加正常情况下的延迟
- `.catch()` 和 `Promise.allSettled` 的性能开销可忽略
- 客户端 `<Await>` 错误处理不影响首次渲染

## 向后兼容性

- 所有修改保持返回数据结构一致
- 不影响现有的成功流程
- 错误对象遵循 `{ status, message }` 约定，与现有 `ResolveError` 组件兼容
