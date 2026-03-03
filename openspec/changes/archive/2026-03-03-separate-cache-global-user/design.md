# Design: Separate Cache for Global and User Data

## Context

当前系统的章节(Chapter)和问题(Problem)数据采用单一缓存策略,将全局数据(title, content等)与用户状态(is_locked, status等)混合存储在同一缓存键下。缓存键格式为 `api:ChapterViewSet:{params}:user_id={id}`,导致:

- 每个用户独立缓存副本
- 全局数据重复存储N次(N=用户数)
- 用户状态更新导致整个缓存失效
- 缓存命中率低,内存利用率差

现有缓存机制:
- `CacheListMixin` 和 `CacheRetrieveMixin` 提供列表和详情缓存
- 缓存键通过 `get_cache_key()` 生成,包含 `user_id`
- `InvalidateCacheMixin` 提供缓存失效能力
- TTL固定为900秒(15分钟)

## Goals / Non-Goals

**Goals:**
- 将全局数据缓存和用户状态缓存分离,实现全局数据跨用户共享
- 保持API响应格式不变,前端无需修改
- 精细化缓存失效,用户状态变化不影响全局数据缓存
- 降低内存占用,提升缓存命中率

**Non-Goals:**
- 不改变现有的 `CacheListMixin` 和 `CacheRetrieveMixin` 基础设施
- 不重构其他全局数据(如Course, Exam)的缓存策略
- 不改变前端路由缓存机制

## Decisions

### Decision 1: 两层缓存架构

**选择**: 采用两层独立的缓存层 - 全局数据缓存层和用户状态缓存层

**理由**:
- 清晰的职责分离: 全局数据层负责静态内容,用户状态层负责动态状态
- 便于独立优化: 全局数据可设置长TTL(30分钟),用户状态可设置短TTL(5分钟)
- 降级策略简单: 任一层缓存失效不影响另一层

**替代方案**:
1. 单层缓存,序列化器拆分 → 无法解决缓存键问题,全局数据仍重复
2. 客户端合并(API返回分离数据) → 改变API格式,前端需修改

### Decision 2: 缓存合并层放在ViewSet

**选择**: 在ViewSet的 `list()` 和 `retrieve()` 方法中实现缓存合并逻辑

**理由**:
- 保持序列化器职责单一: 序列化器专注数据转换,不处理缓存逻辑
- 便于复用: 其他ViewSet可直接复用合并逻辑
- 降级策略简单: 缓存未命中时直接查询数据库

**实现方式**:
```python
class ChapterViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_pk')

        # 1. 获取全局数据缓存
        global_cache_key = f"chapter:global:list:{course_id}"
        global_data = cache.get(global_cache_key)

        if not global_data:
            chapters = Chapter.objects.filter(course_id=course_id)
            global_data = ChapterGlobalSerializer(chapters, many=True).data
            cache.set(global_cache_key, global_data, timeout=1800)  # 30分钟

        # 2. 获取用户状态缓存
        user_status_key = f"chapter:status:{course_id}:{request.user.id}"
        user_status = cache.get(user_status_key)

        if not user_status:
            user_status = self._get_user_status_batch(course_id, request.user)
            cache.set(user_status_key, user_status, timeout=300)  # 5分钟

        # 3. 合并数据
        result = self._merge_global_and_user_status(global_data, user_status)
        return Response(result)
```

### Decision 3: 序列化器拆分为全局和用户状态

**选择**: 创建独立的 `ChapterGlobalSerializer` 和 `ProblemGlobalSerializer` 用于全局数据,用户状态通过辅助函数获取

**理由**:
- 全局数据序列化器可复用: 多个ViewSet可共享同一序列化器
- 用户状态逻辑集中: 避免在多个序列化器中重复实现 `get_status()` 等方法
- 便于测试: 全局数据和用户状态可独立测试

**序列化器字段划分**:

ChapterGlobalSerializer:
```python
class Meta:
    model = Chapter
    fields = ["id", "course", "course_title", "title", "content",
              "order", "created_at", "updated_at"]
```

用户状态获取函数:
```python
def get_chapter_user_status(chapter_ids, user_id, course_id):
    """批量获取章节用户状态"""
    cache_key = f"chapter:status:{course_id}:{user_id}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    # 从快照或数据库获取
    result = _fetch_user_status_from_db(chapter_ids, user_id, course_id)
    cache.set(cache_key, result, timeout=300)  # 5分钟
    return result
```

