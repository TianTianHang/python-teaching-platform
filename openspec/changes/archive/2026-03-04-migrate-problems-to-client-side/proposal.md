## Why

将 Problems 模块从服务器端渲染迁移到客户端渲染，与已完成的 Home、Courses 模块保持一致性。当前 Problems 模块仍使用 SSR loader，在登录后访问时需要验证 session，增加了服务器复杂度。迁移到客户端后可直接使用 localStorage 中的 token，减少服务器端 session 验证开销。

## What Changes

迁移以下页面从 SSR loader 到客户端 useEffect 模式：

- `_layout.problems.tsx` - 题目列表页
- `problems.$problemId/route.tsx` - 题目详情页
- `problems.$problemId.description.tsx` - 题目描述页
- `problems.$problemId.submissions.tsx` - 提交记录页
- `problems.$problemId.check.tsx` - 代码检查页
- `problems.$problemId.save_draft.tsx` - 保存草稿页
- `problems.$problemId.mark_as_solved.tsx` - 标记完成页
- `problems.$problemId.latest_draft.tsx` - 最新草稿页

## Capabilities

### New Capabilities

此变更不引入新能力，仅为技术架构迁移。

### Modified Capabilities

无。现有功能行为保持不变，仅数据获取方式从 SSR 改为 CSR。

## Impact

- 前端路由：`frontend/web-student/app/routes/problems*.tsx`
- 后端 API：无变化
- 依赖：无新增依赖，复用现有的 `clientHttp` 工具