## Context

异步代码评测系统在实现时存在三个异常处理缺陷：

1. **错误的异常类型捕获**：`views.py` 中 `queue_stats` 端点使用 `AttributeError` 捕获 OneToOne 关系缺失的情况，但 Django 实际抛出的是 `RelatedObjectDoesNotExist`
2. **重试失败时的 IntegrityError 风险**：`tasks.py` 在任务重试失败时尝试创建 `JudgingQueueStats`，但该记录已在提交时创建，导致违反 OneToOne 约束
3. **误导性的错误检查**：`tasks.py` 中检查 `queue_stats` 存在性的代码永远不会被执行，因为异常在此之前就已抛出

当前系统状态：
- 异步代码提交流程正常工作（Submission 和 JudgingQueueStats 正确创建）
- Celery 任务执行正常
- 仅在边缘情况下（缺少 queue_stats 或任务重试失败）会出现问题

## Goals / Non-Goals

**Goals:**
- 修复三个异常处理缺陷，确保系统在所有边缘情况下都能正确响应
- 保证错误响应返回正确的 HTTP 状态码（404 而非 500）
- 防止任务重试失败时的系统崩溃（IntegrityError）
- 改进代码可读性和可维护性
- 添加测试覆盖，确保异常处理路径得到验证

**Non-Goals:**
- 不改变现有的异步代码评测流程
- 不修改数据库模型或添加迁移
- 不优化性能或重构现有业务逻辑
- 不修改前端代码

## Decisions

### Decision 1: 使用 Django 基类异常捕获

**选择**: 使用 `django.core.exceptions.ObjectDoesNotExist` 作为异常基类

**理由**:
- `RelatedObjectDoesNotExist` 是 `ObjectDoesNotExist` 的子类
- 使用基类可以捕获所有相关异常，代码更清晰
- 或者可以使用 `Submission.queue_stats.RelatedObjectDoesNotExist` 更精确

**替代方案**:
1. 使用 `AttributeError` - 已证明错误
2. 使用 `Submission.queue_stats.RelatedObjectDoesNotExist` - 更精确但代码较长
3. 使用 `ObjectDoesNotExist` - 平衡了精确性和可读性 ✅

**实现**:
```python
from django.core.exceptions import ObjectDoesNotExist

try:
    queue_stats = submission.queue_stats
except ObjectDoesNotExist:
    return Response({"error": "该提交没有队列统计信息"}, status=404)
```

### Decision 2: 使用 get_or_create 防止重复创建

**选择**: 使用 `JudgingQueueStats.objects.get_or_create()` 替代 `create()`

**理由**:
- 避免违反 OneToOne 约束导致的 IntegrityError
- 如果记录已存在，可以更新状态；如果不存在，可以创建
- 原子操作，线程安全

**替代方案**:
1. 先查询再创建 - 需要两步操作，存在竞态条件
2. 使用事务和异常处理 - 过于复杂
3. get_or_create - Django 提供的原子操作，最适合 ✅

**实现**:
```python
queue_stats, created = JudgingQueueStats.objects.get_or_create(
    submission=submission,
    defaults={
        'status': 'failed',
        'error_message': f"任务执行失败: {str(exc)}"
    }
)
if not created:
    queue_stats.status = 'failed'
    queue_stats.error_message = f"任务执行失败: {str(exc)}"
    queue_stats.save()
```

### Decision 3: 正确处理 queue_stats 访问异常

**选择**: 使用 try-except 捕获 `RelatedObjectDoesNotExist` 并转换为有意义的错误

**理由**:
- 明确处理异常而非依赖永远不会执行的 if 检查
- 提供清晰的错误信息
- 符合 Python 的 EAFP 风格（Easier to Ask for Forgiveness than Permission）

**替代方案**:
1. 使用 `hasattr()` 检查 - 不符合 Django 惯例
2. 使用 `getattr(submission, 'queue_stats', None)` - 隐藏了异常
3. 使用 try-except 捕获特定异常 - 清晰且符合惯例 ✅

**实现**:
```python
try:
    queue_stats = submission.queue_stats
except Submission.queue_stats.RelatedObjectDoesNotExist:
    logger.error(f"Submission {submission_id} missing queue_stats")
    raise ValueError("Submission 没有对应的队列统计信息")
```

## Risks / Trade-offs

### Risk 1: 向后兼容性
**风险**: 修改异常处理逻辑可能影响依赖当前行为的代码
**缓解**: 仅修改错误处理路径，不影响正常流程；添加测试确保行为正确

### Risk 2: 测试覆盖不足
**风险**: 异常处理路径难以触发，可能存在未发现的问题
**缓解**: 添加专门的测试用例覆盖：
  - queue_stats 端点在缺少统计信息时的响应
  - 任务重试失败时的 IntegrityError 处理
  - queue_stats 访问异常的处理

### Risk 3: 日志记录
**风险**: 异常情况可能未被充分记录，难以调试
**缓解**: 在每个异常处理路径添加详细的日志记录，包括 submission_id 和错误类型

## Migration Plan

### 部署步骤
1. 部署后端代码变更（views.py 和 tasks.py）
2. 运行测试验证修复效果
3. 监控错误日志，确认无新的异常

### 回滚策略
- 如果发现问题，立即回滚到之前版本
- 由于仅修改异常处理逻辑，回滚无数据风险
- 无数据库迁移，无需数据回滚

### 监控指标
- 500 错误率降低（queue_stats 端点）
- IntegrityError 异常数量（应为 0）
- 任务重试成功率