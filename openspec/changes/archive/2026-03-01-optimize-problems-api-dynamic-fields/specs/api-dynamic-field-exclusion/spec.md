# API 动态字段排除规范

## ADDED Requirements

### Requirement: 客户端可通过查询参数排除响应字段

系统 SHALL 支持客户端通过 `exclude` 查询参数指定要从 API 响应中排除的字段列表。

#### Scenario: 成功排除单个字段

- **WHEN** 客户端请求 `GET /problems/?exclude=content`
- **THEN** 系统返回 Problem 对象列表，其中不包含 `content` 字段
- **AND** 其他字段（如 `id`, `title`, `type` 等）正常返回

#### Scenario: 成功排除多个字段

- **WHEN** 客户端请求 `GET /problems/?exclude=content,recent_threads,chapter_title`
- **THEN** 系统返回 Problem 对象列表，其中不包含 `content`, `recent_threads`, `chapter_title` 字段
- **AND** 其他字段正常返回

#### Scenario: 字段列表中包含空格

- **WHEN** 客户端请求 `GET /problems/?exclude=content, recent_threads`（注意逗号后的空格）
- **THEN** 系统正确解析字段列表，去除空格
- **AND** 排除 `content` 和 `recent_threads` 字段

#### Scenario: 排除参数为空

- **WHEN** 客户端请求 `GET /problems/?exclude=`
- **THEN** 系统返回所有字段（不排除任何字段）
- **AND** 响应与不提供 `exclude` 参数时相同

### Requirement: 不提供 exclude 参数时保持向后兼容

系统 SHALL 在客户端不提供 `exclude` 参数时，返回所有字段，保持现有 API 行为。

#### Scenario: 不提供 exclude 参数

- **WHEN** 客户端请求 `GET /problems/`（不包含 `exclude` 参数）
- **THEN** 系统返回所有字段，包括 `content`, `recent_threads` 等
- **AND** 响应格式与现有实现完全一致

#### Scenario: 空字段列表

- **WHEN** 客户端请求 `GET /problems/?exclude=`（空值）
- **THEN** 系统返回所有字段
- **AND** 行为与不提供 `exclude` 参数相同

### Requirement: 排除不存在的字段时返回错误

系统 SHALL 在 `exclude` 参数中包含不存在或无效的字段名时，返回 400 错误及错误详情。

#### Scenario: 排除不存在的字段

- **WHEN** 客户端请求 `GET /problems/?exclude=nonexistent_field`
- **THEN** 系统返回 HTTP 400 Bad Request
- **AND** 错误响应包含 `exclude` 字段，说明哪些字段名无效
- **AND** 错误消息格式：`{"exclude": "Invalid fields: nonexistent_field"}`

#### Scenario: 混合有效和无效字段名

- **WHEN** 客户端请求 `GET /problems/?exclude=content,invalid_field`
- **THEN** 系统返回 HTTP 400 Bad Request
- **AND** 错误响应指出 `invalid_field` 无效
- **AND** 不返回任何数据（全部或无）

### Requirement: 详情页 API 同样支持字段排除

系统 SHALL 在详情页 API（`GET /problems/{id}/`）上支持相同的 `exclude` 参数功能。

#### Scenario: 详情页排除嵌套对象

- **WHEN** 客户端请求 `GET /problems/123/?exclude=recent_threads`
- **THEN** 系统返回指定 Problem 对象的详情
- **AND** 响应不包含 `recent_threads` 字段
- **AND** 其他字段（包括 `content`）正常返回

#### Scenario: 详情页排除多个字段

- **WHEN** 客户端请求 `GET /problems/123/?exclude=content,recent_threads,updated_at`
- **THEN** 系统返回 Problem 对象详情，不包含指定的三个字段
- **AND** 其他字段正常返回

### Requirement: 排除嵌套字段时优化数据库查询

系统 SHALL 在客户端排除 `recent_threads` 字段时，跳过 `discussion_threads` 表的预取查询，减少数据库负载。

#### Scenario: 排除 recent_threads 时不执行预取查询

