## Context

### Current State

平台各页面的错误处理存在不一致性：

1. **首页（已优化）**：使用 `Promise.allSettled`、独立的错误状态、ErrorCard 组件、重试功能
2. **课程详情页**：使用 `Promise.all`，一个 API 失败导致整个页面不可用
3. **题目列表页**：基础 ErrorBoundary，无友好错误提示
4. **个人资料页**：完全缺少 ErrorBoundary
5. **会员页**：SSR 但无错误处理

### Technical Constraints

- **SSR 兼容性**：clientLoader 必须在服务端和客户端都能工作
- **React Router v7**：使用 clientLoader 和 ErrorBoundary 模式
- **TypeScript 严格模式**：类型安全
- **中文平台**：错误消息必须本地化
- **已有 ErrorCard 组件**：复用首页优化的组件

### Stakeholders

- **最终用户**：需要友好的错误提示和恢复能力
- **开发者**：需要一致的错误处理模式，易于维护
- **平台**：需要提高可用性和专业形象

## Goals / Non-Goals

**Goals:**
- 为所有主要页面提供一致的错误处理体验
- 确保部分 API 失败不会导致整个页面不可用
- 提供基于状态码的友好中文错误消息
- 允许用户主动重试失败的操作
- 复用现有的 ErrorCard 组件，保持一致性

**Non-Goals:**
- 不修改后端 API 或错误响应格式
- 不改变现有的业务逻辑或功能需求
- 不重构整个数据加载架构（渐进式改进）
- 不为性能测试页添加特殊错误处理（它是诊断工具）

## Decisions

### 1. Promise.all vs Promise.allSettled

**Decision: 课程详情页使用 `Promise.allSettled`**

**Rationale:**
- 课程信息是核心内容，应该始终显示
- 报名信息是次要内容，可以延迟或失败
- `Promise.allSettled` 允许两个请求独立完成，一个失败不影响另一个

**Alternatives Considered:**
- **保持 `Promise.all`**： rejected - 会导致报名 API 失败时课程信息也无法显示
- **分离为两个独立的加载**： rejected - 增加复杂度，`allSettled` 更简洁
- **先加载课程，再加载报名**： rejected - 增加加载时间，用户体验差

### 2. 页面级 vs 组件级错误处理

**Decision: 保持页面级 ErrorBoundary，但不创建通用 wrapper 组件**

**Rationale:**
- 大多数页面只有一个数据源，页面级处理足够
- 创建 wrapper 组件会增加抽象层，可能过度设计
- 复用 ErrorCard 组件已经保证了一致性

**Alternatives Considered:**
- **创建通用的 `SectionWithError` wrapper**： rejected - 可能在后续迭代中需要，但现在不是必需的
- **为每个页面创建独立 Section 组件**： rejected - 只有课程详情页需要，其他页面单一数据源

### 3. SSR 页面的错误处理

**Decision: 会员页保持 SSR，添加 loader 错误处理和 ErrorBoundary**

**Rationale:**
- SSR 有 SEO 优势（虽然是会员页，但搜索引擎可能会索引）
- 首次加载性能更好
- 可以在 loader 中处理错误并返回默认数据

**Alternatives Considered:**
- **转换为 clientLoader**： rejected - 不必要的架构变更，SSR 工作良好
- **完全不处理错误**： rejected - 用户体验差

### 4. 错误处理模式

**Decision: 遵循首页优化的模式，但简化到页面级**

**Pattern for pages with single data source:**
```typescript
// clientLoader
try {
    const data = await clientHttp.get<Type>(endpoint);
    return data;
} catch (error: any) {
    if (error.response?.status === 401) {
        throw redirect('/auth/login');
    }
    throw new Response(JSON.stringify({ message: error.message }), {
        status: error.response?.status || 500,
        statusText: error.message
    });
}

// ErrorBoundary
export function ErrorBoundary({ error }: { error: Error }) {
    // Parse error from Response
    const status = parseInt((error as any).status);
    const message = (error as any).message || '加载失败';

    return <ErrorCard status={status} message={message} ... />;
}
```

