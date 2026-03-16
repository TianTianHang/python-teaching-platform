# 异步代码评测系统 - 详细技术设计

## 1. 当前架构分析

### 1.1 现有数据模型

#### Submission 模型 (backend/courses/models.py:582-629)
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

**需要添加的字段**：
- `task_id = models.CharField(max_length=255, unique=True, null=True, db_index=True)` - Celery 任务 ID
- `estimated_wait_seconds = models.PositiveIntegerField(null=True, blank=True)` - 预估等待时间

#### AlgorithmProblem 模型 (backend/courses/models.py:384-409)
```python
class AlgorithmProblem(models.Model):
    problem = models.OneToOneField(Problem, ...)
    time_limit = models.PositiveSmallIntegerField(default=1000)  # 毫秒
    memory_limit = models.PositiveSmallIntegerField(default=256)  # MB
    code_template = models.JSONField(blank=True, null=True)  # {"python": "..."}
    solution_name = models.JSONField(blank=True, null=True)  # {"python": "solve"}
```

#### TestCase 模型 (backend/courses/models.py:562-579)
```python
class TestCase(models.Model):
    problem = models.ForeignKey(AlgorithmProblem, related_name="test_cases")
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
```

### 1.2 现有服务层

#### CodeExecutorService (backend/courses/services.py:109-263)

**当前执行流程**：
```python
def run_all_test_cases(self, user, problem, code: str, language: str = "python") -> Submission:
    # 1. 创建 Submission 记录，status="pending"
    submission = Submission.objects.create(...)

    # 2. 获取所有测试用例
    test_cases = algorithm_problem.test_cases.all()

    # 3. 遍历测试用例
    for test_case in test_cases:
        # 3.1 生成完整可执行代码
        exec_code = generate_judge0_code(...)

        # 3.2 提交到 Judge0 API
        submit_resp = self.backend.submit_code(...)

        # 3.3 标记为 judging
        submission.status = "judging"
        submission.save()

        # 3.4 等待结果（轮询，最多 30 秒）
        result = self.backend.get_result(submit_resp["token"], timeout_sec=30)

        # 3.5 收集结果
        ...

    # 4. 更新最终状态
    submission.status = final_status
    submission.save()

    return submission
```

**问题**：
- 同步阻塞，每个测试用例最多等待 30 秒
- 多个测试用例串行执行
- 用户体验差，前端长时间等待

### 1.3 现有视图层

#### SubmissionViewSet.create() (backend/courses/views.py:1593-1683)

**当前流程**：
```python
def create(self, request, *args, **kwargs):
    problem_id = request.data.get("problem_id")
    code = request.data.get("code")
    language = request.data.get("language", "python")

    # 情况 1：自由运行（无 problem_id）
    if not problem_id:
        executor = CodeExecutorService()
        result = executor.run_freely(code=code, language=language)
        return Response(result, status=status.HTTP_200_OK)

    # 情况 2：算法题提交
    problem = get_object_or_404(Problem, id=problem_id)
    executor = CodeExecutorService()
    submission = executor.run_all_test_cases(...)  # 同步阻塞

    # 保存代码草稿
    CodeDraft.objects.create(...)

    # 更新问题进度
    if submission.status == "accepted":
        problem_progress, created = ProblemProgress.objects.get_or_create(...)
        problem_progress.status = "solved"
        problem_progress.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### 1.4 现有 Judge0 集成

#### Judge0Backend (backend/courses/judge_backend/Judge0Backend.py)

**关键方法**：
```python
class Judge0Backend(CodeJudgingBackend):
    LANGUAGE_IDS = {
        'python': 71,
        'c': 50,
        'cpp': 54,
        'java': 62,
        'javascript': 63,
        'go': 60,
        'rust': 78,
        'kotlin': 79,
        'swift': 82,
    }

    def submit_code(self, source_code, language_id, stdin="", expected_output=None,
                    time_limit_ms=2000, memory_limit_mb=128) -> Dict:
        # 转换单位：ms -> sec, MB -> KB
        cpu_time_limit_sec = time_limit_ms / 1000.0
        memory_limit_kb = memory_limit_mb * 1024

        # POST /submissions
        response = requests.post(f"{self.base_url}/submissions", ...)
        return response.json()  # {"token": "..."}

    def get_result(self, token: str, timeout_sec: int = 30) -> Dict:
        # 轮询直到完成或超时
        start = time.time()
        while time.time() - start < timeout_sec:
            response = requests.get(f"{self.base_url}/submissions/{token}", ...)
            data = response.json()
            status_id = data.get("status", {}).get("id", 0)

            if status_id >= 3:  # 最终状态
                # 转换单位：sec -> ms, KB -> MB
                time_ms = float(data.get("time")) * 1000.0
                memory_mb = float(data.get("memory")) / 1024.0
                return {
                    "status_id": status_id,
                    "stdout": data.get("stdout", ""),
                    "stderr": data.get("stderr", ""),
                    "time": time_ms,
                    "memory": memory_mb,
                }
            time.sleep(0.5)
