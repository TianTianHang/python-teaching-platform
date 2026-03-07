## Context

**当前状态**

后端缓存系统存在新旧两套key生成机制并存的问题：

1. **旧系统** (需迁移):
   - `CacheListMixin`、`CacheRetrieveMixin` 使用 `get_cache_key()`
   - Key格式: `{prefix}:{view_name}[:parent_keys][:pk][:params][:user_id]`
   - 使用者: CourseViewSet、EnrollmentViewSet、ChapterProgressViewSet、ProblemProgressViewSet、ExamViewSet、ExamSubmissionViewSet、FolderViewSet、FileEntryViewSet

2. **新系统** (已正确):
   - `SeparatedCacheService`、`BusinessCacheService` 使用 `get_standard_cache_key()`
   - Key格式: `{prefix}:{view_name}[:SEPARATED:{type}][:parent_keys][:pk][:params][:user_id]`
   - 使用者: ChapterViewSet、ProblemViewSet、业务服务层缓存

3. **混用问题**:
   - `signals.py:137-170`: ExamViewSet、EnrollmentViewSet缓存失效使用 `get_cache_key()`
   - `signals.py:282+`: Chapter、Problem分离缓存失效使用 `get_standard_cache_key()`

**前置条件**

- ✅ `get_standard_cache_key()` 已实现且功能完整
- ✅ `CacheInvalidator` 已封装统一的缓存失效API
- ✅ `BusinessCacheService` 已正确使用新key生成方法
- ✅ 分离缓存 (Chapter/Problem) 已迁移完成

**约束条件**

- API响应格式保持不变（向后兼容）
- 缓存行为保持不变（TTL、失效逻辑）
- 迁移期间确保缓存命中率不下降
- 不影响业务逻辑（仅实现层重构）

## Goals / Non-Goals

**Goals:**

1. 统一所有ViewSet的缓存key生成逻辑，使用 `get_standard_cache_key()`
2. 统一signals.py中的缓存失效逻辑，使用 `CacheInvalidator`
3. 删除冗余的 `get_cache_key()` 函数和旧的Mixin实现
4. 提高代码可维护性，减少key生成逻辑的重复代码
5. 消除缓存失效遗漏的风险（key格式不匹配）

**Non-Goals:**

- ❌ 不修改 `SeparatedCacheService` 和 `BusinessCacheService`（已经正确）
- ❌ 不修改API响应格式或缓存策略
- ❌ 不引入新的缓存后端或依赖
- ❌ 不改变缓存TTL和失效逻辑

## Decisions

### 1. 创建新的标准Mixin vs 修改现有Mixin

**决策**: 创建全新的 `StandardCacheListMixin` 和 `StandardCacheRetrieveMixin`

**理由**:
- **清晰隔离**: 新旧代码共存期更易区分，便于逐步迁移
- **风险控制**: 新Mixin有问题不影响现有功能（逐步切换）
- **测试友好**: 可以独立测试新Mixin，验证正确性后再全量应用
- **代码整洁**: 避免大量条件判断，逻辑更清晰

**替代方案**: 修改现有 `CacheListMixin` 和 `CacheRetrieveMixin`
- ❌ 增加复杂度：需要维护新旧两套逻辑（通过配置开关）
- ❌ 风险高：一处改动可能影响所有使用旧Mixin的ViewSet
- ❌ 难以回滚：出问题时难以快速恢复

### 2. 用户隔离缓存的user_id注入方式

**决策**: 在StandardCacheMixin中自动检测并注入user_id

```python
# 自动检测用户隔离缓存
class StandardCacheListMixin:
    def list(self, request, *args, **kwargs):
        # 如果queryset中明确过滤了user字段，则视为用户隔离缓存
        user_id = request.user.id if self._is_user_specific_queryset() else None

        cache_key = get_standard_cache_key(
            prefix=self.cache_prefix,
            view_name=self.__class__.__name__,
            user_id=user_id,  # 自动注入
            ...
        )
```

**理由**:
- **零配置**: 减少开发者的认知负担
- **自动化**: 通过queryset过滤逻辑推断缓存类型，无需显式声明
- **一致性**: 所有ViewSet遵循相同规则

**检测逻辑**:
- 检查queryset是否调用了 `.filter(user=...)` 或 `.filter(enrollment__user=...)`
- 检查ViewSet的 `get_queryset()` 方法是否包含user相关过滤
- 典型用户隔离ViewSet: EnrollmentViewSet、ProgressViewSet

**替代方案**: 在ViewSet中显式配置
```python
class EnrollmentViewSet(StandardCacheListMixin, ...):
    cache_is_user_specific = True  # 显式配置
```
- ❌ 增加配置负担，每个ViewSet都需要声明
- ❌ 容易遗漏（开发者忘记配置）

