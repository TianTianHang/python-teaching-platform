# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .views import ProblemViewSet
from .models import DiscussionReply, ProblemProgress
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