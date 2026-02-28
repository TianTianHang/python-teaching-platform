# 设计文档：Problem 解锁查询优化

## 设计原则

**核心策略**：直接复用 Chapter 的成熟快照模式，最小化设计和实现复杂度。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    复用策略：Copy-Paste-Adapt                             │
└─────────────────────────────────────────────────────────────────────────────┘

Chapter 模式 (已验证)              →   Problem 模式 (复制)
═══════════════════════════════════════════════════════════════════════════════
CourseUnlockSnapshot                   ProblemUnlockSnapshot
UnlockSnapshotService                  ProblemUnlockSnapshotService
refresh_unlock_snapshot()              refresh_problem_unlock_snapshot()
ChapterViewSet.get_queryset()          ProblemViewSet.get_queryset()
ChapterSerializer.get_is_locked()      ProblemSerializer.get_is_unlocked()
signals.py                              signals.py (扩展)

复用比例：~85%
特化调整：~15%
```

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           优化后的架构（参考 Chapter）                      │
└─────────────────────────────────────────────────────────────────────────────┘

用户请求                            Celery 异步任务
    │                                    │
    ▼                                    ▼
┌─────────────────┐              ┌──────────────────┐
│ ProblemViewSet  │              │refresh_problem_  │
│                 │◄───────────  │unlock_snapshot   │
│ get_queryset()  │  stale=True  │                  │
└────────┬────────┘              └────────┬─────────┘
         │                                │
         │ 查询快照                        │ 重新计算
         ▼                                ▼
┌─────────────────┐              ┌──────────────────┐
│ProblemUnlock    │              │  PostgreSQL      │
│Snapshot         │              │                  │
│                 │              │  - problems      │
│ unlock_states   │              │  - progress     │
│ (JSON)          │              │  - submissions  │
└─────────────────┘              └──────────────────┘
         │                                │
         │                                │
         ▼                                ▔──────────────┐
┌─────────────────┐                                     │
│  ProblemSerializer│◄────────────────────────────────────┘
│                  │
│ - is_unlocked    │
│ - unlock_        │
│   condition_     │
│   description    │
└─────────────────┘
         │
         ▼
    响应 JSON
```

## 数据模型设计

### ProblemUnlockSnapshot 模型