- **WHEN** 客户端请求 `GET /problems/?exclude=recent_threads`
- **THEN** 系统在 `get_queryset()` 中不执行 `prefetch_related('discussion_threads')`
- **AND** 数据库查询数量减少（从 N+2 减少到 2）
- **AND** 响应时间显著减少

#### Scenario: 包含 recent_threads 时正常预取

- **WHEN** 客户端请求 `GET /problems/`（不排除 `recent_threads`）
- **THEN** 系统正常执行 `prefetch_related('discussion_threads')`
- **AND** 响应包含完整的 `recent_threads` 数据

### Requirement: 字段排除不影响分页和其他查询参数

系统 SHALL 支持 `exclude` 参数与现有的分页、筛选、排序参数同时使用。

#### Scenario: exclude 与分页参数组合

- **WHEN** 客户端请求 `GET /problems/?page=1&page_size=10&exclude=content,recent_threads`
- **THEN** 系统返回第一页的 10 个 Problem 对象
- **AND** 响应不包含 `content` 和 `recent_threads` 字段
- **AND** 分页元数据（count, page, page_size）正常返回

#### Scenario: exclude 与筛选参数组合

- **WHEN** 客户端请求 `GET /problems/?type=algorithm&difficulty=3&exclude=content`
- **THEN** 系统返回筛选后的 Problem 列表（type=algorithm, difficulty=3）
- **AND** 响应不包含 `content` 字段

#### Scenario: exclude 与排序参数组合

- **WHEN** 客户端请求 `GET /problems/?ordering=-created_at&exclude=recent_threads`
- **THEN** 系统返回按 `created_at` 降序排列的 Problem 列表
- **AND** 响应不包含 `recent_threads` 字段

### Requirement: 缓存键包含 exclude 参数

系统 SHALL 在生成缓存键时包含 `exclude` 参数，确保不同的字段排除组合使用不同的缓存。

#### Scenario: 不同 exclude 参数使用不同缓存

- **WHEN** 客户端 A 请求 `GET /problems/?exclude=content`
- **AND** 客户端 B 请求 `GET /problems/?exclude=content,recent_threads`
- **THEN** 两个请求使用不同的缓存键
- **AND** 缓存失效互不影响

#### Scenario: 相同 exclude 参数复用缓存

- **WHEN** 客户端 A 请求 `GET /problems/?exclude=content`
- **AND** 客户端 B 在缓存有效期内请求 `GET /problems/?exclude=content`
- **THEN** 客户端 B 从缓存获取数据（不查询数据库）
- **AND** 响应数据一致

### Requirement: 排除嵌套序列化器中的字段

系统 SHALL 支持排除嵌套序列化器返回的字段，如 `unlock_condition_description` 中的嵌套数据。

#### Scenario: 排除整个嵌套对象

- **WHEN** 客户端请求 `GET /problems/?exclude=unlock_condition_description`
- **THEN** 系统返回 Problem 对象列表
- **AND** 响应不包含 `unlock_condition_description` 字段
- **AND** 其他字段正常返回

#### Scenario: 保留嵌套对象但排除其子字段

- **WHEN** 客户端尝试排除嵌套对象的子字段（当前不支持）
- **THEN** 系统可以返回错误或忽略不支持的字段
- **AND** 未来可扩展支持点号表示法（如 `unlock_condition_description.prerequisite_problems`）

### Requirement: 响应数据大小显著减少

系统 SHALL 在使用合理的 `exclude` 参数时，将响应数据大小减少至少 70%。

#### Scenario: 列表页排除大字段后数据量减少

- **WHEN** 客户端请求 `GET /problems/?exclude=content,recent_threads,chapter_title,updated_at`
- **THEN** 响应数据大小小于 100KB（每页 10 个题目）
- **AND** 相比不排除字段时（约 300KB），减少至少 66%

#### Scenario: 详情页排除嵌套对象后数据量减少

- **WHEN** 客户端请求 `GET /problems/123/?exclude=recent_threads`
- **THEN** 响应数据大小显著减少
- **AND** 不包含 3 个讨论线程及其回复数据
