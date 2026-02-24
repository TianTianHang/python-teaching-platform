## Context

章节列表 API 已实施基本的缓存优化（enrollment 和 completed_chapter_ids），但 Silk 日志显示仍有 34 次查询。分析发现主要 N+1 查询源：
1. `unlock_condition__prerequisite_chapters` 预取未使用 `to_attr`，导致序列化器每次查询
2. `CourseModelSerializer.get_recent_threads()` 未预取，产生 N+1 查询
3. 系统只有学生用户，但代码仍有讲师/管理员检查逻辑

## Goals / Non-Goals

**Goals:**
- 消除 `prerequisite_chapters` 的 N+1 查询（预计减少 20+ 查询）
- 消除 `recent_threads` 的 N+1 查询（预计减少 3-5 查询）
- 移除冗余的用户角色检查
- 将查询总数从 34 降低到 < 15
- 保持所有功能不变

**Non-Goals:**
- 修改 API 响应结构
- 改变业务逻辑
- 添加新功能
- 修改缓存策略

## Decisions

### 1. 使用 `to_attr` 优化 `prerequisite_chapters` 预取

**Decision**: 修改 `get_queryset` 中的 prefetch，使用 `to_attr` 存储预取数据

**Rationale:**
- 当前的 `prefetch_related('unlock_condition__prerequisite_chapters')` 虽然预取了数据，但序列化器中调用 `.all()` 仍会触发查询
- 使用 `to_attr` 可以将预取数据存储在特定属性，序列化器直接访问内存数据
- 这是最有效的消除 N+1 查询的方式

**Implementation:**
```python
prefetch_related(
    Prefetch(
        'unlock_condition__prerequisite_chapters',
        queryset=Chapter.objects.select_related('course'),
        to_attr='prerequisite_chapters_all'
    ),
    Prefetch('progress_records', queryset=progress_qs, to_attr='user_progress')
)
```

**Alternatives considered:**
- 使用 `select_related` ×（prerequisite_chapters 是 ManyToMany，无法使用 select_related）
- 在序列化器中使用缓存 ×（不如 to_attr 直接高效）

### 2. 为 `recent_threads` 添加预取

**Decision**: 在可能调用 `recent_threads` 的 ViewSet 中添加预取

**Rationale:**
- `CourseModelSerializer.get_recent_threads()` 每个课程都执行查询
- 由于章节列表可能返回课程信息，需要预防这种情况

**Implementation:**
```python
# 在可能需要的 ViewSet 中添加
prefetch_related(
    Prefetch(
        'discussion_threads',
        queryset=DiscussionThread.objects.filter(is_archived=False).order_by('-last_activity_at')[:3],
        to_attr='recent_threads_prefetched'
    )
)
```

**Alternatives considered:**
- 移除 `recent_threads` 字段 ×（可能影响前端功能）
- 使用数据库注解 ×（不适用于此场景）

### 3. 移除 `_is_instructor_or_admin()` 检查

**Decision**: 移除用户角色检查逻辑

**Rationale:**
- 系统只有学生用户，该检查永远返回 False
- 移除可减少不必要的数据库查询和代码复杂度

**Implementation:**
```python
# 移除这个检查及其相关逻辑
```

**Alternatives considered:**
- 保留检查以防将来扩展 ×（当前浪费性能，可通过 feature flag 控制）

## Risks / Trade-offs

### [Risk] `to_attr` 可能与现有代码不兼容
- 某些序列化器可能仍在使用 `obj.prerequisite_chapters.all()`
- **Mitigation**: 更新所有相关序列化器使用 `obj.prerequisite_chapters_all`

### [Risk] 过度优化
- 添加过多预取可能增加内存使用
- **Mitigation**: 只对确实产生 N+1 查询的字段添加预取

### [Trade-off] 代码复杂度 vs 性能
- 添加 `to_attr` 需要更新多处序列化器代码
- 但性能提升显著（预计减少 60%+ 查询）

## Migration Plan

1. **修改 ChapterViewSet.get_queryset()**
   - 添加 `to_attr` 到 `unlock_condition__prerequisite_chapters` 预取
   - 移除 `_is_instructor_or_admin()` 检查

2. **更新序列化器**
   - 修改 `ChapterUnlockConditionSerializer.get_prerequisite_chapters()`
   - 使用预取数据替代 `.all()` 查询

3. **添加 Course 预取（可选）**
   - 如果 `recent_threads` 被使用，添加相应的预取

4. **测试验证**
   - 使用 Silk 验证查询数降低
   - 确保序列化器数据正确

5. **回滚方案**
   - 如有问题，可直接回滚到优化前状态
   - 无数据库变更，安全回滚

## Open Questions

1. `recent_threads` 是否在章节列表 API 中实际被使用？
   - 如不使用，可考虑暂时不优化此部分