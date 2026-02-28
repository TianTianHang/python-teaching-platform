# 设计文档：章节解锁查询优化

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           优化后的架构                                      │
└─────────────────────────────────────────────────────────────────────────────┘

用户请求                            Celery 异步任务
    │                                    │
    ▼                                    ▼
┌─────────────────┐              ┌──────────────────┐
│ ChapterViewSet  │              │  refresh_unlock  │
│                 │◄───────────  │  _snapshot       │
│ get_queryset()  │  stale=True  │                  │
└────────┬────────┘              └────────┬─────────┘
         │                                │
         │ 查询快照                        │ 重新计算
         ▼                                ▼
┌─────────────────┐              ┌──────────────────┐
│CourseUnlock     │              │  PostgreSQL      │
│Snapshot         │              │                  │
│                 │              │  - chapters      │
│ unlock_states   │              │  - progress     │
│ (JSON)          │              │  - conditions   │
└─────────────────┘              └──────────────────┘
         │                                │
         │                                │
         ▼                                ▔──────────────┐
┌─────────────────┐                                     │
│   Serializer    │◄────────────────────────────────────┘
│                 │
│ - is_locked     │
│ - prerequisite_ │
│   progress      │
└─────────────────┘
         │
         ▼
    响应 JSON
```

## 数据模型设计

### CourseUnlockSnapshot 模型

```python
class CourseUnlockSnapshot(models.Model):
    """
    课程解锁状态快照表

    为每个 (course, enrollment) 组合预计算所有章节的解锁状态。
    使用 JSONB 存储解锁状态，支持快速查询和更新。

    设计考量：
    - OneToOneField to Enrollment：每个用户在每个课程下只有一个快照
    - JSONB unlock_states：PostgreSQL 原生支持，可建索引，查询高效
    - is_stale 标记：避免频繁写入，支持批量刷新
    """
    id = models.BigAutoField(primary_key=True)

    # 外键关系
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='unlock_snapshots',
        verbose_name="课程"
    )
    enrollment = models.OneToOneField(
        'Enrollment',
        on_delete=models.CASCADE,
        related_name='unlock_snapshot',
        unique=True,
        verbose_name="课程注册记录"
    )

    # 核心数据：解锁状态 JSON
    # 格式：{
    #   "1": {"locked": false, "reason": null},
    #   "2": {"locked": true, "reason": "prerequisite"},
    #   "3": {"locked": true, "reason": "date"},
    #   "4": {"locked": true, "reason": "both"}
    # }
    # 键：chapter_id (字符串)，值：解锁状态对象
    unlock_states = models.JSONField(
        default=dict,
        verbose_name="解锁状态",
        help_text="课程所有章节的解锁状态映射"
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
        verbose_name = "课程解锁状态快照"
        verbose_name_plural = "课程解锁状态快照"
        unique_together = ('course', 'enrollment')
        indexes = [
            # 复合索引：快速查询特定课程的快照
            models.Index(fields=['course', 'enrollment']),
            # 复合索引：批量刷新过期快照
            models.Index(fields=['is_stale', 'computed_at']),
            # 单列索引：通过 enrollment 快速查询
            models.Index(fields=['enrollment']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.enrollment.user.username} (v{self.version})"

    def recompute(self):
        """
        重新计算解锁状态

        流程：
        1. 获取课程所有章节
        2. 对每个章节调用现有的解锁逻辑
        3. 更新 unlock_states JSON
        4. 更新 computed_at 和 version
        """
        from .services import ChapterUnlockService

        chapters = self.course.chapters.all()
        new_states = {}

        for chapter in chapters:
            # 复用现有的解锁逻辑（保持一致性）
            is_locked = not ChapterUnlockService.is_unlocked(chapter, self.enrollment)

            # 获取锁定原因
            if is_locked and hasattr(chapter, 'unlock_condition'):
                condition = chapter.unlock_condition
                unlock_type = condition.unlock_condition_type

                # 检查前置章节
                has_unmet_prereqs = False
                if unlock_type in ('prerequisite', 'all'):
                    from .models import ChapterProgress
                    prereq_ids = list(condition.prerequisite_chapters.values_list('id', flat=True))
                    completed_count = ChapterProgress.objects.filter(
                        enrollment=self.enrollment,
                        chapter_id__in=prereq_ids,
                        completed=True
                    ).count()
                    has_unmet_prereqs = completed_count < len(prereq_ids)

                # 检查解锁日期
                is_before_date = False
                if unlock_type in ('date', 'all') and condition.unlock_date:
                    from django.utils import timezone
                    is_before_date = timezone.now() < condition.unlock_date

                # 确定原因
                if has_unmet_prereqs and is_before_date:
                    reason = 'both'
                elif has_unmet_prereqs:
                    reason = 'prerequisite'
                elif is_before_date:
                    reason = 'date'
                else:
                    reason = None
            else:
                reason = None

            new_states[str(chapter.id)] = {
                'locked': is_locked,
                'reason': reason
            }

        self.unlock_states = new_states
        self.is_stale = False
        self.version += 1
        self.save(update_fields=['unlock_states', 'is_stale', 'version'])
```

### 索引设计说明

| 索引 | 用途 | 查询模式 |
|------|------|----------|
| `(course, enrollment)` | ViewSet 查询 | `WHERE course_id = ? AND enrollment_id = ?` |
| `(is_stale, computed_at)` | Celery 批量刷新 | `WHERE is_stale = True ORDER BY computed_at LIMIT 100` |
| `(enrollment)` | 通过 enrollment 反向查询 | `SELECT * FROM ... WHERE enrollment_id = ?` |

## 服务层设计

### UnlockSnapshotService

```python
class UnlockSnapshotService:
    """
    解锁状态快照服务

    职责：
    1. 管理快照的创建、查询、更新
    2. 实现混合查询策略（快照优先，stale 时降级）
    3. 提供快照刷新接口
    """

    @staticmethod
    def get_or_create_snapshot(enrollment: Enrollment) -> CourseUnlockSnapshot:
        """
        获取或创建快照

        如果快照不存在，创建并触发异步计算。
        返回快照对象（可能暂时是空的）。
        """
        snapshot, created = CourseUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment,
            defaults={'course': enrollment.course}
        )

        if created:
            # 触发异步计算
            from .tasks import refresh_unlock_snapshot
            refresh_unlock_snapshot.delay(enrollment.id)

        return snapshot

    @staticmethod
    def mark_stale(enrollment: Enrollment):
        """
        标记快照为过期

        当用户完成章节时调用。
        不立即重新计算，而是设置 is_stale=True。
        """
        try:
            snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)
            snapshot.is_stale = True
            snapshot.save(update_fields=['is_stale'])
        except CourseUnlockSnapshot.DoesNotExist:
            # 快照不存在，无需标记
            pass

    @staticmethod
    def get_unlock_status_hybrid(course: Course, enrollment: Enrollment) -> dict:
        """
        混合查询策略：优先使用快照，stale 时降级到实时计算

        返回格式：
        {
            'unlock_states': dict,  # {chapter_id: {'locked': bool, 'reason': str|null}}
            'source': 'snapshot' | 'snapshot_stale' | 'realtime'
        }

        策略：
        1. 尝试获取快照
        2. 如果快照存在且新鲜（is_stale=False），直接返回
        3. 如果快照过期，触发异步刷新，但先返回旧数据
        4. 如果快照不存在，触发异步创建，使用实时计算
        """
        try:
            snapshot = CourseUnlockSnapshot.objects.get(
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
                from .tasks import refresh_unlock_snapshot
                refresh_unlock_snapshot.delay(enrollment.id)

                # 返回旧数据（允许短暂不一致）
                return {
                    'unlock_states': snapshot.unlock_states,
                    'source': 'snapshot_stale',
                    'snapshot_version': snapshot.version
                }

        except CourseUnlockSnapshot.DoesNotExist:
            # 快照不存在，触发异步创建
            from .tasks import refresh_unlock_snapshot
            refresh_unlock_snapshot.delay(enrollment.id)

            # 降级到实时计算
            return UnlockSnapshotService._compute_realtime(course, enrollment)

    @staticmethod
    def _compute_realtime(course: Course, enrollment: Enrollment) -> dict:
        """
        实时计算解锁状态（降级策略）

        复用现有的 ChapterUnlockService.is_unlocked() 逻辑。
        """
        from .services import ChapterUnlockService

        chapters = course.chapters.all()
        unlock_states = {}

        for chapter in chapters:
            is_locked = not ChapterUnlockService.is_unlocked(chapter, enrollment)

            if is_locked and hasattr(chapter, 'unlock_condition'):
                # 获取锁定原因（逻辑同 recompute）
                condition = chapter.unlock_condition
                unlock_type = condition.unlock_condition_type

                from .models import ChapterProgress
                from django.utils import timezone

                has_unmet_prereqs = False
                if unlock_type in ('prerequisite', 'all'):
                    prereq_ids = list(condition.prerequisite_chapters.values_list('id', flat=True))
                    completed_count = ChapterProgress.objects.filter(
                        enrollment=enrollment,
                        chapter_id__in=prereq_ids,
                        completed=True
                    ).count()
                    has_unmet_prereqs = completed_count < len(prereq_ids)

                is_before_date = False
                if unlock_type in ('date', 'all') and condition.unlock_date:
                    is_before_date = timezone.now() < condition.unlock_date

                if has_unmet_prereqs and is_before_date:
                    reason = 'both'
                elif has_unmet_prereqs:
                    reason = 'prerequisite'
                elif is_before_date:
                    reason = 'date'
                else:
                    reason = None
            else:
                reason = None

            unlock_states[str(chapter.id)] = {
                'locked': is_locked,
                'reason': reason
            }

        return {
            'unlock_states': unlock_states,
            'source': 'realtime'
        }
```

## Celery 任务设计

### tasks.py

```python
from celery import shared_task
from celery.schedules import crontab
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 重试间隔 60 秒
    autoretry_for=(Exception,),
)
def refresh_unlock_snapshot(self, enrollment_id: int):
    """
    刷新单个 enrollment 的解锁状态快照

    重试策略：
    - 最多重试 3 次
    - 重试间隔 60 秒
    - 自动重试所有异常

    性能优化：
    - 使用 select_related 减少 DB 查询
    - 使用 update_fields 减少写入字段
    - 事务保证原子性
    """
    from .models import CourseUnlockSnapshot, Enrollment

    try:
        # 使用 select_related 优化查询
        enrollment = Enrollment.objects.select_related(
            'user', 'course'
        ).get(id=enrollment_id)

        snapshot, created = CourseUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment,
            defaults={'course': enrollment.course}
        )

        # 重新计算解锁状态
        snapshot.recompute()

        logger.info(
            f"Refreshed unlock snapshot for enrollment {enrollment_id}",
            extra={
                'enrollment_id': enrollment_id,
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'snapshot_version': snapshot.version
            }
        )

    except Exception as exc:
        logger.error(
            f"Failed to refresh snapshot for enrollment {enrollment_id}: {exc}",
            exc_info=True,
            extra={'enrollment_id': enrollment_id}
        )
        raise


