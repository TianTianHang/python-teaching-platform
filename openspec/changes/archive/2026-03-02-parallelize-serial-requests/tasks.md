# 并行化串行请求优化 - 任务清单

## 1. 核心页面优化 (高优先级)

### 1.1 章节详情页优化

- [x] 1.1.1 使用 `Promise.all` 并行化 `chapter`、`problems`、`courseChapters` 三个请求
- [x] 1.1.2 将 `mark_as_completed` POST 请求改为异步执行（移除 `await`，添加 `.catch()`）
- [x] 1.1.3 保持 `unlock_status` 串行检查的快速失败机制
- [x] 1.1.4 验证 TypeScript 类型安全，添加泛型类型标注（如 `Promise.all<[Chapter, Page<Problem>, Page<Chapter>]>`）

### 1.2 章节列表页优化

- [x] 1.2.1 使用 `Promise.all` 并行化 `course` 和 `chapters` 请求
- [x] 1.2.2 保持现有的查询参数（`exclude=content`，分页参数）

### 1.3 考试列表页优化

- [x] 1.3.1 使用 `Promise.all` 并行化 `course` 和 `exams` 请求
- [x] 1.3.2 保持 `course` 用于页面头部信息，`exams` 用于列表渲染

### 1.4 课程详情页优化

- [x] 1.4.1 使用 `Promise.all` 并行化 `course` 和 `userEnrollments` 请求
- [x] 1.4.2 保持 `enrollment` 的条件逻辑（从 `userEnrollments.results[0]` 提取）

## 2. 验证和测试

### 2.1 本地功能测试

- [x] 2.1.1 启动 SSR 服务 (`pnpm run start`)
- [x] 2.1.2 手动测试章节详情页：访问 `/courses/2/chapters/7`，验证数据正常显示
- [x] 2.1.3 手动测试章节列表页：访问 `/courses/2/chapters`，验证课程和章节列表正常
- [x] 2.1.4 手动测试考试列表页：访问 `/courses/2/exams`，验证课程和考试列表正常
- [x] 2.1.5 手动测试课程详情页：访问 `/courses/2`，验证课程和注册信息正常
- [x] 2.1.6 测试边界情况：访问锁定章节（如果有），验证快速失败和 redirect 正常
- [x] 2.1.7 测试错误场景：模拟网络错误，验证 `ResolveError` 组件正常显示

### 2.2 类型检查和构建验证

- [x] 2.2.1 运行 `pnpm run typecheck`，确保无 TypeScript 错误
- [x] 2.2.2 运行 `pnpm run build`，确保构建成功

### 2.3 性能测试 (可选)

- [ ] 2.3.1 运行 Locust 负载测试，记录优化前的基线性能 (P50, P95, P99 延迟，吞吐量)
- [ ] 2.3.2 部署优化后，再次运行 Locust 负载测试
- [ ] 2.3.3 对比优化前后的性能指标，验证预期收益（延迟降低 30-70%，吞吐量提升 50-200%）

## 3. 文档和代码注释

- [x] 3.1 在章节详情页 loader 中添加注释，说明 `Promise.all` 并行化的原因
- [x] 3.2 在异步 POST 请求处添加注释，说明为什么不等待完成
- [ ] 3.3 (可选) 更新项目 CONTRIBUTING.md，添加 loader 性能优化最佳实践
