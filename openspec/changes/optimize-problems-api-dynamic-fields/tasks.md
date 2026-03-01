# Problems API 动态字段过滤优化 - 实施任务

## 1. 后端实现 - Serializer 修改

- [x] 1.1 在 `ProblemSerializer` 中添加 `to_representation()` 方法，实现字段过滤逻辑
  - 从 `context` 获取 `exclude_fields` 集合
  - 调用父类方法获取基础数据
  - 遍历 `exclude_fields`，从响应字典中移除指定字段

- [x] 1.2 修改 `ProblemSerializer.get_recent_threads()` 方法，支持跳过查询
  - 检查 `exclude_fields` 是否包含 `recent_threads`
  - 如果包含，直接返回 `None`，避免执行序列化查询
  - 如果不包含，使用现有的预取数据逻辑

## 2. 后端实现 - ViewSet 修改

- [x] 2.1 在 `ProblemViewSet` 中添加 `get_exclude_fields()` 辅助方法
  - 从 `request.query_params` 获取 `exclude` 参数
  - 分割字符串为字段列表，去除空格
  - 验证字段名是否有效（对比 `ProblemSerializer.Meta.fields`）
  - 如果包含无效字段，抛出 `serializers.ValidationError`
  - 返回字段集合供后续使用

- [x] 2.2 修改 `ProblemViewSet.get_queryset()` 方法，优化数据库查询
  - 调用 `get_exclude_fields()` 获取排除字段集合
  - 保持现有的 `select_related(chapter, unlock_condition)`
  - 添加条件判断：如果 `recent_threads` 不在排除集合中，才执行 `prefetch_related(discussion_threads)`

- [x] 2.3 修改 `ProblemViewSet.list()` 方法，传递 `exclude_fields` 到 serializer
  - 调用 `get_exclude_fields()` 获取排除字段
  - 在调用 `get_serializer()` 时，传递 `exclude_fields=exclude_fields` 到 context
  - 保持其他逻辑不变

- [x] 2.4 修改 `ProblemViewSet.retrieve()` 方法，支持详情页字段排除
  - 复用 `get_exclude_fields()` 和 serializer 传递逻辑
  - 保持与 list() 一致的行为

## 3. 后端测试

- [x] 3.1 添加字段排除功能单元测试
  - 测试排除单个字段：验证响应中不包含该字段，其他字段正常
  - 测试排除多个字段：验证所有指定字段都被排除
  - 测试字段名包含空格：验证正确解析和去除空格
  - 测试空 `exclude` 参数：验证返回所有字段

- [x] 3.2 添加无效字段名验证测试
  - 测试排除不存在的字段：验证返回 400 错误
  - 测试混合有效和无效字段：验证返回错误，不返回数据
  - 测试错误消息格式：验证包含无效字段列表

- [x] 3.3 添加数据库查询优化测试
  - 使用 `assertNumQueries()` 验证排除 `recent_threads` 时查询数量减少
  - 验证不排除时查询数量与现有实现一致
  - 测试详情页查询优化

- [x] 3.4 添加向后兼容性测试
  - 测试不提供 `exclude` 参数时响应与现有实现完全一致
  - 测试空 `exclude` 值时行为相同
  - 测试所有现有功能不受影响

- [x] 3.5 添加与其他查询参数的集成测试
  - 测试 `exclude` 与分页参数组合：验证分页正常，字段排除生效
  - 测试 `exclude` 与筛选参数组合：验证筛选正常，字段排除生效
  - 测试 `exclude` 与排序参数组合：验证排序正常，字段排除生效

- [x] 3.6 运行完整的测试套件
  ```bash
  cd /home/tiantian/project/python-teaching-platform/backend
  uv run python manage.py test courses.test_serializers
   uv run python manage.py test courses.test_views
   ```

## 4. 前端集成

- [x] 4.1 修改 `frontend/web-student/app/routes/_layout.problems.tsx`
  - 在 loader 中构造 `exclude` 参数字符串
  - 包含字段：`content`, `recent_threads`, `status`, `chapter_title`, `updated_at`
  - 更新 API 调用：`http.get<Page<Problem>>(\`/problems/?exclude=${excludeFields}\`)`

- [x] 4.2 前端类型检查
  ```bash
  cd /home/tiantian/project/python-teaching-platform/frontend/web-student
  pnpm run typecheck
  ```
  - 验证 TypeScript 类型正确（可选字段处理）

## 5. 性能验证

- [x] 5.1 使用浏览器 DevTools 验证响应大小减少
  - 在应用前后分别记录 `/problems/` API 的响应大小
  - 验证响应大小减少至少 70%（从 ~300KB 降至 ~50-60KB）

- [x] 5.2 使用 Django Debug Toolbar 或日志验证数据库查询减少
  - 排除 `recent_threads` 时验证不执行 `discussion_threads` 查询
  - 验证总查询数量从 N+2 减少到 2

- [x] 5.3 测试页面加载速度提升
  - 使用 Lighthouse 或浏览器性能工具测量页面加载时间
  - 验证加载速度提升 30-50%

## 6. 文档和清理

- [x] 6.1 添加 API 文档注释
  - 在 `ProblemViewSet` 中添加 `exclude` 参数的文档字符串
  - 说明参数格式、支持的字段列表、使用示例

- [x] 6.2 更新开发者文档（如需要）
  - 记录新的 `exclude` 参数使用方法
  - 提供示例和最佳实践

- [x] 6.3 代码审查和清理
  - 检查代码清晰度和可维护性
  - 添加必要的注释解释关键逻辑
  - 移除调试代码和临时日志

## 7. 部署准备

- [x] 7.1 准备迁移计划
  - 确认部署步骤：后端先行，前端跟进
  - 准备回滚方案：前端移除 `exclude` 参数即可回滚

- [x] 7.2 在测试环境验证
  - 部署到测试环境
  - 执行完整的测试套件
  - 手动测试关键用户场景

- [x] 7.3 监控和日志准备
  - 添加 `exclude` 参数使用情况的日志记录
  - 准备监控指标：响应大小、查询数量、响应时间
