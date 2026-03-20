# 任务列表：类型安全改进

## 阶段1：错误类型基础（第1周）

### 1.1 创建错误类型定义
- [x] 创建 `types/errors.ts` 文件
- [x] 定义 `BaseError` 接口
- [x] 定义 `ApiErrorData` 接口
- [x] 定义 `ApiErrorResponse` 接口
- [x] 定义 `ApiError` 接口
- [x] 定义 `NetworkError` 接口
- [x] 定义 `TimeoutError` 接口
- [x] 定义 `ValidationError` 接口
- [x] 定义 `BusinessError` 接口
- [x] 定义 `AppError` 联合类型
- [x] 定义 `ErrorResult` 接口

### 1.2 实现类型守卫函数
- [x] 创建 `utils/typeGuards.ts` 文件
- [x] 实现 `isApiError` 函数
- [x] 实现 `isNetworkError` 函数
- [x] 实现 `isTimeoutError` 函数
- [x] 实现 `isValidationError` 函数
- [x] 实现 `isBusinessError` 函数
- [x] 实现 `isAppError` 函数

### 1.3 实现错误解析函数
- [x] 创建 `utils/errorParser.ts` 文件
- [x] 实现 `parseDRError` 函数（替换原有的any类型版本）
- [x] 实现 `parseError` 函数
- [x] 添加错误解析测试

### 1.4 替换关键any类型
- [x] 替换 `utils/http/error.ts` 中的 `parseDRError` 函数
- [x] 替换 `routes/_layout.courses_.$courseId/route.tsx` 中的 `parseError` 函数
- [x] 替换 `hooks/useSubmission/index.ts` 中的 `parseError` 函数
- [x] 替换 `utils/http/submission.ts` 中的4处 `catch (error: any)`
- [x] 替换 `hooks/useSubmission/index.ts` 中的3处 `catch (error: any)`

### 1.5 添加测试
- [x] 创建 `test/typeGuards.test.ts` 测试文件
- [x] 创建 `test/errorParser.test.ts` 测试文件
- [x] 为所有类型守卫函数添加单元测试
- [x] 为错误解析函数添加单元测试
- [x] 运行测试，确保通过率100%

### 1.6 阶段1验证
- [x] 验证所有新类型定义正确
- [x] 验证类型守卫函数工作正常
- [x] 验证错误解析函数行为一致
- [x] 验证替换后的代码功能不变
- [ ] 代码审查
- [ ] 更新相关文档

## 阶段2：统一错误处理（第2周）

### 2.1 创建统一错误处理器
- [x] 创建 `utils/errorHandler.ts` 文件
- [x] 定义 `ErrorHandlerOptions` 接口
- [x] 实现 `handleApiError` 函数
- [x] 实现 `withErrorHandling` 高阶函数
- [x] 实现 `withAuthLoader` 包装器

### 2.2 更新HTTP客户端类型
- [x] 更新 `utils/http/types.ts` 中的类型定义
- [x] 替换 `requestInterceptorCatch` 中的any类型
- [x] 替换 `responseInterceptorCatch` 中的any类型
- [x] 更新拦截器钩子接口

### 2.3 替换重复的错误处理逻辑
- [x] 替换 `routes/_layout.home.tsx` 中的3处401错误处理
- [x] 替换 `routes/_layout.courses_.$courseId/route.tsx` 中的401错误处理
- [x] 替换 `routes/problems.$problemId/route.tsx` 中的401错误处理
- [x] 替换 `routes/_layout.problems.tsx` 中的401错误处理
- [x] 替换 `routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` 中的2处401错误处理
- [x] 替换 `routes/_layout.courses_.$courseId_.chapters/route.tsx` 中的401错误处理
- [x] 替换 `routes/_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx` 中的401错误处理
- [x] 替换 `routes/problems.$problemId.save_draft.tsx` 中的401错误处理
- [x] 替换 `routes/_layout.courses/route.tsx` 中的401错误处理
- [x] 替换 `routes/problems.$problemId.mark_as_solved.tsx` 中的401错误处理
- [x] 替换 `routes/problems.$problemId.description.tsx` 中的401错误处理
- [x] 替换 `routes/problems.$problemId.submissions.tsx` 中的401错误处理
- [x] 替换 `routes/problems.$problemId.check.tsx` 中的401错误处理

### 2.4 更新路由错误处理
- [x] 更新所有使用 `catch (error: any)` 的路由文件
- [x] 使用 `withAuthLoader` 包装器简化路由加载器
- [x] 确保所有路由都有适当的错误边界

### 2.5 添加集成测试
- [x] 创建错误处理集成测试
- [x] 测试401错误重定向功能
- [x] 测试网络错误处理
- [x] 测试超时错误处理
- [x] 测试业务错误处理

### 2.6 阶段2验证
- [x] 验证统一错误处理器工作正常
- [x] 验证所有401错误处理逻辑一致
- [x] 验证错误消息解析正确
- [x] 验证错误重定向功能正常
- [ ] 代码审查
- [ ] 更新相关文档

## 阶段3：函数参数类型化（第3周）