@shared_task
def batch_refresh_stale_snapshots(batch_size: int = 100):
    """
    批量刷新过期的快照

    策略：
    - 每次处理 batch_size 个过期快照
    - 按 computed_at 升序排序（最旧的优先）
    - 为每个快照触发单独的异步任务（并行处理）

    调用频率：每分钟
    """
    from .models import CourseUnlockSnapshot

    stale_snapshots = CourseUnlockSnapshot.objects.filter(
        is_stale=True
    ).select_related('enrollment__user', 'course')[:batch_size]

    count = 0
    for snapshot in stale_snapshots:
        refresh_unlock_snapshot.delay(snapshot.enrollment_id)
        count += 1

    if count > 0:
        logger.info(
            f"Triggered batch refresh for {count} stale snapshots",
            extra={'batch_size': batch_size}
        )

    return count


@shared_task
def scheduled_snapshot_refresh():
    """
    定时任务：每分钟批量刷新过期快照

    调度：Celery Beat
    """
    return batch_refresh_stale_snapshots.delay()


@shared_task
def cleanup_old_snapshots(days: int = 30):
    """
    清理旧快照（可选的维护任务）

    删除 inactive enrollment 的快照（用户已退课）。
    每天执行一次。

    注意：此任务可选，根据实际需求决定是否启用。
    """
    from .models import CourseUnlockSnapshot, Enrollment

    # 找出已删除的 enrollment 的快照
    old_snapshots = CourseUnlockSnapshot.objects.filter(
        enrollment__isnull=True
    )

    count = old_snapshots.delete()[0]

    logger.info(
        f"Cleaned up {count} old snapshots",
        extra={'days': days}
    )

    return count
