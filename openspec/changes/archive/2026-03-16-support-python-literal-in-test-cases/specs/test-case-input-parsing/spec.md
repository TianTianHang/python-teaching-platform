## ADDED Requirements

### Requirement: 支持 JSON 格式输入解析

系统应当支持标准 JSON 格式作为测试用例输入，保持向后兼容。

#### Scenario: JSON 数组输入
- **WHEN** 测试用例输入为合法 JSON 数组（如 `[1, 2, 3]` 或 `["hello", 5]`）
- **THEN** 系统应当正确解析为 Python 列表，并解包为位置参数调用用户函数

#### Scenario: JSON 对象输入
- **WHEN** 测试用例输入为合法 JSON 对象（如 `{"n": 5, "s": "hello"}`）
- **THEN** 系统应当正确解析为 Python 字典，并解包为关键字参数调用用户函数

#### Scenario: JSON 字符串输入
- **WHEN** 测试用例输入为 JSON 字符串（如 `"hello"`）
- **THEN** 系统应当正确解析为 Python 字符串，并作为单个参数传递

### Requirement: 支持 Python 字面量输入解析

系统应当支持 Python 基础字面量类型，使得测试用例可以使用更自然的语法。

#### Scenario: 元组输入
- **WHEN** 测试用例输入为 Python 元组格式（如 `[(1,2,3), 2]` 或 `(1, 2, 3)`）
- **THEN** 系统应当正确解析为 Python 元组，并解包为位置参数调用用户函数

#### Scenario: 集合输入
- **WHEN** 测试用例输入为 Python 集合格式（如 `{1, 2, 3}`）
- **THEN** 系统应当正确解析为 Python 集合，并作为参数传递

#### Scenario: 布尔值输入
- **WHEN** 测试用例输入为 `True` 或 `False`
- **THEN** 系统应当正确解析为 Python 布尔值

#### Scenario: None 输入
- **WHEN** 测试用例输入为 `None`
- **THEN** 系统应当正确解析为 Python `None` 对象

#### Scenario: 混合类型输入
- **WHEN** 测试用例输入包含混合类型（如 `[(1,2,3), True, None, "text"]`）
- **THEN** 系统应当正确解析所有元素并保持类型

### Requirement: 解析安全性保证

系统必须保证输入解析过程的安全性，防止代码注入攻击。

#### Scenario: 拒绝执行任意代码
- **WHEN** 测试用例输入包含恶意代码（如 `__import__('os').system('rm -rf /')`）
- **THEN** 系统应当拒绝解析并抛出异常，不执行任何恶意代码

#### Scenario: 拒绝不支持的表达式
- **WHEN** 测试用例输入包含表达式（如 `1+2` 或 `len([1,2,3])`）
- **THEN** 系统应当拒绝解析或按字符串处理，不计算表达式结果

### Requirement: 解析优先级和 Fallback

系统应当按照明确的优先级顺序尝试不同的解析策略。

#### Scenario: JSON 优先解析
- **WHEN** 输入同时是合法 JSON 和合法 Python 字面量（如 `[1, 2, 3]`）
- **THEN** 系统应当优先使用 JSON 解析器处理

#### Scenario: Python 字面量回退
- **WHEN** 输入不是合法 JSON 但是合法 Python 字面量（如 `(1, 2, 3)` 或 `{1, 2, 3}`）
- **THEN** 系统应当使用 Python 字面量解析器处理

#### Scenario: 简单字符串 Fallback
- **WHEN** 输入既不是 JSON 也不是 Python 字面量（如 `hello, world`）
- **THEN** 系统应当按逗号分割作为 fallback，保持与旧版本兼容