```python
class ProblemUnlockSnapshot(models.Model):
    """
    问题解锁状态快照表

    参考 CourseUnlockSnapshot 设计，为每个 (course, enrollment) 组合
    预计算所有题目的解锁状态。

    与 Chapter 的差异：
    - unlock_states 存储更多数据（50-100 problems vs 10-30 chapters）
    - 刷新频率更高（30 秒 vs 1 分钟）
    - 批量大小更大（200 vs 100）
    """
    id = models.BigAutoField(primary_key=True)

    # 外键关系
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='problem_unlock_snapshots',
        verbose_name="课程"
    )
    enrollment = models.OneToOneField(
        'Enrollment',
        on_delete=models.CASCADE,
        related_name='problem_unlock_snapshot',
        unique=True,
        verbose_name="课程注册记录"
    )

    # 核心数据：解锁状态 JSON
    # 格式：{
    #   "10": {"unlocked": false, "reason": "prerequisite"},
    #   "11": {"unlocked": true, "reason": null},
    #   "12": {"unlocked": false, "reason": "date"}
    # }
    # 键：problem_id (字符串)，值：解锁状态对象
    unlock_states = models.JSONField(
        default=dict,
        verbose_name="解锁状态",
        help_text="课程所有题目的解锁状态映射"
    )

    # 元数据
    computed_at = models.DateTimeField(
        auto_now=True,
        verbose_name="计算时间",
        db_index=True
    )
    is_stale = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="是否过期",
        help_text="标记快照是否需要重新计算"
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name="版本号",
        help_text="快照版本，用于乐观锁和监控"
    )

    class Meta:
        verbose_name = "问题解锁状态快照"
        verbose_name_plural = "问题解锁状态快照"
        unique_together = ('course', 'enrollment')
        indexes = [
            models.Index(fields=['course', 'enrollment']),
            models.Index(fields=['is_stale', 'computed_at']),
            models.Index(fields=['enrollment']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.enrollment.user.username} (problems v{self.version})"

    def recompute(self):
        """
        重新计算解锁状态

        流程：
        1. 获取课程所有题目
        2. 对每个题目调用 ProblemUnlockCondition.is_unlocked(user)
        3. 更新 unlock_states JSON
        4. 更新 computed_at 和 version

        注意：
        - 复用现有的 ProblemUnlockCondition.is_unlocked() 逻辑
        - 不重构遗留代码（Phase 2 优化时再考虑）
        """
        from .models import Problem, ProblemUnlockCondition, ProblemProgress, Submission

        problems = Problem.objects.filter(course=self.course)
        new_states = {}

        for problem in problems:
            # 复用现有的解锁逻辑（保持一致性）
            try:
                condition = problem.unlock_condition
                is_unlocked = condition.is_unlocked(self.enrollment.user)

                # 获取锁定原因（如果未解锁）
                reason = None
                if not is_unlocked:
                    if condition.unlock_condition_type in ['prerequisite', 'both']:
                        reason = 'prerequisite'
                    elif condition.unlock_condition_type in ['date', 'both']:
                        if condition.unlock_date:
                            from django.utils import timezone
                            if timezone.now() < condition.unlock_date:
                                reason = 'date'

                new_states[str(problem.id)] = {
                    'unlocked': is_unlocked,
                    'reason': reason
                }
            except ProblemUnlockCondition.DoesNotExist:
                # 无解锁条件，默认解锁
                new_states[str(problem.id)] = {
                    'unlocked': True,
                    'reason': None
                }

        self.unlock_states = new_states
        self.is_stale = False
        self.version += 1
        self.save(update_fields=['unlock_states', 'is_stale', 'version'])
```

### 与 Chapter 模型的差异

| 字段 | Chapter | Problem | 差异说明 |
|------|---------|---------|----------|
| 表名 | `course_unlock_snapshot` | `problem_unlock_snapshot` | 命名区分 |
| JSON 大小 | ~2KB (10-30 chapters) | ~4KB (50-100 problems) | Problem 更多 |
| 刷新频率 | 1 分钟 | 30 秒 | Problem 更频繁 |
| 批量大小 | 100 | 200 | Problem 批量更大 |

## 服务层设计

### ProblemUnlockSnapshotService

