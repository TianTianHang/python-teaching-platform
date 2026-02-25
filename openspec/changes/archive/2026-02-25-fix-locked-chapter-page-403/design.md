## Context

### 当前状态

在提交 f467a06 "perf: optimize chapter query performance from 34 to 12 queries" 之后，`ChapterViewSet` 的行为发生了变化：

**之前**: `get_queryset()` 会过滤掉锁定的章节，学生无法在列表中看到它们
**之后**: `get_queryset()` 使用 `_annotate_is_locked()` 添加 `is_locked_db` 注解，所有章节都可见

同时，`retrieve()` 方法增加了解锁状态检查，锁定章节返回 403：

```python
# backend/courses/views.py:304-348
def retrieve(self, request, *args, **kwargs):
    chapter = self.get_object()
    enrollment = Enrollment.objects.get(user=request.user, course=chapter.course)

    if not ChapterUnlockService.is_unlocked(chapter, enrollment):
        # 返回 403 和友好的错误消息
        return Response({'detail': error_msg}, status=status.HTTP_403_FORBIDDEN)

    return super().retrieve(request, *args, **kwargs)
```

### 问题

前端 `locked.tsx` 路由需要获取章节信息来显示锁定页面：

```typescript
// frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx:10
const chapter = await http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
// ↑ 这里调用 retrieve() API，锁定时返回 403
```

### 现有 API

`unlock_status` API 已存在且被广泛使用，返回解锁状态详情：

```python
# backend/courses/views.py:281-302
@action(detail=True, methods=['get'])
def unlock_status(self, request, pk=None, course_pk=None):
    chapter = self.get_object()
    enrollment = Enrollment.objects.get(user=user, course=chapter.course)
    status_info = ChapterUnlockService.get_unlock_status(chapter, enrollment)
    return Response(status_info)
```

该 API 不会检查解锁状态，总是返回状态信息，已被缓存。

---

## Goals / Non-Goals

**Goals:**
- 修复锁定页面的 403 错误，使其能够正常显示
- 保持 API 性能（利用现有缓存机制）
- 最小化代码变更（避免引入新的 API 端点）
- 向后兼容（不影响现有 API 调用者）

**Non-Goals:**
- 修改 `retrieve()` API 的解锁检查逻辑（安全性需要保留）
- 改变解锁状态的判断规则
- 引入新的数据库查询

---

## Decisions

### 决策 1: 扩展 `unlock_status` API 响应

**选择**: 在 `get_unlock_status()` 返回值中增加 `chapter` 字段，包含章节基本信息

**理由**:
1. **零额外查询**: `unlock_status` action 中的 `chapter = self.get_object()` 已获取完整的 chapter 对象
2. **利用缓存**: `get_unlock_status()` 已有缓存机制（TTL 基于 cache-penetration-protection 策略）
3. **语义合理**: 解锁状态本身就是章节相关信息，返回章节上下文是自然的
4. **单次调用**: 前端只需一次 API 调用即可获取锁定页面所需的所有数据

**响应格式**:
```json
{
  "is_locked": true,
  "reason": "prerequisite",
  "chapter": {
    "id": 1,
    "title": "第二章：Python 基础语法",
    "order": 2,
    "course_title": "Python 编程入门"
  },
  "prerequisite_progress": {
    "total": 2,
    "completed": 0,
    "remaining": [...]
  },
  "unlock_date": null,
  "time_until_unlock": null
}
```

### 决策 2: 字段选择

**选择**: 仅返回 `id`, `title`, `order`, `course_title` 四个字段

**理由**:
1. **最小化数据**: 锁定页面只需要显示章节标题和基本信息
2. **避免敏感数据**: 不返回 `content` 等需要解锁后才能查看的内容
3. **保持一致性**: 这些字段在章节列表中也已返回

### 决策 3: 前端类型定义

**选择**: 在 `ChapterUnlockStatus` 接口中添加可选的 `chapter` 字段

**理由**:
1. **向后兼容**: 现有调用者不需要立即更新
2. **渐进式迁移**: `locked.tsx` 可以立即使用，其他页面稍后可选迁移

```typescript
export interface ChapterUnlockStatus {
  is_locked: boolean;
  reason?: 'prerequisite' | 'date' | 'both' | null;
  chapter?: {  // 新增，可选
    id: number;
    title: string;
    order: number;
    course_title: string;
  };
  // ... 其他字段保持不变
}
```

### 替代方案（未采用）

**方案 A: 新增 `basic_info` API**
- ❌ 需要两次 API 调用
- ❌ 需要新的 endpoint 和测试
- ❌ 可能增加数据库查询

**方案 B: 修改 `retrieve` 添加查询参数**
- ❌ 可能被滥用，绕过解锁检查
- ❌ 增加安全风险

**方案 C: 前端使用 URL state 传递数据**
- ❌ 数据可能过期（刷新页面后丢失）
- ❌ 用户体验不佳

---

## Risks / Trade-offs

### Risk: 现有 API 调用者可能依赖响应格式

**缓解措施**: `chapter` 字段设为可选，向后兼容。现有调用者忽略新字段即可继续工作。

### Risk: `unlock_status` 响应体积增大

**缓解措施**: 只包含 4 个轻量级字段，对响应体积影响可忽略不计（< 100 bytes）。

### Risk: 缓存失效可能影响性能

**缓解措施**: `get_unlock_status()` 已有缓存，且 TTL 设置合理（基于 cache-penetration-protection 策略）。新增字段不影响缓存命中率。

### Trade-off: API 职责轻微混合

`unlock_status` 现在既返回状态又返回基本信息，职责略有增加。

**理由**: 这是实用主义的选择——章节信息是解锁状态的上下文，而非独立概念。相比引入新 API，这是更简单的方案。

---

## Migration Plan

1. **后端变更**
   - 修改 `ChapterUnlockService.get_unlock_status()` 返回 `chapter` 字段
   - 更新相关测试用例

2. **前端变更**
   - 更新 `ChapterUnlockStatus` 类型定义
   - 修改 `locked.tsx` loader，移除 `retrieve` API 调用

3. **验证步骤**
   - 后端测试: `uv run pytest backend/courses/tests/test_chapter_unlock_service.py -k get_unlock_status`
   - 前端测试: 访问锁定章节页面，确认正常显示
   - 性能测试: 确认 API 响应时间未增加

4. **部署策略**
   - 先部署后端（向后兼容）
   - 后部署前端（依赖新字段）

---

## Open Questions

无
