"""
Celery tasks for cache warming.

This module implements three warming strategies:
1. Startup warming: Warm core data on application startup
2. On-demand warming: Refresh expired data asynchronously
3. Scheduled warming: Periodic refresh of hot data
"""

import logging
import time
from typing import List, Dict, Any, Optional
from celery import shared_task
from django.core.cache import cache
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

# 用于防止重复预热任务的锁
WARMING_LOCK_PREFIX = "cache_warming_lock"
# 统计键前缀
WARMING_STATS_PREFIX = "cache_warming_stats"


class WarmingPriority:
    """缓存预热优先级定义"""

    # 高优先级：课程列表和详情
    HIGH = 1
    # 中优先级：章节和题目
    MEDIUM = 2
    # 低优先级：其他数据
    LOW = 3


def get_warming_lock_key(warming_type: str, identifier: str) -> str:
    """获取预热锁键"""
    return f"{WARMING_LOCK_PREFIX}:{warming_type}:{identifier}"


def get_warming_stats_key() -> str:
    """获取预热统计键"""
    return WARMING_STATS_PREFIX


def acquire_warming_lock(lock_key: str, timeout: int = 300) -> bool:
    """获取预热锁，防止重复预热

    Args:
        lock_key: 锁键
        timeout: 锁超时时间（秒）

    Returns:
        是否成功获取锁
    """
    redis_conn = get_redis_connection("default")
    # 使用 SET NX EX 命令实现分布式锁
    return redis_conn.set(lock_key, "1", nx=True, ex=timeout)


def release_warming_lock(lock_key: str):
    """释放预热锁"""
    redis_conn = get_redis_connection("default")
    redis_conn.delete(lock_key)


def record_warming_stats(warming_type: str, count: int, duration: float):
    """记录预热统计信息

    Args:
        warming_type: 预热类型 (startup, on_demand, scheduled)
        count: 预热的数据数量
        duration: 预热耗时（秒）
    """
    try:
        redis_conn = get_redis_connection("default")
        stats_key = get_warming_stats_key()

        pipe = redis_conn.pipeline()
        pipe.hincrby(stats_key, f"{warming_type}_count", count)
        pipe.hincrby(stats_key, f"{warming_type}_tasks", 1)
        pipe.hincrbyfloat(stats_key, f"{warming_type}_duration", duration)
        pipe.hset(stats_key, f"{warming_type}_last_run", time.time())
        pipe.expire(stats_key, 86400)  # 统计保留 24 小时
        pipe.execute()
    except Exception as e:
        logger.warning(f"Failed to record warming stats: {e}")


@shared_task(bind=True, max_retries=3)
def warm_startup_cache(self):
    """启动预热任务：预热核心数据

    在应用启动时触发，预热最常访问的数据：
    1. 课程列表
    2. 前 100 个课程的详情
    3. 每个课程的前 5 个章节
    4. 前 100 个热门题目
    """
    start_time = time.time()
    warmed_count = 0
    lock_key = get_warming_lock_key("startup", "global")

    if not acquire_warming_lock(lock_key, timeout=600):
        logger.info("Startup warming already in progress, skipping")
        return {"status": "skipped", "reason": "already_running"}

    try:
        logger.info("Starting startup cache warming...")

        # 1. 预热课程列表
        warmed_count += _warm_course_list()

        # 2. 预热热门课程详情
        warmed_count += _warm_popular_courses(limit=100)

        # 3. 预热每个课程的前几个章节
        warmed_count += _warm_course_chapters(course_limit=100, chapters_per_course=5)

        # 4. 预热热门题目
        warmed_count += _warm_popular_problems(limit=100)

        duration = time.time() - start_time
        record_warming_stats("startup", warmed_count, duration)

        logger.info(f"Startup warming completed: {warmed_count} items in {duration:.2f}s")
        return {"status": "success", "count": warmed_count, "duration": duration}

    except Exception as e:
        logger.error(f"Startup warming failed: {e}")
        raise self.retry(exc=e, countdown=60)
    finally:
        release_warming_lock(lock_key)


