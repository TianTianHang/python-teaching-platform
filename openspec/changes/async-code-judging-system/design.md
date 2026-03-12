## Context

当前系统使用同步评测模式，`SubmissionViewSet.create()` 直接调用 `CodeExecutorService.run_all_test_cases()`，导致：
- 用户等待 2-30 秒无法进行其他操作
- 高并发时服务器负载高
- CPU 资源利用率低

现有基础设施已具备 Django + Celery + Redis 环境，`CodeExecutorService` 已封装 Judge0 API，需要在此基础上改造为异步架构。

## Goals / Non-Goals

**Goals:**
- 用户体验：响应时间 < 100ms，提供实时状态反馈
- 系统稳定性：队列容量管理，防止过载
- 可扩展性：支持动态调整 Worker 数量
- 可观测性：实时监控队列状态和性能指标

**Non-Goals:**
- 重写 Judge0 集成（保持现有后端不变）
- 实现实时 WebSocket 通知（轮询机制足够）
- 多语言评测支持（保持现有语言支持）

## Decisions

### 1. 三层超时设计

**决策**: 采用排队超时 → 软超时 → 硬超时的三层保护
- **排队超时（120秒）**：用户愿意等待的最长时间
- **软超时（270秒）**：优雅退出，保存部分结果
- **硬超时（300秒）**：强制终止，防止资源泄漏

**替代方案考虑**:
- 单一超时：无法区分排队等待和执行时间
- 无排队超时：用户可能无限等待
**选择理由**: 三层设计兼顾用户体验和系统保护

### 2. Redis 缓存容量状态

**决策**: 使用 Redis 缓存队列容量，30秒过期
- **优点**: 减少数据库查询，提高性能
- **缺点**: 短暂不一致（可接受）

**替代方案考虑**:
- 实时计算：性能开销大
- 不使用缓存：数据库压力大
**选择理由**: 容量状态不需要实时一致，缓存提升性能

### 3. 专用 Celery 队列

**决策**: 创建独立的 `code_judging` 队列，使用专用 Worker
- **优点**: 隔离评测任务，优先级控制
- **缺点**: 增加部署复杂度

**替代方案考虑**:
- 默认队列：可能被其他任务影响
- 多队列：过度设计
**选择理由**: 评测任务是 CPU 密集型，需要专门资源

### 4. 前端轮询机制

**决策**: 采用 2 秒间隔轮询，最多 60 次
- **优点**: 实现简单，兼容 SSR
- **缺点**: 网络开销（可接受）

**替代方案考虑**:
- WebSocket：需要额外服务，SSR 兼容性差
- Server-Sent Events：类似轮询，实现复杂
**选择理由**: 轮询机制简单可靠，满足 SSR 要求

## Risks / Trade-offs

### [Risk] 队列积压
- **影响**: 系统响应变慢，用户体验下降
- **Mitigation**: 设置容量限制 (max_queue_size=18)，动态扩容 Worker

### [Risk] 超时频繁
- **影响**: 用户需要重新提交
- **Mitigation**: 优化评测逻辑，合理设置超时时间

### [Risk] 数据不一致
- **影响**: 队列状态和实际状态不符
- **Mitigation**: 事务保证，定期清理过期数据

### [Risk] 资源泄漏
- **影响**: Worker 进程内存泄漏
- **Mitigation**: 设置 max_tasks_per_child=100，定期重启

### [Trade-off] 实现复杂度 vs 功能完整性
- **权衡**: 增加了系统复杂度，但显著提升用户体验
- **决策**: 值得，因为评测是核心功能

## 详细设计

### 1. 现有架构分析

#### 1.1 数据模型

**Submission 模型** (backend/courses/models.py:582-629)
```python
class Submission(models.Model):
    STATUS_CHOICES = (
        ("pending", "待评测"),
        ("judging", "评测中"),
        ("accepted", "通过"),
        ("wrong_answer", "答案错误"),
        ("time_limit_exceeded", "超时"),
        ("memory_limit_exceeded", "内存超限"),
        ("runtime_error", "运行时错误"),
        ("compilation_error", "编译错误"),
        ("internal_error", "系统错误"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=50, default="python")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    execution_time = models.FloatField(null=True, blank=True)  # 毫秒
    memory_used = models.FloatField(null=True, blank=True)  # KB
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**AlgorithmProblem 模型** (backend/courses/models.py:384-409)
```python
class AlgorithmProblem(models.Model):
    problem = models.OneToOneField(Problem, ...)
    time_limit = models.PositiveSmallIntegerField(default=1000)  # 毫秒
    memory_limit = models.PositiveSmallIntegerField(default=256)  # MB
    code_template = models.JSONField(blank=True, null=True)  # {"python": "..."}
    solution_name = models.JSONField(blank=True, null=True)  # {"python": "solve"}
