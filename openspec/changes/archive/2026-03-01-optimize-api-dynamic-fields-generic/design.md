# 通用动态字段排除 API - 技术设计

## Context

### 当前状态

- `ProblemViewSet` 已实现 `exclude` 参数，但代码与特定 ViewSet 耦合
- 其他 API（Submission、Chapter、Exam 等）存在类似的数据冗余问题
- 缓存机制使用 `CacheListMixin` 和 `CacheRetrieveMixin`，通过 `allowed_params` 控制缓存键

### 约束条件

- **缓存兼容性**：必须确保不同的 `exclude` 参数生成不同的缓存键
- **向后兼容**：不能破坏现有 API 的行为
- **DRF 集成**：需要与 DRF 的序列化器和视图集机制无缝集成
- **性能**：字段排除逻辑本身不能引入显著性能开销

## Goals / Non-Goals

**Goals:**
1. 创建可复用的 `DynamicFieldsMixin`，适用于所有 ViewSet
2. 创建可复用的 `DynamicFieldsSerializerMixin`，适用于所有 Serializer
3. 规范化 `exclude` 参数（排序、去重），最大化缓存命中率
4. 集成到缓存键生成逻辑，避免缓存数据混乱
5. 提供字段验证，防止无效字段名

**Non-Goals:**
1. 强制所有 ViewSet 使用此功能（保持可选）
2. 实现复杂的字段选择逻辑（如通配符、嵌套字段）
3. 修改现有的缓存失效策略

## Decisions

### 1. Mixin 架构：ViewSet + Serializer 双层设计

**决策**：将功能拆分为两个独立的 Mixin

```python
# ViewSet 层：捕获和验证 exclude 参数
class DynamicFieldsMixin:
    def get_exclude_fields(self) -> set[str]:
        """解析并验证 exclude 参数"""
        ...

    def get_serializer_context(self):
        """将 exclude_fields 传递到 serializer context"""
        ...

# Serializer 层：实际执行字段排除
class DynamicFieldsSerializerMixin:
    def to_representation(self, instance):
        """从响应中移除排除的字段"""
        ...
```

**理由**：
- **关注点分离**：ViewSet 负责参数处理，Serializer 负责数据转换
- **灵活性**：可以独立使用任一 Mixin
- **DRF 兼容**：符合 DRF 的 `context` 传递模式

**替代方案**：仅在 ViewSet 层处理，通过修改序列化器字段实现
- ❌ 不够灵活，难以处理嵌套序列化器
- ❌ 违反 DRF 的最佳实践

### 2. Exclude 参数规范化：自动排序和去重

**决策**：在 `get_exclude_fields()` 中对字段名进行排序

```python
def get_exclude_fields(self) -> set[str]:
    exclude = self.request.query_params.get('exclude', '')
    fields = set(f.strip() for f in exclude.split(',') if f.strip())
    return fields
```

缓存键生成时，对 `exclude` 参数值进行排序：

```python
# 在缓存键生成逻辑中
if 'exclude' in filtered:
    # 将 'code,output' 和 'output,code' 统一为 'code,output'
    exclude_fields = sorted(filtered['exclude'].split(','))
    filtered['exclude'] = ','.join(exclude_fields)
```

**理由**：
- **缓存命中率**：`?exclude=code,output` 和 `?exclude=output,code` 生成相同的缓存键
- **用户体验**：用户无需关心字段顺序
- **简单性**：排序操作成本低，收益明显

**替代方案**：不进行规范化
- ❌ 相同语义的请求生成不同缓存键，浪费缓存空间

### 3. 字段验证：在 ViewSet 层提前验证

**决策**：在 `DynamicFieldsMixin.get_exclude_fields()` 中验证字段合法性

```python
def get_exclude_fields(self) -> set[str]:
    exclude = self.request.query_params.get('exclude', '')
    fields = set(f.strip() for f in exclude.split(','))

    if fields:
        serializer_class = self.get_serializer_class()
        valid_fields = self._get_serializable_fields(serializer_class)
        invalid = fields - valid_fields

        if invalid:
            raise ValidationError(f"Invalid fields: {invalid}")

    return fields
```

**理由**：
- **快速失败**：在参数验证阶段立即返回错误，而不是执行查询后再失败
- **清晰的错误信息**：明确告知用户哪些字段名无效
- **安全性**：防止意外暴露敏感字段

