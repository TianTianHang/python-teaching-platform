## Context

当前章节列表查询实现：

1. **ChapterViewSet.get_queryset()**：
   - 使用 `select_related('course')` 预取课程
   - 使用 `prefetch_related('unlock_condition__prerequisite_chapters__course')` 预取解锁条件
   - 为学生用户调用 `_filter_locked_chapters()` 过滤锁定章节

2. **ChapterSerializer.get_is_locked()**：
   - 调用 `ChapterUnlockService.is_unlocked(chapter, enrollment)`
   - 该方法执行 `condition.prerequisite_chapters.exists()` 查询
   - 检查前置章节完成状态

3. **性能问题**：
   - 列表接口中每个章节都触发 Service 层调用
   - Service 层的 `exists()` 绕过 prefetch 数据，产生额外查询
   - 没有缓存时查询数量爆炸式增长

## Goals / Non-Goals

**Goals:**
- 将 `is_locked` 计算完全移到数据库层，避免 N+1 查询
- 列表查询总次数从 ~30+ 减少到 ~2-3 次
- 保持所有现有功能不变
- 维持现有的缓存策略

**Non-Goals:**
- 修改 `prerequisite_progress` 的实现（继续使用 Service 层 + 缓存）
- 改变讲师/管理员的行为（始终看到所有章节）
- 修改 API 响应格式
- 优化单个章节详情接口的性能

## Decisions

### Decision 1: 使用 `annotate()` 而非 `filter()` + `Exists`

**方案对比：**

```python
# 当前方案 (filter)
queryset = queryset.filter(~locked_conditions)

# 新方案 (annotate)
queryset = queryset.annotate(is_locked_db=Case(...))
```

**选择原因：**
- `annotate()` 保留所有章节，只添加字段，便于序列化器读取
- `filter()` 会过滤掉锁定章节，某些场景可能需要显示锁定状态
- `is_locked_db` 字段可以用于前端 UI 控制（如显示进度指示）

### Decision 2: 子查询而非 JOIN 计算前置章节

**实现方案：**

```python
# 使用 Subquery 获取每个前置章节的完成状态
completed_prereq = Subquery(
    ChapterProgress.objects.filter(
        enrollment=enrollment,
        chapter_id=OuterRef('prereq_id'),
        completed=True
    ).values_list('chapter_id', flat=True)[:1]
)

# 检查是否有前置章节未完成
has_unmet_prereqs = Exists(
    ChapterUnlockCondition.objects.filter(
        chapter=OuterRef('pk'),
        unlock_condition_type__in=['prerequisite', 'all']
    ).filter(
        Q(prerequisite_chapters__isnull=False) &
        ~Q(prerequisite_chapters__progress__chapter_id=completed_prereq)
    )
)
```

**替代方案（使用 JOIN + Group By）被拒绝的原因：**
- SQL 更复杂，难以维护
- 可能产生重复计数
- 不必要的表连接

### Decision 3: 保留回退机制

在 `ChapterSerializer.get_is_locked()` 中实现：

```python
def get_is_locked(self, obj):
    # 优先使用数据库注解
    if hasattr(obj, 'is_locked_db'):
        return obj.is_locked_db

    # 回退到 Service 层（用于详情接口等场景）
    if not hasattr(obj, 'unlock_condition') or obj.unlock_condition is None:
        return False

    # ... 原有逻辑
```

**选择原因：**
- 保持兼容性，不影响其他接口（如 retrieve）
- 应对边缘情况（数据库注解不可用时）

### Decision 4: 按用户类型选择性添加注解

在 `get_queryset()` 中：

```python
if user.is_authenticated and not self._is_instructor_or_admin():
    # 学生用户：添加注解
    queryset = queryset.annotate(is_locked_db=...)
else:
    # 讲师/管理员/未登录：不过滤，不注解
    # 序列化器返回默认值（False）
    pass
```

**选择原因：**
- 避免不必要的计算
- 讲师需要看到所有章节，无需锁定检查
- 未登录用户默认视为未锁定

## Risks / Trade-offs

### [Risk] 子查询的 N+1 问题
- **风险**：`OuterRef` 在 EXISTS 子查询中可能导致查询爆炸
- **缓解**：使用 `enrollment` 作为固定条件，确保子查询可以被优化

### [Risk] 复杂 SQL 影响性能
- **风险**：多层嵌套的 EXISTS 和 CASE 语句可能导致查询缓慢
- **缓解**：
  1. 添加数据库索引确保 `chapterunlockcondition.chapter_id` 有索引
  2. 添加 `chapterunlockcondition.prerequisite_chapters_id` 组合索引
  3. 使用 `DEBUG SQL` 输出生成的查询进行分析

### [Risk] 边缘情况处理
- **风险**：没有解锁条件的章节、没有 progress 记录的情况
- **缓解**：在注解中明确处理 None 值，使用默认值

### [Risk] 缓存失效复杂性
- **风险**：数据库注解可能绕过现有缓存机制
- **缓解**：保持 Service 层缓存用于详情接口，列表接口使用数据库层优化

### Trade-offs
- **时间 vs 优化**：当前方案需要调试复杂 SQL，但性能提升显著
- **复杂度 vs 维护**：增加了查询复杂度，但降低了序列化层复杂度
- **即时优化 vs 渐进优化**：选择一步到位，避免半途而废