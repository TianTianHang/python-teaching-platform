# 统一Cache服务层 - 技术设计

## Context

**当前状态**

系统中存在多种cache使用方式，导致代码不一致、缺少observability、难以维护：

1. **courses/views.py（分离缓存）**：直接使用`django.core.cache.cache`，绕过了CacheResult、metrics和穿透保护
   - 全局数据缓存：`chapter:global:list:{course_id}`
   - 手动合并用户状态，代码复杂且易出错
   - 无Prometheus metrics记录
   - 无缓存穿透保护

2. **file_management/views.py**：使用CacheListMixin/CacheRetrieveMixin
   - 标准化实现，有完整的metrics和穿透保护
   - 但无法复用于分离缓存场景

3. **courses/services.py（业务逻辑）**：直接使用`cache.get/set`
   - 快照缓存、执行结果缓存缺少统一接口
   - 代码重复，TTL不一致

4. **signals.py（缓存失效）**：手动构造cache key
   - 容易出错，key格式不一致
   - 缺少类型安全

**问题根源**

缺少服务层抽象（Service Layer），导致业务代码直接与基础设施耦合。每次使用cache都需要重复处理：key构造、序列化、metrics记录、穿透保护、失效逻辑。

**前置条件**

- ✅ `utils/cache.py`已提供`get_cache()`, `set_cache()`, `delete_cache()`, `CacheResult`
- ✅ `metrics/cache_metrics.py`已提供Prometheus metrics
- ✅ Redis 7和django-redis已配置
- ✅ `mixins/cache_mixin.py`已实现CacheListMixin/CacheRetrieveMixin

**约束条件**

- 不修改现有代码（保持向后兼容）
- 不引入新的依赖（使用现有基础设施）
- 性能：服务层调用开销 < 1ms（纯内存操作）

## Goals / Non-Goals

**Goals:**

1. 提供统一的服务层API，封装cache操作的重复逻辑
2. 为分离缓存场景（全局+用户状态）提供标准实现
3. 为业务逻辑缓存（services.py）提供类型安全的接口
4. 统一cache key命名规范，支持模式匹配和批量失效
5. 确保所有cache操作自动记录metrics和穿透保护

**Non-Goals:**

- 不修改现有的courses/views.py、services.py代码（由后续change完成）
- 不替换CacheMixin（继续用于标准ViewSet场景）
- 不引入新的缓存后端或存储系统
- 不实现自动化的缓存预热（已有on-demand warming）
- 不修改缓存失效的时机（只提供API，不决定何时调用）

## Decisions

### 1. 服务层架构：独立服务类 vs 单一CacheService增强

**决策**：创建三个独立服务类（SeparatedCacheService、BusinessCacheService、CacheInvalidator）

**理由**：
- **单一职责**：每个服务类专注于一个场景，易于理解和测试
- **类型安全**：独立服务类可以使用类型提示，IDE支持更好
- **灵活性**：调用方可以选择使用哪个服务，不必引入不依赖的功能
- **可测试性**：每个服务可以独立mock和单元测试

**替代方案**：增强现有的`utils/cache.py`，添加所有新功能
- **缺点**：单一文件过大（当前200+行，增加后500+行），难以维护
- **缺点**：无法分离关注点，违反单一职责原则

### 2. Cache key标准化：get_standard_cache_key()增强

**决策**：增强`utils/cache.py`中的`get_cache_key()`函数，添加`is_separated`参数

```python
def get_standard_cache_key(
    prefix: str,
    view_name: str,
    pk: Optional[int] = None,
    parent_pks: Optional[Dict[str, int]] = None,
    query_params: Optional[Dict] = None,
    user_id: Optional[int] = None,
    is_separated: bool = False  # 新增：是否是分离缓存
) -> str:
    """生成标准化的缓存key

    Returns:
        格式: {prefix}:{view_name}[:SEPARATED][:parent_keys][:pk][:params][:user_id]

        示例:
        - 普通缓存: "courses:ChapterViewSet:course_pk=1:page=1:user_id=123"
        - 分离缓存全局: "courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1"
        - 分离缓存用户: "courses:ChapterViewSet:SEPARATED:STATUS:course_pk=1:user_id=123"
    """
```

