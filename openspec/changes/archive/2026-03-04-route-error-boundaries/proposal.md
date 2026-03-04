# 提案：路由级错误边界改进

## 概述

修复前端学生端 (`web-student`) 中4个关键路由页面的错误处理缺陷，防止 API 请求失败时整个页面崩溃，提升用户体验和系统稳定性。

## 问题背景

当前多个路由页面的 loader 函数存在以下问题：

1. **直接 await 而无错误捕获**：API 失败时抛出未捕获异常，导致整个页面崩溃
2. **Promise.all 风险**：并行请求中任何一个失败都会导致整个 loader 失败
3. **客户端 Await 缺少错误边界**：服务端返回的 Promise 在客户端解析失败时无降级处理

这些缺陷会导致：
- 用户看到白屏或错误堆栈
- 无法重试或返回上一页
- 影响核心学习流程（如课程学习、章节浏览、题目练习）

## 目标

### 主要目标

- ✅ 确保所有 API 请求失败时页面不会崩溃
- ✅ 为用户提供友好的错误提示和重试机制
- ✅ 保持现有功能不受影响（向后兼容）

### 次要目标

- 统一错误处理模式，便于后续维护
- 提供可复用的错误处理组件模式

## 范围

### 包含的页面

| 页面 | 文件路径 | 问题描述 |
|------|----------|----------|
| **章节详情页** | `app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` | `unlockStatus` 请求无错误处理，失败时页面崩溃 |
| **章节列表页** | `app/routes/_layout.courses_.$courseId_.chapters/route.tsx` | `Promise.all` 中的两个请求无错误处理 |
| **课程详情页** | `app/routes/_layout.courses_.$courseId/route.tsx` | `enrollmentPromise` 在客户端 `<Await>` 中缺少错误边界 |
| **题目详情页** | `app/routes/problems.$problemId/route.tsx` | 仅检查 `undefined`，未处理 API 错误响应 |

### 不包含的内容

- ❌ 后端 API 错误处理改进（超出范围）
- ❌ 全局错误边界组件重构（作为后续工作）
- ❌ 其他未列出的页面（如会员页、讨论页等，作为后续迭代）

## 成功标准

1. **功能验收**
   - [ ] 所有4个页面的 API 请求失败时，页面正常渲染错误提示
   - [ ] 用户可以通过"返回"按钮或刷新页面进行恢复
   - [ ] 错误提示清晰、友好，不暴露技术细节

2. **技术验收**
   - [ ] 所有 loader 都使用 `.catch()` 或 `withAuth` 包装
   - [ ] 客户端 `<Await>` 组件都有错误处理 children
   - [ ] 代码通过 TypeScript 类型检查
   - [ ] 现有功能回归测试通过

3. **性能验收**
   - [ ] 错误处理不影响正常情况下的性能
   - [ ] 错误恢复响应时间 < 100ms

## 风险与依赖

### 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 修改 loader 逻辑可能影响现有数据流 | 中 | 充分测试，保持返回数据结构一致 |
| 客户端 Await 错误处理可能引入新 bug | 中 | 参考 `_layout.problems.tsx` 的成熟模式 |
| 错误提示文案不准确 | 低 | 使用通用错误提示，如"加载失败，请重试" |

### 依赖

- 现有的 `ResolveError` 组件 (`app/components/ResolveError.tsx`)
- 现有的 `withAuth` 工具 (`app/utils/loaderWrapper.ts`)
- React Router 的 `<Await>` 组件错误处理机制

## 实施计划

### Phase 1: 章节详情页（高优先级）
- `unlockStatus` 添加 `.catch()` 处理
- 失败时显示友好错误提示

### Phase 2: 章节列表页（高优先级）
- `Promise.all` 拆分为独立请求，各自添加错误处理
- 使用 `Promise.allSettled` 或单独 `.catch()`

### Phase 3: 课程详情页（中优先级）
- `enrollmentPromise` 添加错误处理
- 客户端 `<Await>` 添加错误边界

### Phase 4: 题目详情页（中优先级）
- 完善 `problem === undefined` 检查逻辑
- 处理 API 错误响应对象

## 后续工作

- 评估其他页面的错误处理（会员页、讨论页等）
- 考虑创建全局错误边界组件
- 文档化错误处理最佳实践

## 参考资料

- React Router Error Handling: https://reactrouter.com/start/framework/errors
- 现有良好实践：`app/routes/_layout.problems.tsx:58-63`
- 现有良好实践：`app/routes/_layout.home.tsx:42-54`