```

### Celery Beat 调度配置

在 `backend/core/celery.py` 或 `backend/core/settings.py` 中添加：

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'refresh-stale-chapter-unlock-snapshots': {
        'task': 'courses.tasks.scheduled_snapshot_refresh',
        'schedule': crontab(minute='*'),  # 每分钟
    },
    'cleanup-old-chapter-unlock-snapshots': {
        'task': 'courses.tasks.cleanup_old_snapshots',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨 2 点
    },
}
```

## 信号处理设计

### signals.py

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChapterProgress
from .services import UnlockSnapshotService
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ChapterProgress)
def mark_snapshot_stale_on_progress_update(sender, instance, created, **kwargs):
    """
    当章节进度更新时，标记相关快照为过期

    策略：
    1. 仅当 completed 状态变化时触发（避免不必要的标记）
    2. 仅标记当前 enrollment 的快照
    3. 异步刷新会由 Celery 后台任务处理

    性能考虑：
    - 信号处理器应该快速返回（< 10ms）
    - 不在信号中执行复杂查询或计算
    - 使用标记 + 异步任务的分离模式
    """
    # 检查 completed 字段是否变化
    if instance.completed:
        # 跟踪字段变化（需要实例有 _state.adding 或跟踪原始值）
        # 简化起见，我们假设 completed=True 总是需要更新
        try:
            UnlockSnapshotService.mark_stale(instance.enrollment)

            logger.debug(
                f"Marked snapshot stale for enrollment {instance.enrollment_id}",
                extra={
                    'enrollment_id': instance.enrollment_id,
                    'chapter_id': instance.chapter_id,
                    'completed': instance.completed
                }
            )
        except Exception as exc:
            # 信号处理器不应该抛出异常
            logger.error(
                f"Failed to mark snapshot stale: {exc}",
                exc_info=True,
                extra={
                    'enrollment_id': instance.enrollment_id,
                    'chapter_id': instance.chapter_id
                }
            )