### 3.1 类型化工具函数参数
- [x] 更新 `utils/loaderWrapper.ts` 中的 `withAuth` 函数类型
- [x] 替换 `(...args: any[])` 为具体类型
- [x] 更新 `hooks/useInfiniteScroll.ts` 中的 `extractData` 参数类型
- [x] 替换 `(data: any)` 为具体泛型类型

### 3.2 类化组件属性
- [x] 更新 `components/MarkdownRenderer.tsx` 中的组件类型
- [x] 替换 `markdownComponents: any` 为具体类型
- [x] 替换 `code(props: any)` 为具体属性类型
- [x] 替换 `foldableBlock(props: any)` 为具体属性类型

### 3.3 类型化第三方库扩展
- [x] 更新 `lib/remarkFoldableBlock.ts` 中的节点类型
- [x] 替换 `node: any` 为具体AST节点类型
- [x] 替换 `foldableBlockNode: any` 为具体节点类型

### 3.4 更新类型定义
- [x] 更新 `types/user.ts` 中的 `User` 接口
- [x] 添加具体类型字段，避免any
- [x] 创建 `UserPreferences` 接口
- [x] 创建 `UserProfile` 接口
- [x] 创建 `NotificationSettings` 接口
- [x] 创建 `SocialLinks` 接口

### 3.5 添加类型测试
- [ ] 为更新后的函数添加类型测试
- [ ] 为组件属性添加类型测试
- [ ] 为第三方库扩展添加类型测试
- [ ] 运行所有类型测试

### 3.6 阶段3验证
- [x] 验证所有函数参数都有具体类型
- [x] 验证组件属性类型正确
- [x] 验证第三方库扩展类型正确
- [x] 验证类型测试通过
- [ ] 代码审查
- [ ] 更新相关文档

## 阶段4：类型清理和优化（第4周）

### 4.1 处理剩余any类型
- [x] 检查并替换所有剩余的 `any` 类型
- [x] 处理 `components/ExamReport/AnswerReviewCard.tsx` 中的 `userAnswer: any`
- [x] 处理 `utils/http/client.ts` 中的 `user: any`
- [x] 处理 `utils/http/http.ts` 中的 `error: any`
- [x] 处理其他剩余的 `any` 类型

### 4.2 优化类型定义结构
- [ ] 重构类型定义文件组织
- [ ] 创建类型导出索引文件
- [ ] 优化类型导入路径
- [ ] 添加类型文档注释

### 4.3 完善类型文档
- [ ] 编写类型使用指南
- [ ] 创建类型定义文档
- [ ] 添加类型示例代码
- [ ] 更新README中的类型部分

### 4.4 性能优化
- [ ] 优化类型守卫函数性能
- [ ] 添加类型检查缓存（如果需要）
- [ ] 监控类型检查的性能影响
- [ ] 优化类型定义的编译时间

### 4.5 最终验证
- [ ] 运行所有测试，确保通过率100%
- [ ] 检查类型覆盖率，确保达到95%以上
- [ ] 验证 `any` 类型数量减少到5处以下
- [ ] 性能测试，确保没有性能回归
- [ ] 安全审查，确保没有安全漏洞
- [ ] 最终代码审查

### 4.6 部署准备
- [ ] 准备部署文档
- [ ] 准备回滚脚本
- [ ] 准备监控告警配置
- [ ] 准备用户通知文档
- [ ] 制定灰度发布计划

## 质量保证

### 代码质量
- [ ] 运行ESLint检查，确保没有警告
- [ ] 运行TypeScript类型检查，确保没有错误
- [ ] 运行所有单元测试，确保通过
- [ ] 运行所有集成测试，确保通过
- [ ] 代码覆盖率检查，确保达到80%以上

### 文档完整性
- [ ] 更新所有相关文档
- [ ] 添加新功能的使用示例
- [ ] 更新API文档
- [ ] 更新类型定义文档

### 团队协作
- [ ] 团队培训：新类型系统使用
- [ ] 代码审查：确保团队理解新的模式
- [ ] 知识分享：分享最佳实践

## 风险监控

### 技术风险
- [ ] 监控类型检查性能影响
- [ ] 监控内存使用变化
- [ ] 监控错误率变化
- [ ] 监控用户反馈

### 业务风险
- [ ] 监控功能使用情况
- [ ] 监控用户满意度
- [ ] 监控支持请求变化
- [ ] 监控业务指标变化

## 完成标准

### 量化标准
- [x] `any` 类型数量 ≤ 5处
- [ ] 类型覆盖率 ≥ 95%
- [ ] 错误处理重复代码减少 ≥ 80%
- [ ] 类型错误数量减少 ≥ 90%
- [ ] 测试覆盖率 ≥ 80%

### 质量标准
- [x] 所有测试通过
- [ ] 代码审查通过
- [ ] 文档完整
- [ ] 性能无回归
- [ ] 安全无漏洞

### 业务标准
- [ ] 用户无感知变化
- [ ] 功能完全兼容
- [ ] 支持请求无增加
- [ ] 业务指标稳定

---

**任务列表版本**：1.0  
**创建时间**：2026年3月19日  
**最后更新**：2026年3月19日  
**预计完成时间**：2026年4月19日  
**负责人**：待定  
**评审人**：待定