```

### 1.5 现有 Celery 配置

#### settings.py (backend/core/settings.py:378-404)
```python
# Celery 配置
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/3")
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ENABLE_UTC = True
CELERY_RESULT_EXTENDED = True
CELERY_TASK_TRACK_STARTED = True

# Celery Beat 定时任务
CELERY_BEAT_SCHEDULE = {
    "cache-performance-summary": {
        "task": "common.cache_warming.tasks.cache_performance_summary",
        "schedule": 60.0,
    },
    "refresh-stale-snapshots": {
        "task": "courses.tasks.batch_refresh_stale_snapshots",
        "schedule": crontab(minute="*"),  # 每分钟
    },
}
```

#### 现有任务示例 (backend/courses/tasks.py:6-66)
```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def refresh_unlock_snapshot(self, enrollment_id: int):
    """刷新单个 enrollment 的解锁状态快照"""
    enrollment = Enrollment.objects.select_related('user', 'course').get(id=enrollment_id)
    snapshot, created = CourseUnlockSnapshot.objects.get_or_create(
        enrollment=enrollment,
        defaults={'course': enrollment.course}
    )
    snapshot.recompute()
```

---

## 2. 详细实现方案

### 2.1 数据层实现

#### 2.1.1 创建 JudgingQueueStats 模型

**文件**: `backend/courses/models.py`

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

    def __str__(self):
        return f"Submission {self.submission_id} - {self.status}"

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

#### 2.1.2 修改 Submission 模型

**文件**: `backend/courses/models.py`

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
            # ... 现有索引 ...
            models.Index(fields=['task_id']),
            models.Index(fields=['status', 'created_at']),
        ]
```

#### 2.1.3 创建数据库迁移

**文件**: `backend/courses/migrations/000X_add_judging_queue_stats.py`

```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '000Y_previous_migration'),
    ]

    operations = [
        # 1. 添加 Submission 新字段
        migrations.AddField(
            model_name='submission',
            name='task_id',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Celery 任务 ID',
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
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(
                    db_index=True,
                    help_text='Celery 任务 ID',
                    max_length=255,
                    unique=True,
                    verbose_name='Celery 任务 ID'
                )),
                ('status', models.CharField(
                    choices=[('pending', '等待中'), ('started', '已开始'), ('success', '成功'),
                             ('failed', '失败'), ('timeout', '超时'), ('cancelled', '已取消')],
                    db_index=True,
                    default='pending',
                    max_length=20,
                    verbose_name='队列状态'
                )),
                ('queued_at', models.DateTimeField(
                    auto_now_add=True,
                    db_index=True,
                    help_text='入队时间',
                    verbose_name='入队时间'
                )),
                ('started_at', models.DateTimeField(
                    blank=True,
                    help_text='开始执行时间',
                    null=True,
                    verbose_name='开始执行时间'
                )),
                ('completed_at', models.DateTimeField(
                    blank=True,
                    help_text='完成时间',
                    null=True,
                    verbose_name='完成时间'
                )),
                ('queue_wait_seconds', models.FloatField(
                    blank=True,
                    help_text='队列等待时间（秒）',
                    null=True,
                    verbose_name='队列等待时间（秒）'
                )),
                ('execution_seconds', models.FloatField(
                    blank=True,
                    help_text='实际执行时间（秒）',
                    null=True,
                    verbose_name='实际执行时间（秒）'
                )),
                ('total_seconds', models.FloatField(
                    blank=True,
                    help_text='总耗时（秒）',
                    null=True,
                    verbose_name='总耗时（秒）'
                )),
                ('error_message', models.TextField(
                    blank=True,
                    help_text='错误信息',
                    verbose_name='错误信息'
                )),
                ('retry_count', models.PositiveSmallIntegerField(
                    default=0,
                    help_text='重试次数',
                    verbose_name='重试次数'
                )),
                ('submission', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='queue_stats',
                    to='courses.submission',
                    verbose_name='关联的提交记录'
                )),
            ],
            options={
                'verbose_name': '评测队列统计',
                'verbose_name_plural': '评测队列统计',
                'indexes': [
                    models.Index(fields=['status', 'queued_at'], name='courses_judg_status_que_idx'),
                    models.Index(fields=['task_id'], name='courses_judg_task_id_idx'),
                    models.Index(fields=['submission'], name='courses_judg_submiss_idx'),
                ],
            },
        ),
    ]
```

