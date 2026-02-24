## Context

`/api/v1/enrollments/` 端点当前执行 14 次数据库查询。Silk 分析显示 N+1 查询主要来自 `EnrollmentSerializer`：

**当前查询分解**：
1. 基础查询：`Enrollment.objects.filter(user=request.user)` - 1 次
2. `user_username` 字段 - N 次（每条记录查询一次 user 表）
3. `course_title` 字段 - N 次（每条记录查询一次 course 表）
4. `get_progress_percentage()` 中 `obj.course.chapters.count()` - N 次
5. `get_progress_percentage()` 中 `obj.chapter_progress.filter(completed=True).count()` - N 次
6. `get_next_chapter()` 方法 - N 次复杂查询（本次不优化）

**EnrollmentSerializer 当前实现**：
```python
class EnrollmentSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')  # N+1
    course_title = serializers.ReadOnlyField(source='course.title')    # N+1
    progress_percentage = serializers.SerializerMethodField()          # N+1

    def get_progress_percentage(self, obj):
        total_chapters = obj.course.chapters.count()                  # N+1
        completed_chapters = obj.chapter_progress.filter(completed=True).count()  # N+1
        return round((completed_chapters / total_chapters) * 100, 2)
```

**EnrollmentViewSet 当前实现**：
```python
class EnrollmentViewSet(CacheListMixin, ...):
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)  # 无任何优化
```

## Goals / Non-Goals

**Goals:**
- 消除 `user`、`course`、`chapters`、`chapter_progress` 的 N+1 查询
- 将查询总数从 14 降低到 < 7
- 保持 API 响应结构和功能完全不变
- 使用现有代码模式（与 ProblemViewSet、ChapterViewSet 的优化模式一致）

**Non-Goals:**
- 修改 `get_next_chapter()` 方法（逻辑复杂，需要单独的优化方案）
- 修改 API 响应结构
- 改变业务逻辑
- 添加新功能

## Decisions

### 1. 使用 `select_related('user', 'course')` 优化基础关系

**Decision**: 在 `EnrollmentViewSet.get_queryset()` 中添加 `user` 和 `course` 到 `select_related`

**Rationale:**
- `user` 和 `course` 都是 ForeignKey 关系，`select_related` 适合优化一对一/多对一关系
- `user_username` 使用 `source='user.username'`，`course_title` 使用 `source='course.title'`
- 当前每条记录都触发查询（N 次查询）

**Implementation:**
```python
def get_queryset(self):
    queryset = super().get_queryset().filter(user=self.request.user)
    queryset = queryset.select_related('user', 'course')
    # ... 其他优化
    return queryset
```

**Expected savings**: ~2N queries（N 个 user + N 个 course）

**Alternatives considered:**
- 只 select_related `course` ×（user 字段也在使用中）
- 使用 `prefetch_related` ×（ForeignKey 应该用 `select_related`）

### 2. 使用 `prefetch_related('chapter_progress')` 优化进度查询

**Decision**: 添加 `chapter_progress` 的 prefetch

**Rationale:**
- `get_progress_percentage()` 调用 `obj.chapter_progress.filter(completed=True).count()`
- prefetch 后可以在内存中计算已完成章节数，无需额外查询

**Implementation:**
```python
queryset = queryset.prefetch_related('chapter_progress')
```

**Serializer 修改**：
```python
def get_progress_percentage(self, obj):
    # 使用预取的数据避免 N+1 查询
    completed_chapters = sum(1 for cp in obj.chapter_progress.all() if cp.completed)
    total_chapters = obj.course.chapters.count()  # 仍需优化
    if total_chapters == 0:
        return 0
    return round((completed_chapters / total_chapters) * 100, 2)
```

**Expected savings**: ~N queries（chapter_progress）

**Alternatives considered:**
- 使用注解（annotate）×（需要在 queryset 层面添加，序列化器仍需改动）
- 移除 `progress_percentage` 字段 ×（影响前端功能）