### 3. 迁移策略：逐步迁移 vs 一次性迁移

**决策**: 逐步迁移，每次迁移1-2个ViewSet

**理由**:
- **风险可控**: 每次迁移范围小，问题容易定位和回滚
- **渐进式**: 可以观察缓存命中率指标，确保迁移正常
- **灵活性**: 可以根据进度调整优先级

**迁移顺序**:
1. **第一批**: CourseViewSet、ExamViewSet（纯全局数据，最简单）
2. **第二批**: EnrollmentViewSet、ProgressViewSets（用户隔离，中等复杂度）
3. **第三批**: FolderViewSet、FileEntryViewSet（file_management，独立模块）
4. **最后**: 清理旧代码

**替代方案**: 一次性迁移所有ViewSet
- ❌ 风险过高，出问题时难以定位
- ❌ 回滚成本高

### 4. 缓存失效统一：CacheInvalidator封装

**决策**: signals.py中所有缓存失效统一使用 `CacheInvalidator`

**当前问题**:
```python
# 旧方法 (signals.py:137)
cache_key = get_cache_key(prefix=ExamViewSet.cache_prefix, view_name=ExamViewSet.__name__, pk=exam.pk)
cache.delete(cache_key)

# 新方法 (signals.py:282)
status_cache_key = get_standard_cache_key(prefix="courses", view_name="business:ChapterStatus", ...)
cache.delete(status_cache_key)
```

**统一后**:
```python
# 统一使用CacheInvalidator
CacheInvalidator.invalidate_viewset(
    prefix="courses",
    view_name="ExamViewSet",
    pk=exam.id
)

CacheInvalidator.invalidate_viewset_list(
    prefix="courses",
    view_name="EnrollmentViewSet",
    parent_pks={"course_pk": course_id}
)
```

**理由**:
- **封装性**: 内部统一使用 `get_standard_cache_key()`
- **类型安全**: 静态方法提供类型提示
- **易维护**: key生成逻辑集中在一处

### 5. 缓存key生成策略

## Risks / Trade-offs

### Risk 1: 缓存key格式变更导致缓存未命中

**风险**: 新key格式与旧key不兼容，迁移后缓存命中率下降

**缓解**:
- 双写策略：同时写入新旧两个key，过渡期1周
- 监控：观察 Prometheus 指标 `cache_requests_total`，如命中率下降 > 10% 则回滚
- 渐进式迁移：每次迁移1-2个ViewSet，小范围验证

### Risk 2: 用户隔离缓存user_id注入逻辑错误

**风险**: 自动检测逻辑判断失误，导致user_id未注入或错误注入

**缓解**:
- 单元测试：覆盖所有用户隔离ViewSet的检测逻辑
- 集成测试：验证缓存key是否包含正确的user_id
- 人工review：代码审查时确认每个ViewSet的key格式正确

### Risk 3: signals.py缓存失效遗漏

**风险**: 统一使用CacheInvalidator后，某些失效场景被遗漏

**缓解**:
- 完整测试：覆盖所有缓存失效信号（post_save、post_delete等）
- 日志验证：观察缓存失效日志，确保所有key都被正确删除
- 对照检查：逐一比对旧代码的失效逻辑，确保无遗漏

### Risk 4: 迁移期间代码库处于不一致状态

**风险**: 新旧代码并存期间，部分ViewSet用旧Mixin，部分用新Mixin

**缓解**:
- 明确标注：在ViewSet注释中标记"已迁移"或"待迁移"
- 迁移看板：使用TODO标记跟踪进度
- 代码审查：确保新迁移的ViewSet使用新Mixin

### Trade-off: 灵活性 vs 简洁性

**选择**: 优先灵活性，接受稍多的配置参数

**示例**:
```python
# 灵活但参数多
cache_key = get_standard_cache_key(
    prefix="courses",
    view_name="CourseViewSet",
    pk=pk,
    parent_pks=parent_pks,
    query_params=query_params,
    user_id=user_id
)
```

**理由**:
- 适应性强：支持所有缓存场景（全局、用户隔离、分离缓存）
- 扩展性好：未来增加新参数无需破坏现有代码
- 类型安全：Python类型提示提供IDE支持

## Migration Plan

### 阶段1: 准备工作

**1.1 创建新的StandardCacheMixin**
- 在 `common/mixins/cache_mixin.py` 中新增：
  - `StandardCacheListMixin`
  - `StandardCacheRetrieveMixin`
- 实现 `get_standard_cache_key()` 调用逻辑
- 实现自动user_id检测逻辑
- 添加单元测试验证key生成正确性