```

**TestCase 模型** (backend/courses/models.py:562-579)
```python
class TestCase(models.Model):
    problem = models.ForeignKey(AlgorithmProblem, related_name="test_cases")
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
```

#### 1.2 服务层

**CodeExecutorService** (backend/courses/services.py:109-263)
- 同步执行所有测试用例
- 使用 Judge0Backend 实际执行
- 串行处理，阻塞式等待

#### 1.3 视图层

**SubmissionViewSet.create()** (backend/courses/views.py:1593-1683)
- 同步模式：立即执行代码
- 自由模式：无 problem_id 时立即执行
- 更新问题进度和保存草稿

#### 1.4 现有 Judge0 集成

**Judge0Backend** (backend/courses/judge_backend/Judge0Backend.py)
- 9 种语言支持（Python, C, C++, Java, JavaScript, Go, Rust, Kotlin, Swift）
- submit_code(): 提交代码到 Judge0
- get_result(): 轮询结果（最多 30 秒）

#### 1.5 Celery 配置

**现有配置** (backend/core/settings.py:378-404)
```python
CELERY_BROKER_URL = "redis://localhost:6379/3"
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_EXTENDED = True
```

**现有任务示例** (backend/courses/tasks.py)
- refresh_unlock_snapshot: 刷新解锁快照
- batch_refresh_stale_snapshots: 批量刷新过期快照

### 2. 数据层实现

#### 2.1 JudgingQueueStats 模型

```python
class JudgingQueueStats(models.Model):
    """
    评测队列统计模型
    跟踪每个异步评测任务的状态和性能指标
    """

    STATUS_CHOICES = (
        ("pending", "等待中"),
        ("started", "已开始"),
        ("success", "成功"),
        ("failed", "失败"),
        ("timeout", "超时"),
        ("cancelled", "已取消"),
    )

    # 关联字段
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name="queue_stats",
        verbose_name="关联的提交记录",
    )

    # Celery 任务信息
    task_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Celery 任务 ID",
        help_text="用于追踪任务状态和取消任务"
    )

    # 队列状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="队列状态"
    )

    # 时间戳
    queued_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="入队时间",
        db_index=True,
        help_text="任务创建并加入队列的时间"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="开始执行时间",
        help_text="Worker 开始处理任务的时间"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="完成时间",
        help_text="任务完成（成功或失败）的时间"
    )

    # 性能指标
    queue_wait_seconds = models.FloatField(
        null=True,
        blank=True,
        verbose_name="队列等待时间（秒）",
        help_text="从入队到开始执行的时间差"
    )

    execution_seconds = models.FloatField(
        null=True,
        blank=True,
        verbose_name="实际执行时间（秒）",
        help_text="从开始执行到完成的时间差"
    )

    total_seconds = models.FloatField(
        null=True,
        blank=True,
        verbose_name="总耗时（秒）",
        help_text="从入队到完成的总时间"
    )

    # 错误信息
    error_message = models.TextField(
        blank=True,
        verbose_name="错误信息",
        help_text="任务失败或超时的详细错误信息"
    )

    # 重试信息
    retry_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="重试次数",
        help_text="任务被重试的次数"
    )

    class Meta:
        verbose_name = "评测队列统计"
        verbose_name_plural = "评测队列统计"
        indexes = [
            models.Index(fields=['status', 'queued_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['submission']),
        ]

    def calculate_performance_metrics(self):
        """计算性能指标"""
        if self.started_at and self.queued_at:
            self.queue_wait_seconds = (self.started_at - self.queued_at).total_seconds()

        if self.completed_at and self.started_at:
            self.execution_seconds = (self.completed_at - self.started_at).total_seconds()

        if self.completed_at and self.queued_at:
            self.total_seconds = (self.completed_at - self.queued_at).total_seconds()

        self.save(update_fields=[
            'queue_wait_seconds',
            'execution_seconds',
            'total_seconds'
        ])
```

#### 2.2 Submission 模型扩展

```python
class Submission(models.Model):
    # ... 现有字段 ...

    # 新增字段
    task_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Celery 任务 ID",
        help_text="异步评测任务的 Celery 任务 ID，用于追踪和取消"
    )

    estimated_wait_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="预估等待时间（秒）",
        help_text="基于当前队列负载预估的等待时间"
    )

    class Meta:
        verbose_name = "提交记录"
        verbose_name_plural = "提交记录"
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['task_id']),
        ]