---

### 2.2 核心服务实现

#### 2.2.1 JudgingCapacityService

**文件**: `backend/courses/services.py`

```python
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from typing import Dict, Literal
import logging

logger = logging.getLogger(__name__)


class JudgingCapacityService:
    """
    评测容量管理服务

    职责：
    1. 计算当前队列容量和负载
    2. 提供容量检查和预估等待时间
    3. 缓存容量信息以提高性能
    """

    # 配置常量
    TOTAL_CAPACITY = 18  # 总容量（3 workers × 6 concurrent tasks）
    WARNING_THRESHOLD = 10  # 警告阈值
    FULL_THRESHOLD = 18  # 满载阈值

    # 缓存配置
    CACHE_KEY = "judging:capacity:status"
    CACHE_TIMEOUT = 30  # 30 秒缓存

    @classmethod
    def get_current_capacity(cls) -> Dict[str, any]:
        """
        获取当前队列容量信息

        返回:
        {
            "pending_count": 5,           # 等待中的任务数
            "running_count": 3,           # 执行中的任务数
            "total_capacity": 18,         # 总容量
            "available_slots": 10,        # 剩余槽位数
            "status": "available",        # available/busy/full
            "estimated_wait_seconds": 30  # 预估等待时间（秒）
        }
        """
        # 1. 尝试从缓存获取
        cached_data = cache.get(cls.CACHE_KEY)
        if cached_data:
            logger.debug("Using cached capacity data")
            return cached_data

        # 2. 从数据库计算
        capacity_data = cls._calculate_capacity()

        # 3. 缓存结果
        cache.set(cls.CACHE_KEY, capacity_data, cls.CACHE_TIMEOUT)

        return capacity_data

    @classmethod
    def _calculate_capacity(cls) -> Dict[str, any]:
        """从数据库计算当前容量"""
        from .models import JudgingQueueStats

        now = timezone.now()

        # 统计各状态的任务数
        pending_count = JudgingQueueStats.objects.filter(
            status="pending"
        ).count()

        running_count = JudgingQueueStats.objects.filter(
            status="started"
        ).count()

        # 计算剩余容量
        used_slots = pending_count + running_count
        available_slots = max(0, cls.TOTAL_CAPACITY - used_slots)

        # 判断系统状态
        if used_slots >= cls.FULL_THRESHOLD:
            status = "full"
        elif used_slots >= cls.WARNING_THRESHOLD:
            status = "busy"
        else:
            status = "available"

        # 计算预估等待时间
        estimated_wait_seconds = cls._estimate_wait_time(
            pending_count,
            running_count
        )

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
    def _estimate_wait_time(cls, pending_count: int, running_count: int) -> int:
        """
        估算等待时间

        策略：
        1. 每个正在运行的任务预估剩余 60 秒
        2. 每个等待中的任务预估 90 秒（包含执行时间）
        3. 取平均值并向上取整
        """
        avg_running_time = 60  # 假设平均每个任务运行 60 秒
        avg_task_time = 90     # 假设平均每个任务（包含等待）90 秒

        # 预估正在运行任务的剩余时间
        estimated_running_remaining = running_count * (avg_running_time / 2)

        # 预估等待任务的总时间
        estimated_pending_time = pending_count * avg_task_time

        # 总等待时间
        total_wait = estimated_running_remaining + estimated_pending_time

        return int(total_wait)

    @classmethod
    def check_capacity(cls) -> tuple[bool, str | None, int | None]:
        """
        检查是否接受新提交

        返回: (is_allowed, error_message, estimated_wait)
        """
        capacity = cls.get_current_capacity()

        if capacity["status"] == "full":
            return False, "系统繁忙，请稍后再试", None

        return True, None, capacity["estimated_wait_seconds"]

    @classmethod
    def clear_cache(cls):
        """清除容量缓存"""
        cache.delete(cls.CACHE_KEY)
        logger.info("Cleared judging capacity cache")
```

#### 2.2.2 修改 CodeExecutorService 支持异步

**文件**: `backend/courses/services.py`