### 3. 使用 `Prefetch('course__chapters')` 优化章节计数

**Decision**: 添加嵌套 prefetch for `course__chapters`

**Rationale:**
- `get_progress_percentage()` 调用 `obj.course.chapters.count()`
- 使用 `Prefetch` 对象可以预取所有章节，在内存中计数

**Implementation:**
```python
from django.db.models import Prefetch

queryset = queryset.prefetch_related(
    'chapter_progress',
    Prefetch('course__chapters', queryset=Chapter.objects.all(), to_attr='all_chapters')
)
```

**Serializer 修改**：
```python
def get_progress_percentage(self, obj):
    # 使用预取的数据避免 N+1 查询
    total_chapters = len(obj.course.all_chapters) if hasattr(obj.course, 'all_chapters') else obj.course.chapters.count()
    completed_chapters = sum(1 for cp in obj.chapter_progress.all() if cp.completed)
    if total_chapters == 0:
        return 0
    return round((completed_chapters / total_chapters) * 100, 2)
```

**Expected savings**: ~N queries（chapters count）

**Alternatives considered:**
- 使用 `select_related('course')` + `prefetch_related('course__chapters')` ×（需要先 select_related 再 prefetch_related）
- 使用数据库注解计算总数 ×（会增加基础查询复杂度）

### 4. 使用 `hasattr()` 作为安全的回退模式

**Decision**: 序列化器使用 `hasattr(obj.course, 'all_chapters')` 检查预取数据

**Rationale:**
- 确保在没有预取的情况下仍能正常工作（如 retrieve 单个对象时）
- 向后兼容，不破坏其他使用场景
- 与现有代码模式一致

**Pattern:**
```python
# 优先使用预取数据，回退到数据库查询
total_chapters = len(obj.course.all_chapters) if hasattr(obj.course, 'all_chapters') else obj.course.chapters.count()
```

## Risks / Trade-offs

### [Risk] `get_next_chapter()` 未优化可能成为新的瓶颈

- 如果用户数据量增加，`get_next_chapter()` 的复杂查询可能成为主要性能问题
- **Mitigation**: 本次优化专注于低风险、高收益的改动；`get_next_chapter()` 需要更仔细的设计，可以单独优化

### [Risk] 预取所有章节可能增加内存使用

- 如果课程章节很多（如 >100），预取所有章节会显著增加内存占用
- **Mitigation**: 现有课程章节数量较少（通常 <20），内存影响可接受；如果未来增长，可考虑使用注解或其他优化

### [Trade-off] 预取查询开销 vs N+1 查询

- 预取会增加初始查询复杂度（更多 JOIN）
- 但整体查询数显著减少（14 → < 7），响应时间提升

## Migration Plan

1. **修改 EnrollmentViewSet.get_queryset()**
   - 添加 `select_related('user', 'course')`
   - 添加 `prefetch_related('chapter_progress')`
   - 添加 `Prefetch('course__chapters', queryset=Chapter.objects.all(), to_attr='all_chapters')`

2. **更新 EnrollmentSerializer.get_progress_percentage()**
   - 修改为使用预取的 `all_chapters` 和 `chapter_progress`

3. **添加必要的 import**
   - `from django.db.models import Prefetch`
   - `from courses.models import Chapter`（可能已存在）

4. **测试验证**
   - 使用 Silk 验证查询数降低到 < 7
   - 运行单元测试确保功能正常
   - 手动验证 `progress_percentage` 数据正确性

5. **回滚方案**
   - 如有问题，可直接回滚（无数据库变更）
   - 保留 fallback 逻辑确保兼容性

## Open Questions

1. 是否需要在 `EnrollmentViewSet` 中添加 `get_queryset()` 方法的缓存？
   - **决策**: 否，已有 `CacheListMixin` 提供缓存，不需要重复缓存

2. `get_next_chapter()` 的优化方案是什么？
   - **决策**: 暂不优化，需要更复杂的方案（可能需要数据库层面的优化或业务逻辑调整）