### Decision 4: 扩展现有快照模型

**选择**: 在 `CourseUnlockSnapshot` 和 `ProblemUnlockSnapshot` 的 `unlock_states` 字段中增加 `status` 字段

**理由**:
- 快照已有 `unlock_states` 字段存储锁定状态,扩展成本低
- 快照作为用户状态缓存的持久化源,一致性高
- 避免额外的数据库表

**快照数据结构扩展**:
```json
{
  "1": {
    "locked": false,
    "reason": null,
    "status": "completed"  // 新增字段
  },
  "2": {
    "locked": true,
    "reason": "prerequisite",
    "status": "not_started"  // 新增字段
  }
}
```

### Decision 5: 精细化缓存失效信号

**选择**: 创建独立的信号处理器,分别处理全局数据变更和用户状态变更

**理由**:
- 精细化控制: 用户进度变化仅失效用户状态缓存,章节内容变化仅失效全局数据缓存
- 降低影响范围: 用户状态更新不再影响其他用户的缓存
- 提升缓存利用率: 全局数据缓存可长时间保持

**信号处理器设计**:
```python
# backend/courses/signals.py

@receiver(post_save, sender=ChapterProgress)
def on_chapter_progress_change(sender, instance, **kwargs):
    """用户进度变化 → 仅失效用户状态缓存"""
    user_id = instance.enrollment.user_id
    course_id = instance.enrollment.course_id
    cache.delete(f"chapter:status:{course_id}:{user_id}")

@receiver(post_save, sender=Chapter)
def on_chapter_content_change(sender, instance, **kwargs):
    """章节内容变化 → 失效全局数据缓存"""
    cache.delete(f"chapter:global:{instance.id}")
    cache.delete(f"chapter:global:list:{instance.course_id}")
```

## Risks / Trade-offs

### Risk 1: 缓存合并延迟

**风险**: 需要两次缓存查询(全局+用户状态)后合并,增加响应延迟

**缓解措施**:
- 使用Redis pipeline批量查询,减少网络往返
- 合并逻辑简单(<5ms),整体响应时间仍低于单层缓存未命中场景
- 缓存命中率提升后,响应时间实际降低

### Risk 2: 数据一致性

**风险**: 全局数据和用户状态分别失效,可能出现短暂不一致

**缓解措施**:
- 用户状态TTL较短(5分钟),不一致窗口短
- 关键操作(如章节完成)主动失效用户状态缓存
- 降级策略: 任一层缓存失效,从数据库查询

### Risk 3: 快照字段迁移

**风险**: 扩展快照 `unlock_states` 字段需要数据迁移

**缓解措施**:
- 字段为JSON格式,扩展无需schema变更
- 提供迁移脚本,批量更新现有快照数据
- 支持渐进式迁移:读取时兼容旧格式,写入时使用新格式

## Migration Plan

### 阶段1: 准备阶段(无破坏性变更)

1. 创建 `ChapterGlobalSerializer` 和 `ProblemGlobalSerializer`
2. 创建用户状态获取辅助函数 `get_chapter_user_status()` 和 `get_problem_user_status()`
3. 添加快照迁移脚本,扩展 `unlock_states` 字段
4. 添加信号处理器

### 阶段2: 切换缓存策略(可选灰度)

1. 在 `ChapterViewSet` 中添加分离缓存逻辑
2. 使用feature flag控制新旧缓存策略切换
3. 监控缓存命中率、内存占用、响应时间
4. 验证数据一致性

### 阶段3: 扩展到其他ViewSet

1. 对 `ProblemViewSet` 应用相同策略
2. 清理旧的缓存键(可选,自动过期)

### 回滚策略

- 通过feature flag快速切回旧缓存策略
- 保留旧缓存键,新旧策略并行运行
- 回滚无需数据迁移,仅配置切换

## Open Questions

1. **是否需要扩展到其他全局数据**: Course, Exam等是否也需要分离缓存?
   - 建议: 先验证章节和问题的效果,再决定是否推广

2. **用户状态缓存批量查询优化**: 是否需要对同一课程的多个章节批量查询用户状态?
   - 建议: 是,使用Redis MGET批量获取,减少查询次数

3. **缓存键命名规范**: 是否需要统一的命名规范(如 `{model}:{scope}:{id}`)?
   - 建议: 是,制定缓存键命名规范文档,避免混乱