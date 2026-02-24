import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        import courses.signals  # 替换为你的实际路径
        # 触发启动预热任务（异步执行，不阻塞启动）
        try:
            from common.cache_warming.tasks import warm_startup_cache
            warm_startup_cache.delay()
            logger.info("Startup cache warming task queued")
        except Exception as e:
            logger.warning(f"Failed to queue startup warming task: {e}")