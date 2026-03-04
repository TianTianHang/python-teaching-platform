## 1. 题目列表页 (_layout.problems.tsx)

- [x] 1.1 移除 server loader，使用 useEffect + clientHttp 获取数据
- [x] 1.2 添加加载状态 (useState)
- [x] 1.3 添加错误处理 (401 跳转登录页)
- [x] 1.4 添加 Skeleton 组件作为加载占位
- [x] 1.5 运行 typecheck 验证

## 2. 题目详情页 (problems.$problemId/route.tsx)

- [x] 2.1 移除 server loader，使用 useEffect 获取数据
- [x] 2.2 处理 next_type/next_id 参数的客户端获取
- [x] 2.3 保持 ProblemPage 组件逻辑不变
- [x] 2.4 添加错误处理和加载状态
- [x] 2.5 运行 typecheck 验证

## 3. 题目描述页 (problems.$problemId.description.tsx)

- [x] 3.1 分析当前 loader 实现 (无 loader，使用 parent route data)
- [x] 3.2 迁移到客户端 useEffect (独立获取数据)
- [x] 3.3 运行 typecheck 验证

## 4. 提交记录页 (problems.$problemId.submissions.tsx)

- [x] 4.1 分析当前 loader 实现
- [x] 4.2 迁移到客户端 useEffect
- [x] 4.3 运行 typecheck 验证

## 5. 代码检查页 (problems.$problemId.check.tsx)

- [x] 5.1 分析当前 loader 实现 (无 loader，仅有 action)
- [x] 5.2 迁移到客户端 useEffect (N/A - action 无需迁移)
- [x] 5.3 运行 typecheck 验证 (N/A)

## 6. 保存草稿页 (problems.$problemId.save_draft.tsx)

- [x] 6.1 分析当前 loader 实现 (无 loader，仅有 action)
- [x] 6.2 迁移到客户端 useEffect (N/A - action 无需迁移)
- [x] 6.3 运行 typecheck 验证 (N/A)

## 7. 标记完成页 (problems.$problemId.mark_as_solved.tsx)

- [x] 7.1 分析当前 loader 实现 (无 loader，仅有 action)
- [x] 7.2 迁移到客户端 useEffect (N/A - action 无需迁移)
- [x] 7.3 运行 typecheck 验证 (N/A)

## 8. 最新草稿页 (problems.$problemId.latest_draft.tsx)

- [x] 8.1 分析当前 loader 实现
- [x] 8.2 迁移到客户端 useEffect
- [x] 8.3 运行 typecheck 验证

## 9. 验证测试

- [ ] 9.1 启动开发服务器 (pnpm run dev)
- [ ] 9.2 登录后访问题目列表，验证加载正常
- [ ] 9.3 访问题目详情，验证显示正常
- [ ] 9.4 测试题目提交功能
- [ ] 9.5 测试 Token 过期自动刷新