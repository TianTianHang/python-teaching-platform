# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .views import ProblemViewSet, EnrollmentViewSet
from .models import DiscussionReply, ProblemProgress, Enrollment
from common.utils.cache import delete_cache_pattern, get_cache_key


@receiver([post_save, post_delete], sender=DiscussionReply)
def update_thread_reply_count(sender, instance, **kwargs):
    """
    当 DiscussionReply 被创建或删除时，更新其所属 DiscussionThread 的 reply_count。
    """
    thread = instance.thread

    # 使用数据库 COUNT 保证准确性（避免并发问题）
    thread.reply_count = thread.replies.count()

    # 同时更新 last_activity_at（可选但推荐）
    from django.utils import timezone
    thread.last_activity_at = timezone.now()

    # 使用 update_fields 避免触发 thread 的 save 信号（如果有的话）
    thread.save(update_fields=['reply_count', 'last_activity_at'])


@receiver([post_save, post_delete], sender=ProblemProgress)
def invalidate_problem_progress_cache(sender, instance, **kwargs):
    """
    当 ProblemProgress 模型被保存或删除时，清除相关的缓存
    """
    # 清除与该用户相关的所有问题列表缓存
    base_key = get_cache_key(
        prefix=ProblemViewSet.cache_prefix,
        view_name=ProblemViewSet.__name__  # ✅ 正确获取类名
    )
    # print("Invalidating cache with base key:", base_key)
    delete_cache_pattern(f"{base_key}:*")


# 添加必要的导入
from django.db.models import Sum
from django.core.cache import cache
from django.utils import timezone
from .models import ExamProblem
from .views import ExamViewSet


@receiver(post_save, sender=ExamProblem)
def update_exam_total_score_on_save(sender, instance, created, **kwargs):
    """
    当 ExamProblem 被创建或更新时，自动更新关联 Exam 的 total_score。
    通过 _skip_exam_problem_signals 标志避免 Exam 创建时的多次触发。
    """
    # 检查是否应该跳过信号（Exam 创建时）
    if hasattr(instance.exam, '_skip_exam_problem_signals') and instance.exam._skip_exam_problem_signals:
        return

    _update_exam_total_score(instance)


@receiver(post_delete, sender=ExamProblem)
def update_exam_total_score_on_delete(sender, instance, **kwargs):
    """
    当 ExamProblem 被删除时，自动更新关联 Exam 的 total_score。
    """
    # 注意：删除操作通常不会在 Exam 创建时发生，所以不需要检查标志
    _update_exam_total_score(instance)


def _update_exam_total_score(exam_problem_instance):
    """
    更新 Exam 的 total_score 的辅助函数
    """
    try:
        # 1. 获取关联的 Exam 对象
        exam = exam_problem_instance.exam

        # 2. 使用数据库聚合计算总分（保证并发安全）
        result = exam.exam_problems.aggregate(total_score=Sum('score'))
        new_total_score = result['total_score'] or 0  # 处理 None 情况（无题目时）

        # 3. 更新 total_score 和 updated_at
        # updated_at 字段不是 auto_now 更新的，需要显式指定
        exam.total_score = new_total_score
        if exam.passing_score > new_total_score:
            exam.passing_score = int(new_total_score*0.6)# 确保及格分不超过总分
        exam.updated_at = timezone.now()
        exam.save(update_fields=['total_score', 'updated_at'])

        # 4. 清除缓存
        # 4a. 清除该 Exam 的详情缓存
        cache_key = get_cache_key(
            prefix=ExamViewSet.cache_prefix,
            view_name=ExamViewSet.__name__,
            pk=exam.pk
        )
        cache.delete(cache_key)

        # 4b. 清除该 Exam 所属课程的列表缓存
        base_key = get_cache_key(
            prefix=ExamViewSet.cache_prefix,
            view_name=ExamViewSet.__name__
        )
        delete_cache_pattern(f"{base_key}:*")

    except Exception:
        # Edge case: Exam 被删除（虽然 CASCADE 会先删除 ExamProblem）
        # 使用 broad exception to catch any unexpected issues
        pass


@receiver(post_save, sender=Enrollment)
def invalidate_enrollment_cache_on_create(sender, instance, created, **kwargs):
    """
    当 Enrollment 被创建时，清除 EnrollmentViewSet 的所有列表缓存。

    这解决了 CourseViewSet.enroll() 创建 Enrollment 后，
    EnrollmentViewSet 缓存未失效导致前端仍显示空列表的问题。

    无论通过何种方式创建 Enrollment（ViewSet、信号、管理命令），
    都会自动清除缓存，确保数据一致性。
    """
    if created:
        # 清除 EnrollmentViewSet 的所有列表缓存
        base_key = get_cache_key(
            prefix=EnrollmentViewSet.cache_prefix,
            view_name=EnrollmentViewSet.__name__
        )
        delete_cache_pattern(f"{base_key}:*")