@shared_task(bind=True, max_retries=2)
def warm_on_demand_cache(self, cache_key: str, view_name: str, pk: Optional[int] = None):
    """按需预热任务：刷新指定的缓存

    当请求发现过期数据时触发，异步刷新该缓存。

    Args:
        cache_key: 需要预热的缓存键
        view_name: 视图名称
        pk: 对象主键（可选）
    """
    lock_key = get_warming_lock_key("on_demand", cache_key)

    if not acquire_warming_lock(lock_key, timeout=60):
        logger.debug(f"On-demand warming already in progress for {cache_key}")
        return {"status": "skipped", "reason": "already_running"}

    try:
        start_time = time.time()
        logger.debug(f"Starting on-demand warming for {cache_key}")

        # 根据视图名称预热相应数据
        warmed = _warm_by_view_name(view_name, pk)

        duration = time.time() - start_time
        record_warming_stats("on_demand", 1 if warmed else 0, duration)

        return {"status": "success", "warmed": warmed}

    except Exception as e:
        logger.warning(f"On-demand warming failed for {cache_key}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        release_warming_lock(lock_key)


@shared_task(bind=True)
def warm_scheduled_cache(self):
    """定时预热任务：刷新热点数据

    定期执行（如每小时），根据访问统计刷新热点数据。
    """
    start_time = time.time()
    warmed_count = 0
    lock_key = get_warming_lock_key("scheduled", "global")

    if not acquire_warming_lock(lock_key, timeout=600):
        logger.info("Scheduled warming already in progress, skipping")
        return {"status": "skipped", "reason": "already_running"}

    try:
        logger.info("Starting scheduled cache warming...")

        # 1. 刷新高频访问的课程
        warmed_count += _warm_high_priority_courses()

        # 2. 刷新高频访问的题目
        warmed_count += _warm_high_priority_problems()

        duration = time.time() - start_time
        record_warming_stats("scheduled", warmed_count, duration)

        logger.info(f"Scheduled warming completed: {warmed_count} items in {duration:.2f}s")
        return {"status": "success", "count": warmed_count, "duration": duration}

    except Exception as e:
        logger.error(f"Scheduled warming failed: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        release_warming_lock(lock_key)


# ============ 辅助函数 ============

def _warm_course_list() -> int:
    """预热课程列表"""
    try:
        from courses.models import Course
        from courses.serializers import CourseModelSerializer
        from common.utils.cache import get_cache_key, set_cache

        # 获取所有课程
        courses = Course.objects.all()[:50]
        serializer = CourseModelSerializer(courses, many=True)

        cache_key = get_cache_key(
            prefix="api",
            view_name="CourseViewSet",
            query_params={}
        )

        set_cache(cache_key, serializer.data, timeout=900)
        logger.debug(f"Warmed course list: {len(serializer.data)} items")
        return 1

    except Exception as e:
        logger.warning(f"Failed to warm course list: {e}")
        return 0


def _warm_popular_courses(limit: int = 100) -> int:
    """预热热门课程详情"""
    try:
        from courses.models import Course
        from courses.serializers import CourseModelSerializer
        from common.utils.cache import get_cache_key, set_cache

        # 获取课程
        courses = Course.objects.all()[:limit]
        count = 0

        for course in courses:
            cache_key = get_cache_key(
                prefix="api",
                view_name="CourseViewSet",
                pk=course.pk
            )
            serializer = CourseModelSerializer(course)
            set_cache(cache_key, serializer.data, timeout=900)
            count += 1

        logger.debug(f"Warmed {count} courses")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm popular courses: {e}")
        return 0


def _warm_course_chapters(course_limit: int = 100, chapters_per_course: int = 5) -> int:
    """预热课程章节"""
    try:
        from courses.models import Chapter
        from courses.serializers import ChapterSerializer
        from common.utils.cache import get_cache_key, set_cache

        courses = _get_popular_course_ids(course_limit)
        count = 0

        for course_id in courses:
            chapters = Chapter.objects.filter(course_id=course_id)[:chapters_per_course]

            for chapter in chapters:
                cache_key = get_cache_key(
                    prefix="api",
                    view_name="ChapterViewSet",
                    pk=chapter.pk,
                    parent_pks={"course_pk": course_id}
                )
                serializer = ChapterSerializer(chapter)
                set_cache(cache_key, serializer.data, timeout=900)
                count += 1

        logger.debug(f"Warmed {count} chapters for {len(courses)} courses")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm course chapters: {e}")
        return 0


def _warm_popular_problems(limit: int = 100) -> int:
    """预热热门题目"""
    try:
        from courses.models import Problem
        from courses.serializers import ProblemSerializer
        from common.utils.cache import get_cache_key, set_cache

        # 获取题目
        problems = Problem.objects.all()[:limit]
        count = 0

        for problem in problems:
            cache_key = get_cache_key(
                prefix="api",
                view_name="ProblemViewSet",
                pk=problem.pk
            )
            serializer = ProblemSerializer(problem)
            set_cache(cache_key, serializer.data, timeout=900)
            count += 1

        logger.debug(f"Warmed {count} problems")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm popular problems: {e}")
        return 0


def _warm_high_priority_courses() -> int:
    """刷新高优先级（高频访问）课程"""
    try:
        from common.utils.cache import AdaptiveTTLCalculator
        from courses.models import Course
        from courses.serializers import CourseModelSerializer
        from common.utils.cache import get_cache_key, set_cache

        count = 0

        # 查找命中率高的课程缓存统计
        courses = Course.objects.all()[:50]

        for course in courses:
            cache_key = get_cache_key(
                prefix="api",
                view_name="CourseViewSet",
                pk=course.pk
            )

            hit_rate = AdaptiveTTLCalculator.get_hit_rate(cache_key)

            # 如果命中率 > 30%，预热
            if hit_rate and hit_rate > 0.3:
                serializer = CourseModelSerializer(course)
                set_cache(cache_key, serializer.data, timeout=1800)
                count += 1

        logger.debug(f"Warmed {count} high priority courses")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm high priority courses: {e}")
        return 0


def _warm_high_priority_problems() -> int:
    """刷新高优先级（高频访问）题目"""
    try:
        from common.utils.cache import AdaptiveTTLCalculator
        from courses.models import Problem
        from courses.serializers import ProblemSerializer
        from common.utils.cache import get_cache_key, set_cache

        count = 0
        problems = Problem.objects.all()[:100]

        for problem in problems:
            cache_key = get_cache_key(
                prefix="api",
                view_name="ProblemViewSet",
                pk=problem.pk
            )

            hit_rate = AdaptiveTTLCalculator.get_hit_rate(cache_key)

            # 如果命中率 > 30%，预热
            if hit_rate and hit_rate > 0.3:
                serializer = ProblemSerializer(problem)
                set_cache(cache_key, serializer.data, timeout=1800)
                count += 1

        logger.debug(f"Warmed {count} high priority problems")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm high priority problems: {e}")
        return 0


def _get_popular_course_ids(limit: int) -> List[int]:
    """获取热门课程 ID 列表"""
    try:
        from courses.models import Course
        return list(Course.objects.all().values_list('id', flat=True)[:limit])
    except Exception:
        return []


def _warm_by_view_name(view_name: str, pk: Optional[int]) -> bool:
    """根据视图名称预热数据"""
    try:
        from common.utils.cache import get_cache_key, set_cache

        if view_name == "CourseViewSet" and pk:
            from courses.models import Course
            from courses.serializers import CourseModelSerializer

            course = Course.objects.filter(id=pk).first()
            if course:
                cache_key = get_cache_key(prefix="api", view_name=view_name, pk=pk)
                serializer = CourseModelSerializer(course)
                set_cache(cache_key, serializer.data, timeout=900)
                return True

        elif view_name == "ChapterViewSet" and pk:
            from courses.models import Chapter
            from courses.serializers import ChapterSerializer

            chapter = Chapter.objects.filter(id=pk).select_related('course').first()
            if chapter:
                cache_key = get_cache_key(
                    prefix="api",
                    view_name=view_name,
                    pk=pk,
                    parent_pks={"course_pk": chapter.course_id}
                )
                serializer = ChapterSerializer(chapter)
                set_cache(cache_key, serializer.data, timeout=900)
                return True

        elif view_name == "ProblemViewSet" and pk:
            from courses.models import Problem
            from courses.serializers import ProblemSerializer

            problem = Problem.objects.filter(id=pk).first()
            if problem:
                cache_key = get_cache_key(prefix="api", view_name=view_name, pk=pk)
                serializer = ProblemSerializer(problem)
                set_cache(cache_key, serializer.data, timeout=900)
                return True

        return False

    except Exception as e:
        logger.warning(f"Failed to warm by view_name {view_name}: {e}")
        return False
