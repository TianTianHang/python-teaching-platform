# 并行化串行请求优化 - 设计文档

## Context

### 当前架构

前端 SSR 服务使用 React Router v7，每个页面通过 `loader` 函数在服务端获取数据。当前实现中，多个 loader 函数存在串行 API 请求问题：

```typescript
// 典型的串行请求模式（章节详情页）
export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);

  // ❌ 串行请求 1
  const unlockStatus = await http.get<ChapterUnlockStatus>(...); // 100ms
  if (unlockStatus.is_locked) return redirect(...);

  // ❌ 串行请求 2（必须等请求 1 完成）
  const chapter = await http.get<Chapter>(...); // 150ms

  // ❌ 串行请求 3（必须等请求 2 完成，且有条件）
  if (chapter.status == "not_started") {
    await http.post(...); // 80ms
  }

  // ❌ 串行请求 4（必须等前面的 await 完成）
  const problems = http.get<Page<Problem>>(...); // 200ms

  // ❌ 串行请求 5（必须等前面的 await 完成）
  const courseChapters = await http.get<Page<Chapter>>(...); // 180ms

  return { chapter, problems, courseChapters };
});
// 总耗时: 710ms
```

### 部署环境

- **SSR 服务**：PM2 集群模式（`instances: "max"`，通常 4 个进程）
- **后端通信**：Django API (http://backend:8000/api/v1)
- **连接池**：已配置 HTTP Agent（`maxSockets: 50`，进程级连接池）

### 问题影响

1. **单请求延迟高**：章节详情页 710ms，其中 510ms 是串行等待导致的浪费
2. **内存压力大**：串行请求占用连接和内存更久 → 请求积压 → GC 频繁 → 级联延迟
3. **吞吐量受限**：理论吞吐量 1100 req/s，实际仅 200 req/s（18% 利用率）

### 约束

- 必须保持 SSR 兼容性（loader 在服务端执行）
- 不能破坏现有的 JWT 认证流程和 401 刷新机制
- 必须保持错误处理逻辑（`catch` 块）
- 必须支持 React Router v7 的 `defer` 流式渲染（可选）

## Goals / Non-Goals

**Goals:**

- 并行化 loader 中的独立 API 请求，使用 `Promise.all` 减少总等待时间
- 异步执行非关键 POST 请求（如 `mark_as_completed`），避免阻塞响应
- 保持现有的错误处理逻辑和快速失败机制
- 向后兼容，不破坏任何现有功能
- 提供清晰的代码模式，供后续 loader 优化参考

**Non-Goals:**

- 不改动后端 API 或配置
- 不添加复杂的请求缓存（可后续优化）
- 不修改客户端（浏览器）的数据获取逻辑
- 不实现流式渲染（使用 `defer`），作为独立优化项

## Decisions

### 1. 使用 Promise.all 并行化独立请求

**决定**：使用 `Promise.all` 并行执行独立的 API 请求，而非手动 Promise 链或第三方库。

**理由**：

- `Promise.all` 是原生 API，无需额外依赖
- 所有请求同时发起，总耗时 = 最慢的请求（而非请求之和）
- 任何一个请求失败，`Promise.all` 会立即 reject，符合错误传播语义
- 与现有代码风格一致（已有部分 loader 使用 `http.get().catch()` 模式）

**替代方案**：

- ❌ **Promise.allSettled**：所有请求都会等待完成，即使某个失败。不适用于我们有依赖的场景。
- ❌ **手动 Promise 链**：代码冗长，易出错，难以维护。
- ❌ **`async/await` 串行**：正是当前问题所在。

**代码示例**：

```typescript
// 优化前：串行请求
const course = await http.get<Course>(`/courses/${courseId}`); // 150ms
const chapters = await http.get<Page<Chapter>>(`/courses/${courseId}/chapters`); // 200ms
// 总耗时: 350ms

// 优化后：并行请求
const [course, chapters] = await Promise.all([
  http.get<Course>(`/courses/${courseId}`), // 150ms
  http.get<Page<Chapter>>(`/courses/${courseId}/chapters`), // 200ms
]);
// 总耗时: 200ms (取最慢)
```

### 2. 保持关键串行检查的快速失败机制

**决定**：保留 `unlock_status` 的串行检查，避免不必要的 API 调用。

**理由**：

- 如果章节被锁定，后续 `chapter`、`problems` 请求会被浪费
- `unlock_status` 检查本身很快（~100ms），是值得的早期验证
- 快速失败可以节省后端资源和带宽

**代码示例**：

```typescript
// 先检查锁定状态（串行）
const unlockStatus = await http.get<ChapterUnlockStatus>(...);
if (unlockStatus.is_locked) {
  return redirect(...); // 快速失败，不执行后续请求
}

// 解锁后，并行获取所有数据
const [chapter, problems, courseChapters] = await Promise.all([...]);
```

### 3. 异步执行非关键 POST 请求

**决定**：将 `mark_as_completed` POST 请求改为异步执行（fire-and-forget），不阻塞 loader 响应。

**理由**：

- 这个 POST 请求仅用于标记学习进度，不影响页面渲染
- 用户不需要等待这个请求完成就能看到内容
- 即使 POST 失败，也不影响用户体验（静默失败即可）

**代码示例**：

```typescript
// 优化前：阻塞响应
if (chapter.status === "not_started") {
  await http.post(...); // ❌ 阻塞 80ms
}
return { chapter, problems, courseChapters };

// 优化后：异步执行
if (chapter.status === "not_started") {
  http.post(...).catch(() => {
    // 静默失败，不影响用户体验
  });
}
return { chapter, problems, courseChapters };
```

### 4. 保持现有的错误处理逻辑

**决定**：继续使用 `.catch()` 捕获单个请求错误，返回包含 `status` 和 `message` 的错误对象，而非让 `Promise.all` 失败。

**理由**：

- 某些非关键数据失败时，页面仍应渲染（如 `courseChapters` 侧边栏）
- 组件层已有 `ResolveError` 处理错误对象
- 保持向后兼容，不破坏现有的错误传播链

**代码示例**：

```typescript
const [chapter, problems, courseChapters] = await Promise.all([
  http.get<Course>(`/courses/${courseId}/chapters/${chapterId}`),
  http.get<Page<Problem>>(`/courses/${courseId}/chapters/${chapterId}/problems?exclude=content`)
    .catch((e: AxiosError) => ({
      status: e.status,
      message: e.message,
    })),
  http.get<Page<Chapter>>(`/courses/${courseId}/chapters?exclude=content`)
    .catch((e: AxiosError) => ({
      status: e.status || 500,
      message: e.message,
    })),
]);
```

### 5. 不修改 `http.get()` 的调用方式

**决定**：保持 `http.get().catch()` 的调用模式，不将其包装为自动并行的辅助函数。

**理由**：

- 引入辅助函数会增加抽象层，降低代码可读性
- 每个页面的并行化模式略有不同（串行检查、条件 POST 等）
- 现有代码已使用 `http.get().catch()` 模式，保持一致性

**未来优化**：

- 如果 10+ 个页面都需要类似优化，可以考虑创建通用的 `parallelize()` 辅助函数
- 目前 4 个页面，直接使用 `Promise.all` 更清晰

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| **Promise.all 部分失败**：某个请求失败导致整个 `Promise.all` reject，页面无法渲染 | 使用 `.catch()` 捕获单个请求错误，返回错误对象而非抛出异常。组件层根据 `status` 字段判断是否显示 `ResolveError` |
| **异步 POST 失败**：`mark_as_completed` 静默失败导致学习进度未记录 | 添加 `.catch()` 日志记录（可选），或改为 Celery 异步任务（后端改动）。当前权衡：用户体验 > 进度记录准确性 |
| **错误传播复杂化**：多个请求的错误可能同时发生，难以调试 | 保持每个请求的 `.catch()` 独立，返回错误对象包含 `status` 和 `message`，便于定位问题源 |
| **类型安全性**：`Promise.all` 返回类型可能不匹配 | 使用 TypeScript 泛型明确标注返回类型，如 `Promise.all<[Course, Page<Chapter>]>([...])` |
| **回滚风险**：代码改动可能引入新 bug | 逐个文件部署，每次部署后观察监控指标。保持 Git commit 原子性，方便回滚 |

## Migration Plan

### 阶段 1：核心页面优化（高优先级）

1. **章节详情页**（`_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`）
   - 改动：使用 `Promise.all` 并行化 `chapter`、`problems`、`courseChapters`
   - 改动：异步化 `mark_as_completed` POST 请求
   - 预期收益：710ms → 200ms（-72%）
   - 工作量：1 小时

2. **章节列表页**（`_layout.courses_.$courseId_.chapters/route.tsx`）
   - 改动：使用 `Promise.all` 并行化 `course` 和 `chapters`
   - 预期收益：350ms → 200ms（-43%）
   - 工作量：30 分钟

3. **考试列表页**（`_layout.courses_.$courseId_.exams.tsx`）
   - 改动：使用 `Promise.all` 并行化 `course` 和 `exams`
   - 预期收益：280ms → 150ms（-46%）
   - 工作量：30 分钟

### 阶段 2：次要页面优化（中优先级）

4. **课程详情页**（`_layout.courses_.$courseId/route.tsx`）
   - 改动：使用 `Promise.all` 并行化 `course` 和 `userEnrollments`
   - 预期收益：320ms → 150ms（-53%）
   - 工作量：30 分钟

### 验证步骤

每个页面改动后：

1. **本地功能测试**
   - 启动 SSR 服务：`pnpm run start`
   - 手动测试页面渲染，确保数据正常显示
   - 测试边界情况：空数据、网络错误、锁定章节

2. **类型检查**
   - 运行：`pnpm run typecheck`
   - 确保无 TypeScript 错误

3. **构建验证**
   - 运行：`pnpm run build`
   - 确保构建成功

4. **性能测试（可选）**
   - 使用 Locust 运行负载测试
   - 对比优化前后的 P50、P95、P99 延迟

### 部署策略

- **推荐部署顺序**：章节详情页 → 章节列表页 → 考试列表页 → 课程详情页
- **分批部署**：每次部署 1-2 个文件，观察监控指标后再继续
- **监控指标**：
  - 错误率（不应增加）
  - P95 延迟（应降低 30%+）
  - 吞吐量（应提升 50%+）
  - 内存使用（应降低）

### 回滚策略

- 所有改动集中在 loader 函数，不涉及配置或依赖
- 如发现问题，立即 `git revert` 相关 commit
- 重启 PM2 服务：`pm2 restart react-router-ssr`
- 回滚风险低，改动可逆

## Open Questions

无。此优化方案明确且低风险，技术方案已验证，可直接实施。

### 未来优化方向（不在本次范围）

1. **流式渲染**：使用 React Router v7 的 `defer` 和 `<Suspense>`，进一步提升感知性能
2. **请求缓存**：在 Session 或 Redis 中缓存 `unlock_status`、`courseChapters` 等数据
3. **批量 API**：后端提供聚合端点（如 `/chapter-detail-batch/`），单次请求获取所有数据
4. **请求去重**：防止短时间内重复请求同一资源
