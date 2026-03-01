# Problems API 动态字段过滤优化 - 技术设计

## Context

### 当前实现

**ProblemSerializer**（`backend/courses/serializers.py`）：
- 使用标准的 `ModelSerializer`，固定返回所有字段
- 包含嵌套序列化器：`recent_threads`（3个完整线程）、`unlock_condition_description`
- 所有 API 端点（list、retrieve）使用相同的序列化器

**ProblemViewSet**（`backend/courses/views.py`）：
- `get_queryset()` 预取 `discussion_threads`（限制3条）
- 预取逻辑对所有 action 一致，无法根据需求调整

### 问题分析

```
当前数据流：
┌─────────────────────────────────────────────────────────────┐
│  GET /problems/                                              │
│    ↓                                                         │
│  ProblemViewSet.get_queryset()                               │
│    ├─ select_related(chapter, unlock_condition)              │
│    └─ prefetch_related(discussion_threads × 3) ← 总是执行    │
│    ↓                                                         │
│  ProblemSerializer                                           │
│    ├─ id, type, title, difficulty ✓                          │
│    ├─ recent_threads ← 220KB ❌ 列表页不需要                 │
│    ├─ content ← 20KB ❌ 列表页不需要                         │
│    └─ unlock_condition_description ✓                         │
│    ↓                                                         │
│  JSON Response (~300KB)                                      │
│    ├─ 实际需要: 50KB (17%)                                  │
│    └─ 冗余数据: 250KB (83%)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 技术约束

- **Django REST Framework 3.16.1**：需要利用 DRF 的序列化器扩展机制
- **缓存一致性**：现有的 15 分钟缓存机制需要兼容
- **向后兼容**：不破坏现有 API 行为，不传参数时保持原样
- **前端 SSR**：所有数据获取必须服务端兼容

## Goals / Non-Goals

**Goals:**
1. 减少 `/problems/` 列表 API 的响应数据量 70-80%
2. 支持前端通过查询参数动态控制返回字段
3. 优化数据库查询，跳过被排除字段的预取操作
4. 保持完全向后兼容，不传参数时行为不变
5. 提供清晰可测试的实现

**Non-Goals:**
1. 不修改其他 API（courses、chapters）- 仅优化 problems API
2. 不改变业务逻辑或数据模型
3. 不引入新的外部依赖
4. 不修改前端类型定义（使用现有 TypeScript 类型）

## Decisions

### 决策 1：使用查询参数 `exclude` 而非 `fields`

**选择：** 采用 `?exclude=fields` 参数排除字段

**替代方案：**
- `?fields=id,title,difficulty` - 明确指定包含的字段
- `?view=list|detail` - 预定义视图模式

**理由：**
- **更安全**：排除字段比包含字段更安全，避免遗漏必需字段
- **更简洁**：列表页需要排除的字段少（5个），比需要包含的字段少（7个）
- **向后兼容**：不传参数时返回所有字段，行为不变
- **灵活性**：支持任意字段组合，前端可按需调整

**示例：**
```
# 列表页：排除不需要的大字段
GET /problems/?exclude=content,recent_threads,chapter_title,updated_at

# 详情页：排除特定嵌套对象
GET /problems/123/?exclude=recent_threads

# 默认行为：返回所有字段（向后兼容）
GET /problems/
```

### 决策 2：在 Serializer 层实现字段过滤

**选择：** 在 `ProblemSerializer.to_representation()` 方法中实现字段排除

**替代方案：**
- 在 `ViewSet.list()` 方法中手动过滤响应数据
- 创建独立的 `ProblemListSerializer` 类

**理由：**
- **复用性高**：字段过滤逻辑在序列化器中，list 和 retrieve 都可使用
- **DRF 惯例**：`to_representation()` 是 DRF 提供的数据转换钩子，适合此场景
- **代码清晰**：过滤逻辑集中在一处，易于维护和测试
- **嵌套对象支持**：可以在序列化器层面控制嵌套对象的查询

**实现：**
```python
def to_representation(self, instance):
    """动态排除字段"""
    data = super().to_representation(instance)
    exclude_fields = self.context.get('exclude_fields', set())
    for field in exclude_fields:
        data.pop(field, None)
    return data
