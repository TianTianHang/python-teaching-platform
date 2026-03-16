## Why

当前代码评测系统在处理测试用例输入时，只支持标准JSON格式。这导致Python特有的数据类型（如元组 `(1,2,3)`、`True`/`False`/`None` 等）无法直接使用。例如，测试用例输入 `[(1,2,3),2]` 会解析失败，因为JSON不支持元组语法，用户必须改为 `[[1,2,3],2]` 才能正常工作。这增加了题目设计者的负担，也降低了测试用例的可读性。

## What Changes

- 增强 `generate_judge0_code()` 函数生成的代码模板，支持Python字面量解析
- 使用 `ast.literal_eval()` 安全地解析Python基础类型（元组、集合、布尔值、None等）
- 保持向后兼容：优先尝试JSON解析，失败后再尝试Python字面量
- 列表和元组都支持解包为位置参数，行为保持一致

## Capabilities

### New Capabilities
- `test-case-input-parsing`: 测试用例输入解析能力，支持JSON和Python字面量两种格式

### Modified Capabilities
<!-- 无需求层面的变更，仅为实现细节增强 -->

## Impact

- **受影响文件**: `backend/courses/services.py` 中的 `generate_judge0_code()` 函数
- **API变更**: 无
- **数据库变更**: 无
- **测试用例格式**: 现有JSON格式测试用例保持兼容，新增支持Python字面量格式
