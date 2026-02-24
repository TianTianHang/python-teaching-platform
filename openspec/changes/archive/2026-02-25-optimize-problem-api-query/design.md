## Context

`/api/v1/problems/` 端点当前执行 37 次数据库查询。Silk 分析显示虽然已有部分优化（`unlock_condition` 的 `select_related`、`algorithm_info/choice_info/fillblank_info` 的条件 prefetch、用户进度 prefetch），但仍有 27 次 N+1 查询来自：
1. `discussion_threads` - 每个问题都查询最新讨论帖（12 次）
2. `chapter` - 每个问题都查询章节标题（12 次）
3. `test_cases` - 每个算法题都查询测试用例（约 13 次）
4. `prerequisite_problems` - prefetch 未使用 `to_attr`，序列化器调用 `.all()` 仍触发查询（约 2 次）

现有代码模式可复用：ChapterViewSet 已成功使用 `to_attr` 优化 `prerequisite_chapters`，类似模式可应用到 ProblemViewSet。

## Goals / Non-Goals

**Goals:**
- 消除 `discussion_threads`、`chapter`、`test_cases`、`prerequisite_problems` 的 N+1 查询
- 将查询总数从 37 降低到 < 15
- 保持 API 响应结构和功能完全不变
- 使用现有代码模式（ChapterViewSet 的 `to_attr` 模式）确保一致性

**Non-Goals:**
- 修改 API 响应结构
- 改变业务逻辑
- 添加新功能
- 修改缓存策略（保留现有 CacheListMixin 等机制）

## Decisions

### 1. 使用 `select_related('chapter')` 优化章节查询

**Decision**: 在 `ProblemViewSet.get_queryset()` 中添加 `chapter` 到 `select_related`

**Rationale:**
- `ProblemSerializer.chapter_title` 使用 `source="chapter.title"`
- 当前每条记录都触发一次查询（12 个问题 = 12 次查询）
- `chapter` 是 ForeignKey，`select_related` 适合优化一对一关系

**Implementation:**
```python
queryset = queryset.select_related('chapter', 'unlock_condition')
```

**Alternatives considered:**
- 使用 `prefetch_related` ×（ForeignKey 应该用 `select_related`）
- 移除 `chapter_title` 字段 ×（影响前端功能）

### 2. 使用带 `to_attr` 的 `Prefetch` 优化 `discussion_threads`

**Decision**: 添加 `discussion_threads` 的 prefetch，使用 `to_attr='recent_threads_list'`

**Rationale:**
- `ProblemSerializer.get_recent_threads()` 调用 `obj.discussion_threads.filter(is_archived=False).order_by('-last_activity_at')[:3]`
- 使用 `to_attr` 存储预取数据，序列化器直接从内存读取
- prefetch queryset 可以预先应用 filter 和 order_by，减少序列化时计算

**Implementation:**
```python
from django.db.models import Prefetch
from courses.models import DiscussionThread

prefetches.append(Prefetch(
    'discussion_threads',
    queryset=DiscussionThread.objects.filter(is_archived=False)
                                     .order_by('-last_activity_at')[:3],
    to_attr='recent_threads_list'
))
```

序列化器修改：
```python
def get_recent_threads(self, obj):
    threads = getattr(obj, 'recent_threads_list',
                      obj.discussion_threads.filter(is_archived=False)
                                             .order_by('-last_activity_at')[:3])
    return DiscussionThreadSerializer(threads, many=True, context=self.context).data
```

**Alternatives considered:**
- 不预取，接受 N+1 查询 ×（性能目标要求 < 15 查询）
- 移除 `recent_threads` 字段 ×（影响前端功能）

### 3. 使用带 `to_attr` 的嵌套 `Prefetch` 优化 `test_cases`

**Decision**: 为算法题的测试用例添加嵌套 prefetch，使用 `to_attr='sample_test_cases'`

**Rationale:**
- `AlgorithmProblemSerializer.get_sample_cases()` 调用 `obj.test_cases.filter(is_sample=True)`
- `test_cases` 是 `AlgorithmProblem` 的反向关系，需要嵌套 prefetch：`algorithm_info__test_cases`
- 只在查询包含 `algorithm` 类型问题时才需要此 prefetch

