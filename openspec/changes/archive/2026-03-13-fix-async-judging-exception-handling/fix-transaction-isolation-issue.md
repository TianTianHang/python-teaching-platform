# 异步代码评测事务隔离问题修复

## 问题描述

**错误日志**：
```
[2026-03-13 22:37:40,373: ERROR/MainProcess] Submission 50 not found, not retrying
```

**根本原因**：
在 `@transaction.atomic` 装饰的视图方法中，异步任务 `judge_submission_async.delay()` 在事务提交前启动。由于数据库事务隔离，异步任务无法看到未提交的数据，导致查询 `Submission.objects.get(id=submission_id)` 失败。

---

## 修复方案

### 核心修改

使用 Django 的 `transaction.on_commit()` 钩子，确保异步任务在事务成功提交后才启动。

**修改文件**：`backend/courses/views.py:1767-1803`

```python
# 之前：在事务内直接启动异步任务（错误）
task = judge_submission_async.delay(submission.id)
submission.task_id = task.id
submission.save(update_fields=['task_id'])

# 现在：在事务提交后启动异步任务（正确）
def start_async_judging():
    """在事务提交后启动异步评测任务"""
    try:
        task = judge_submission_async.delay(submission.id)
        # 更新 task_id（独立的数据库操作）
        Submission.objects.filter(id=submission.id).update(task_id=task.id)
    except Exception as e:
        # 标记提交失败
        Submission.objects.filter(id=submission.id).update(
            status="internal_error",
            error=f"启动评测任务失败: {str(e)}"
        )

# 注册事务提交后的回调
transaction.on_commit(start_async_judging)
```

---

## 技术细节

### 1. 执行顺序对比

**修复前**：
```
1. 事务开始
2. 创建 Submission (id=50)
3. 创建 JudgingQueueStats
4. 启动异步任务 ⚠️ (事务未提交)
5. 异步任务查询 Submission → DoesNotExist ❌
6. 事务提交
```

**修复后**：
```
1. 事务开始
2. 创建 Submission (id=50)
3. 创建 JudgingQueueStats
4. 注册 on_commit 回调
5. 事务提交 ✅
6. on_commit 回调执行
7. 启动异步任务 ✅
8. 异步任务查询 Submission → 成功 ✅
```

### 2. task_id 处理

**响应中的 task_id**：
- 初始值：`null`（在响应返回时异步任务还未启动）
- 客户端应使用 `submission_id` 轮询状态
- `task_id` 在事务提交后由异步任务生成并更新到数据库

**前端类型更新**：
```typescript
// frontend/web-student/app/types/submission.ts
export interface AsyncSubmissionResponse {
  task_id: string | null;  // 初始为 null，事务提交后才生成
  // ...
}
```

### 3. API 兼容性

- ✅ 前端使用 `'task_id' in result` 判断异步响应，`null` 值不影响判断逻辑
- ✅ 前端通过 `submission_id` 轮询，不依赖初始 `task_id` 的值
- ✅ 所有现有测试通过（20/20）

---

## 其他优化

### 合并重复的数据库保存

**问题**：Submission 被保存两次（`estimated_wait_seconds` 和 `task_id`）

**修复**：合并为一次保存
```python
# 之前：两次保存
submission.save(update_fields=['estimated_wait_seconds'])
# ...
submission.save(update_fields=['task_id'])

# 现在：一次保存
submission.task_id = task_id
submission.estimated_wait_seconds = estimated_wait
submission.save(update_fields=['task_id', 'estimated_wait_seconds'])
```

**性能提升**：减少 50% 的数据库写操作

### 移除未使用的变量

```python
# 之前：创建变量但未使用
queue_stats = JudgingQueueStats.objects.create(...)

# 现在：直接创建，无冗余变量
JudgingQueueStats.objects.create(...)
```

---

## 测试验证

```bash
$ .venv/bin/python manage.py test courses.tests.test_views.SubmissionViewSetTestCase --keepdb
Using existing test database for alias 'default'...
....................
----------------------------------------------------------------------
Ran 20 tests in 1.318s

OK
```

---

## 最佳实践

1. **事务 + 异步任务**：使用 `transaction.on_commit()` 确保数据持久化后再启动异步任务
2. **API 设计**：客户端应使用持久化标识符（如 `submission_id`）而非内部实现细节（如 `task_id`）
3. **类型安全**：使用 `| null` 明确标记可能为 null 的字段，避免前端假设字段总是有值

---

## 参考资料

- Django 文档：[Performing actions after commit](https://docs.djangoproject.com/en/stable/topics/db/transactions/#performing-actions-after-commit)
- Celery 文档：[Task Queues and Database Transactions](https://docs.celeryq.dev/en/stable/userguide/tasks.html#database-transactions)