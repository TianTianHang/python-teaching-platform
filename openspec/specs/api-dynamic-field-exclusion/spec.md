# 动态字段排除 API Spec

## ADDED Requirements

### Requirement: Exclude query parameter

系统 SHALL 支持 `exclude` 查询参数，允许客户端指定要从响应中排除的字段列表。

#### Scenario: 成功排除单个字段
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=code`
- **THEN** 响应中不包含 `code` 字段
- **AND** 其他字段正常返回

#### Scenario: 成功排除多个字段
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=code,output,error`
- **THEN** 响应中不包含 `code`、`output`、`error` 字段
- **AND** 其他字段正常返回

#### Scenario: 字段顺序无关性
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=code,output`
- **AND** 另一个客户端请求 `GET /api/submissions/?exclude=output,code`
- **THEN** 两个请求返回相同的数据
- **AND** 生成相同的缓存键

#### Scenario: 不包含 exclude 参数
- **WHEN** 客户端请求 `GET /api/submissions/`（不包含 exclude 参数）
- **THEN** 返回完整的响应数据
- **AND** 行为与未实现此功能时相同

### Requirement: 字段验证

系统 SHALL 验证 `exclude` 参数中的字段名是否有效。如果包含无效字段名，系统 SHALL 返回 400 错误。

#### Scenario: 无效字段名
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=invalid_field,code`
- **THEN** 系统返回 HTTP 400 Bad Request
- **AND** 错误消息包含无效字段名列表：`Invalid fields: {'invalid_field'}`

#### Scenario: 所有字段都无效
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=foo,bar,baz`
- **THEN** 系统返回 HTTP 400 Bad Request
- **AND** 错误消息列出所有无效字段

#### Scenario: 空字符串参数
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=`
- **THEN** 系统忽略该参数
- **AND** 返回完整的响应数据

#### Scenario: 重复字段名
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=code,code,output`
- **THEN** 系统自动去重
- **AND** 视为 `exclude=code,output`

### Requirement: 缓存键集成

系统 SHALL 将规范化后的 `exclude` 参数包含在缓存键中，确保不同的字段排除组合生成不同的缓存键。

#### Scenario: 不同排除参数生成不同缓存键
- **WHEN** 客户端 A 请求 `GET /api/submissions/?exclude=code`
- **AND** 客户端 B 请求 `GET /api/submissions/?exclude=code,output`
- **THEN** 两个请求生成不同的缓存键
- **AND** 缓存数据不互相干扰

#### Scenario: 相同排除参数生成相同缓存键
- **WHEN** 客户端 A 请求 `GET /api/submissions/?exclude=code,output`
- **AND** 客户端 B 请求 `GET /api/submissions/?exclude=output,code`（顺序不同）
- **THEN** 两个请求生成相同的缓存键（字段顺序已规范化）
- **AND** 第二个请求命中第一个请求的缓存

### Requirement: 嵌套序列化器字段排除

系统 SHALL 支持排除嵌套序列化器的顶级字段，但不需要支持嵌套字段路径（如 `user.password`）。

#### Scenario: 排除嵌套序列化器对象
- **WHEN** 响应包含嵌套序列化器（如 `user` 字段）
- **AND** 客户端请求 `GET /api/submissions/?exclude=user`
- **THEN** 响应中不包含整个 `user` 对象

#### Scenario: 不能排除嵌套字段路径
- **WHEN** 客户端请求 `GET /api/submissions/?exclude=user.username`
- **THEN** 系统返回 HTTP 400 Bad Request
- **AND** 错误消息说明不支持嵌套字段路径

### Requirement: SerializerMethodField 支持

系统 SHALL 正确处理 `SerializerMethodField` 类型的字段，支持排除。

#### Scenario: 排除方法字段
- **WHEN** 响应包含方法字段（如 `is_unlocked`）
- **AND** 客户端请求 `GET /api/problems/?exclude=is_unlocked`
- **THEN** 响应中不包含 `is_unlocked` 字段
- **AND** 对应的方法不会被调用（性能优化）

### Requirement: 向后兼容

系统 SHALL 保持向后兼容，不使用 `exclude` 参数的请求行为不变。

#### Scenario: 现有客户端不受影响
- **WHEN** 现有客户端请求 `GET /api/submissions/`（不包含 exclude 参数）
- **THEN** 响应格式与实现此功能前完全相同
- **AND** 不引入任何破坏性变更

### Requirement: 分页响应支持

系统 SHALL 在分页响应中正确支持字段排除。

#### Scenario: 分页列表排除字段
- **WHEN** 客户端请求 `GET /api/submissions/?page=1&page_size=20&exclude=code`
- **THEN** 返回分页响应
- **AND** `results` 数组中的每个对象都不包含 `code` 字段
- **AND** 分页元数据（count, next, previous）正常返回

### Requirement: 详情响应支持

系统 SHALL 在详情（retrieve）响应中正确支持字段排除。

#### Scenario: 详情排除字段
- **WHEN** 客户端请求 `GET /api/submissions/123/?exclude=code,output`
- **THEN** 返回单个提交对象
- **AND** 该对象不包含 `code` 和 `output` 字段
- **AND** 其他字段正常返回