```

### 决策 3：在 ViewSet 层优化数据库查询

**选择：** 在 `ProblemViewSet.get_queryset()` 中根据 `exclude` 参数动态调整 `prefetch_related`

**替代方案：**
- 总是预取所有数据，在序列化时忽略（浪费数据库查询）
- 在序列化器的 `get_recent_threads()` 方法中惰性查询（N+1 问题）

**理由：**
- **性能最优**：跳过不必要的数据库查询，减少数据库负载
- **避免 N+1**：保持现有的预取策略，仅在被排除时跳过
- **清晰分离**：查询优化在 ViewSet，字段过滤在 Serializer，职责分明

**实现：**
```python
def get_queryset(self):
    exclude_param = self.request.query_params.get('exclude', '')
    exclude_fields = set(f.strip() for f in exclude_param.split(',') if f.strip())

    queryset = Problem.objects.select_related(
        'chapter', 'chapter__course', 'unlock_condition'
    )

    # 仅在 recent_threads 未被排除时预取
    if 'recent_threads' not in exclude_fields:
        queryset = queryset.prefetch_related(
            Prefetch('discussion_threads', ...)
        )

    return queryset
```

### 决策 4：保持 Serializer 单一性

**选择：** 保持单一的 `ProblemSerializer` 类，通过 `context` 传递排除参数

**替代方案：**
- 创建 `ProblemListSerializer` 和 `ProblemDetailSerializer`
- 在 `get_serializer_class()` 中动态选择

**理由：**
- **代码简洁**：避免重复定义字段和方法
- **易于维护**：字段变更只需修改一处
- **灵活性**：同一个序列化器支持任意字段组合，不仅限于 list/detail
- **渐进迁移**：前端可以逐步调整排除字段，不需要后端发布多个版本

**权衡：**
- **可读性**：需要在 `to_representation()` 中查看字段过滤逻辑
- **缓解**：添加清晰的注释和文档说明

## Architecture

### 组件交互

```
┌─────────────────────────────────────────────────────────────┐
│                      API 请求流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HTTP Request                                             │
│     GET /problems/?exclude=content,recent_threads            │
│     ↓                                                        │
│  2. ProblemViewSet.list()                                   │
│     ├─ 解析 exclude 参数 → {'content', 'recent_threads'}    │
│     ├─ get_queryset()                                       │
│     │   ├─ select_related(chapter, unlock_condition)        │
│     │   └─ ❌ 跳过 prefetch_related(discussion_threads)     │
│     └─ get_serializer(..., exclude_fields={...})            │
│        ↓                                                     │
│  3. ProblemSerializer                                       │
│     ├─ to_representation(instance)                          │
│     │   ├─ 获取所有字段数据                                 │
│     │   └─ remove('content', 'recent_threads')              │
│     └─ get_recent_threads(obj)                              │
│         └─ if 'recent_threads' in exclude_fields:           │
│              return None  ← 跳过序列化                       │
│     ↓                                                        │
│  4. JSON Response (~50KB)                                   │
│     └─ 仅包含需要的字段                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                    字段过滤流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Request Query Params                                        │
│  ┌─────────────────┐                                        │
│  │ ?exclude=A,B,C  │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────┐                    │
│  │ ViewSet                             │                    │
│  │ ├─ Parse exclude → {A, B, C}        │                    │
│  │ ├─ Optimize queryset (skip prefetch)│                    │
│  │ └─ Pass to serializer context       │                    │
│  └─────────────────┬───────────────────┘                    │
│                    │                                         │
│                    ▼                                         │
│  ┌─────────────────────────────────────┐                    │
│  │ Serializer                           │                    │
│  │ ├─ to_representation()              │                    │
│  │ │   └─ Remove A, B, C from dict     │                    │
│  │ └─ get_recent_threads()             │                    │
│  │     └─ Skip if excluded              │                    │
│  └─────────────────┬───────────────────┘                    │
│                    │                                         │
│                    ▼                                         │
│  ┌─────────────────────────────────────┐                    │
│  │ Response Data                       │                    │
│  │ └─ {id, title, ...} # no A, B, C    │                    │
│  └─────────────────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

### Risk 1: 字段名拼写错误

**风险：** 前端传入错误的字段名（如 `contents` 而非 `content`），导致字段未被排除

**缓解措施：**
- 在后端添加验证：检查 `exclude` 参数中的字段名是否有效
- 提供清晰的 API 文档和字段列表
- 添加单元测试覆盖常见拼写错误场景

**实现：**
```python
def get_exclude_fields(self):
    """解析并验证 exclude 参数"""
    exclude_param = self.request.query_params.get('exclude', '')
    exclude_fields = [f.strip() for f in exclude_param.split(',') if f.strip()]

    # 验证字段名有效性
    valid_fields = set(ProblemSerializer().get_fields().keys())
    invalid_fields = set(exclude_fields) - valid_fields

    if invalid_fields:
        raise serializers.ValidationError({
            'exclude': f'Invalid fields: {", ".join(invalid_fields)}'
        })

    return set(exclude_fields)
```