```

#### 2.3 数据库迁移

```python
# backend/courses/migrations/000X_add_judging_queue_stats.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    operations = [
        # 1. 添加 Submission 新字段
        migrations.AddField(
            model_name='submission',
            name='task_id',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                unique=True,
                verbose_name='Celery 任务 ID'
            ),
        ),
        migrations.AddField(
            model_name='submission',
            name='estimated_wait_seconds',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='预估等待时间（秒）',
                null=True,
                verbose_name='预估等待时间（秒）'
            ),
        ),

        # 2. 创建 JudgingQueueStats 模型
        migrations.CreateModel(
            name='JudgingQueueStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, ...)),
                ('task_id', models.CharField(max_length=255, unique=True, ...)),
                ('status', models.CharField(...)),
                ('queued_at', models.DateTimeField(auto_now_add=True, db_index=True, ...)),
                ('started_at', models.DateTimeField(null=True, ...)),
                ('completed_at', models.DateTimeField(null=True, ...)),
                ('queue_wait_seconds', models.FloatField(null=True, ...)),
                ('execution_seconds', models.FloatField(null=True, ...)),
                ('total_seconds', models.FloatField(null=True, ...)),
                ('error_message', models.TextField(blank=True, ...)),
                ('retry_count', models.PositiveSmallIntegerField(default=0, ...)),
                ('submission', models.OneToOneField(...)),
            ],
            options={
                'verbose_name': '评测队列统计',
                'verbose_name_plural': '评测队列统计',
                'indexes': [...],
            },
        ),
    ]
```

### 3. 核心服务实现

#### 3.1 JudgingCapacityService

```python
class JudgingCapacityService:
    """
    评测容量管理服务
    """
    TOTAL_CAPACITY = 18  # 3 workers × 6 concurrent
    WARNING_THRESHOLD = 10
    FULL_THRESHOLD = 18
    CACHE_KEY = "judging:capacity:status"
    CACHE_TIMEOUT = 30  # 30 seconds

    @classmethod
    def get_current_capacity(cls) -> Dict[str, any]:
        """
        获取当前容量信息
        返回: {
            "pending_count": 5,
            "running_count": 3,
            "total_capacity": 18,
            "available_slots": 10,
            "status": "available",
            "estimated_wait_seconds": 30
        }
        """
        cached_data = cache.get(cls.CACHE_KEY)
        if cached_data:
            return cached_data

        capacity_data = cls._calculate_capacity()
        cache.set(cls.CACHE_KEY, capacity_data, cls.CACHE_TIMEOUT)
        return capacity_data

    @classmethod
    def _calculate_capacity(cls) -> Dict[str, any]:
        """从数据库计算当前容量"""
        from .models import JudgingQueueStats

        now = timezone.now()
        pending_count = JudgingQueueStats.objects.filter(status="pending").count()
        running_count = JudgingQueueStats.objects.filter(status="started").count()

        used_slots = pending_count + running_count
        available_slots = max(0, cls.TOTAL_CAPACITY - used_slots)

        if used_slots >= cls.FULL_THRESHOLD:
            status = "full"
        elif used_slots >= cls.WARNING_THRESHOLD:
            status = "busy"
        else:
            status = "available"

        estimated_wait_seconds = cls._estimate_wait_time(pending_count, running_count)

        return {
            "pending_count": pending_count,
            "running_count": running_count,
            "total_capacity": cls.TOTAL_CAPACITY,
            "available_slots": available_slots,
            "status": status,
            "estimated_wait_seconds": estimated_wait_seconds,
            "calculated_at": now.isoformat(),
        }

    @classmethod
    def check_capacity(cls) -> tuple[bool, str | None, int | None]:
        """检查是否接受新提交"""
        capacity = cls.get_current_capacity()
        if capacity["status"] == "full":
            return False, "系统繁忙，请稍后再试", None
        return True, None, capacity["estimated_wait_seconds"]
