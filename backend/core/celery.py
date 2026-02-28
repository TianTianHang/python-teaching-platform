import os
from celery.schedules import crontab

from celery import Celery


# 设置 Django 的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')


# 从 Django settings 中加载 CELERY_ 开头的配置
app.config_from_object('django.conf:settings', namespace='CELERY')


# 自动发现各 app 下的 tasks.py
app.autodiscover_tasks()

# Beat 调度配置
app.conf.beat_schedule = {
    'refresh-stale-chapter-unlock-snapshots': {
        'task': 'courses.tasks.scheduled_snapshot_refresh',
        'schedule': crontab(minute='*'),  # 每分钟执行
    },
    'cleanup-old-chapter-unlock-snapshots': {
        'task': 'courses.tasks.cleanup_old_snapshots',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨 2 点
    },
    'refresh-stale-problem-unlock-snapshots': {
        'task': 'courses.tasks.scheduled_problem_snapshot_refresh',
        'schedule': crontab(minute='*'),  # 每分钟执行
    },
    'cleanup-old-problem-unlock-snapshots': {
        'task': 'courses.tasks.cleanup_old_problem_snapshots',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨 3 点
    },
}

# 任务时间限制
app.conf.task_soft_time_limit = 300  # 5分钟软超时
app.conf.task_time_limit = 600  # 10分钟硬超时