```python
class CodeExecutorService:
    """代码执行服务 - 支持同步和异步模式"""

    def __init__(self, backend=None):
        self.backend = backend or Judge0Backend()

    def run_all_test_cases(
        self,
        user,
        problem,
        code: str,
        language: str = "python",
        async_mode: bool = False
    ) -> Submission:
        """
        运行所有测试用例

        Args:
            user: 提交用户
            problem: 问题对象
            code: 提交的代码
            language: 编程语言
            async_mode: 是否异步模式（默认 False）

        Returns:
            Submission 对象
            - 同步模式：返回包含完整结果的 Submission
            - 异步模式：返回 pending 状态的 Submission（需要轮询获取结果）
        """
        logger.info(
            "Code execution started",
            extra={
                "user_id": user.id,
                "problem_id": problem.id,
                "language": language,
                "code_length": len(code),
                "async_mode": async_mode,
            },
        )

        # 创建 Submission 记录
        submission = Submission.objects.create(
            user=user,
            problem=problem,
            code=code,
            language=language,
            status="pending"
        )

        if async_mode:
            # 异步模式：启动 Celery 任务
            return self._execute_async(submission)
        else:
            # 同步模式：立即执行（保持向后兼容）
            return self._execute_sync(submission)

    def _execute_sync(self, submission: Submission) -> Submission:
        """同步执行所有测试用例（原有逻辑）"""
        from .judging_utils.code_generator import generate_judge0_code

        user = submission.user
        problem = submission.problem
        code = submission.code
        language = submission.language

        try:
            algorithm_problem = problem.algorithm_info
            test_cases = algorithm_problem.test_cases.all()

            if not test_cases.exists():
                self._update_submission_with_result(
                    submission=submission,
                    final_status="compilation_error",
                    output="",
                    error="No test cases available for this problem",
                    execution_time_ms=None,
                    memory_used_mb=None,
                )
                return submission

            language_id = self.backend.get_language_id(language)
            solve_func = algorithm_problem.solution_name.get(language, "solve")

            all_passed = True
            max_time_ms = 0.0
            max_memory_mb = 0.0
            final_output = ""
            final_error = ""

            for test_case in test_cases:
                exec_code = generate_judge0_code(
                    user_code=code.strip(),
                    solve_func=solve_func,
                    language=language
                )

                submit_resp = self.backend.submit_code(
                    source_code=exec_code,
                    language_id=language_id,
                    stdin=test_case.input_data,
                    expected_output=test_case.expected_output,
                    time_limit_ms=algorithm_problem.time_limit,
                    memory_limit_mb=algorithm_problem.memory_limit,
                )

                submission.status = "judging"
                submission.save()

                result = self.backend.get_result(
                    submit_resp["token"],
                    timeout_sec=30
                )

                # ... 收集结果 ...

            final_status = "accepted" if all_passed else final_status

            self._update_submission_with_result(
                submission=submission,
                final_status=final_status,
                output=final_output.rstrip(),
                error=final_error.rstrip(),
                execution_time_ms=max_time_ms if max_time_ms > 0 else None,
                memory_used_mb=max_memory_mb if max_memory_mb > 0 else None,
            )

        except Exception as e:
            logger.error(
                f"Code execution failed",
                extra={"user_id": user.id, "problem_id": problem.id, "error": str(e)},
                exc_info=True,
            )

            self._update_submission_with_result(
                submission=submission,
                final_status="internal_error",
                output="",
                error=str(e),
                execution_time_ms=None,
                memory_used_mb=None,
            )

        return submission

    def _execute_async(self, submission: Submission) -> Submission:
        """异步执行：启动 Celery 任务"""
        from .tasks import judge_submission_async

        # 容量检查
        is_allowed, error_msg, estimated_wait = JudgingCapacityService.check_capacity()

        if not is_allowed:
            # 容量已满，更新 submission 并抛出异常
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

        logger.info(
            f"Async judging task created",
            extra={
                "submission_id": submission.id,
                "task_id": task.id,
                "estimated_wait_seconds": estimated_wait,
            },
        )

        return submission


class CapacityFullError(Exception):
    """容量已满异常"""
    pass
```

---

### 2.3 异步任务实现

#### 2.3.1 创建 judge_submission_async 任务

**文件**: `backend/courses/tasks.py`

