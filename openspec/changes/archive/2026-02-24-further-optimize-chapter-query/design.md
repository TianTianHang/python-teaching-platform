## Context

当前章节列表接口（GET /api/v1/courses/{id}/chapters/）已进行了一轮优化，查询数从 63 降低到 34。但分析发现仍有以下重复查询问题：

### 问题 1: `_annotate_is_locked` 重复查询 `completed_chapter_ids`
```python
# views.py:179-182 - 重复查询
completed_chapter_ids = ChapterProgress.objects.filter(
    enrollment=enrollment,
    completed=True
).values_list('chapter_id', flat=True)
```
但在 `get_queryset` 中已经查询过（line 118-120）：
```python
self._completed_chapter_ids = set(
    progress_qs.filter(completed=True).values_list('chapter_id', flat=True)
)
```

### 问题 2: `enrollment` 未传递给 serializer context
`get_queryset` 中已获取 `enrollment`（line 115），但 `get_serializer_context` 没有传递它。
这导致 serializer 的回退逻辑需要再次查询：
```python
# serializers.py:169
enrollment = Enrollment.objects.get(user=request.user, course=obj.course)
```

注意：系统只有学生用户，所有用户都使用相同的查询逻辑。

## Goals / Non-Goals

**Goals:**
- 消除 `_annotate_is_locked` 中的重复 `completed_chapter_ids` 查询
- 将 `enrollment` 传递给 serializer context，消除回退查询
- 查询数从 34 降低到 < 25

**Non-Goals:**
- 修改 API 响应结构
- 修改数据模型
- 改变业务逻辑

## Decisions

### 1. 复用 `self._completed_chapter_ids` 缓存

**Decision**: 在 `_annotate_is_locked` 中使用 `self._completed_chapter_ids` 而不是重新查询

**Rationale:**
- `get_queryset` 中已经查询并缓存了 `completed_chapter_ids`
- `_annotate_is_locked` 在 `get_queryset` 之后被调用，缓存可用
- 消除重复的数据库查询

**Alternatives considered:**
- 传递 `completed_chapter_ids` 作为参数 ×（增加方法签名复杂度）
- 使用类变量缓存 ×（可能的并发问题）

### 2. 将 `enrollment` 添加到 serializer context

**Decision**: 在 `get_queryset` 中缓存 `enrollment`，在 `get_serializer_context` 中传递

**Rationale:**
- `enrollment` 在 `get_queryset` 中已经查询过
- serializer 的回退逻辑需要 `enrollment`
- 通过 context 传递是 Django REST Framework 的标准做法

**Implementation:**
```python
# get_queryset 中
self._enrollment = enrollment

# get_serializer_context 中
if hasattr(self, '_enrollment'):
    context['enrollment'] = self._enrollment
```

**Alternatives considered:**
- 在 serializer 中再次查询 ×（导致 N+1 查询）
- 使用 select_related 预取 ×（enrollment 不在 Chapter 模型关系链上）


## Risks / Trade-offs

### [Risk 1] `self._completed_chapter_ids` 可能在某些情况下不可用
- 如果 `get_queryset` 的执行顺序改变，缓存可能不存在
- **Mitigation**: 在 `_annotate_is_locked` 中添加检查，如果缓存不存在则回退到原查询


### [Trade-off] 代码复杂度 vs 性能
- 添加缓存传递逻辑略微增加代码复杂度
- 但显著提升性能，值得这个 trade-off

## Migration Plan

1. **修改 `get_queryset`**:
   - 添加 `self._enrollment = enrollment` 缓存

2. **修改 `_annotate_is_locked`**:
   - 使用 `self._completed_chapter_ids` 缓存

3. **修改 `get_serializer_context`**:
   - 传递 `enrollment` 到 context

4. **测试**:
   - 运行单元测试
   - 使用 Silk 验证查询数降低

5. **回滚方案**:
   - 如有问题，直接回滚代码即可
   - 无数据库变更，回滚无风险

## Open Questions

None（本次优化范围明确，无待决问题）
