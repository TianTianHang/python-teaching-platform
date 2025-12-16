import os

from celery import Celery


# 设置 Django 的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')


# 从 Django settings 中加载 CELERY_ 开头的配置
app.config_from_object('django.conf:settings', namespace='CELERY')


# 自动发现各 app 下的 tasks.py
app.autodiscover_tasks()