```

#### 3.2 CodeExecutorService 扩展

```python
class CodeExecutorService:
    def run_all_test_cases(
        self,
        user,
        problem,
        code: str,
        language: str = "python",
        async_mode: bool = False
    ) -> Submission:
        """
        支持同步和异步的代码执行
        """
        # 创建 Submission
        submission = Submission.objects.create(...)

        if async_mode:
            return self._execute_async(submission)
        else:
            return self._execute_sync(submission)  # 保持原逻辑

    def _execute_async(self, submission: Submission) -> Submission:
        """异步执行：启动 Celery 任务"""
        from .tasks import judge_submission_async

        # 容量检查
        is_allowed, error_msg, estimated_wait = JudgingCapacityService.check_capacity()
        if not is_allowed:
            submission.status = "internal_error"
            submission.error = error_msg
            submission.save()
            raise CapacityFullError(error_msg)

        # 启动异步任务
        task = judge_submission_async.delay(submission.id)

        # 更新 submission
        submission.task_id = task.id
        submission.estimated_wait_seconds = estimated_wait
        submission.save()

        return submission

class CapacityFullError(Exception):
    """容量已满异常"""
    pass
```

### 4. 异步任务实现

#### 4.1 judge_submission_async 任务

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=270,  # 4.5 minutes
    time_limit=300,       # 5 minutes
    autoretry_for=(ConnectionError, TimeoutError),
)
def judge_submission_async(self, submission_id: int):
    """
    异步执行代码评测
    """
    from .models import Submission, JudgingQueueStats
    from .services import CodeExecutorService

    try:
        submission = Submission.objects.select_related('user', 'problem').get(id=submission_id)
        queue_stats = submission.queue_stats
    except Submission.DoesNotExist:
        return

    try:
        # 1. 更新状态为 started
        submission.status = "judging"
        submission.save(update_fields=['status'])
        queue_stats.status = "started"
        queue_stats.started_at = timezone.now()
        queue_stats.save()

        # 2. 执行评测（使用现有同步逻辑）
        executor = CodeExecutorService()
        result_submission = executor._execute_sync(submission)

        # 3. 更新状态为 success
        queue_stats.status = "success"
        queue_stats.completed_at = timezone.now()
        queue_stats.calculate_performance_metrics()
        queue_stats.save()

        # 清除容量缓存
        JudgingCapacityService.clear_cache()

    except SoftTimeLimitExceeded:
        # 软超时处理
        submission.status = "time_limit_exceeded"
        submission.error = "任务执行超时（4.5分钟）"
        submission.save()

        queue_stats.status = "timeout"
        queue_stats.completed_at = timezone.now()
        queue_stats.error_message = "SoftTimeLimitExceeded after 270s"
        queue_stats.calculate_performance_metrics()
        queue_stats.save()

        JudgingCapacityService.clear_cache()

    except Exception as exc:
        # 错误处理
        submission.status = "internal_error"
        submission.error = f"任务执行失败: {str(exc)}"
        submission.save()

        queue_stats.status = "failed"
        queue_stats.completed_at = timezone.now()
        queue_stats.error_message = str(exc)
        queue_stats.retry_count = self.request.retries
        queue_stats.calculate_performance_metrics()
        queue_stats.save()

        JudgingCapacityService.clear_cache()

        # 重试判断
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

    return {
        "submission_id": submission_id,
        "status": submission.status,
        "task_id": self.request.id,
    }
```

#### 4.2 Celery 任务路由配置

```python
# backend/core/settings.py
CELERY_TASK_ROUTES = {
    'courses.tasks.judge_submission_async': {
        'queue': 'code_judging',
        'routing_key': 'code_judging',
    },
}

# 添加清理任务
@shared_task
def cleanup_old_queue_stats(days=7):
    """清理过期的队列统计记录"""
    from .models import JudgingQueueStats
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    deleted_count = JudgingQueueStats.objects.filter(
        completed_at__lt=cutoff_date
    ).delete()
    return deleted_count
```

### 5. 视图层修改

#### 5.1 SubmissionViewSet.create()