```python
class ProblemUnlockSnapshotService:
    """
    问题解锁状态快照服务

    参考 UnlockSnapshotService 实现，提供相同的功能：
    1. 管理快照的创建、查询、更新
    2. 实现混合查询策略（快照优先，stale 时降级）
    3. 提供快照刷新接口
    """

    @staticmethod
    def get_or_create_snapshot(enrollment: 'Enrollment') -> 'ProblemUnlockSnapshot':
        """
        获取或创建快照

        如果快照不存在，创建并触发异步计算。
        返回快照对象（可能暂时是空的）。
        """
        snapshot, created = ProblemUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment,
            defaults={'course': enrollment.course}
        )

        if created:
            # 触发异步计算
            from .tasks import refresh_problem_unlock_snapshot
            refresh_problem_unlock_snapshot.delay(enrollment.id)

        return snapshot

    @staticmethod
    def mark_stale(enrollment: 'Enrollment'):
        """
        标记快照为过期

        当用户解决题目时调用。
        不立即重新计算，而是设置 is_stale=True。
        """
        try:
            snapshot = ProblemUnlockSnapshot.objects.get(enrollment=enrollment)
            snapshot.is_stale = True
            snapshot.save(update_fields=['is_stale'])
        except ProblemUnlockSnapshot.DoesNotExist:
            # 快照不存在，无需标记
            pass

    @staticmethod
    def get_unlock_status_hybrid(course: 'Course', enrollment: 'Enrollment') -> dict:
        """
        混合查询策略：优先使用快照，stale 时降级到实时计算

        返回格式：
        {
            'unlock_states': dict,  # {problem_id: {'unlocked': bool, 'reason': str|null}}
            'source': 'snapshot' | 'snapshot_stale' | 'realtime'
        }

        策略：
        1. 尝试获取快照
        2. 如果快照存在且新鲜（is_stale=False），直接返回
        3. 如果快照过期，触发异步刷新，但先返回旧数据
        4. 如果快照不存在，触发异步创建，使用实时计算
        """
        try:
            snapshot = ProblemUnlockSnapshot.objects.get(
                course=course,
                enrollment=enrollment
            )

            if not snapshot.is_stale:
                # 快照新鲜，直接使用
                return {
                    'unlock_states': snapshot.unlock_states,
                    'source': 'snapshot',
                    'snapshot_version': snapshot.version
                }
            else:
                # 快照过期，触发异步刷新
                from .tasks import refresh_problem_unlock_snapshot
                refresh_problem_unlock_snapshot.delay(enrollment.id)

                # 返回旧数据（允许短暂不一致）
                return {
                    'unlock_states': snapshot.unlock_states,
                    'source': 'snapshot_stale',
                    'snapshot_version': snapshot.version
                }

        except ProblemUnlockSnapshot.DoesNotExist:
            # 快照不存在，触发异步创建
            from .tasks import refresh_problem_unlock_snapshot
            refresh_problem_unlock_snapshot.delay(enrollment.id)

            # 降级到实时计算
            return ProblemUnlockSnapshotService._compute_realtime(course, enrollment)

    @staticmethod
    def _compute_realtime(course: 'Course', enrollment: 'Enrollment') -> dict:
        """
        实时计算解锁状态（降级策略）

        复用现有的 ProblemUnlockCondition.is_unlocked() 逻辑。
        """
        from .models import Problem

        problems = Problem.objects.filter(course=course)
        unlock_states = {}

        for problem in problems:
            try:
                condition = problem.unlock_condition
                is_unlocked = condition.is_unlocked(enrollment.user)

                reason = None
                if not is_unlocked:
                    if condition.unlock_condition_type in ['prerequisite', 'both']:
                        reason = 'prerequisite'
                    elif condition.unlock_condition_type in ['date', 'both']:
                        if condition.unlock_date:
                            from django.utils import timezone
                            if timezone.now() < condition.unlock_date:
                                reason = 'date'

                unlock_states[str(problem.id)] = {
                    'unlocked': is_unlocked,
                    'reason': reason
                }
            except ProblemUnlockCondition.DoesNotExist:
                unlock_states[str(problem.id)] = {
                    'unlocked': True,
                    'reason': None
                }

        return {
            'unlock_states': unlock_states,
            'source': 'realtime'
        }
```

### 或：扩展现有 UnlockSnapshotService

**可选方案**：不创建新服务，而是扩展现有的 `UnlockSnapshotService`：

```python
class UnlockSnapshotService:
    """
    通用的解锁状态快照服务（扩展支持 Problem）
    """

    CONTENT_TYPE_CHOICES = ['chapter', 'problem']

    @staticmethod
    def get_unlock_status_hybrid(
        course: 'Course',
        enrollment: 'Enrollment',
        content_type: str = 'chapter'  # 新增参数
    ) -> dict:
        """
        混合查询策略（扩展支持 Problem）

        content_type: 'chapter' | 'problem'
        """
        if content_type == 'chapter':
            snapshot_model = CourseUnlockSnapshot
            task_func = refresh_unlock_snapshot
            compute_func = UnlockSnapshotService._compute_chapter_realtime
        elif content_type == 'problem':
            snapshot_model = ProblemUnlockSnapshot
            task_func = refresh_problem_unlock_snapshot
            compute_func = UnlockSnapshotService._compute_problem_realtime
        else:
            raise ValueError(f"Invalid content_type: {content_type}")

        # ... 统一逻辑

    @staticmethod
    def _compute_chapter_realtime(course, enrollment):
        # Chapter 特定逻辑（现有实现）
        pass

    @staticmethod
    def _compute_problem_realtime(course, enrollment):
        # Problem 特定逻辑（新增）
        pass
```