**理由**：
- **向后兼容**：现有`get_cache_key()`调用不受影响（默认`is_separated=False`）
- **可读性**：`SEPARATED:GLOBAL/STATUS`标记清晰表达意图
- **模式匹配**：标准格式支持`delete_cache_pattern("courses:ChapterViewSet:SEPARATED:*")`

**替代方案1**：在服务层内部构造key，不增强`get_cache_key()`
- **缺点**：导致两套key构造逻辑，容易不一致
- **缺点**：无法复用现有的parent_pks排序、query_params过滤逻辑

**替代方案2**：使用hash key（如`"file_dir:" + md5(...)`）
- **缺点**：不可读，难以调试
- **缺点**：无法使用模式匹配批量失效

### 3. SeparatedCacheService实现：使用回调模式 vs 直接查询

**决策**：使用回调模式（`data_fetcher: Callable`）

```python
class SeparatedCacheService:
    @staticmethod
    def get_global_data(
        cache_key: str,
        data_fetcher: Callable[[], Any],  # 回调函数
        ttl: int = 1800
    ) -> Tuple[Any, bool]:  # (data, is_cache_hit)
```

**理由**：
- **解耦**：服务层不依赖Django模型，可以用于任何场景
- **可测试**：调用方可以传入mock函数，无需测试数据库
- **灵活性**：fetcher可以执行复杂逻辑（join、序列化等）

**替代方案**：在服务层直接调用`Chapter.objects.filter(...)`
- **缺点**：服务层与模型耦合，难以复用
- **缺点**：无法支持业务逻辑层的缓存需求

### 4. CacheInvalidator设计：静态方法 vs 实例方法

**决策**：使用静态方法（`@staticmethod`）

```python
class CacheInvalidator:
    @staticmethod
    def invalidate_viewset(prefix: str, view_name: str, pk: int, ...):
        cache_key = get_standard_cache_key(...)
        delete_cache(cache_key)
```

**理由**：
- **无状态**：失效操作不需要实例变量
- **简单**：调用方直接`CacheInvalidator.invalidate_viewset(...)`，无需实例化
- **性能**：避免对象创建开销

**替代方案**：实例方法（需要先`invalidator = CacheInvalidator()`）
- **缺点**：增加调用复杂度，无实际收益

### 5. 错误处理：静默失败 vs 抛出异常

**决策**：缓存失效操作静默失败，缓存读取操作抛出异常

**失效操作（静默）**：
```python
def delete_cache(key):
    try:
        cache.delete(key)
    except Exception as e:
        logger.debug(f"Failed to delete cache {key}: {e}")
        # 不抛出异常，避免影响业务逻辑
```

**读取操作（抛异常）**：
```python
def get_global_data(...):
    result = get_cache(cache_key, return_result=True)
    if result.is_null_value:
        raise NotFound("Resource not found")  # 抛出404
```

**理由**：
- **失效操作**：通常是副作用（如信号处理器），失败不应阻断主流程
- **读取操作**：直接影响业务逻辑，失败需要调用方处理

## Risks / Trade-offs

### Risk 1: 服务层性能开销

**风险**：每次cache操作增加一层函数调用，可能影响性能

**缓解**：
- 服务层方法使用`@staticmethod`，避免实例化开销
- 内联简单的key构造逻辑，编译器优化后开销 < 1μs
- 基准测试：对比直接`cache.get()`和`SeparatedCacheService.get_global_data()`

### Risk 2: Cache key格式变更导致缓存未命中

**风险**：`get_standard_cache_key()`格式改变后，旧key无法读取

**缓解**：
- **Phase 1（本change）**：只添加新服务，不修改现有key
- **Phase 2（迁移）**：逐步替换，保留旧key兼容期（设置双TTL）
- **监控**：上线后观察cache hit rate，如下降 > 10%则回滚