**1.2 更新测试辅助函数**
- 创建 `mock_standard_cache_service()` 测试辅助函数
- 更新 `test_views.py` 中的mock期望

### 阶段2: 迁移ViewSet

**2.1 迁移CourseViewSet**
- 替换继承: `StandardCacheListMixin, StandardCacheRetrieveMixin`
- 设置 `cache_prefix = "courses"`
- 运行测试：`pytest backend/courses/tests/test_views.py -v -k "course"`
- 手动验证：访问 `/api/courses/` 检查缓存key

**2.2 迁移ExamViewSet**
- 同上步骤
- 更新 `signals.py:137` 的缓存失效逻辑

**2.3 迁移EnrollmentViewSet**
- 替换继承
- 验证user_id自动注入
- 更新 `signals.py:167` 的缓存失效逻辑

**2.4 迁移ProgressViewSets**
- ChapterProgressViewSet
- ProblemProgressViewSet
- ExamSubmissionViewSet
- 验证用户隔离缓存正确性

**2.5 迁移file_management ViewSets**
- FolderViewSet
- FileEntryViewSet
- 独立测试：`pytest backend/file_management/tests/`

### 阶段3: 统一signals.py缓存失效

**3.1 替换ExamViewSet缓存失效**
```python
# 旧代码
cache_key = get_cache_key(prefix=ExamViewSet.cache_prefix, view_name=ExamViewSet.__name__, pk=exam.pk)
cache.delete(cache_key)

# 新代码
CacheInvalidator.invalidate_viewset(
    prefix="courses",
    view_name="ExamViewSet",
    pk=exam.id
)
```

**3.2 替换EnrollmentViewSet缓存失效**
```python
# 旧代码
base_key = get_cache_key(prefix=EnrollmentViewSet.cache_prefix, view_name=EnrollmentViewSet.__name__)
delete_cache_pattern(f"{base_key}:*")

# 新代码
CacheInvalidator.invalidate_viewset_list(
    prefix="courses",
    view_name="EnrollmentViewSet"
)
```

**3.3 验证所有缓存失效信号**
- 运行集成测试：`pytest backend/courses/tests/test_signals.py -v`
- 验证缓存失效日志

### 阶段4: 清理旧代码

**4.1 移除旧函数和类**
- 删除 `get_cache_key()` 函数
- 删除 `CacheListMixin`、`CacheRetrieveMixin` 类
- 保留 `InvalidateCacheMixin`（仍被使用）

**4.2 更新测试**
- 删除所有测试中的 `get_cache_key()` 引用
- 更新mock期望
- 验证所有测试通过

### 阶段3: 统一signals.py缓存失效

**3.1 替换ExamViewSet缓存失效**
```python
# 旧代码
cache_key = get_cache_key(prefix=ExamViewSet.cache_prefix, view_name=ExamViewSet.__name__, pk=exam.pk)
cache.delete(cache_key)

# 新代码
CacheInvalidator.invalidate_viewset(
    prefix="courses",
    view_name="ExamViewSet",
    pk=exam.id
)
```

**3.2 替换EnrollmentViewSet缓存失效**
```python
# 旧代码
base_key = get_cache_key(prefix=EnrollmentViewSet.cache_prefix, view_name=EnrollmentViewSet.__name__)
delete_cache_pattern(f"{base_key}:*")

# 新代码
CacheInvalidator.invalidate_viewset_list(
    prefix="courses",
    view_name="EnrollmentViewSet"
)
```

**3.3 验证所有缓存失效信号**
- 运行集成测试：`pytest backend/courses/tests/test_signals.py -v`
- 验证缓存失效日志

### 阶段4: 清理旧代码

**4.1 移除旧函数和类**
- 删除 `get_cache_key()` 函数
- 删除 `CacheListMixin`、`CacheRetrieveMixin` 类
- 保留 `InvalidateCacheMixin`（仍被使用）

**4.2 更新测试**
- 删除所有测试中的 `get_cache_key()` 引用
- 更新mock期望
- 验证所有测试通过

### 阶段5: 验证和文档

**5.1 运行完整测试套件**
- 验证所有测试通过
- 检查缓存key格式正确性

**5.2 添加文档和注释**
- 为新Mixin添加docstring
- 为user_id检测逻辑添加注释
- 更新模块级文档

## Open Questions

**背景**: BusinessCacheService已在业务服务层使用，不属于ViewSet层

**决策**: 不迁移，理由：
- BusinessCacheService不是ViewSet，不需要Mixin
- 已经正确使用 `get_standard_cache_key()`
- 迁移收益不大，可能引入新风险

**结论**: 仅迁移ViewSet层，业务服务层保持现状