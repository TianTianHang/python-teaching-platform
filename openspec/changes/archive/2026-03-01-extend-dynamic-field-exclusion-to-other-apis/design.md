# 扩展动态字段排除功能到其他 API - 技术设计

## Context

### 当前状态

- **ProblemViewSet** 已成功应用 `DynamicFieldsMixin` 和 `DynamicFieldsSerializerMixin`，支持 `exclude` 参数
- 通用 Mixin 实现已存在于 `backend/common/mixins/dynamic_fields_mixin.py` 和 `backend/common/serializers.py`
- 缓存键规范化逻辑已在 `backend/common/utils/cache.py` 中实现
- `openspec/specs/api-dynamic-field-exclusion/spec.md` 已定义完整的需求规范

### 约束条件

- **缓存兼容性**：必须确保不同的 `exclude` 参数生成不同的缓存键
- **向后兼容**：不能破坏现有 API 的行为
- **DRF 集成**：需要与 DRF 的序列化器和视图集机制无缝集成
- **前端 SSR**：所有 API 调用必须在服务端正常工作（使用 `createHttp(request)`）

### 待迁移的 ViewSet 状态

| ViewSet | 当前 Mixin | 优化潜力 | 复杂度 |
|---------|-----------|---------|--------|
| SubmissionViewSet | 无 | 90%+ | 低 |
| ChapterViewSet | CacheListMixin + CacheRetrieveMixin | 60-70% | 中 |
| DiscussionThreadViewSet | 无 | 50-60% | 低 |

## Goals / Non-Goals

**Goals:**
1. 将 `DynamicFieldsMixin` 应用到 Submission、Chapter、DiscussionThread 三个 ViewSet
2. 为对应的 Serializer 添加 `DynamicFieldsSerializerMixin`
3. 在前端集成 `exclude` 参数到相关页面
4. 添加完整的集成测试覆盖
5. 保持完全向后兼容

**Non-Goals:**
1. 修改现有的 `DynamicFieldsMixin` 实现（保持通用性）
2. 修改 `api-dynamic-field-exclusion` spec（已有完整定义）
3. 强制所有前端页面使用 `exclude` 参数（保持可选）
4. 实现复杂的嵌套字段排除（如 `user.username`）

## Decisions

### 1. 实施顺序：按优化价值优先

**决策**：按照以下顺序实施

1. **SubmissionViewSet**（最高优先级，90%+ 冗余）
2. **ChapterViewSet**（中高优先级，60-70% 冗余，已有缓存支持）
3. **DiscussionThreadViewSet**（中等优先级，50-60% 冗余）

**理由**：
- SubmissionViewSet 优化效果最明显，用户感知最强
- ChapterViewSet 已有缓存基础设施，实施风险低
- DiscussionThreadViewSet 相对独立，影响范围小

**替代方案**：按 ViewSet 代码顺序实施
- ❌ 忽略了优化价值的差异
- ❌ 无法快速验证效果

### 2. Mixin 继承顺序

**决策**：`DynamicFieldsMixin` 应放在继承链的合适位置

```python
# ChapterViewSet（已有 CacheListMixin）
class ChapterViewSet(DynamicFieldsMixin,  # 新增，放在最前
    CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):

# SubmissionViewSet（无缓存）
class SubmissionViewSet(DynamicFieldsMixin,  # 新增
    viewsets.ModelViewSet):

# DiscussionThreadViewSet（无缓存）
class DiscussionThreadViewSet(DynamicFieldsMixin,  # 新增
    viewsets.ModelViewSet):
```

**理由**：
- `DynamicFieldsMixin` 需要在 `get_serializer_context()` 中调用 `super()`
- 放在继承链前面确保 `exclude_fields` 正确传递到 Serializer
- 不影响其他 Mixin 的功能

**替代方案**：放在继承链后面
- ❌ 可能导致 `get_serializer_context()` 调用链断裂

### 3. SerializerMethodField 优化策略

**决策**：仅对计算密集的字段添加提前返回优化

```python
def get_status(self, obj):
    exclude_fields = self.context.get('exclude_fields', set())
    if 'status' in exclude_fields:
        return None  # 跳过计算
    # 原有逻辑
```

**理由**：
- 避免不必要的数据库查询
- 保持代码简洁，不过度优化
- 仅在确实有性能收益时添加

**不优化的情况**：
- 简单字段访问（如 `obj.field`）
- 已缓存的计算结果
- 性能影响微小的字段

### 4. 前端集成策略

**决策**：在前端 loader 中直接添加 `exclude` 参数，不创建抽象层

```typescript
// 直接在 loader 中添加
const excludeFields = "code,output,error";
queryParams.set("exclude", excludeFields);
```

**理由**：
- 简单直接，易于理解
- 不引入额外的复杂性
- 与现有的 `_layout.problems.tsx` 模式一致

**替代方案**：创建统一的 API 调用封装
- ❌ 增加抽象层，过度设计
- ❌ 不同的 API 有不同的 exclude 需求

### 5. 前端 exclude 字段选择

**决策**：为每个 API 选择固定的 exclude 字段组合

| API | 排除字段 | 理由 |
|-----|---------|------|
| Submission | `code,output,error` | 列表页不需要详情 |
| Chapter | `content,recent_threads,status` | 列表页不需要富文本 |
| DiscussionThread | `content,replies` | 列表页不需要完整内容 |

