# Problems API 动态字段过滤优化

## Why

当前 `/problems/` API 在列表页面返回了大量不必要的数据，导致严重的网络传输浪费和性能问题：

- **数据冗余率高达 83%**：每页 10 个题目返回约 300KB 数据，其中 250KB 是前端不需要的冗余数据
- **嵌套数据过深**：每个 problem 包含 3 个完整讨论线程 + 60 条回复 + 63 个用户对象（~220KB）
- **大文本字段冗余**：`content` 字段包含完整的 markdown 内容（~20KB），列表页完全不需要
- **前端解析负担**：需要解析大量无用数据，影响页面加载速度

这些问题在移动网络和低带宽环境下更为严重，需要立即优化以提升用户体验。

## What Changes

### 新增能力

- **动态字段排除参数**：API 支持通过 `?exclude=fields` 参数动态排除不需要的字段
  - 例如：`GET /problems/?exclude=content,recent_threads` 仅返回基础字段
  - 例如：`GET /problems/?exclude=content,recent_threads,status,chapter_title` 精确控制返回字段

- **智能查询优化**：当 `recent_threads` 被排除时，自动跳过 `discussion_threads` 的预取查询，避免不必要的数据库访问

### API 变更

- **`GET /problems/`** 列表接口：
  - 新增查询参数 `exclude`（可选）：逗号分隔的要排除的字段名
  - 保持向后兼容：不传 `exclude` 参数时行为不变

- **`GET /problems/{id}/`** 详情接口：
  - 新增查询参数 `exclude`（可选）：允许在详情页也排除特定字段
  - 保持向后兼容：不传 `exclude` 参数时行为不变

### 实现细节

- 修改 `ProblemSerializer` 添加动态字段过滤逻辑
- 修改 `ProblemViewSet` 支持解析和传递 `exclude` 参数
- 优化 `get_queryset()` 根据 `exclude` 参数动态调整 `prefetch_related`

## Capabilities

### New Capabilities

- **`api-dynamic-field-exclusion`**：API 动态字段排除能力
  - 允许客户端通过查询参数指定要排除的字段
  - 自动优化嵌套查询，避免加载被排除字段的数据
  - 支持多个字段批量排除

### Modified Capabilities

无。这是纯 API 层面的性能优化，不改变业务逻辑或需求规范。

## Impact

### Affected Components

- **Backend**：
  - `backend/courses/serializers.py` - `ProblemSerializer` 添加字段过滤逻辑
  - `backend/courses/views.py` - `ProblemViewSet` 添加 `exclude` 参数支持

- **Frontend**：
  - `frontend/web-student/app/routes/_layout.problems.tsx` - 更新 API 调用添加 `exclude` 参数
  - `frontend/web-student/app/types/course.ts` - 类型定义保持不变（可选字段）

### 性能预期

- **网络传输**：减少约 70-80% 的响应数据量（从 300KB 降至 50-60KB）
- **数据库查询**：当排除 `recent_threads` 时，避免预取 `discussion_threads` 表
- **前端解析**：减少 JSON 解析和对象创建开销
- **页面加载**：预期提升 30-50% 的列表页加载速度

### 风险评估

- **低风险**：完全向后兼容，不传参数时行为不变
- **渐进式**：前端可逐步迁移，先优化列表页，再优化其他页面
- **测试友好**：可单独测试 exclude 参数的各项功能

### 依赖影响

无外部依赖变更。仅涉及项目内部的 API 层优化。