**优势**：避免代码重复
**劣势**：增加服务复杂度

**推荐**：Phase 1 使用独立服务（快速复制），Phase 2 再考虑合并

## Celery 任务设计

### tasks.py 扩展

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def refresh_problem_unlock_snapshot(self, enrollment_id: int):
    """
    刷新单个 enrollment 的题目解锁状态快照

    参考 refresh_unlock_snapshot 实现。
    """
    from .models import ProblemUnlockSnapshot, Enrollment

    try:
        enrollment = Enrollment.objects.select_related(
            'user', 'course'
        ).get(id=enrollment_id)

        snapshot, created = ProblemUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment,
            defaults={'course': enrollment.course}
        )

        # 重新计算解锁状态
        snapshot.recompute()

        logger.info(
            "Refreshed problem unlock snapshot for enrollment {enrollment_id}",
            extra={
                'enrollment_id': enrollment_id,
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'snapshot_version': snapshot.version
            }
        )

    except Enrollment.DoesNotExist:
        logger.warning(
            "Enrollment {enrollment_id} no longer exists, skipping snapshot refresh",
            extra={'enrollment_id': enrollment_id}
        )
        return None
    except Exception as exc:
        logger.error(
            "Failed to refresh problem snapshot for enrollment {enrollment_id}: {exc}",
            exc_info=True,
            extra={'enrollment_id': enrollment_id}
        )
        raise


@shared_task
def batch_refresh_stale_problem_snapshots(batch_size: int = 200):
    """
    批量刷新过期的题目快照

    注意：batch_size 比 Chapter 大（200 vs 100）
    因为 Problem 数量更多，且需要更频繁刷新。
    """
    from .models import ProblemUnlockSnapshot

    # 清理 orphaned snapshots
    orphaned_count = ProblemUnlockSnapshot.objects.filter(
        enrollment__isnull=True
    ).delete()[0]

    if orphaned_count > 0:
        logger.info(
            "Cleaned up {count} orphaned problem snapshots",
            extra={'count': orphaned_count}
        )

    stale_snapshots = ProblemUnlockSnapshot.objects.filter(
        is_stale=True
    ).select_related('enrollment__user', 'course').order_by('computed_at')[:batch_size]

    count = 0
    for snapshot in stale_snapshots:
        refresh_problem_unlock_snapshot.delay(snapshot.enrollment_id)
        count += 1

    if count > 0:
        logger.info(
            "Triggered batch refresh for {count} stale problem snapshots",
            extra={'batch_size': batch_size}
        )

    return count


@shared_task
def scheduled_problem_snapshot_refresh():
    """
    定时任务：每 30 秒批量刷新过期快照

    注意：频率比 Chapter 高（30 秒 vs 1 分钟）
    因为 Problem 访问更频繁，需要更短的延迟。
    """
    return batch_refresh_stale_problem_snapshots.delay()
```

### Celery Beat 调度配置

在 `backend/core/celery.py` 或 `backend/core/settings.py` 中添加：

```python
app.conf.beat_schedule = {
    # 现有 Chapter 配置
    'refresh-stale-chapter-unlock-snapshots': {
        'task': 'courses.tasks.scheduled_snapshot_refresh',
        'schedule': crontab(minute='*'),  # 每分钟
    },

    # 新增 Problem 配置
    'refresh-stale-problem-unlock-snapshots': {
        'task': 'courses.tasks.scheduled_problem_snapshot_refresh',
        'schedule': crontab(second='*/30'),  # 每 30 秒
    },

    # 其他任务...
}
```

## 信号处理设计

### signals.py 扩展

```python
@receiver(post_save, sender=ProblemProgress)
def mark_problem_snapshot_stale_on_progress_update(sender, instance, created, **kwargs):
    """
    当题目进度更新时，标记相关快照为过期

    参考 mark_snapshot_stale_on_progress_update 实现。

    策略：
    1. 仅当 status='solved' 时触发（避免不必要的标记）
    2. 仅标记当前 enrollment 的快照
    3. 异步刷新会由 Celery 后台任务处理

    性能考虑：
    - 信号处理器应该快速返回（< 10ms）
    - 不在信号中执行复杂查询或计算
    - 使用标记 + 异步任务的分离模式
    """
    # 检查 status 是否为 'solved'
    if instance.status == 'solved':
        try:
            from .services import ProblemUnlockSnapshotService
            ProblemUnlockSnapshotService.mark_stale(instance.enrollment)

            logger.debug(
                "Marked problem snapshot stale for enrollment {enrollment_id}",
                extra={
                    'enrollment_id': instance.enrollment_id,
                    'problem_id': instance.problem_id,
                    'status': instance.status
                }
            )
        except Exception as exc:
            # 信号处理器不应该抛出异常
            logger.error(
                "Failed to mark problem snapshot stale: {exc}",
                exc_info=True,
                extra={
                    'enrollment_id': instance.enrollment_id,
                    'problem_id': instance.problem_id
                }
            )
