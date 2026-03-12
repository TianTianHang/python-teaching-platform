from celery import shared_task
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
    - 自动重试所有异常（DoesNotExist 除外）

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

    except Enrollment.DoesNotExist:
        # Enrollment 已被删除，无需重试，直接返回
        logger.warning(
            f"Enrollment {enrollment_id} no longer exists, skipping snapshot refresh",
            extra={'enrollment_id': enrollment_id}
        )
        return None
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
    - 自动清理 orphaned snapshots（enrollment 已删除）

    调用频率：每分钟
    """
    from .models import CourseUnlockSnapshot

    # 先清理 orphaned snapshots（快照存在但 enrollment 已删除）
    orphaned_count = CourseUnlockSnapshot.objects.filter(
        enrollment__isnull=True
    ).delete()[0]

    if orphaned_count > 0:
        logger.info(
            f"Cleaned up {orphaned_count} orphaned snapshots (enrollment deleted)",
            extra={'count': orphaned_count}
        )

    stale_snapshots = CourseUnlockSnapshot.objects.filter(
        is_stale=True
    ).select_related('enrollment__user', 'course').order_by('computed_at')[:batch_size]

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


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 重试间隔 60 秒
    autoretry_for=(Exception,),
)
def refresh_problem_unlock_snapshot(self, enrollment_id: int):
    """
    刷新单个 enrollment 的问题解锁状态快照

    重试策略：
    - 最多重试 3 次
    - 重试间隔 60 秒
    - 自动重试所有异常（DoesNotExist 除外）

    性能优化：
    - 使用 select_related 减少 DB 查询
    - 使用 update_fields 减少写入字段
    - 事务保证原子性
    """
    from .models import ProblemUnlockSnapshot, Enrollment

    try:
        # 使用 select_related 优化查询
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
            f"Refreshed problem unlock snapshot for enrollment {enrollment_id}",
            extra={
                'enrollment_id': enrollment_id,
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'snapshot_version': snapshot.version
            }
        )

    except Enrollment.DoesNotExist:
        # Enrollment 已被删除，无需重试，直接返回
        logger.warning(
            f"Enrollment {enrollment_id} no longer exists, skipping problem snapshot refresh",
            extra={'enrollment_id': enrollment_id}
        )
        return None
    except Exception as exc:
        logger.error(
            f"Failed to refresh problem snapshot for enrollment {enrollment_id}: {exc}",
            exc_info=True,
            extra={'enrollment_id': enrollment_id}
        )
        raise


@shared_task
def batch_refresh_stale_problem_snapshots(batch_size: int = 200):
    """
    批量刷新过期的问题快照

    策略：
    - 每次处理 batch_size 个过期快照
    - 按 computed_at 升序排序（最旧的优先）
    - 为每个快照触发单独的异步任务（并行处理）
    - 自动清理 orphaned snapshots（enrollment 已删除）

    调用频率：每30秒（比 Chapter 更频繁，Problem 访问更频繁）
    """
    from .models import ProblemUnlockSnapshot

    # 先清理 orphaned snapshots（快照存在但 enrollment 已删除）
    orphaned_count = ProblemUnlockSnapshot.objects.filter(
        enrollment__isnull=True
    ).delete()[0]

    if orphaned_count > 0:
        logger.info(
            f"Cleaned up {orphaned_count} orphaned problem snapshots (enrollment deleted)",
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
            f"Triggered batch refresh for {count} stale problem snapshots",
            extra={'batch_size': batch_size}
        )

    return count


@shared_task
def scheduled_problem_snapshot_refresh():
    """
    定时任务：每30秒批量刷新过期的问题快照

    调度：Celery Beat
    """
    return batch_refresh_stale_problem_snapshots.delay()


@shared_task
def cleanup_old_problem_snapshots(days: int = 30):
    """
    清理旧的问题快照（可选的维护任务）

    删除 inactive enrollment 的快照（用户已退课）。
    每天执行一次。

    注意：此任务可选，根据实际需求决定是否启用。
    """
    from .models import ProblemUnlockSnapshot

    # 找出已删除的 enrollment 的快照
    old_snapshots = ProblemUnlockSnapshot.objects.filter(
        enrollment__isnull=True
    )

    count = old_snapshots.delete()[0]

    logger.info(
        f"Cleaned up {count} old problem snapshots",
        extra={'days': days}
    )

    return count


# ============================================================================
# Async Code Judging System Tasks
# ============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,  # 重试间隔 30 秒
    soft_time_limit=270,  # 软超时 4.5 分钟
    time_limit=300,  # 硬超时 5 分钟
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def judge_submission_async(self, submission_id: int):
    """
    异步执行代码评测任务

    三层超时设计：
    - 队列超时（120秒）：在 judge_submission_view 中检查
    - 软超时（270秒）：优雅退出，保存已执行结果
    - 硬超时（300秒）：强制终止任务

    任务流程：
    1. 更新 Submission 和 JudgingQueueStats 为 judging 状态
    2. 执行代码评测
    3. 更新结果到数据库
    4. 清理临时资源
    5. 更新为最终状态

    重试策略：
    - 最多重试 3 次
    - 重试间隔 30 秒
    - 自动重试临时错误（网络错误、数据库锁等）
    """
    from django.utils import timezone
    from .services import CodeExecutorService, CODE_JUDGING_CONFIG
    from .models import Submission, JudgingQueueStats
    from django.db import transaction

    logger = logging.getLogger(__name__)

    try:
        # 使用 select_related 优化查询
        submission = Submission.objects.select_related(
            'user', 'problem'
        ).get(id=submission_id)

        # 获取队列统计信息
        queue_stats = submission.queue_stats
        if not queue_stats:
            raise ValueError("Submission 没有对应的队列统计信息")

        # 标记任务开始执行
        with transaction.atomic():
            submission.status = 'judging'
            submission.save(update_fields=['status'])

            queue_stats.status = 'started'
            queue_stats.started_at = timezone.now()
            queue_stats.save(update_fields=['status', 'started_at'])

        logger.info(
            f"Started judging submission {submission_id}",
            extra={
                'submission_id': submission_id,
                'user_id': submission.user_id,
                'problem_id': submission.problem_id,
                'language': submission.language,
            }
        )

        # 执行代码评测
        executor = CodeExecutorService()
        try:
            # 执行评测
            judged_submission = executor.run_all_test_cases(
                user=submission.user,
                problem=submission.problem,
                code=submission.code,
                language=submission.language
            )

            # 记录执行时间
            execution_time = (timezone.now() - queue_stats.started_at).total_seconds()
            queue_stats.execution_seconds = int(execution_time)

            # 更新提交记录中的执行时间和内存使用
            if judged_submission.execution_time is not None:
                judged_submission.execution_time = float(judged_submission.execution_time)
            if judged_submission.memory_used is not None:
                judged_submission.memory_used = float(judged_submission.memory_used)

            logger.info(
                f"Judging completed for submission {submission_id}",
                extra={
                    'submission_id': submission_id,
                    'status': judged_submission.status,
                    'execution_time_ms': judged_submission.execution_time,
                    'memory_used_mb': judged_submission.memory_used,
                    'execution_seconds': execution_time
                }
            )

        except Exception as exc:
            # 处理执行中的错误
            error_type = type(exc).__name__

            logger.error(
                f"Error during judging for submission {submission_id}: {exc}",
                exc_info=True,
                extra={
                    'submission_id': submission_id,
                    'error_type': error_type,
                }
            )

            # 根据错误类型设置状态
            if error_type == 'SoftTimeLimitExceeded':
                # 软超时 - 保存部分结果
                queue_stats.status = 'timeout'
                queue_stats.error_message = f"评测超时（{CODE_JUDGING_CONFIG['soft_timeout_sec']}秒）"
            else:
                # 其他错误
                queue_stats.status = 'failed'
                queue_stats.error_message = str(exc)

            queue_stats.completed_at = timezone.now()
            queue_stats.save()

            # 标记提交失败
            submission.status = 'internal_error'
            submission.error = queue_stats.error_message
            submission.save(update_fields=['status', 'error'])

            # 不重试任务超时
            if error_type == 'SoftTimeLimitExceeded':
                logger.warning(
                    f"Task timeout for submission {submission_id}, not retrying",
                    extra={'submission_id': submission_id}
                )
                return

            # 重新抛出异常以触发重试
            raise exc

        # 评测成功完成
        with transaction.atomic():
            # 更新提交状态
            submission.status = judged_submission.status
            submission.output = judged_submission.output
            submission.error = judged_submission.error
            submission.execution_time = judged_submission.execution_time
            submission.memory_used = judged_submission.memory_used
            submission.save()

            # 更新队列统计
            queue_stats.status = 'success'
            queue_stats.completed_at = timezone.now()
            queue_stats.save()

        logger.info(
            f"Successfully completed judging for submission {submission_id}",
            extra={
                'submission_id': submission_id,
                'final_status': judged_submission.status,
                'total_execution_seconds': execution_time
            }
        )

        return {
            'submission_id': submission_id,
            'status': judged_submission.status,
            'execution_time_ms': judged_submission.execution_time,
            'memory_used_mb': judged_submission.memory_used,
            'execution_seconds': execution_time
        }

    except Submission.DoesNotExist:
        # 提交记录不存在，无需重试
        logger.error(
            f"Submission {submission_id} not found, not retrying",
            extra={'submission_id': submission_id}
        )
        return None

    except Exception as exc:
        # 记录错误并触发重试
        retry_count = self.request.retries

        logger.error(
            f"Failed to judge submission {submission_id} (attempt {retry_count + 1}): {exc}",
            exc_info=True,
            extra={
                'submission_id': submission_id,
                'retry_count': retry_count,
                'max_retries': self.max_retries
            }
        )

        # 如果达到最大重试次数，标记任务失败
        if retry_count >= self.max_retries:
            try:
                submission = Submission.objects.select_related(
                    'user', 'problem'
                ).get(id=submission_id)

                JudgingQueueStats.objects.create(
                    submission=submission,
                    status='failed',
                    error_message=f"任务执行失败: {str(exc)} (已重试{self.max_retries}次)"
                )

                submission.status = 'internal_error'
                submission.error = f"任务执行失败: {str(exc)}"
                submission.save()

            except Submission.DoesNotExist:
                pass

            logger.error(
                f"Max retries exceeded for submission {submission_id}, marking as failed",
                extra={'submission_id': submission_id}
            )
            return None

        # 重新抛出异常以触发 Celery 自动重试
        raise exc


@shared_task
def cleanup_old_queue_stats(days: int = 7):
    """
    清理旧的队列统计信息

    删除超过指定天数的已完成/失败/超时的队列记录
    每天执行一次
    """
    from .models import JudgingQueueStats
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    # 删除旧记录
    deleted_count = JudgingQueueStats.objects.filter(
        status__in=['success', 'failed', 'timeout'],
        created_at__lt=cutoff_date
    ).delete()[0]

    logger.info(
        f"Cleaned up {deleted_count} old queue statistics",
        extra={'days': days}
    )

    return deleted_count