```python
class SubmissionViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        支持同步/异步两种模式
        """
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language", "python")
        async_mode = request.data.get("async", True)  # 默认异步

        # 自由运行（不使用异步）
        if not problem_id:
            executor = CodeExecutorService()
            result = executor.run_freely(code=code, language=language)
            return Response(result, status=status.HTTP_200_OK)

        # 算法题提交
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.type != "algorithm":
            return Response({"error": "Only algorithm problems allow code submission"}, status=400)

        try:
            executor = CodeExecutorService()

            if async_mode:
                # 异步模式
                submission = executor.run_all_test_cases(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    async_mode=True
                )

                CodeDraft.objects.create(...)

                return Response({
                    "message": "代码已提交，正在评测中",
                    "task_id": submission.task_id,
                    "submission": serializer.data,
                }, status=status.HTTP_202_ACCEPTED)

            else:
                # 同步模式（向后兼容）
                submission = executor.run_all_test_cases(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    async_mode=False
                )

                # ... 更新进度逻辑 ...

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except CapacityFullError as e:
            return Response({
                "error": str(e),
                "status": "capacity_full"
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        except Exception as e:
            return Response({"error": f"Error executing code: {str(e)}"}, status=500)
```

#### 5.2 新增 API 接口

```python
class SubmissionViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):

    @action(detail=False, methods=["get"])
    def queue_status(self, request):
        """获取队列状态"""
        capacity = JudgingCapacityService.get_current_capacity()
        return Response({
            "pending_count": capacity["pending_count"],
            "running_count": capacity["running_count"],
            "total_capacity": capacity["total_capacity"],
            "available_slots": capacity["available_slots"],
            "status": capacity["status"],
            "estimated_wait_seconds": capacity["estimated_wait_seconds"],
        })

    @action(detail=True, methods=["get"])
    def task_status(self, request, pk=None):
        """获取特定提交的任务状态"""
        submission = self.get_object()
        if not submission.task_id:
            return Response({"error": "This submission is not an async task"}, status=400)

        queue_stats = submission.queue_stats
        return Response({
            "submission_id": submission.id,
            "task_id": submission.task_id,
            "submission_status": submission.status,
            "queue_status": queue_stats.status,
            "queued_at": queue_stats.queued_at.isoformat(),
            "started_at": queue_stats.started_at.isoformat() if queue_stats.started_at else None,
            "completed_at": queue_stats.completed_at.isoformat() if queue_stats.completed_at else None,
            "queue_wait_seconds": queue_stats.queue_wait_seconds,
            "execution_seconds": queue_stats.execution_seconds,
            "total_seconds": queue_stats.total_seconds,
            "error_message": queue_stats.error_message if queue_stats.error_message else None,
        })
```

### 6. 前端实现方案

#### 6.1 类型定义

```typescript
// frontend/web-student/app/types/submission.ts
export interface AsyncSubmissionReq extends SubmissionReq {
  async?: boolean;  // 默认 true
}

export interface AsyncSubmissionRes {
  message: string;
  task_id: string;
  submission: SubmissionRes;
}

export interface QueueStatusRes {
  pending_count: number;
  running_count: number;
  total_capacity: number;
  available_slots: number;
  status: 'available' | 'busy' | 'full';
  estimated_wait_seconds: number;
}

export interface TaskStatusRes {
  submission_id: number;
  task_id: string;
  submission_status: SubmissionStatus;
  queue_status: 'pending' | 'started' | 'success' | 'failed' | 'timeout' | 'cancelled';
  queued_at: string;
  started_at: string | null;
  completed_at: string | null;
  queue_wait_seconds: number | null;
  execution_seconds: number | null;
  total_seconds: number | null;
  error_message: string | null;
}
```

#### 6.2 API 客户端

```typescript
// frontend/web-student/app/lib/clientHttp.ts
export async function getQueueStatus(): Promise<QueueStatusRes> {
  const response = await clientHttp.get<QueueStatusRes>('/submissions/queue-status/');
  return response;
}

export async function getTaskStatus(submissionId: number): Promise<TaskStatusRes> {
  const response = await clientHttp.get<TaskStatusRes>(`/submissions/${submissionId}/task_status/`);
  return response;
}

export async function submitCodeAsync(data: AsyncSubmissionReq): Promise<AsyncSubmissionRes> {
  const response = await clientHttp.post<AsyncSubmissionRes>('/submissions/', {
    ...data,
    async: true,
  });
  return response;
}
```

#### 6.3 轮询 Hook

