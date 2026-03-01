# Specs 说明

此变更不创建新的 spec 文件，因为：

1. **已有完整的 spec 定义**：`openspec/specs/api-dynamic-field-exclusion/spec.md` 已经定义了动态字段排除的完整需求

2. **此变更是实现已有的 spec**：将 `api-dynamic-field-exclusion` spec 应用到更多的 ViewSet（Submission、Chapter、DiscussionThread）

3. **不涉及新的能力或需求变更**：所有的功能需求、约束条件、边界情况都已在现有 spec 中定义

## 引用的 Spec

- **openspec/specs/api-dynamic-field-exclusion/spec.md**：动态字段排除 API 的完整规范

此 spec 定义了：
- `exclude` 查询参数的行为
- 字段验证规则
- 缓存键集成要求
- 错误处理规范
- 向后兼容性要求

## 实施依据

此变更的实施应完全遵循 `openspec/specs/api-dynamic-field-exclusion/spec.md` 中定义的要求，确保新迁移的 ViewSet 与 ProblemViewSet 的行为一致。
