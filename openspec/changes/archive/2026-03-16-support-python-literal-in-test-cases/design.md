## Context

当前代码评测系统的输入解析逻辑位于 `backend/courses/services.py` 的 `generate_judge0_code()` 函数中。该函数生成一个 Python 代码模板，在 Judge0 沙箱环境中执行。现有逻辑：

```python
try:
    args = json.loads(input_data)
except json.JSONDecodeError:
    args = input_data.split(", ")  # Fallback
```

问题：
- JSON 不支持元组 `(1,2,3)`、集合 `{1,2,3}`、`True`/`False`/`None` 等 Python 特有类型
- 用户输入 `[(1,2,3),2]` 会解析失败，因为 `(1,2,3)` 不是合法 JSON

## Goals / Non-Goals

**Goals:**
- 支持 Python 字面量类型：元组、集合、`True`/`False`、`None`、复数等
- 保持向后兼容：现有 JSON 格式测试用例继续正常工作
- 保证解析安全性：不使用 `eval()`，避免代码注入风险
- 保持参数解包行为一致

**Non-Goals:**
- 不支持自定义类型或类实例
- 不支持表达式计算（如 `1+2`、`len([1,2])`）
- 不修改数据库中的现有测试用例
- 不涉及前端 UI 变更

## Decisions

### 决策 1：使用 `ast.literal_eval()` 解析 Python 字面量

**选择**: 使用 Python 标准库 `ast.literal_eval()` 安全解析

**理由**:
- `ast.literal_eval()` 只解析字面量，不执行任意代码，比 `eval()` 安全
- 支持所有 Python 基础类型：列表、元组、字典、集合、数字、字符串、布尔值、None
- 是 Python 标准库，无额外依赖

**替代方案考虑**:
- 使用 `eval()`：❌ 安全风险，可能执行恶意代码
- 自定义解析器：❌ 复杂度高，容易遗漏边界情况

### 决策 2：解析顺序 - JSON 优先

**选择**: 先尝试 `json.loads()`，失败后再尝试 `ast.literal_eval()`

**理由**:
- JSON 是标准格式，解析速度快
- 保持向后兼容，现有测试用例行为不变
- JSON 解析失败才回退到 Python 字面量解析

```python
def parse_input(input_data):
    # 1. 优先尝试 JSON
    try:
        return json.loads(input_data)
    except json.JSONDecodeError:
        pass

    # 2. 尝试 Python 字面量
    try:
        return ast.literal_eval(input_data)
    except (ValueError, SyntaxError):
        pass

    # 3. Fallback: 按逗号分割（兼容极简单题目）
    return input_data.split(', ') if ', ' in input_data else input_data
```

### 决策 3：参数解包行为保持一致

**选择**: 列表和元组都解包为位置参数

**理由**:
- 与现有行为一致，不会破坏已有题目
- 用户无需关心输入是列表还是元组

```python
if isinstance(args, (list, tuple)):
    result = solve_func(*args)  # 解包为位置参数
elif isinstance(args, dict):
    result = solve_func(**args)  # 解包为关键字参数
else:
    result = solve_func(args)  # 单个参数
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| `ast.literal_eval()` 解析错误信息不够友好 | 在模板中添加简单错误处理，解析失败时返回明确错误 |
| 某些边界情况（如空字符串）可能解析为 `None` | 保留现有 Fallback 逻辑，确保不会崩溃 |
| 用户可能误用不支持的类型（如函数调用） | 在文档中明确说明支持的类型范围 |

## Migration Plan

**部署步骤**:
1. 修改 `backend/courses/services.py` 中的 `generate_judge0_code()` 函数
2. 运行现有测试用例确保向后兼容
3. 新增测试用例验证 Python 字面量支持

**回滚策略**:
- 直接回滚代码修改即可，不影响数据库或现有数据

## Open Questions

无