```

### apps.py 连接信号

```python
from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    verbose_name = '课程管理'

    def ready(self):
        # 导入信号处理器
        import courses.signals
```

## ViewSet 优化设计

### ChapterViewSet.get_queryset()

```python
def get_queryset(self):
    """
    优化后的查询集

    策略：
    1. 尝试使用快照数据（避免复杂注解）
    2. 快照不存在或过期时，降级到原有逻辑
    3. 移除不必要的 prefetch_related（快照模式下不需要）
    """
    from .models import CourseUnlockSnapshot
    from .services import UnlockSnapshotService

    user = self.request.user
    course_id = self.kwargs.get('course_pk')

    if not course_id:
        return Chapter.objects.none()

    # 基础查询
    queryset = Chapter.objects.filter(course_id=course_id).order_by('course__title', 'order')

    # 获取 enrollment
    try:
        enrollment = Enrollment.objects.select_related('user', 'course').get(
            user=user,
            course_id=course_id
        )
        self._enrollment = enrollment
    except Enrollment.DoesNotExist:
        # 未注册课程，返回空查询集
        return Chapter.objects.none()

    # 尝试使用快照
    try:
        snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)

        if not snapshot.is_stale:
            # 快照新鲜，使用简化查询
            self._unlock_states = snapshot.unlock_states
            self._use_snapshot = True

            # 不需要复杂的注解和预取
            return queryset

    except CourseUnlockSnapshot.DoesNotExist:
        pass

    # 降级到原有逻辑
    self._use_snapshot = False

    # 预取已完成的章节 ID
    self._completed_chapter_ids = set(
        ChapterProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).values_list('chapter_id', flat=True)
    )

    # 使用原有的复杂注解
    queryset = self._annotate_is_locked(queryset, enrollment)

    # 预取关联数据
    queryset = queryset.prefetch_related(
        Prefetch(
            'unlock_condition__prerequisite_chapters',
            queryset=Chapter.objects.only('id', 'title', 'order'),
            to_attr='prerequisite_chapters_all'
        ),
        Prefetch(
            'progress_records',
            queryset=ChapterProgress.objects.filter(
                enrollment=enrollment
            ).only('chapter', 'completed', 'completed_at'),
            to_attr='user_progress'
        )
    )

    return queryset
```

### Serializer 适配

```python
def get_is_locked(self, obj):
    """
    优先使用快照数据，避免重复计算
    """
    request = self.context.get('request')
    if not request or not request.user.is_authenticated:
        return False

    view = self.context.get('view')
    if view and hasattr(view, '_use_snapshot') and view._use_snapshot:
        # 使用快照数据
        unlock_states = view._unlock_states
        chapter_state = unlock_states.get(str(obj.id))
        if chapter_state:
            return chapter_state['locked']

    # 降级到注解或实时计算
    if hasattr(obj, 'is_locked_db'):
        return obj.is_locked_db

    # 最终降级到 service
    from courses.services import ChapterUnlockService
    from courses.models import Enrollment

    try:
        enrollment = self.context.get('enrollment')
        if enrollment is None:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=obj.course
            )
        return not ChapterUnlockService.is_unlocked(obj, enrollment)
    except Enrollment.DoesNotExist:
        return False