```typescript
// frontend/web-student/app/hooks/useSubmissionPolling.ts
export function useSubmissionPolling({
  submissionId,
  initialDelay = 2000,  // 2秒
  interval = 2000,      // 2秒
  maxAttempts = 60,     // 2分钟
  onComplete,
  onError,
}: UseSubmissionPollingOptions) {
  const [status, setStatus] = useState<TaskStatusRes | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const poll = async () => {
      try {
        const response = await getTaskStatus(submissionId);
        setStatus(response);
        setError(null);
        setAttempt(prev => prev + 1);

        // 检查是否完成
        if (response.queue_status === 'success' || response.queue_status === 'failed' || response.queue_status === 'timeout') {
          setIsLoading(false);
          onComplete?.(response);
          return;
        }

        if (attempt >= maxAttempts) {
          setIsLoading(false);
          setError(new Error('轮询超时，请刷新页面重试'));
          return;
        }

        timeoutId = setTimeout(poll, interval);

      } catch (err) {
        const error = err as Error;
        setError(error);
        setIsLoading(false);
        onError?.(error);
      }
    };

    timeoutId = setTimeout(poll, initialDelay);

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [submissionId, initialDelay, interval, maxAttempts, attempt, onComplete, onError]);

  return { status, isLoading, error, attempt };
}
```

### 7. 部署和监控

#### 7.1 Worker 配置

```yaml
# backend/docker-compose.yml
services:
  celery-code-judging-worker:
    build: .
    command: celery -A core worker -l info -Q code_judging -c 6 --max-tasks-per-child=10
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/3
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    volumes:
      - ./:/app
    depends_on:
      - redis
    restart: unless-stopped
```

#### 7.2 环境变量

```bash
# backend/.env.example
# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/3
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Judge0 配置
JUDGE0_BASE_URL=http://192.168.122.137:2358

# 代码评测配置
CODE_JUDGING_MAX_WORKERS=3
CODE_JUDGING_CONCURRENCY_PER_WORKER=6
CODE_JUDGING_SOFT_TIME_LIMIT=270
CODE_JUDGING_HARD_TIME_LIMIT=300
```

#### 7.3 管理命令

```python
# backend/courses/management/commands/monitor_judging_queue.py
class Command(BaseCommand):
    help = 'Monitor and display judging queue status'

    def handle(self, *args, **options):
        capacity = JudgingCapacityService.get_current_capacity()

        self.stdout.write(self.style.SUCCESS('=== Judging Queue Status ==='))
        self.stdout.write(f"Pending: {capacity['pending_count']}")
        self.stdout.write(f"Running: {capacity['running_count']}")
        self.stdout.write(f"Available: {capacity['available_slots']}/{capacity['total_capacity']}")
        self.stdout.write(f"Status: {capacity['status']}")
        self.stdout.write(f"Est. Wait: {capacity['estimated_wait_seconds']}s")
```

### 8. 测试策略

#### 8.1 单元测试

```python
# backend/courses/tests/test_services.py
class JudgingCapacityServiceTest(TestCase):
    def test_get_current_capacity(self):
        capacity = JudgingCapacityService.get_current_capacity()
        self.assertIn('pending_count', capacity)
        self.assertEqual(capacity['total_capacity'], 18)

    def test_check_capacity(self):
        is_allowed, error_msg, estimated_wait = JudgingCapacityService.check_capacity()
        self.assertTrue(is_allowed)
        self.assertIsNone(error_msg)

class CodeExecutorServiceAsyncTest(TestCase):
    def test_async_submission(self):
        # 测试异步提交
        pass
```

#### 8.2 集成测试

```python
# backend/courses/tests/test_views.py
class SubmissionAsyncTestCase(TestCase):
    def test_async_submission_accepted(self):
        response = self.client.post('/api/submissions/', {
            'code': 'print("hello")',
            'language': 'python',
            'problem_id': self.problem.id,
            'async': True,
        })
        self.assertEqual(response.status_code, 202)
        self.assertIn('task_id', response.data)

    def test_queue_status_endpoint(self):
        response = self.client.get('/api/submissions/queue-status/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pending_count', response.data)
```


## Open Questions

1. **Worker 数量配置**：初始设置 3 个 Worker 是否合适？是否需要根据负载动态调整？
2. **缓存策略**：30 秒缓存时间是否合理？是否需要根据系统负载动态调整？
3. **告警阈值**：队列长度达到多少时触发告警？需要定义具体的 SLA 指标
4. **前端超时处理**：网络异常时如何处理轮询中断？需要重试机制吗？