**理由**：
- 固定模式最大化缓存命中率
- 用户可以点击详情查看完整数据
- 简化前端代码

**替代方案**：根据页面状态动态调整 exclude
- ❌ 增加复杂度
- ❌ 降低缓存命中率

### 6. 测试策略

**决策**：为每个 ViewSet 创建独立的测试类，使用相同的测试模式

```python
class SubmissionViewSetExcludeTestCase(TestCase):
    def test_exclude_single_field(self):
        # 测试单字段排除

    def test_exclude_multiple_fields(self):
        # 测试多字段排除

    def test_exclude_invalid_field(self):
        # 测试无效字段验证
```

**理由**：
- 与现有的 `ProblemViewSetTestCase` 模式一致
- 易于维护和扩展
- 确保功能正确性

## Risks / Trade-offs

### Risk 1: 缓存变体爆炸

**风险**：不同的 `exclude` 组合生成大量缓存键，降低缓存命中率

**缓解措施**：
1. **规范化字段顺序**：已在 `get_cache_key()` 中实现
2. **前端固定模式**：使用固定的 exclude 组合
3. **监控缓存使用**：通过 Django Debug Toolbar 观察缓存命中率

### Risk 2: 前端页面功能异常

**风险**：exclude 关键字段导致前端页面功能失效

**缓解措施**：
1. **详情页单独请求**：点击列表项时请求完整数据
2. **测试覆盖**：确保前端页面功能正常
3. **逐步推出**：先在单个页面验证，再扩展到其他页面

### Risk 3: SerializerMethodField 优化遗漏

**风险**：某些计算密集的 `SerializerMethodField` 未添加提前返回优化，导致性能提升不明显

**缓解措施**：
1. **性能测试**：实施前后测量响应时间
2. **逐步优化**：先实现基础功能，再针对性优化
3. **代码审查**：检查所有 `SerializerMethodField` 是否需要优化

### Risk 4: 测试覆盖不足

**风险**：新增功能未充分测试，导致边界情况下的错误

**缓解措施**：
1. **参考现有测试**：复用 `ProblemViewSet` 的测试模式
2. **自动化测试**：确保所有测试通过后再合并
3. **手动验证**：在浏览器中手动测试前端页面

## Trade-offs

| 方面 | 优势 | 劣势 |
|------|------|------|
| **后端迁移** | 代码复用，实施快速 | 需要修改多个文件 |
| **前端集成** | 显著减少数据传输 | 需要修改多个 loader |
| **固定 exclude 模式** | 最大化缓存命中率 | 灵活性降低 |
| **SerializerMethodField 优化** | 避免不必要的计算 | 增加少量代码复杂度 |

## Migration Plan

### 部署步骤

1. **Phase 1: 后端迁移 - SubmissionViewSet**
   - 添加 `DynamicFieldsMixin` 到 `SubmissionViewSet`
   - 添加 `DynamicFieldsSerializerMixin` 到 `SubmissionSerializer`
   - 添加集成测试（约 10 个测试用例）
   - 验证功能正确性

2. **Phase 2: 后端迁移 - ChapterViewSet**
   - 添加 `DynamicFieldsMixin` 到 `ChapterViewSet`
   - 添加 `DynamicFieldsSerializerMixin` 到 `ChapterSerializer`
   - 优化 `SerializerMethodField`（`status`, `prerequisite_progress`, `is_locked`）
   - 添加集成测试（约 10 个测试用例）
   - 验证功能正确性

3. **Phase 3: 后端迁移 - DiscussionThreadViewSet**
   - 添加 `DynamicFieldsMixin` 到 `DiscussionThreadViewSet`
   - 添加 `DynamicFieldsSerializerMixin` 到 `DiscussionThreadSerializer`
   - 优化 `get_replies` 方法
   - 添加集成测试（约 10 个测试用例）
   - 验证功能正确性

4. **Phase 4: 前端集成**
   - 修改 `submission.tsx`
   - 修改 `problems.$problemId.submissions.tsx`
   - 修改 `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
   - 修改 `threads.tsx`（可选）
   - 验证前端页面正常工作

5. **Phase 5: 性能验证**
   - 使用浏览器 DevTools 测量响应大小
   - 验证优化效果符合预期
   - 检查缓存命中率

### 回滚策略

- **后端回滚**：移除 Mixin 继承即可恢复原行为
- **前端回滚**：移除 `exclude` 参数即可恢复原行为
- **数据回滚**：无数据库变更，无需数据迁移
- **缓存回滚**：缓存会自动过期（15 分钟 TTL）

## Open Questions

1. **DiscussionThreadViewSet 是否需要添加 CacheListMixin？**
   - 建议：先不添加，观察缓存需求后再决定
   - 理由：`DynamicFieldsMixin` 可以独立工作，不强制要求缓存支持

2. **是否需要为所有 `SerializerMethodField` 添加优化？**
   - 建议：仅对有数据库查询的计算密集字段添加优化
   - 理由：过早优化增加复杂度，先测量性能再决定

3. **前端是否需要支持用户自定义 exclude 参数？**
   - 建议：暂不支持，使用固定的 exclude 模式
   - 理由：简化前端逻辑，最大化缓存命中率