```python
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=270,  # 4.5 分钟软超时
    time_limit=300,       # 5 分钟硬超时
    autoretry_for=(ConnectionError, TimeoutError),
)
def judge_submission_async(self, submission_id: int):
    """
    异步执行代码评测任务

    Args:
        submission_id: Submission 记录的 ID

    超时策略：
    - 软超时 (270s/4.5min): 抛出 SoftTimeLimitExceeded，优雅处理
    - 硬超时 (300s/5min): Worker 强制终止任务

    重试策略：
    - 最多重试 3 次
    - 重试间隔 60 秒
    - 自动重试 ConnectionError 和 TimeoutError
    """
    from .models import Submission, JudgingQueueStats
    from .services import CodeExecutorService

    # 获取 submission 和 queue_stats
    try:
        submission = Submission.objects.select_related('user', 'problem').get(
            id=submission_id
        )
        queue_stats = submission.queue_stats
    except Submission.DoesNotExist:
        logger.error(
            f"Submission {submission_id} not found",
            extra={"submission_id": submission_id}
        )
        return

    try:
        # 1. 更新状态为 started
        submission.status = "judging"
        submission.save(update_fields=['status'])

        queue_stats.status = "started"
        queue_stats.started_at = timezone.now()
        queue_stats.save(update_fields=['status', 'started_at'])

        logger.info(
            f"Task started",
            extra={
                "task_id": self.request.id,
                "submission_id": submission_id,
            }
        )

        # 2. 执行评测（同步逻辑）
        executor = CodeExecutorService()
        result_submission = executor._execute_sync(submission)

        # 3. 更新状态为 success
        queue_stats.status = "success"
        queue_stats.completed_at = timezone.now()
        queue_stats.calculate_performance_metrics()
        queue_stats.save()

        # 清除容量缓存
        JudgingCapacityService.clear_cache()

        logger.info(
            f"Task completed successfully",
            extra={
                "task_id": self.request.id,
                "submission_id": submission_id,
                "final_status": result_submission.status,
                "execution_time": result_submission.execution_time,
            }
        )

    except SoftTimeLimitExceeded:
        # 软超时处理
        logger.warning(
            f"Task soft timeout exceeded",
            extra={
                "task_id": self.request.id,
                "submission_id": submission_id,
            }
        )

        submission.status = "time_limit_exceeded"
        submission.error = "任务执行超时（4.5分钟）"
        submission.save(update_fields=['status', 'error'])

        queue_stats.status = "timeout"
        queue_stats.completed_at = timezone.now()
        queue_stats.error_message = "SoftTimeLimitExceeded after 270s"
        queue_stats.calculate_performance_metrics()
        queue_stats.save()

        JudgingCapacityService.clear_cache()

    except Submission.DoesNotExist:
        logger.error(
            f"Submission {submission_id} deleted during execution",
            extra={"submission_id": submission_id}
        )

    except Exception as exc:
        logger.error(
            f"Task failed",
            extra={
                "task_id": self.request.id,
                "submission_id": submission_id,
                "error": str(exc),
            },
            exc_info=True
        )

        # 更新状态为 failed
        try:
            submission.status = "internal_error"
            submission.error = f"任务执行失败: {str(exc)}"
            submission.save(update_fields=['status', 'error'])

            queue_stats.status = "failed"
            queue_stats.completed_at = timezone.now()
            queue_stats.error_message = str(exc)
            queue_stats.retry_count = self.request.retries
            queue_stats.calculate_performance_metrics()
            queue_stats.save()
        except Exception as save_error:
            logger.error(
                f"Failed to update submission status",
                extra={"submission_id": submission_id, "error": str(save_error)}
            )

        JudgingCapacityService.clear_cache()

        # 判断是否重试
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying task",
                extra={
                    "task_id": self.request.id,
                    "submission_id": submission_id,
                    "retry_count": self.request.retries + 1,
                }
            )
            raise self.retry(exc=exc)

    return {
        "submission_id": submission_id,
        "status": submission.status,
        "task_id": self.request.id,
    }
```

#### 2.3.2 配置 Celery 任务路由

**文件**: `backend/core/settings.py`

```python
# Celery 任务路由配置
CELERY_TASK_ROUTES = {
    'courses.tasks.judge_submission_async': {
        'queue': 'code_judging',        # 专用队列
        'routing_key': 'code_judging',
    },
    'courses.tasks.refresh_unlock_snapshot': {
        'queue': 'default',
        'routing_key': 'default',
    },
    'courses.tasks.batch_refresh_stale_snapshots': {
        'queue': 'default',
        'routing_key': 'default',
    },
}

# Celery Beat 调度
CELERY_BEAT_SCHEDULE = {
    # ... 现有任务 ...

    # 清理过期的 JudgingQueueStats 记录（保留 7 天）
    "cleanup-old-queue-stats": {
        "task": "courses.tasks.cleanup_old_queue_stats",
        "schedule": crontab(hour=2, minute=0),  # 每天凌晨 2 点
    },
}
```

**文件**: `backend/courses/tasks.py`