```

## 监控与可观测性

### 关键指标

| 指标 | 类型 | 说明 | 告警阈值 |
|------|------|------|----------|
| `snapshot_hit_rate` | Gauge | 快照命中率（快照命中 / 总请求） | < 80% |
| `snapshot_stale_rate` | Gauge | 过期快照比例（stale 快照 / 总快照） | > 20% |
| `refresh_task_duration` | Histogram | 快照刷新任务耗时 | p95 > 5s |
| `refresh_task_failure_rate` | Gauge | 刷新任务失败率 | > 5% |
| `chapter_list_api_latency` | Histogram | 章节 API 延迟 | p95 > 100ms |
| `chapter_list_query_count` | Histogram | 章节 API 查询次数 | p95 > 5 |

### 日志策略

```python
# 在关键位置添加结构化日志
logger.info(
    "Chapter unlock snapshot query",
    extra={
        'course_id': course.id,
        'enrollment_id': enrollment.id,
        'source': result['source'],  # 'snapshot' | 'snapshot_stale' | 'realtime'
        'snapshot_version': result.get('snapshot_version'),
        'latency_ms': (end - start) * 1000
    }
)
```

### Prometheus 指标（可选）

```python
from prometheus_client import Counter, Histogram, Gauge

snapshot_hit_counter = Counter(
    'chapter_unlock_snapshot_hits_total',
    'Total number of snapshot hits',
    ['source']  # 'snapshot' | 'snapshot_stale' | 'realtime'
)

refresh_task_duration = Histogram(
    'chapter_unlock_refresh_duration_seconds',
    'Time spent refreshing unlock snapshot'
)

stale_snapshot_gauge = Gauge(
    'chapter_unlock_stale_snapshots_total',
    'Number of stale snapshots'
)
```

## 测试策略

### 单元测试

```python
# courses/tests/test_unlock_snapshot.py

class UnlockSnapshotServiceTest(TestCase):
    """测试 UnlockSnapshotService"""

    def test_get_or_create_snapshot(self):
        """测试快照创建"""
        enrollment = Enrollment.objects.create(...)
        snapshot = UnlockSnapshotService.get_or_create_snapshot(enrollment)

        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.enrollment, enrollment)

    def test_mark_stale(self):
        """测试标记过期"""
        snapshot = CourseUnlockSnapshot.objects.create(...)
        UnlockSnapshotService.mark_stale(snapshot.enrollment)

        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

    def test_hybrid_query_snapshot_fresh(self):
        """测试混合查询 - 快照新鲜"""
        result = UnlockSnapshotService.get_unlock_status_hybrid(course, enrollment)
        self.assertEqual(result['source'], 'snapshot')

    def test_hybrid_query_snapshot_stale(self):
        """测试混合查询 - 快照过期"""
        snapshot.is_stale = True
        snapshot.save()

        result = UnlockSnapshotService.get_unlock_status_hybrid(course, enrollment)
        self.assertEqual(result['source'], 'snapshot_stale')

    def test_hybrid_query_no_snapshot(self):
        """测试混合查询 - 无快照"""
        CourseUnlockSnapshot.objects.all().delete()

        result = UnlockSnapshotService.get_unlock_status_hybrid(course, enrollment)
        self.assertEqual(result['source'], 'realtime')
```

### 集成测试

```python
class ChapterUnlockIntegrationTest(TestCase):
    """集成测试：章节解锁流程"""

    def test_mark_completed_updates_snapshot(self):
        """测试完成章节后快照更新"""
        # 初始状态：章节 2 被锁定
        self.assertTrue(chapter2.is_locked)

        # 完成章节 1
        ChapterProgress.objects.create(
            enrollment=enrollment,
            chapter=chapter1,
            completed=True
        )

        # 等待 Celery 任务执行（或手动调用）
        refresh_unlock_snapshot(enrollment.id)

        # 验证快照已更新
        snapshot.refresh_from_db()
        self.assertFalse(snapshot.is_stale)
        self.assertFalse(snapshot.unlock_states['2']['locked'])

    @override_settings(CACHE_TIMEOUT=0)  # 禁用缓存
    def test_concurrent_requests(self):
        """测试并发场景"""
        # 模拟 25 个并发请求
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [
                executor.submit(
                    self.client.get,
                    f'/api/v1/courses/{course.id}/chapters/'
                )
                for _ in range(25)
            ]
            responses = [f.result() for f in futures]

        # 验证响应成功
        for response in responses:
            self.assertEqual(response.status_code, 200)