```

## ViewSet 优化设计

### ProblemViewSet.get_queryset()

```python
def get_queryset(self):
    """
    优化后的查询集（参考 ChapterViewSet.get_queryset）

    策略：
    1. 尝试使用快照数据（避免 N+1 查询）
    2. 快照不存在或过期时，降级到原有逻辑
    3. 保持现有的 prefetch_related（兼容其他字段）
    """
    from .models import ProblemUnlockSnapshot

    queryset = super().get_queryset()
    user = self.request.user
    course_id = self.kwargs.get('course_pk')

    # 获取 enrollment
    enrollment = None
    if course_id and user.is_authenticated:
        try:
            enrollment = Enrollment.objects.select_related('user', 'course').get(
                user=user,
                course_id=course_id
            )
            self._enrollment = enrollment

            # 尝试使用快照
            try:
                snapshot = ProblemUnlockSnapshot.objects.get(enrollment=enrollment)

                if not snapshot.is_stale:
                    # 快照新鲜，使用简化查询
                    self._unlock_states = snapshot.unlock_states
                    self._use_snapshot = True

                    # 仍然需要 prefetch_related（其他字段需要）
                    # 但不需要复杂的 is_unlocked 计算
                    return queryset  # 已有基础查询

            except ProblemUnlockSnapshot.DoesNotExist:
                # 快照不存在，降级到原有逻辑
                self._use_snapshot = False

        except Enrollment.DoesNotExist:
            # 未注册课程，返回空查询集
            pass

    # 降级模式：保持原有逻辑
    if not hasattr(self, '_use_snapshot'):
        self._use_snapshot = False

    # 原有的 prefetch_related 逻辑（保持不变）
    # ... (现有代码)

    return queryset
```

### ProblemViewSet.get_serializer_context()

```python
def get_serializer_context(self):
    """
    向序列化器传递额外的上下文
    """
    context = super().get_serializer_context()

    # 传递 enrollment
    if hasattr(self, '_enrollment'):
        context['enrollment'] = self._enrollment

    # 传递快照相关变量
    if hasattr(self, '_use_snapshot'):
        context['use_snapshot'] = self._use_snapshot
    if hasattr(self, '_unlock_states'):
        context['unlock_states'] = self._unlock_states

    return context
```

## Serializer 适配

### ProblemSerializer.get_is_unlocked()

```python
def get_is_unlocked(self, obj):
    """
    获取当前用户对该问题的解锁状态
    优先使用快照数据，然后回退到原有逻辑
    """
    request = self.context.get('request')
    if not request or not request.user.is_authenticated:
        return False

    # 优先使用快照数据
    view = self.context.get('view')
    if view and hasattr(view, '_use_snapshot') and view._use_snapshot:
        # 使用快照数据
        unlock_states = getattr(view, '_unlock_states', {})
        problem_state = unlock_states.get(str(obj.id))
        if problem_state:
            return problem_state['unlocked']

    # 降级到原有逻辑（保持不变）
    try:
        unlock_condition = obj.unlock_condition
        return unlock_condition.is_unlocked(request.user)
    except AttributeError:
        # 如果没有解锁条件，则默认为已解锁
        return True