### Risk 2: 缓存一致性

**风险：** 不同的 `exclude` 参数组合可能导致缓存失效策略复杂化

**缓解措施：**
- 现有的 `@cache_response` 装饰器已支持基于查询参数的缓存键生成
- 不同的 `exclude` 参数会自动生成不同的缓存键
- 缓存失效逻辑（create/update/delete）保持不变

**验证：**
```python
# 测试不同 exclude 参数的缓存键
GET /problems/?exclude=content  → cache_key: problems:list:exclude=content
GET /problems/?exclude=content,recent_threads  → 不同缓存键
```

### Trade-off 1: 灵活性 vs 复杂性

**权衡：** 支持任意字段组合增加了灵活性，但也增加了代码复杂度

**评估：**
- **接受复杂度**：实现成本可控（约 80 行代码）
- **收益明显**：减少 70-80% 网络传输，显著提升性能
- **可维护**：逻辑集中在两个方法中，易于理解和测试

### Trade-off 2: 查询优化 vs 代码清晰

**权衡：** 在 `get_queryset()` 中添加条件判断影响可读性

**评估：**
- **添加注释**：清晰说明为什么跳过预取
- **提取方法**：将 `get_exclude_fields()` 提取为独立方法
- **测试覆盖**：确保查询优化逻辑正确工作

## Migration Plan

### 阶段 1：后端实现（第 1-2 天）

1. **修改 ProblemSerializer**
   - 添加 `to_representation()` 方法实现字段过滤
   - 修改 `get_recent_threads()` 支持跳过查询

2. **修改 ProblemViewSet**
   - 添加 `get_exclude_fields()` 方法解析和验证参数
   - 修改 `get_queryset()` 根据 `exclude` 优化预取
   - 修改 `list()` 和 `retrieve()` 传递 `exclude_fields`

3. **单元测试**
   - 测试字段排除功能
   - 测试查询优化（验证 SQL 查询数量）
   - 测试向后兼容性（不传参数）

### 阶段 2：前端集成（第 3 天）

1. **更新 API 调用**
   - 修改 `frontend/web-student/app/routes/_layout.problems.tsx`
   - 添加 `exclude=content,recent_threads,status,chapter_title,updated_at` 参数

2. **性能验证**
   - 使用浏览器 DevTools 验证响应大小减少
   - 测试页面加载速度提升

### 阶段 3：监控和优化（第 4 天）

1. **添加日志和监控**
   - 记录 `exclude` 参数使用情况
   - 监控响应大小和查询性能

2. **文档更新**
   - 更新 API 文档说明 `exclude` 参数
   - 添加使用示例

### 回滚策略

- **完全向后兼容**：不传 `exclude` 参数时行为完全不变
- **渐进式迁移**：可以先在测试环境验证，再部署到生产
- **前端回滚**：如果出现问题，前端可以移除 `exclude` 参数，立即恢复

### 测试策略

**单元测试：**
```python
def test_exclude_fields():
    """测试字段排除功能"""
    response = client.get('/problems/?exclude=content,recent_threads')
    assert response.status_code == 200
    data = response.data['results'][0]
    assert 'content' not in data
    assert 'recent_threads' not in data
    assert 'id' in data  # 其他字段正常返回

def test_exclude_invalid_field():
    """测试无效字段名"""
    response = client.get('/problems/?exclude=invalid_field')
    assert response.status_code == 400
    assert 'exclude' in response.data

def test_exclude_reduces_queries():
    """测试查询优化"""
    with assertNumQueries(2):  # 减少 1 个查询
        client.get('/problems/?exclude=recent_threads')
```

**集成测试：**
```python
def test_list_page_exclude():
    """测试列表页排除参数"""
    response = api_client.get('/problems/?exclude=content,recent_threads')
    assert response.status_code == 200
    # 验证响应大小减少
    assert len(response.content) < 100000  # < 100KB

def test_backward_compatibility():
    """测试向后兼容性"""
    response1 = api_client.get('/problems/')
    response2 = api_client.get('/problems/?exclude=')
    assert response1.data == response2.data
```

## Open Questions

1. **是否需要支持 `fields` 参数（包含模式）？**
   - 当前仅支持 `exclude`（排除模式）
   - 如果有需求，可以后续添加支持

2. **是否需要添加字段白名单？**
   - 某些敏感字段可能需要强制返回（如 `is_unlocked`）
   - 当前实现允许排除任何字段，可能需要限制

3. **是否需要为其他 API 添加类似功能？**
   - 当前仅优化 problems API
   - 如果效果好，可以扩展到 courses、chapters 等