```python
@shared_task
def cleanup_old_queue_stats(days=7):
    """清理过期的队列统计记录"""
    from .models import JudgingQueueStats
    from django.utils import timezone

    cutoff_date = timezone.now() - timezone.timedelta(days=days)

    deleted_count = JudgingQueueStats.objects.filter(
        completed_at__lt=cutoff_date
    ).delete()

    logger.info(
        f"Cleaned up old queue stats",
        extra={"deleted_count": deleted_count, "days": days}
    )

    return deleted_count
```

---

### 2.4 视图层修改

#### 2.4.1 修改 SubmissionViewSet.create()

**文件**: `backend/courses/views.py`

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

class SubmissionViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):

    # ... 现有代码 ...

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        创建新的提交记录

        支持两种模式：
        1. 同步模式（async=false）：立即执行，返回完整结果
        2. 异步模式（async=true，默认）：创建任务，立即返回 task_id

        请求参数：
        - code: 提交的代码（必填）
        - language: 编程语言（默认 python）
        - problem_id: 问题 ID（可选，不提供则自由运行）
        - async: 是否异步模式（默认 true）
        """
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language", "python")
        async_mode = request.data.get("async", True)  # 默认异步

        if not code:
            return Response(
                {"error": "Code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 情况 1：自由运行（无 problem_id）
        # 注意：自由运行不使用异步模式
        if not problem_id:
            try:
                executor = CodeExecutorService()
                result = executor.run_freely(code=code, language=language)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Error executing code: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # 情况 2：算法题提交
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.type != "algorithm":
            return Response(
                {"error": "Only algorithm problems allow code submission"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            executor = CodeExecutorService()

            if async_mode:
                # 异步模式：创建任务并立即返回
                submission = executor.run_all_test_cases(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    async_mode=True
                )

                # 保存代码草稿
                CodeDraft.objects.create(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    save_type="submission",
                    submission=submission,
                )

                # 返回 202 Accepted
                serializer = self.get_serializer(submission)
                return Response(
                    {
                        "message": "代码已提交，正在评测中",
                        "task_id": submission.task_id,
                        "submission": serializer.data,
                    },
                    status=status.HTTP_202_ACCEPTED
                )

            else:
                # 同步模式（向后兼容）
                submission = executor.run_all_test_cases(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    async_mode=False
                )

                # 保存代码草稿
                CodeDraft.objects.create(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    save_type="submission",
                    submission=submission,
                )

                # 如果提交成功，更新问题进度
                if submission.status == "accepted":
                    chapter = problem.chapter
                    course = chapter.course if chapter else None

                    if course:
                        enrollment, _ = Enrollment.objects.get_or_create(
                            user=request.user, course=course
                        )

                        problem_progress, created = ProblemProgress.objects.get_or_create(
                            enrollment=enrollment,
                            problem=problem,
                            defaults={
                                "status": "solved",
                                "attempts": 1,
                                "best_submission": submission,
                            },
                        )

                        if not created:
                            problem_progress.status = "solved"
                            problem_progress.attempts += 1
                            if (
                                not problem_progress.best_submission
                                or submission.execution_time
                                < problem_progress.best_submission.execution_time
                            ):
                                problem_progress.best_submission = submission
                            problem_progress.save()

                serializer = self.get_serializer(submission)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except CapacityFullError as e:
            # 容量已满
            return Response(
                {
                    "error": str(e),
                    "status": "capacity_full"
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        except Exception as e:
            logger.error(
                f"Error creating submission",
                extra={"user_id": request.user.id, "problem_id": problem_id, "error": str(e)},
                exc_info=True,
            )
            return Response(
                {"error": f"Error executing code: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
```

#### 2.4.2 添加 queue_status API

**文件**: `backend/courses/views.py`

```python
class SubmissionViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):

    # ... 现有代码 ...

    @action(detail=False, methods=["get"])
    def queue_status(self, request):
        """
        获取队列状态

        返回当前系统的队列容量信息
        """
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
        """
        获取特定提交的任务状态

        Args:
            pk: Submission ID

        返回:
        {
            "submission_id": 123,
            "task_id": "abc-123",
            "submission_status": "judging",
            "queue_status": "started",
            "queued_at": "2025-01-15T10:00:00Z",
            "started_at": "2025-01-15T10:01:00Z",
            "completed_at": null,
            "queue_wait_seconds": 60,
            "execution_seconds": null,
            "total_seconds": null,
        }
        """
        submission = self.get_object()

        if not submission.task_id:
            return Response(
                {"error": "This submission is not an async task"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            queue_stats = submission.queue_stats
        except JudgingQueueStats.DoesNotExist:
            return Response(
                {"error": "Queue stats not found"},
                status=status.HTTP_404_NOT_FOUND
            )

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

---

## 3. 前端实现方案

### 3.1 类型定义

**文件**: `frontend/web-student/app/types/submission.ts`

```typescript
// ... 现有类型 ...

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

### 3.2 API 客户端

**文件**: `frontend/web-student/app/lib/clientHttp.ts`

```typescript
// ... 现有代码 ...

// 获取队列状态
export async function getQueueStatus(): Promise<QueueStatusRes> {
  const response = await clientHttp.get<QueueStatusRes>('/submissions/queue-status/');
  return response;
}

// 获取任务状态
export async function getTaskStatus(submissionId: number): Promise<TaskStatusRes> {
  const response = await clientHttp.get<TaskStatusRes>(`/submissions/${submissionId}/task_status/`);
  return response;
}

// 异步提交代码
export async function submitCodeAsync(data: AsyncSubmissionReq): Promise<AsyncSubmissionRes> {
  const response = await clientHttp.post<AsyncSubmissionRes>('/submissions/', {
    ...data,
    async: true,
  });
  return response;
}
```

### 3.3 轮询 Hook

**文件**: `frontend/web-student/app/hooks/useSubmissionPolling.ts`

```typescript
import { useState, useEffect, useRef } from 'react';
import { getTaskStatus } from '../lib/clientHttp';
import type { TaskStatusRes } from '../types/submission';

interface UseSubmissionPollingOptions {
  submissionId: number;
  initialDelay?: number;      // 初始延迟（毫秒）
  interval?: number;           // 轮询间隔（毫秒）
  maxAttempts?: number;        // 最大尝试次数
  onComplete?: (status: TaskStatusRes) => void;
  onError?: (error: Error) => void;
}

export function useSubmissionPolling({
  submissionId,
  initialDelay = 2000,
  interval = 2000,
  maxAttempts = 60,
  onComplete,
  onError,
}: UseSubmissionPollingOptions) {
  const [status, setStatus] = useState<TaskStatusRes | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [attempt, setAttempt] = useState(0);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null;

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

        // 检查是否超过最大尝试次数
        if (attempt >= maxAttempts) {
          setIsLoading(false);
          setError(new Error('轮询超时，请刷新页面重试'));
          return;
        }

        // 继续轮询
        timeoutId = setTimeout(poll, interval);

      } catch (err) {
        const error = err as Error;
        setError(error);
        setIsLoading(false);
        onError?.(error);
      }
    };

    // 启动轮询
    timeoutId = setTimeout(poll, initialDelay);

    // 清理函数
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [submissionId, initialDelay, interval, maxAttempts, attempt, onComplete, onError]);

  return { status, isLoading, error, attempt };
}
```

### 3.4 提交组件示例

**文件**: `frontend/web-student/app/components/CodeSubmissionForm.tsx`

```typescript
import { useState } from 'react';
import { submitCodeAsync } from '../lib/clientHttp';
import { useSubmissionPolling } from '../hooks/useSubmissionPolling';

export function CodeSubmissionForm({ problemId }: { problemId: number }) {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [submissionId, setSubmissionId] = useState<number | null>(null);

  const { status, isLoading, error } = useSubmissionPolling({
    submissionId: submissionId!,
    onComplete: (status) => {
      console.log('Submission completed:', status);
    },
    onError: (error) => {
      console.error('Polling error:', error);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const result = await submitCodeAsync({
        code,
        language,
        problem_id: problemId,
        async: true,
      });

      setSubmissionId(result.submission.id);
    } catch (error) {
      console.error('Submission failed:', error);
    }
  };

  if (isLoading && status) {
    return (
      <div className="submission-status">
        <h3>评测中...</h3>
        <p>状态: {getStatusText(status.queue_status)}</p>
        {status.queued_at && !status.started_at && (
          <p>队列中，前面有 {status.queue_wait_seconds} 秒</p>
        )}
        {status.started_at && !status.completed_at && (
          <p>执行中，已用 {status.execution_seconds} 秒</p>
        )}
      </div>
    );
  }

  if (error) {
    return (
      <div className="submission-error">
        <h3>提交失败</h3>
        <p>{error.message}</p>
        <button onClick={() => window.location.reload()}>刷新重试</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="输入代码..."
      />
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="java">Java</option>
      </select>
      <button type="submit">提交</button>
    </form>
  );
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    pending: '等待中...',
    started: '评测中...',
    success: '完成',
    failed: '失败',
    timeout: '超时',
    cancelled: '已取消',
  };
  return statusMap[status] || status;
}
```

---

## 4. 部署配置

### 4.1 Worker 启动脚本

**文件**: `backend/docker-compose.yml`

```yaml
services:
  # ... 现有服务 ...

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

### 4.2 环境变量

**文件**: `backend/.env.example`

```bash
# ... 现有配置 ...

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

---

## 5. 监控和管理

### 5.1 管理命令

**文件**: `backend/courses/management/commands/monitor_judging_queue.py`

```python
from django.core.management.base import BaseCommand
from courses.models import JudgingQueueStats
from courses.services import JudgingCapacityService
from django.utils import timezone
from datetime import timedelta


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

        # 显示最近的任务
        recent_tasks = JudgingQueueStats.objects.order_by('-queued_at')[:10]
        self.stdout.write(self.style.SUCCESS('\n=== Recent Tasks ==='))

        for task in recent_tasks:
            self.stdout.write(
                f"#{task.submission_id} [{task.status}] "
                f"Queued: {task.queued_at.strftime('%H:%M:%S')} "
                f"Duration: {task.total_seconds or 0:.1f}s"
            )
```

---

## 6. 测试策略

### 6.1 单元测试

**文件**: `backend/courses/tests/test_services.py`

```python
from django.test import TestCase
from courses.services import JudgingCapacityService, CodeExecutorService
from courses.models import Submission, JudgingQueueStats
from django.contrib.auth import get_user_model

User = get_user_model()


class JudgingCapacityServiceTest(TestCase):
    """测试容量管理服务"""

    def test_get_current_capacity(self):
        """测试获取当前容量"""
        capacity = JudgingCapacityService.get_current_capacity()

        self.assertIn('pending_count', capacity)
        self.assertIn('running_count', capacity)
        self.assertIn('total_capacity', capacity)
        self.assertEqual(capacity['total_capacity'], 18)

    def test_check_capacity(self):
        """测试容量检查"""
        is_allowed, error_msg, estimated_wait = JudgingCapacityService.check_capacity()

        self.assertTrue(is_allowed)
        self.assertIsNone(error_msg)
        self.assertIsNotNone(estimated_wait)


class CodeExecutorServiceAsyncTest(TestCase):
    """测试异步代码执行服务"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_async_submission(self):
        """测试异步提交"""
        # ... 测试代码 ...
        pass