```

## 监控与可观测性

### 关键指标

| 指标 | 类型 | 说明 | 告警阈值 |
|------|------|------|----------|
| `problem_snapshot_hit_rate` | Gauge | 快照命中率 | < 80% |
| `problem_snapshot_stale_rate` | Gauge | 过期快照比例 | > 20% |
| `problem_refresh_task_duration` | Histogram | 快照刷新任务耗时 | p95 > 10s |
| `problem_refresh_task_failure_rate` | Gauge | 刷新任务失败率 | > 5% |
| `problem_list_api_latency` | Histogram | Problem API 延迟 | p95 > 200ms |
| `problem_list_query_count` | Histogram | Problem API 查询次数 | p95 > 10 |

### 日志策略

```python
# 在关键位置添加结构化日志
logger.info(
    "Problem unlock snapshot query",
    extra={
        'course_id': course.id,
        'enrollment_id': enrollment.id,
        'source': result['source'],  # 'snapshot' | 'snapshot_stale' | 'realtime'
        'snapshot_version': result.get('snapshot_version'),
        'latency_ms': (end - start) * 1000,
        'problem_count': len(result['unlock_states'])
    }
)
```

## 测试策略

### 单元测试

```python
# courses/tests/test_problem_unlock_snapshot.py

class ProblemUnlockSnapshotTest(TestCase):
    """测试 ProblemUnlockSnapshot"""

    def test_recompute_basic(self):
        """测试基础 recompute 逻辑"""
        # 创建测试数据
        enrollment = Enrollment.objects.create(...)
        problems = Problem.objects.create_batch(5, course=enrollment.course)

        # 创建快照并计算
        snapshot = ProblemUnlockSnapshot.objects.create(
            enrollment=enrollment,
            course=enrollment.course
        )
        snapshot.recompute()

        # 验证
        self.assertEqual(len(snapshot.unlock_states), 5)
        self.assertFalse(snapshot.is_stale)
        self.assertEqual(snapshot.version, 2)

    def test_recompute_with_prerequisites(self):
        """测试有前置题目的 recompute"""
        # ...

class ProblemUnlockSnapshotServiceTest(TestCase):
    """测试 ProblemUnlockSnapshotService"""

    def test_get_unlock_status_hybrid_snapshot_fresh(self):
        """测试混合查询 - 快照新鲜"""
        # ...

    def test_get_unlock_status_hybrid_snapshot_stale(self):
        """测试混合查询 - 快照过期"""
        # ...

    def test_get_unlock_status_hybrid_no_snapshot(self):
        """测试混合查询 - 无快照"""
        # ...
```

### 集成测试

```python
class ProblemUnlockIntegrationTest(TestCase):
    """集成测试：题目解锁流程"""

    def test_solve_problem_updates_snapshot(self):
        """测试解题后快照更新"""
        # 初始状态：problem 2 被锁定
        self.assertFalse(problem2.is_unlocked)

        # 解决 problem 1
        ProblemProgress.objects.create(
            enrollment=enrollment,
            problem=problem1,
            status='solved'
        )

        # 等待 Celery 任务执行（或手动调用）
        refresh_problem_unlock_snapshot(enrollment.id)

        # 验证快照已更新
        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)
        self.assertTrue(snapshot.unlock_states['2']['unlocked'])
```

### 性能测试

```python
class ProblemUnlockPerformanceTest(TestCase):
    """性能测试"""

    def test_query_comparison(self):
        """对比优化前后的查询性能"""
        # 优化前：N+1 查询
        start = time.time()
        for _ in range(100):
            # 模拟原有逻辑（调用 is_unlocked）
            list(problems)  # 每个调用 is_unlocked
        old_duration = time.time() - start

        # 优化后：使用快照
        start = time.time()
        for _ in range(100):
            ProblemUnlockSnapshotService.get_unlock_status_hybrid(
                course, enrollment
            )
        new_duration = time.time() - start

        # 验证性能提升
        improvement = old_duration / new_duration
        self.assertGreater(improvement, 10)  # 至少 10 倍提升
