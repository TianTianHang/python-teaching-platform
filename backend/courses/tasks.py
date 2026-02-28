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
            "Refreshed unlock snapshot for enrollment {enrollment_id}",
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
            "Enrollment {enrollment_id} no longer exists, skipping snapshot refresh",
            extra={'enrollment_id': enrollment_id}
        )
        return None
    except Exception as exc:
        logger.error(
            "Failed to refresh snapshot for enrollment {enrollment_id}: {exc}",
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
            "Cleaned up {count} orphaned snapshots (enrollment deleted)",
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
            "Triggered batch refresh for {count} stale snapshots",
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
        "Cleaned up {count} old snapshots",
        extra={'days': days}
    )

    return count