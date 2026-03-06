## Why

当前后端缓存系统存在新旧双key并存问题：旧CacheMixin使用`get_cache_key()`，新SeparatedCache/BusinessCacheService使用`get_standard_cache_key()`，导致signals.py中混用两种方法清除缓存。这种不一致性造成代码维护混乱，且存在缓存失效遗漏的风险（写入用新key，清除用旧key）。

## What Changes

- **移除旧缓存系统**: 删除`CacheListMixin`、`CacheRetrieveMixin`和`get_cache_key()`函数
- **创建统一缓存Mixin**: 新增`StandardCacheListMixin`和`StandardCacheRetrieveMixin`，统一使用`get_standard_cache_key()`生成key，自动检测并注入user_id
- **批量迁移ViewSet**: 将8个使用旧CacheMixin的ViewSet迁移到新Mixin（CourseViewSet、EnrollmentViewSet、ChapterProgressViewSet、ProblemProgressViewSet、ExamViewSet、ExamSubmissionViewSet、FolderViewSet、FileEntryViewSet）
- **统一缓存失效**: signals.py中所有缓存失效逻辑统一使用`CacheInvalidator`，内部封装`get_standard_cache_key()`
- **清理旧代码**: 删除`common/mixins/cache_mixin.py`中的旧Mixin实现

## Capabilities

### New Capabilities
- `unified-cache-key-generation`: 统一的缓存key生成和失效机制，所有ViewSet和业务服务层使用相同的key生成逻辑

### Modified Capabilities
- 无（这是实现层重构，API契约不变，缓存行为不变）

## Impact

**后端影响**:
- `backend/courses/views.py`: 8个ViewSet的继承关系变更
- `backend/file_management/views.py`: 2个ViewSet的继承关系变更
- `backend/courses/signals.py`: 统一使用`CacheInvalidator`替代直接调用`get_cache_key()`
- `backend/common/mixins/cache_mixin.py`: 删除旧的Mixin类，新增标准Mixin
- `backend/common/utils/cache.py`: 删除`get_cache_key()`函数

**前端影响**: 无（API响应格式不变）

**依赖变更**: 无新增外部依赖

**测试影响**: 需要更新所有涉及ViewSet缓存和signals.py的测试用例