```

## 部署检查清单

### 迁移前

- [ ] 备份数据库
- [ ] 在测试环境执行迁移
- [ ] 验证快照表创建成功
- [ ] 验证索引创建成功
- [ ] 运行单元测试和集成测试

### 迁移中

- [ ] 部署代码（包含新模型、服务、任务）
- [ ] 执行数据库迁移 `python manage.py migrate`
- [ ] 重启 Django 应用
- [ ] 重启 Celery worker
- [ ] 重启 Celery beat
- [ ] 验证 Celery 任务正常运行

### 迁移后

- [ ] 监控快照创建率（应该快速达到 ~100% enrollment 覆盖）
- [ ] 监控 API 延迟（应该显著下降）
- [ ] 监控数据库负载（查询数应该显著下降）
- [ ] 监控 Celery 队列长度（不应该堆积）
- [ ] 验证数据一致性（对比快照和实时计算）

## 与 Chapter 对比总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Chapter vs Problem 优化对比                             │
└─────────────────────────────────────────────────────────────────────────────┘

实现复杂度：
═══════════════════════════════════════════════════════════════════════════════
Chapter: 需要设计 + 实现                          │
Problem: 复制 Chapter 模式                        │
                                                 │
复杂度: 中等                                      │
复杂度: 低（模式已验证）                          │

实现时间: 5-8 天                                 │
实现时间: 1-2 天                                 │

风险: 中等（新模式）                              │
风险: 低（已验证）                                │

═══════════════════════════════════════════════════════════════════════════════

性能优化空间：
═══════════════════════════════════════════════════════════════════════════════
Chapter: 5 次查询 → 2 次                          │
Problem: 300+ 次查询 → 2 次                       │
                                                 │
优化收益: 60-80%                                  │
优化收益: 98%+                                    │

优化前: 200-500ms                                 │
优化前: 500-2000ms                                │

优化后: 20-50ms                                   │
优化后: 50-100ms                                 │

═══════════════════════════════════════════════════════════════════════════════

配置差异：
═══════════════════════════════════════════════════════════════════════════════
                        │ Chapter      │ Problem
═════════════════════════┼──────────────┼──────────────
刷新频率                 │ 1 分钟       │ 30 秒
批量大小                 │ 100          │ 200
快照大小                 │ ~2KB         │ ~4KB
存储需求                 │ ~20MB        │ ~40MB

═══════════════════════════════════════════════════════════════════════════════

Phase 2 统一优化：
═══════════════════════════════════════════════════════════════════════════════
1. 合并 CourseUnlockSnapshot 和 ProblemUnlockSnapshot
2. 创建通用 ContentUnlockSnapshot
3. 抽象通用服务层
4. 添加其他可解锁内容（Quiz, Exam）

预计节省：30-40% 代码重复
```

## 未来优化方向

### Phase 2: 统一快照表

```python
class ContentUnlockSnapshot(models.Model):
    """
    统一的内容解锁状态快照表

    替代 CourseUnlockSnapshot 和 ProblemUnlockSnapshot。
    """
    enrollment = OneToOneField(Enrollment)
    content_type = CharField(max_length=20)  # 'chapter' | 'problem'
    unlock_states = JSONField()
    is_stale = BooleanField(default=False)
    # ...

    class Meta:
        unique_together = ('enrollment', 'content_type')
```

### Phase 3: 通用服务层

```python
class UnlockSnapshotService:
    """
    统一的解锁快照服务

    支持 Chapter, Problem, Quiz, Exam 等所有可解锁内容。
    """
    @staticmethod
    def get_unlock_status(content_type, course, enrollment):
        # 统一接口
        pass
```

### Phase 4: 智能刷新策略

```python
# 根据用户活跃度动态调整刷新频率
active_users: 30 秒
inactive_users: 5 分钟

# 根据内容类型调整
problem: 30 秒
chapter: 1 分钟
quiz: 2 分钟
exam: 5 分钟
```