```

### 6.2 集成测试

**文件**: `backend/courses/tests/test_views.py`

```python
class SubmissionAsyncTestCase(TestCase):
    """测试异步提交 API"""

    def setUp(self):
        self.user = User.objects.create_user(...)
        self.client.force_authenticate(user=self.user)
        self.problem = Problem.objects.create(...)

    def test_async_submission_accepted(self):
        """测试异步提交返回 202"""
        response = self.client.post(
            '/api/submissions/',
            {
                'code': 'print("hello")',
                'language': 'python',
                'problem_id': self.problem.id,
                'async': True,
            }
        )

        self.assertEqual(response.status_code, 202)
        self.assertIn('task_id', response.data)

    def test_queue_status_endpoint(self):
        """测试队列状态接口"""
        response = self.client.get('/api/submissions/queue-status/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('pending_count', response.data)
```

---

## 7. 迁移和回滚策略

### 7.1 灰度发布

**阶段 1**: 小范围测试（10% 用户）
- 使用用户 ID 哈希分流
- 监控错误率和性能

**阶段 2**: 逐步扩大（50% 用户）
- 根据阶段 1 结果调整
- 收集用户反馈

**阶段 3**: 全量发布（100% 用户）
- 所有人使用异步系统

### 7.2 回滚计划

**触发条件**:
- 错误率超过 5%
- 平均等待时间超过 2 分钟
- 用户投诉增加

**回滚步骤**:
1. 修改 `SubmissionViewSet.create()` 中的 `async_mode` 默认值为 `False`
2. 重启服务
3. 继续完成队列中的任务
4. 通知用户

---

## 8. 总结

这个详细的技术设计基于对现有代码库的深入探索，提供了：

1. **完整的数据模型设计**：JudgingQueueStats 和 Submission 扩展
2. **详细的服务层实现**：JudgingCapacityService 和修改后的 CodeExecutorService
3. **健壮的异步任务**：带有超时、重试和错误处理的 Celery 任务
4. **清晰的 API 修改**：向后兼容的视图层修改
5. **实用的前端实现**：类型定义、API 客户端和轮询 Hook
6. **可操作的部署方案**：Docker Compose 配置和管理命令
7. **全面的测试策略**：单元测试和集成测试

所有实现都基于现有代码库的架构和模式，确保了一致性和可维护性。
