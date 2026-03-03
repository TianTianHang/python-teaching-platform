## Context

### 当前架构

项目使用 React Router v7 + SSR，但数据加载策略不统一：

**流式式页面**（已优化）：
- Home、Courses list、Problems list 页面的 loader 直接返回 Promise，不使用 `await`
- React Router 自动流式传输数据，`onShellReady` 在 ~50ms 内触发
- 组件中使用 `<Suspense>` + `<Await>` 处理异步数据

**阻塞式页面**（待优化）：
- 章节详情页（`_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`）
- 课程详情页（`_layout.courses_.$courseId/route.tsx`）
- Loader 中使用 `await Promise.all([...])` 等待所有数据
- `onShellReady` 延迟 ~250-350ms，阻塞首屏渲染

### 约束条件

- **SSR 兼容性**：所有数据获取必须在服务器端工作，使用 `createHttp(request)` 而不是浏览器 API
- **SEO 友好**：现有 `isbot` 检查确保爬虫获得完整内容，不能破坏此行为
- **渐进式增强**：Skeleton 必须精确匹配最终内容，避免布局偏移（CLS）
- **中文平台**：UI 和内容均为中文，设计需考虑中文字符的渲染特性

## Goals / Non-Goals

**Goals:**
- 将章节详情页和课程详情页的首屏加载时间减少 60-80%
- 建立统一的流式渲染模式，为未来页面提供可复用模板
- 保持现有功能完整性，只优化性能不改变行为
- 改善用户感知性能（渐进式内容加载 + 精确 Skeleton）

**Non-Goals:**
- 不修改后端 API（前端优化为主）
- 不改变现有功能逻辑（如重定向、错误处理等）
- 不追求 100% 的流式覆盖率（某些数据确实需要等待）
- 不引入新的外部依赖（使用 React Router v7 内置能力）

## Decisions

### 决策 1：数据分优先级策略

**选择**：将数据分为三个优先级，而非全部流式或全部等待

| 优先级 | 数据 | 策略 | 理由 |
|--------|------|------|------|
| P0 | unlockStatus | 必须等待 | 用于 redirect 决策，阻塞后续渲染 |
| P1 | chapter / course | 流式传输 | 主要内容，用户等待的核心数据 |
| P2 | problems / syllabus | 流式传输 | 次要内容，可以稍后加载 |
| P3 | courseChapters | 流式传输 | 侧边栏导航，最低优先级 |

**理由**：
- P0 数据影响页面路由决策，必须同步获取
- P1-P3 数据不影响页面框架，可以渐进式传输
- 优先级对齐用户视觉焦点（主内容 > 辅助内容 > 导航）

**替代方案**：
- 全部流式：会导致 redirect 逻辑复杂化（需要在组件中处理）
- 全部等待：回到原有问题，失去流式渲染的优势

### 决策 2：细粒度 Suspense 边界

**选择**：为不同内容区域添加独立的 `<Suspense>` 边界，而不是一个大的 Suspense 包裹整个页面

```tsx
// 细粒度边界
<Suspense fallback={<ChapterTitleSkeleton />}>
  <Await resolve={chapter}>...</Await>
</Suspense>

<Suspense fallback={<ChapterContentSkeleton />}>
  <Await resolve={chapter}>...</Await>
</Suspense>

<Suspense fallback={<ProblemsSkeleton />}>
  <Await resolve={problems}>...</Await>
</Suspense>
```

**理由**：
- 用户更快看到部分内容（标题先于完整内容）
- 提供更精确的加载状态反馈
- 允许不同数据以不同速度到达

**替代方案**：
- 单一大边界：简单但用户体验差（长时间空白）
- 不使用 Suspense：无法利用 React Router v7 的流式能力

### 决策 3：Skeleton 匹配策略

**选择**：每个 Skeleton 必须精确匹配最终内容的尺寸和布局，使用实际组件的样式 token