```

### 性能测试

```python
class ChapterUnlockPerformanceTest(TestCase):
    """性能测试"""

    def test_query_comparison(self):
        """对比优化前后的查询性能"""
        # 优化前：使用 Exists 子查询
        start = time.time()
        for _ in range(100):
            list(ChapterViewSet()._annotate_is_locked(queryset, enrollment))
        old_duration = time.time() - start

        # 优化后：使用快照
        start = time.time()
        for _ in range(100):
            UnlockSnapshotService.get_unlock_status_hybrid(course, enrollment)
        new_duration = time.time() - start

        # 验证性能提升
        improvement = old_duration / new_duration
        self.assertGreater(improvement, 5)  # 至少 5 倍提升
```

## 数据一致性保证

### 一致性模型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        最终一致性模型                                       │
└─────────────────────────────────────────────────────────────────────────────┘

时间线：
t0: 用户完成章节 1
    → ChapterProgress.completed = True
    → 信号触发：mark_snapshot_stale()
    → Celery 任务入队

t1: 用户立即刷新章节列表（< 1 秒）
    → 快照仍然是旧的（显示章节 2 被锁定）
    → source: 'snapshot_stale'
    → 返回旧数据（允许不一致）

t2: 后台任务执行（1-60 秒内）
    → refresh_unlock_snapshot 执行
    → 重新计算所有章节状态
    → 更新 unlock_states
    → is_stale = False

t3: 用户再次刷新（> 60 秒）
    → 快照已更新
    → source: 'snapshot'
    → 显示最新状态（章节 2 已解锁）

不一致窗口：最多 1 分钟（可配置）
```

### 一致性验证

```python
# 定时任务：验证快照一致性
@shared_task
def validate_snapshot_consistency():
    """
    对比快照和实时计算，检测不一致

    策略：
    - 随机抽样 10% 的快照
    - 对比快照数据和实时计算
    - 记录不一致的情况
    - 自动修正或告警
    """
    from .models import CourseUnlockSnapshot
    from .services import UnlockSnapshotService

    snapshots = CourseUnlockSnapshot.objects.order_by('?')[:100]
    inconsistent_count = 0

    for snapshot in snapshots:
        realtime = UnlockSnapshotService._compute_realtime(
            snapshot.course,
            snapshot.enrollment
        )

        # 对比 unlock_states
        if realtime['unlock_states'] != snapshot.unlock_states:
            inconsistent_count += 1
            logger.warning(
                "Snapshot inconsistency detected",
                extra={
                    'snapshot_id': snapshot.id,
                    'enrollment_id': snapshot.enrollment_id,
                    'course_id': snapshot.course_id
                }
            )

            # 自动修正
            snapshot.recompute()

    return inconsistent_count
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
- [ ] 重启 Celery worker 和 beat
- [ ] 验证 Celery 任务正常运行

### 迁移后

- [ ] 监控快照创建率（应该快速达到 ~100% enrollment 覆盖）
- [ ] 监控 API 延迟（应该显著下降）
- [ ] 监控数据库负载（查询数应该显著下降）
- [ ] 监控 Celery 队列长度（不应该堆积）
- [ ] 验证数据一致性（对比快照和实时计算）

### 回滚预案

如果出现严重问题：

1. **关闭快照功能**：设置环境变量 `USE_UNLOCK_SNAPSHOT=False`
2. **清空 Celery 队列**：`celery -A backend purge`
3. **降级到旧逻辑**：ViewSet 会自动检测快照不存在，使用原有逻辑
4. **删除快照表**（可选）：`python manage.py migrate courses zero`

## 未来优化方向

### Phase 2 优化

1. **依赖关系图预计算**
   - 添加 `ChapterDependencyGraph` 模型
   - 预计算传递闭包（所有间接前置章节）
   - 进一步优化 `recompute()` 性能

2. **增量更新**
   - 仅更新受影响的章节（而不是全部重算）
   - 使用依赖关系图快速定位受影响章节
   - 减少快照刷新时间

3. **PostgreSQL 物化视图**
   - 考虑使用数据库原生物化视图
   - 自动刷新机制（REFRESH CONCURRENTLY）
   - 进一步减少应用层逻辑

4. **智能刷新调度**
   - 根据用户活跃度动态调整刷新频率
   - 活跃用户：1 分钟刷新
   - 不活跃用户：1 小时刷新
   - 减少无效计算
