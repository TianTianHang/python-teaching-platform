# 通用动态字段排除 API

## Why

当前后端 API 返回完整的数据模型，导致大量不必要的数据传输。例如：
- **Problems API**：列表页返回 `content`、`test_cases` 等大字段，造成 70-80% 数据冗余
- **Submission API**：提交历史列表返回完整 `code`、`output`、`error`，冗余可能超过 90%
- **Chapter API**：章节列表返回完整 `content`（富文本+图片），数据量巨大

虽然 `ProblemViewSet` 已实现 `exclude` 参数，但该实现是重复代码，无法复用到其他 ViewSet。需要创建通用的 Mixin 机制，让所有 API 都能享受字段排除的优化。

## What Changes

- **新增通用 Mixin**：创建 `DynamicFieldsMixin`（ViewSet 层）和 `DynamicFieldsSerializerMixin`（Serializer 层）
- **缓存键集成**：将 `exclude` 参数规范化后加入缓存键，避免缓存数据混乱
- **字段验证**：自动验证排除字段的合法性，防止无效字段名
- **向后兼容**：不影响现有 API，可选使用 `exclude` 参数

## Capabilities

### New Capabilities
- `dynamic-field-exclusion`：通过 `?exclude=field1,field2` 查询参数动态排除响应字段的能力

### Modified Capabilities
无（仅新增可选功能，不改变现有 API 行为）

## Impact

**影响的代码**：
- `backend/common/mixins/__init__.py`：新增 `DynamicFieldsMixin`
- `backend/common/serializers.py`：新增 `DynamicFieldsSerializerMixin`
- `backend/common/mixins/cache_mixin.py`：修改 `_get_allowed_cache_params()` 包含 `exclude`
- `backend/courses/views.py`：`SubmissionViewSet`、`ChapterViewSet` 等应用 `DynamicFieldsMixin`
- `backend/courses/serializers.py`：对应的 Serializer 应用 `DynamicFieldsSerializerMixin`

**API 变更**：
- 所有使用 `DynamicFieldsMixin` 的 ViewSet 支持可选的 `exclude` 查询参数
- 例如：`GET /api/submissions/?exclude=code,output,error`

**性能影响**：
- ✅ 响应大小减少 70-90%（取决于使用场景）
- ✅ 数据传输时间显著降低
- ⚠️ 缓存变体增加（不同的 exclude 组合生成不同的缓存键）
- ✅ 通过规范化 exclude 字段顺序，最大化缓存命中率

**依赖变更**：无新增依赖
