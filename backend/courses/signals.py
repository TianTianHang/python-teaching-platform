# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DiscussionReply


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