### Risk 3: 过度抽象导致学习曲线

**风险**：三个服务类增加了API复杂度，开发者可能困惑何时用哪个

**缓解**：
- **文档**：每个服务类添加清晰的docstring和使用示例
- **指南**：创建`docs/cache_best_practices.md`，说明决策树
  - ViewSet list/retrieve → 用CacheMixin
  - 分离缓存（全局+用户） → 用SeparatedCacheService
  - 业务逻辑缓存 → 用BusinessCacheService
  - 缓存失效 → 用CacheInvalidator

### Trade-off 1: 灵活性 vs 简洁性

**选择**：优先灵活性，接受额外的参数

**示例**：
```python
# 灵活但参数多
def invalidate_viewset(prefix, view_name, pk=None, parent_pks=None, user_id=None, is_separated=False)

# 简洁但不灵活
def invalidate_viewset(cache_key: str)  # 调用方自己构造key
```

**理由**：服务层价值在于封装key构造逻辑，如果要求调用方自己构造key，则失去了抽象意义

### Trade-off 2: 向后兼容 vs 代码一致性

**选择**：优先向后兼容，允许两套API共存

**策略**：
- 旧代码继续使用`cache.get/set`（不修改）
- 新代码和迁移后代码使用服务层API
- 长期（6个月后）考虑deprecate直接使用`cache`

## Migration Plan

### Phase 1: 创建服务层（本change）

**步骤**：
1. 创建`backend/common/services/`目录
2. 实现`SeparatedCacheService`（separated_cache.py）
3. 实现`BusinessCacheService`（business_cache.py）
4. 增强`utils/cache.py`的`get_standard_cache_key()`
5. 实现`CacheInvalidator`类（添加到`utils/cache.py`）
6. 编写单元测试（`tests/test_separated_cache.py`等）

**验证**：
- 单元测试覆盖率 > 90%
- 集成测试：使用服务层缓存和读取数据
- 性能测试：服务层开销 < 1μs

**回滚**：删除新增的服务文件，不影响现有功能

### Phase 2-4: 迁移现有代码（后续change）

不包含在本change范围内，将创建独立的changes：
- Phase 2: 迁移courses/views.py的分离缓存
- Phase 3: 迁移courses/services.py的业务逻辑缓存
- Phase 4: 迁移signals.py的失效逻辑

## Open Questions

### Q1: CacheInvalidator是否需要批量失效方法？

**问题**：Spec中提到`invalidate_course_caches(course_id)`，但这是否应该由CacheInvalidator提供，还是由调用方组合多个失效操作？

**选项**：
- **A**：提供高级方法（如`invalidate_course_caches`），封装常见场景
- **B**：只提供原子方法（如`invalidate_viewset`），由调用方组合

**倾向**：选择B，理由：
- 高级方法难以覆盖所有场景（课程、章节、问题的组合）
- 调用方使用循环组合更灵活
- 未来可以添加helper函数，但不放在核心API中

**待确认**：实现时先选择B，观察使用模式，如发现大量重复代码再添加helper。

### Q2: 分离缓存的TTL如何配置？

**问题**：全局数据和用户状态可能需要不同的TTL，是否支持分别配置？

**选项**：
- **A**：`get_global_data(key, fetcher, ttl=1800)`和`get_user_status(key, fetcher, ttl=900)`各自独立配置
- **B**：统一TTL，简化API

**倾向**：选择A，理由：
- 全局数据变化少，可以更长TTL（30分钟）
- 用户状态变化频繁，需要较短TTL（15分钟）
- 分别配置更灵活，调用方可以根据业务特点调整

**待确认**：在实现中使用选项A。

### Q3: 是否需要支持缓存预热？

**问题**：服务层是否需要提供`warm_global_data()`方法？

**决策**：不需要，理由：
- 现有的`cache_warming/tasks.py`已支持按需预热
- 预热逻辑与业务场景强相关，不应由服务层硬编码
- 调用方可以自行调用`set_cache()`实现预热