**Pattern for pages with multiple data sources (Course Detail):**
```typescript
// clientLoader
const results = await Promise.allSettled([
    clientHttp.get<Course>(`/courses/${courseId}`),
    clientHttp.get<Enrollment>(`/enrollments/?course=${courseId}`)
]);

const courseResult = results[0];
const enrollmentResult = results[1];

return {
    course: courseResult.status === 'fulfilled' ? courseResult.value : null,
    courseError: courseResult.status === 'rejected' ? parseError(courseResult.reason) : null,
    enrollment: enrollmentResult.status === 'fulfilled' ? enrollmentResult.value : null,
    enrollmentError: enrollmentResult.status === 'rejected' ? parseError(enrollmentResult.reason) : null,
};
```

**Rationale:**
- 与首页模式一致，降低认知负担
- 简化实现，避免过度抽象
- ErrorCard 组件已经提供了友好消息和重试功能

### 5. 错误信息的本地化

**Decision: 继续使用 ErrorCard 组件内部的 `getFriendlyErrorMessage` 函数**

**Rationale:**
- 已有完善的中文消息映射
- 支持网络错误、超时、各种 HTTP 状态码
- 集中管理，易于维护

**Alternatives Considered:**
- **使用 i18n 库**： rejected - 增加依赖，平台目前是中文专用
- **分散到各页面**： rejected - 代码重复，不一致

## Implementation Strategy

### Phase 1: Quick Wins (1-2 hours)

1. **题目列表页** - 替换 ErrorBoundary，使用 ErrorCard
2. **个人资料页** - 添加 ErrorBoundary
3. **会员页** - 添加 ErrorBoundary

### Phase 2: Medium Effort (2-3 hours)

1. **课程详情页** - 重构为 `allSettled`，分离课程信息和报名信息的错误处理
2. 调整 UI，在报名信息加载失败时显示适当的占位符或重试按钮

### Phase 3: Polish (optional)

1. 提取共享的 `parseError` 工具函数
2. 更新文档，记录错误处理模式
3. 考虑创建可复用的错误处理 hook（如果多个页面需要类似逻辑）

## Risks / Trade-offs

### Risk 1: Promise.allSettled 增加复杂度
**Mitigation:**
- 提供清晰的类型定义和注释
- 遵循首页已验证的模式
- 编写测试用例覆盖各种失败场景

### Risk 2: SSR 页面的错误处理可能不一致
**Mitigation:**
- 保持 ErrorBoundary 用于客户端导航
- Loader 返回默认数据或抛出 Response
- 测试 SSR 和客户端渲染两种场景

### Risk 3: 过度抽象
**Mitigation:**
- 遵循 YAGNI 原则（You Aren't Gonna Need It）
- 只在多个页面真正需要时才创建通用组件
- 先实现具体页面，再识别共同模式

### Trade-off: 代码重复 vs 抽象
**Decision:**
- 接受适量的代码重复（ErrorCard 复用，但错误处理逻辑分散）
- 避免过早抽象
- 如果后续发现重复过多，再提取共同模式

## Open Questions

1. **是否需要创建通用的错误处理 hook（如 `useErrorRetry`）？**
   - 初步判断：不需要，各页面的重试逻辑差异较大
   - 待实现后评估是否需要

2. **课程详情页的报名信息加载失败时，"Enroll" 按钮的行为应该如何？**
   - 选项 A: 禁用按钮，显示错误消息
   - 选项 B: 保持按钮可用，点击时尝试报名（天然重试）
   - 初步建议：选项 B，因为报名操作本身就是重试

3. **是否需要为所有错误添加日志记录？**
   - 初步判断：是的，但可以后续添加
   - 建议使用现有的错误追踪系统（如果有的话）