```tsx
// ❌ 不好的 Skeleton
<Box sx={{ minHeight: 100 }}>
  <Skeleton variant="text" />
</Box>

// ✅ 好的 Skeleton
<Box sx={{ minHeight: 400, p: spacing.md }}>
  <Skeleton variant="text" width={200} height={36} />
  <Skeleton variant="text" width="60%" height={20} sx={{ mt: spacing.sm }} />
  <Skeleton variant="rectangular" height={200} sx={{ mt: spacing.md }} />
</Box>
```

**理由**：
- 减少布局偏移（CLS），改善 Core Web Vitals
- 提供更平滑的视觉过渡
- 使用设计系统的 spacing token保持一致性

**替代方案**：
- 通用 Skeleton：简单但会导致内容跳动
- 不使用 Skeleton：空白屏幕体验更差

### 决策 4：组件拆分策略

**选择**：为需要流式渲染的部分提取独立的组件，每个组件管理自己的 Suspense 边界

**理由**：
- 保持主组件简洁，专注于页面结构
- 流式逻辑封装在子组件中，易于测试和复用
- 符合单一职责原则

**示例**：
```tsx
// 主组件保持简单
export default function ChapterDetail({ loaderData, params }) {
  return (
    <>
      <ChapterTitle chapter={loaderData.chapter} />
      <ChapterContent chapter={loaderData.chapter} />
      <ChapterProblems problems={loaderData.problems} />
      <ChapterSidebar chapters={loaderData.courseChapters} />
    </>
  );
}

// 子组件封装 Suspense
function ChapterTitle({ chapter }) {
  return (
    <Suspense fallback={<ChapterTitleSkeleton />}>
      <Await resolve={chapter}>
        {(resolved) => <Typography variant="h4">{resolved.title}</Typography>}
      </Await>
    </Suspense>
  );
}
```

### 决策 5：错误处理策略

**选择**：保持现有的 `.catch()` 模式，在 loader 中捕获错误并返回错误对象

```tsx
const problems = http.get<Page<Problem>>(...)
  .catch((e: AxiosError) => ({
    status: e.status,
    message: e.message,
  }));
```

**理由**：
- 错误对象也是可序列化的，可以流式传输
- 组件中的 `<Await>` 已经处理了错误对象（检查 `status` 字段）
- 与现有模式一致，无需修改错误处理逻辑

**替代方案**：
- 抛出错误：会导致整个页面流式传输中断
- 使用 ErrorBoundary：增加复杂度，现有模式已足够

## Risks / Trade-offs

### 风险 1：布局偏移（CLS）增加

**描述**：Skeleton 尺寸不准确可能导致内容加载后发生跳动

**缓解措施**：
- 使用实际组件的样式 token 构建 Skeleton
- 为 Skeleton 设置固定的 `minHeight`
- 使用 Chrome DevTools 的 CLS 审计工具验证
- 在 staging 环境进行 A/B 测试

### 风险 2：组件复杂度增加

**描述**：多个 Suspense 边界和 Await 组件使代码更复杂

**缓解措施**：
- 提取可复用的流式渲染组件（如 `<StreamedChapterTitle>`）
- 编写详细的代码注释和最佳实践文档
- 进行团队代码审查，确保一致性
- 考虑使用 React Router 的 `defer` 工具函数简化代码（如果 v7 支持）

### 风险 3：SEO 回归

**描述**：流式传输可能影响爬虫对完整内容的抓取

**缓解措施**：
- 现有的 `isbot` 检查已使用 `onAllReady` 策略，确保爬虫获得完整内容
- 使用 Google Search Console 验证抓取效果
- 在 staging 环境模拟爬虫请求测试
- 监控核心页面的索引覆盖率

### 风险 4：过度优化

**描述**：某些页面的数据加载时间很短（< 100ms），流式渲染可能不明显

**缓解措施**：
- 在改造前使用 Chrome DevTools 测量实际性能
- 优先优化用户访问量大、数据加载慢的页面
- 设置性能阈值（如 TTFB > 150ms 才考虑流式）
- 通过真实用户监控（RUM）验证优化效果

### 风险 5：维护成本

**描述**：更多的 Skeleton 组件和 Suspense 边界增加维护负担

