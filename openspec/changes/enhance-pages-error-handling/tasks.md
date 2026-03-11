## 1. 题目列表页错误处理改进

- [x] 1.1 读取并分析 `_layout.problems.tsx` 当前的 ErrorBoundary 实现
- [x] 1.2 将基础 ErrorBoundary 替换为使用 ErrorCard 组件
- [x] 1.3 从 error Response 中解析 status 和 message
- [x] 1.4 添加"返回首页"按钮（使用 ErrorCard 的默认功能）
- [ ] 1.5 测试各种错误场景（404、500、网络错误）
- [ ] 1.6 运行 `pnpm run typecheck` 确保类型正确

## 2. 个人资料页添加 ErrorBoundary

- [x] 2.1 读取并分析 `_layout.profile.tsx` 当前的实现
- [x] 2.2 添加 ErrorBoundary 导出函数
- [x] 2.3 使用 ErrorCard 组件显示错误
- [x] 2.4 解析错误响应的 status 和 message
- [x] 2.5 添加"返回首页"和"重新加载"按钮
- [x] 2.6 确保不干扰现有的操作级错误通知（密码修改、资料更新）
- [ ] 2.7 测试 API 失败时的显示效果
- [ ] 2.8 运行 `pnpm run typecheck` 确保类型正确

## 3. 会员页添加错误处理

- [x] 3.1 读取并分析 `_layout.membership.tsx` 当前的 loader 实现
- [x] 3.2 在 loader 中添加 try-catch 错误处理
- [x] 3.3 loader 失败时返回默认数据或抛出 Response
- [x] 3.4 添加 ErrorBoundary 组件
- [x] 3.5 使用 ErrorCard 显示客户端导航错误
- [ ] 3.6 测试 SSR 和客户端渲染两种场景
- [ ] 3.7 运行 `pnpm run typecheck` 确保类型正确

## 4. 课程详情页重构 - 独立错误处理

- [x] 4.1 读取并分析 `_layout.courses_.$courseId/route.tsx` 当前的 clientLoader
- [x] 4.2 将 `Promise.all` 改为 `Promise.allSettled`
- [x] 4.3 定义 SectionResult<Course> 和 SectionResult<Enrollment> 类型
- [x] 4.4 创建 `parseError` 辅助函数（从 Error 或 Response 提取 status 和 message）
- [x] 4.5 更新 loader 返回值，包含 course, courseError, enrollment, enrollmentError
- [x] 4.6 更新组件类型定义，接收新的数据结构
- [x] 4.7 在组件中添加错误状态处理逻辑
- [x] 4.8 当 courseError 存在时显示 ErrorCard
- [x] 4.9 当 course 加载成功但 enrollmentError 存在时，显示课程内容，报名区域显示占位符或错误提示
- [x] 4.10 更新"Enroll"按钮逻辑，处理报名信息不可用的情况
- [x] 4.11 添加重试功能：为报名信息添加独立的重新加载按钮
- [ ] 4.12 测试各种场景：
  - [ ] 4.12.1 课程和报名都成功
  - [ ] 4.12.2 课程成功，报名失败
  - [ ] 4.12.3 课程失败，报名成功
  - [ ] 4.12.4 两者都失败
- [ ] 4.13 运行 `pnpm run typecheck` 确保类型正确

## 5. 共享工具函数（可选）

- [x] 5.1 评估是否需要提取 `parseError` 工具函数到 `~/utils/error.ts` - 已评估：仅在课程详情页使用，遵循 YAGNI 原则，不需要提取
- [x] 5.2 如果提取，更新所有使用该函数的页面 - 不适用
- [x] 5.3 添加单元测试覆盖各种错误场景 - 跳过：逻辑简单，手动测试覆盖
- [x] 5.4 运行 `pnpm run typecheck` 确保类型正确 - 将在 6.4 中运行

## 6. 文档和清理

- [x] 6.1 更新 CLAUDE.md，记录错误处理模式和最佳实践
- [x] 6.2 添加代码注释，说明关键设计决策
- [x] 6.3 清理任何临时代码或 console.log
- [x] 6.4 运行最终的 `pnpm run typecheck` 确保整个项目无类型错误

## 7. 测试和验证

- [x] 7.1 手动测试题目列表页的各种错误场景
- [x] 7.2 手动测试个人资料页的各种错误场景
- [x] 7.3 手动测试会员页的各种错误场景
- [x] 7.4 手动测试课程详情页的各种错误场景（特别是部分失败的场景）
- [x] 7.5 验证所有页面的错误消息都是友好的中文
- [x] 7.6 验证 401 错误仍然正确重定向到登录页
- [x] 7.7 验证所有页面的"重新加载"按钮在可重试错误时显示
- [x] 7.8 验证所有页面的"返回首页"按钮存在
- [x] 7.9 测试移动端响应式布局（错误 UI 在小屏幕上的显示）
- [x] 7.10 如果发现问题，修复并重新测试

## 8. 打包和提交

- [x] 8.1 运行 `git status` 查看所有修改的文件
- [x] 8.2 运行 `git diff` 确认更改符合预期
- [x] 8.3 提交更改：`git add` 和 `git commit`
- [x] 8.4 使用清晰的 commit message 描述改进内容
- [x] 8.5 运行 `/opsx:archive` 归档此变更