**Implementation:**
```python
from courses.models import TestCase

if type_param == 'algorithm':
    prefetches.append('algorithm_info')
    prefetches.append(Prefetch(
        'algorithm_info__test_cases',
        queryset=TestCase.objects.filter(is_sample=True).order_by('id'),
        to_attr='sample_test_cases'
    ))
else:
    # 未指定 type，预取所有类型（包括 test_cases）
    prefetches.extend(['algorithm_info', 'choice_info', 'fillblank_info'])
    prefetches.append(Prefetch(
        'algorithm_info__test_cases',
        queryset=TestCase.objects.filter(is_sample=True).order_by('id'),
        to_attr='sample_test_cases'
    ))
```

序列化器修改：
```python
def get_sample_cases(self, obj):
    sample_test_cases = getattr(obj, 'sample_test_cases',
                                 obj.test_cases.filter(is_sample=True).order_by('id'))
    return TestCaseSerializer(sample_test_cases, many=True).data
```

**Alternatives considered:**
- 使用 `select_related` ×（test_cases 是 ManyToMany 反向关系，无法使用）
- 在算法题详情页才加载 ×（列表页也需要此数据）

### 4. 为 `prerequisite_problems` 添加 `to_attr`

**Decision**: 修改现有 `prerequisite_problems` prefetch，添加 `to_attr='prerequisite_problems_all'`

**Rationale:**
- 当前 prefetch：`Prefetch('unlock_condition__prerequisite_problems')` 未使用 `to_attr`
- `get_unlock_condition_description()` 调用 `.all()` 仍触发查询
- 添加 `to_attr` 后，序列化器可从内存读取数据

**Implementation:**
```python
prefetches.append(Prefetch(
    'unlock_condition__prerequisite_problems',
    to_attr='prerequisite_problems_all'
))
```

序列化器修改：
```python
prereq_problems = getattr(unlock_condition, 'prerequisite_problems_all',
                          unlock_condition.prerequisite_problems.all())
```

**Alternatives considered:**
- 保持现状 ×（仍有约 2 次 N+1 查询）
- 使用数据库注解 ×（不适用于 ManyToMany 关系）

### 5. 使用 `getattr()` 作为安全的回退模式

**Decision**: 所有序列化器使用 `getattr(obj, 'to_attr_name', fallback_queryset)` 模式

**Rationale:**
- 确保在没有预取的情况下仍能正常工作（如 retrieve 单个对象时）
- 与现有代码模式一致（ChapterUnlockConditionSerializer 已使用此模式）
- 向后兼容，不破坏其他使用场景

**Pattern:**
```python
# 优先使用预取数据，回退到数据库查询
data = getattr(obj, 'prefetched_attr_name', obj.related_queryset.filter(...))
```

## Risks / Trade-offs

### [Risk] `discussion_threads` 预取可能与动态过滤冲突

- 如果前端需要不同的过滤条件，预取可能不适用
- **Mitigation**: 预取使用与序列化器相同的过滤条件，确保一致性

### [Risk] 条件 prefetch 增加代码复杂度

- `test_cases` prefetch 需要根据 `type` 参数条件添加
- **Mitigation**: 清晰的注释说明条件逻辑，遵循现有模式

### [Risk] 过度预取增加内存使用

- 预取所有关系可能增加内存占用
- **Mitigation**: 只对确实产生 N+1 查询的字段添加预取，使用 filter 限制预取数据量（如 `[:3]`）

### [Trade-off] 预取查询开销 vs N+1 查询

- 预取会增加初始查询复杂度
- 但整体查询数显著减少（37 → < 15），响应时间提升 50%+

## Migration Plan

1. **修改 ProblemViewSet.get_queryset()**
   - 添加 `select_related('chapter')`
   - 添加 `discussion_threads` prefetch with `to_attr`
   - 添加 `test_cases` nested prefetch with `to_attr`（条件性）
   - 为 `prerequisite_problems` 添加 `to_attr`

2. **更新序列化器**
   - 修改 `ProblemSerializer.get_recent_threads()`
   - 修改 `AlgorithmProblemSerializer.get_sample_cases()`
   - 修改 `ProblemSerializer.get_unlock_condition_description()`

3. **添加必要的 import**
   - `from courses.models import DiscussionThread, TestCase`
   - `from django.db.models import Prefetch`（应该已存在）

4. **测试验证**
   - 使用 Silk 验证查询数降低到 < 15
   - 运行单元测试确保功能正常
   - 手动验证 API 响应数据正确性

5. **回滚方案**
   - 如有问题，可直接回滚（无数据库变更）
   - 保留 fallback 逻辑确保兼容性

## Open Questions

1. `type` 参数未指定时，是否仍需预取 `test_cases`？
   - **决策**: 是，因为列表可能包含混合类型的问题