**缓解措施**：
- 建立设计系统级别的 Skeleton 组件库
- 提供 CLI 工具自动生成 Skeleton 模板
- 定期审查和清理不再使用的 Skeleton
- 在组件文档中明确标注流式渲染的使用场景

## Migration Plan

### 阶段 1：验证模式（1-2 天）

**目标**：在低风险页面验证流式渲染模式

**步骤**：
1. 选择一个低流量的简单页面（如课程列表页的某个子页面）
2. 改造 loader 移除 `await`，组件中添加 Suspense 边界
3. 创建匹配的 Skeleton 组件
4. 使用 Chrome DevTools 测量性能指标（TTFB, FCP, LCP, TTI）
5. 进行代码审查，确保模式正确

**验收标准**：
- TTFB 减少 > 60%
- CLS < 0.1
- 无功能回归

### 阶段 2：核心页面改造（3-5 天）

**目标**：改造章节详情页和课程详情页

**步骤**：
1. **章节详情页改造**
   - 修改 loader：移除 `await Promise.all`
   - 添加多个 Suspense 边界（标题、内容、题目、侧边栏）
   - 创建/优化 4 个 Skeleton 组件
   - 处理 `chapter.id` 依赖问题（侧边栏需要当前章节 ID）
   - 更新错误处理逻辑

2. **课程详情页改造**
   - 采用相同模式
   - 创建对应的 Skeleton 组件

3. **测试和验证**
   - 单元测试：验证 loader 返回正确的 Promise 对象
   - 集成测试：验证 Suspense 边界正常工作
   - 性能测试：使用 Lighthouse 和 WebPageTest
   - 用户测试：验证渐进式加载的感知体验

**验收标准**：
- FCP 减少 > 50%
- LCP 减少 > 30%
- CLS < 0.1
- 所有现有测试通过

### 阶段 3：最佳实践固化（1-2 天）

**目标**：总结模式，为团队提供指导

**步骤**：
1. 编写流式渲染最佳实践文档
2. 创建可复用的流式组件模板
3. 提供 ESLint 规则（如禁止在 loader 中使用 `await Promise.all`）
4. 进行团队分享和培训

**交付物**：
- `docs/streaming-render-guide.md`
- `app/components/streaming/` 组件库
- ESLint 插件或规则配置

### 阶段 4：全面推广（持续）

**目标**：将模式应用到其他适合的页面

**步骤**：
1. 识别其他使用 `await Promise.all` 的页面
2. 按优先级（流量 × 性能提升）排序
3. 逐步改造，每个页面遵循阶段 2 的流程
4. 持续监控性能指标

### 回滚策略

**触发条件**：
- CLS > 0.25（Core Web Vitals "需改进"阈值）
- 用户投诉增加 > 20%
- 发现严重的 SEO 回退

**回滚步骤**：
1. 使用 Git revert 快速回滚到前一版本
2. 分析根本原因
3. 修复后重新部署

**缓解措施**：
- 使用 feature flag 控制流式渲染的启用
- 分阶段发布（先 10% 用户，再 50%，最后 100%）
- 保持旧代码分支的可用性

## Open Questions

1. **章节 ID 依赖问题**：侧边栏组件需要 `chapter.id`，但 `chapter` 数据还在流式传输中，如何处理？
   - 选项 A：从 URL params 派生（`params.chapterId`）
   - 选项 B：将侧边栏的 Suspense 边界嵌套在 chapter 的 Await 中
   - **待决定**：需要评估用户体验影响

2. **性能监控**：如何持续监控流式渲染的性能收益？
   - 需要集成真实的用户监控（RUM）工具
   - **待决定**：选择哪个 RUM 提供商（如 Vercel Analytics, Cloudflare Web Analytics）

3. **移动端优化**：移动端的 Suspense 边界是否需要不同的策略？
   - 移动端网络更慢，可能需要更激进的流式策略
   - **待决定**：是否为移动端创建独立的 Skeleton 和边界

4. **服务端缓存**：是否需要在 API 层添加更细粒度的缓存控制？
   - 例如：章节内容可以缓存 5 分钟，题目列表缓存 1 分钟
   - **待决定**：需要分析后端 API 的缓存策略