**替代方案**：在 Serializer 层静默忽略无效字段
- ❌ 用户难以调试，不知道为什么某些字段没有被排除

### 4. 缓存集成：修改 `_get_allowed_cache_params()`

**决策**：在 `CacheListMixin` 和 `CacheRetrieveMixin` 中将 `exclude` 加入 `allowed_params`

```python
def _get_allowed_cache_params(self):
    common_params = {'page', 'page_size', 'limit', 'offset', 'search', 'exclude'}  # 添加 exclude
    filter_fields = ...
    ordering_fields = ...
    return common_params | filter_fields | ordering_fields
```

**理由**：
- **正确性**：确保不同的 `exclude` 参数生成不同的缓存键
- **最小改动**：只需修改一处代码，所有使用 `CacheListMixin` 的 ViewSet 都受益
- **一致性**：与现有的 `allowed_params` 机制保持一致

**替代方案**：在每个 ViewSet 中单独处理
- ❌ 代码重复，容易遗漏
- ❌ 维护成本高

### 5. 实施顺序：先通用后具体

**决策**：按照以下顺序实施

1. 创建 `DynamicFieldsMixin` 和 `DynamicFieldsSerializerMixin`
2. 修改 `CacheListMixin._get_allowed_cache_params()`
3. 应用到 `SubmissionViewSet`（最高优化价值）
4. 应用到 `ChapterViewSet`
5. 根据需要扩展到其他 ViewSet

**理由**：
- **增量实施**：每一步都可以独立测试
- **快速验证**：先在 Submission API 上验证效果
- **风险控制**：如果发现问题，影响范围可控

## Risks / Trade-offs

### Risk 1: 缓存变体爆炸

**风险**：不同的 `exclude` 组合生成大量缓存键，降低缓存命中率

**缓解措施**：
1. **规范化字段顺序**：`code,output` 和 `output,code` 生成相同键
2. **监控缓存使用**：记录缓存键数量，识别异常模式
3. **文档建议**：推荐常用的 `exclude` 组合，鼓励前端使用固定模式

### Risk 2: 性能开销

**风险**：字段验证和规范化增加每个请求的处理时间

**缓解措施**：
1. **轻量级操作**：集合操作和字符串排序，复杂度 O(n)
2. **仅在需要时执行**：如果 `exclude` 参数为空，跳过所有逻辑
3. **性能测试**：在实施前后进行基准测试，确保开销可接受

### Risk 3: 嵌套序列化器

**风险**：嵌套序列化器中的字段可能无法正确排除

**缓解措施**：
1. **文档说明**：明确此功能仅适用于顶级字段
2. **递归支持（可选）**：如果需求强烈，可以后续添加递归排除逻辑

## Trade-offs

| 方面 | 优势 | 劣势 |
|------|------|------|
| **通用 Mixin** | 代码复用，维护成本低 | 需要额外的抽象层 |
| **缓存键包含 exclude** | 保证数据正确性 | 可能降低缓存命中率 |
| **字段验证** | 清晰的错误信息 | 增加少量性能开销 |
| **参数规范化** | 最大化缓存命中率 | 需要额外的排序逻辑 |

## Migration Plan

### 部署步骤

1. **Phase 1: 核心实现**
   - 创建 `DynamicFieldsMixin` 和 `DynamicFieldsSerializerMixin`
   - 修改 `CacheListMixin._get_allowed_cache_params()`
   - 添加单元测试

2. **Phase 2: 试点应用**
   - 应用到 `SubmissionViewSet`
   - 性能测试和监控
   - 根据反馈调整

3. **Phase 3: 扩展应用**
   - 应用到 `ChapterViewSet`、`ExamViewSet` 等
   - 更新 API 文档

### 回滚策略

- **代码回滚**：所有改动都是新增 Mixin，移除 Mixin 即可回滚
- **数据回滚**：无数据库变更，无需数据迁移
- **缓存回滚**：缓存会自动过期（15 分钟 TTL）

## Open Questions

1. **是否需要支持嵌套字段排除？**
   - 例如：`?exclude=user.password,problem.test_cases`
   - 建议：先实现顶级字段排除，根据需求决定是否添加

2. **是否需要预设模式？**
   - 例如：`?preset=lite` 自动排除 `code,output,error`
   - 建议：先实现基础功能，根据前端使用情况决定

3. **缓存键的最大变体数量？**
   - 需要监控和限制，避免缓存空间浪费
   - 建议：实施后观察 1-2 周，收集实际数据
