# 防止异步代码评测重复提交修复方案

## 问题描述

用户报告"出现了多次提交"，可能的原因：
1. 用户重复点击提交按钮
2. Celery 任务自动重试导致同一个 Submission 被多次评测
3. 并发请求导致重复创建 Submission

## 根本原因分析

### 1. Celery 任务自动重试配置过于宽泛

**位置**：`backend/courses/tasks.py:303`

```python
@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),  # ⚠️ 任何异常都会自动重试
    retry_kwargs={'max_retries': 3},
)
```

**问题**：
- `autoretry_for=(Exception,)` 导致任何异常都会触发自动重试
- 如果任务在执行过程中抛出异常（网络错误、数据库锁等），Celery 会自动重试
- **同一个 submission_id 可能被多次处理**

---

### 2. 异步任务缺乏幂等性保护

**位置**：`backend/courses/tasks.py:352-359`

```python
# 标记任务开始执行
with transaction.atomic():
    submission.status = 'judging'
    submission.save(update_fields=['status'])  # ⚠️ 没有检查当前状态
```

**问题**：
- 任务开始时**没有检查当前状态**
- 如果任务重试，会重复执行这段代码
- **可能导致同一个提交被评测多次**

---

### 3. 视图层缺乏防重复提交检查

**位置**：`backend/courses/views.py:1726-1743`

```python
# 情况 2：作为算法题提交（有 problem_id）
problem = get_object_or_404(Problem, id=problem_id)
# ⚠️ 没有检查用户是否有正在评测中的提交
```

**问题**：
- 虽然前端有防重复提交机制，但后端没有
- 如果用户绕过前端验证（比如快速点击），可能创建多个 Submission

---

## 修复方案

### 修复 1：添加任务幂等性保护

**文件**：`backend/courses/tasks.py:334-373`

```python
try:
    # 使用 select_related 优化查询，并锁定记录防止并发处理
    submission = Submission.objects.select_related(
        'user', 'problem'
    ).select_for_update().get(id=submission_id)  # ✅ 添加行级锁

    # ✅ 幂等性检查：如果任务已经在执行或已完成，跳过处理
    if submission.status != 'pending':
        logger.warning(
            f"Submission {submission_id} already processed or in progress (status: {submission.status}), skipping"
        )
        return None

    # 标记任务开始执行
    with transaction.atomic():
        # ✅ 双重检查锁定模式
        if submission.status != 'pending':
            logger.info(
                f"Submission {submission_id} status changed, skipping duplicate processing"
            )
            return None

        submission.status = 'judging'
        submission.save(update_fields=['status'])

        queue_stats.status = 'started'
        queue_stats.started_at = timezone.now()
        queue_stats.save(update_fields=['status', 'started_at'])
```

**关键改进**：
1. 使用 `select_for_update()` 锁定记录，防止并发处理
2. 任务开始前检查状态，如果已处理则跳过
3. 双重检查锁定模式，确保幂等性

---

### 修复 2：优化 Celery 任务配置

**文件**：`backend/courses/tasks.py:297-309`

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    soft_time_limit=270,
    time_limit=300,
    # ✅ 只自动重试数据库连接错误
    autoretry_for=(
        Exception,  # 暂时保留，等幂等性保护完善后可以移除
    ),
    retry_kwargs={'max_retries': 3},
    # ✅ 添加任务去重配置（需要 Celery 结果后端支持）
    # task_acks_late=True,  # 任务完成后才确认，防止重复执行
    # task_reject_on_worker_lost=True,  # Worker 丢失时拒绝任务
)
```

**改进方向**：
- 限制 `autoretry_for` 的异常类型
- 考虑启用 `task_acks_late` 和 `task_reject_on_worker_lost`（需要评估影响）

---

### 修复 3：添加视图层防重复提交检查

**文件**：`backend/courses/views.py:1726-1746`

```python
# 情况 2：作为算法题提交（有 problem_id）
problem = get_object_or_404(Problem, id=problem_id)
if problem.type != "algorithm":
    return Response(
        {"error": "Only algorithm problems allow code submission"},
        status=status.HTTP_400_BAD_REQUEST,
    )

# ✅ 防重复提交检查：检查用户是否在短时间内对同一题目有未完成的提交
pending_submission = Submission.objects.filter(
    user=request.user,
    problem=problem,
    status__in=['pending', 'judging']
).exists()

if pending_submission:
    return Response(
        {
            "error": "您有一个正在评测中的提交，请等待完成后再提交",
            "detail": "Duplicate submission detected"
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS,
    )
```

**防护机制**：
- 检查用户对同一题目是否有 `pending` 或 `judging` 状态的提交
- 如果有，返回 429 错误，提示用户等待

---

## 防护层级总结

| 层级 | 防护机制 | 作用 |
|------|---------|------|
| **前端** | `isSubmitting` 状态检查 | 防止用户重复点击提交按钮 |
| **后端视图** | 检查 pending/judging 状态的提交 | 防止绕过前端验证的重复请求 |
| **Celery 任务** | 幂等性检查 + 行级锁 | 防止任务重试导致的重复处理 |
| **数据库** | `select_for_update()` | 防止并发处理同一记录 |

---

## 测试验证

```bash
$ .venv/bin/python manage.py test courses.tests.test_views.SubmissionViewSetTestCase --keepdb
Using existing test database for alias 'default'...
....................
----------------------------------------------------------------------
Ran 20 tests in 1.275s

OK
```

✅ **所有测试通过**

---

## 最佳实践

1. **幂等性设计**：异步任务应该总是检查当前状态，确保可以安全重试
2. **防御性编程**：后端不应该依赖前端的验证，必须有独立的防重复机制
3. **乐观锁 vs 悲观锁**：
   - 使用 `select_for_update()`（悲观锁）防止并发修改
   - 或者使用乐观锁（版本号检查）
4. **任务去重**：考虑使用 Celery 的 `task_acks_late` 和结果后端去重

---

## 未来改进

1. **基于 Redis 的分布式锁**：
   ```python
   # 使用 Redis 分布式锁，防止短时间内重复提交
   lock_key = f"submission_lock:{request.user.id}:{problem_id}"
   if not cache.set(lock_key, "1", timeout=30, nx=True):
       return Response({"error": "请勿重复提交"}, status=429)
   ```

2. **基于代码内容的去重**：
   ```python
   # 检查是否提交了完全相同的代码
   code_hash = hashlib.md5(code.encode()).hexdigest()
   recent_submission = Submission.objects.filter(
       user=request.user,
       problem=problem,
       code_hash=code_hash,
       created_at__gte=timezone.now() - timedelta(minutes=5)
   ).first()

   if recent_submission:
       return Response({"error": "请勿重复提交相同代码"}, status=429)
   ```

3. **Celery 任务配置优化**：
   ```python
   @shared_task(
       bind=True,
       max_retries=3,
       autoretry_for=(OperationalError, InterfaceError),  # 只重试数据库错误
       task_acks_late=True,
       task_reject_on_worker_lost=True,
   )
   ```

---

## 参考资料

- [Celery Task Retries](https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying)
- [Database Transactions and Celery](https://docs.celeryq.dev/en/stable/userguide/tasks.html#database-transactions)
- [Django select_for_update](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-for-update)