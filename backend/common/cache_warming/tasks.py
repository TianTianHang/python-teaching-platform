"""
Celery tasks for cache warming - Separated Cache GLOBAL Layer.

This module implements cache warming for the SeparatedCacheService GLOBAL layer:
- Startup warming: Warm GLOBAL data for chapters and problems on app startup
- On-demand warming: Refresh expired GLOBAL data asynchronously
- Scheduled warming: Periodic refresh of hot (high hit rate > 30%) data

Warming Scope:
- Startup: First 100 courses' chapter lists + first 1000 chapters' problem lists (10 problems each)
- Scheduled: High hit rate chapters and problems
- On-demand: Single chapter or problem when accessed

Cache Key Format: courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=X
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from celery import shared_task
from django.core.cache import cache
from django_redis import get_redis_connection

from common.utils.cache import get_standard_cache_key

logger = logging.getLogger(__name__)

WARMING_LOCK_PREFIX = "cache_warming_lock"
WARMING_STATS_PREFIX = "cache_warming_stats"


class WarmingPriority:
    """Cache warming priority definition"""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


def get_warming_lock_key(warming_type: str, identifier: str) -> str:
    """Get warming lock key"""
    return f"{WARMING_LOCK_PREFIX}:{warming_type}:{identifier}"


def get_warming_stats_key() -> str:
    """Get warming stats key"""
    return WARMING_STATS_PREFIX


def acquire_warming_lock(lock_key: str, timeout: int = 300) -> bool:
    """Acquire warming lock to prevent duplicate warming

    Args:
        lock_key: Lock key
        timeout: Lock timeout (seconds)

    Returns:
        Whether lock was acquired successfully
    """
    redis_conn = get_redis_connection("default")
    return redis_conn.set(lock_key, "1", nx=True, ex=timeout)


def release_warming_lock(lock_key: str):
    """Release warming lock"""
    redis_conn = get_redis_connection("default")
    redis_conn.delete(lock_key)


def record_warming_stats(warming_type: str, count: int, duration: float):
    """Record warming statistics

    Args:
        warming_type: Warming type (startup, on_demand, scheduled)
        count: Number of items warmed
        duration: Duration in seconds
    """
    try:
        redis_conn = get_redis_connection("default")
        stats_key = get_warming_stats_key()

        pipe = redis_conn.pipeline()
        pipe.hincrby(stats_key, f"{warming_type}_count", count)
        pipe.hincrby(stats_key, f"{warming_type}_tasks", 1)
        pipe.hincrbyfloat(stats_key, f"{warming_type}_duration", duration)
        pipe.hset(stats_key, f"{warming_type}_last_run", time.time())
        pipe.expire(stats_key, 86400)
        pipe.execute()
    except Exception as e:
        logger.warning(f"Failed to record warming stats: {e}")


DEFAULT_GLOBAL_TTL = 1800
DEFAULT_COURSE_TTL = 900


def _warm_courses_list(course_limit: int = 100) -> int:
    """Warm GLOBAL cache for course list

    Pre-warms course list cache using StandardCacheListMixin key format.

    Args:
        course_limit: Number of courses to process (default: 100)

    Returns:
        Number of course lists warmed
    """
    try:
        from courses.models import Course
        from courses.serializers import CourseModelSerializer

        courses = list(Course.objects.all()[:course_limit])

        if not courses:
            return 0

        serializer = CourseModelSerializer(courses, many=True)
        data = serializer.data

        cache_key = get_standard_cache_key(
            prefix="api",
            view_name="CourseViewSet",
            query_params={"page": "1"},
        )

        from common.utils.cache import set_cache

        set_cache(cache_key, data, DEFAULT_COURSE_TTL)

        logger.info(f"Warmed course list cache (page=1) with {len(courses)} courses")
        return 1

    except Exception as e:
        logger.error(f"Failed to warm course list: {e}")
        return 0


def _warm_courses_detail(course_limit: int = 100) -> int:
    """Warm GLOBAL cache for course detail views

    Pre-warms individual course detail cache using StandardCacheRetrieveMixin key format.

    Args:
        course_limit: Number of courses to process (default: 100)

    Returns:
        Number of course details warmed
    """
    try:
        from courses.models import Course
        from courses.serializers import CourseModelSerializer
        from common.utils.cache import set_cache

        courses = Course.objects.all()[:course_limit]

        count = 0
        redis_conn = get_redis_connection("default")
        pipe = redis_conn.pipeline()

        for course in courses:
            cache_key = get_standard_cache_key(
                prefix="api",
                view_name="CourseViewSet",
                pk=course.id,
            )
            serializer = CourseModelSerializer(course)
            pipe.set(
                cache_key,
                json.dumps(serializer.data, ensure_ascii=False, default=str),
                ex=DEFAULT_COURSE_TTL,
            )
            count += 1

        pipe.execute()
        logger.info(f"Warmed {count} course detail caches")
        return count

    except Exception as e:
        logger.error(f"Failed to warm course details: {e}")
        return 0


def _warm_chapters_global(course_limit: int = 100) -> int:
    """Warm GLOBAL cache for chapter lists

    Pre-warms chapter list cache for all chapters in the first N courses.
    Uses ChapterGlobalSerializer and SEPARATED:GLOBAL cache keys.

    Args:
        course_limit: Number of courses to process (default: 100)

    Returns:
        Number of chapters warmed
    """
    try:
        from courses.models import Chapter
        from courses.serializers import ChapterGlobalSerializer
        from common.utils.cache import get_standard_cache_key, set_cache
        from collections import defaultdict

        chapters = (
            Chapter.objects.select_related("course")
            .filter(course__id__isnull=False)
            .order_by("course__id", "order")[: course_limit * 30]
        )

        chapters_by_course = defaultdict(list)
        for chapter in chapters:
            chapters_by_course[chapter.course_id].append(chapter)

        count = 0
        redis_conn = get_redis_connection("default")
        pipe = redis_conn.pipeline()

        for course_pk, course_chapters in chapters_by_course.items():
            cache_key = get_standard_cache_key(
                prefix="courses",
                view_name="ChapterViewSet",
                parent_pks={"course_pk": course_pk},
                is_separated=True,
                separated_type="GLOBAL",
            )
            serializer = ChapterGlobalSerializer(course_chapters, many=True)
            pipe.set(
                cache_key,
                json.dumps(list(serializer.data), ensure_ascii=False, default=str),
                ex=DEFAULT_GLOBAL_TTL,
            )
            count += 1

        pipe.execute()
        logger.info(
            f"Warmed {count} chapter lists (GLOBAL layer) for {course_limit} courses"
        )
        return count

    except Exception as e:
        logger.warning(f"Failed to warm chapters global: {e}")
        return 0


def _warm_problems_global(
    chapter_limit: int = 1000, problems_per_chapter: int = 10
) -> int:
    """Warm GLOBAL cache for problem lists

    Pre-warms problem list cache for the first N chapters.
    Uses ProblemGlobalSerializer and SEPARATED:GLOBAL cache keys.

    Args:
        chapter_limit: Number of chapters to process (default: 1000)
        problems_per_chapter: Number of problems per chapter (default: 10)

    Returns:
        Number of problem lists warmed
    """
    try:
        from courses.models import Problem
        from courses.serializers import ProblemGlobalSerializer
        from common.utils.cache import get_standard_cache_key, set_cache

        chapters = (
            Problem.objects.filter(chapter__isnull=False)
            .values_list("chapter_id", flat=True)
            .distinct()[:chapter_limit]
        )

        count = 0
        redis_conn = get_redis_connection("default")
        pipe = redis_conn.pipeline()

        for chapter_pk in chapters:
            problems = Problem.objects.filter(chapter_id=chapter_pk).order_by("id")[
                :problems_per_chapter
            ]

            if not problems:
                continue

            cache_key = get_standard_cache_key(
                prefix="courses",
                view_name="ProblemViewSet",
                parent_pks={"chapter_pk": chapter_pk},
                is_separated=True,
                separated_type="GLOBAL",
            )
            serializer = ProblemGlobalSerializer(problems, many=True)
            pipe.set(
                cache_key,
                json.dumps(list(serializer.data), ensure_ascii=False, default=str),
                ex=DEFAULT_GLOBAL_TTL,
            )
            count += 1

        pipe.execute()
        logger.info(f"Warmed {count} problem lists (GLOBAL layer)")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm problems global: {e}")
        return 0


def _warm_high_priority_chapters_global() -> int:
    """Warm high hit-rate chapter GLOBAL caches

    Uses AdaptiveTTLCalculator.get_hit_rate() to identify chapters with >30% hit rate.

    Returns:
        Number of high-priority chapters warmed
    """
    try:
        from courses.models import Chapter
        from common.utils.cache import AdaptiveTTLCalculator
        from courses.serializers import ChapterGlobalSerializer
        from common.utils.cache import get_standard_cache_key

        chapters = Chapter.objects.select_related("course").all()[:50]

        count = 0
        redis_conn = get_redis_connection("default")
        pipe = redis_conn.pipeline()

        for chapter in chapters:
            cache_key = get_standard_cache_key(
                prefix="courses",
                view_name="ChapterViewSet",
                pk=chapter.pk,
                parent_pks={"course_pk": chapter.course_id},
                is_separated=True,
                separated_type="GLOBAL",
            )

            hit_rate = AdaptiveTTLCalculator.get_hit_rate(cache_key)

            if hit_rate and hit_rate > 0.3:
                serializer = ChapterGlobalSerializer(chapter)
                pipe.set(
                    cache_key,
                    json.dumps(dict(serializer.data), ensure_ascii=False, default=str),
                    ex=DEFAULT_GLOBAL_TTL,
                )
                count += 1

        pipe.execute()
        logger.info(f"Warmed {count} high-priority chapters (GLOBAL layer)")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm high priority chapters: {e}")
        return 0


def _warm_high_priority_problems_global() -> int:
    """Warm high hit-rate problem GLOBAL caches

    Uses AdaptiveTTLCalculator.get_hit_rate() to identify problems with >30% hit rate.

    Returns:
        Number of high-priority problem lists warmed
    """
    try:
        from courses.models import Problem
        from common.utils.cache import AdaptiveTTLCalculator
        from courses.serializers import ProblemGlobalSerializer
        from common.utils.cache import get_standard_cache_key

        chapters = (
            Problem.objects.filter(chapter__isnull=False)
            .values_list("chapter_id", flat=True)
            .distinct()[:100]
        )

        count = 0
        redis_conn = get_redis_connection("default")
        pipe = redis_conn.pipeline()

        for chapter_pk in chapters:
            course_pk = Problem.objects.filter(chapter_id=chapter_pk).first()
            if course_pk:
                course_pk = course_pk.chapter.course_id
            else:
                continue

            cache_key = get_standard_cache_key(
                prefix="courses",
                view_name="ProblemViewSet",
                parent_pks={"chapter_pk": chapter_pk, "course_pk": course_pk},
                is_separated=True,
                separated_type="GLOBAL",
            )

            hit_rate = AdaptiveTTLCalculator.get_hit_rate(cache_key)

            if hit_rate and hit_rate > 0.3:
                problems = Problem.objects.filter(chapter_id=chapter_pk).order_by("id")[
                    :10
                ]
                serializer = ProblemGlobalSerializer(problems, many=True)
                pipe.set(
                    cache_key,
                    json.dumps(list(serializer.data), ensure_ascii=False, default=str),
                    ex=DEFAULT_GLOBAL_TTL,
                )
                count += 1

        pipe.execute()
        logger.info(f"Warmed {count} high-priority problem lists (GLOBAL layer)")
        return count

    except Exception as e:
        logger.warning(f"Failed to warm high priority problems: {e}")
        return 0


def _warm_chapter_global_by_pk(chapter_pk: int, course_pk: int) -> bool:
    """On-demand warm a single chapter's GLOBAL cache

    Args:
        chapter_pk: Chapter primary key
        course_pk: Course primary key (parent)

    Returns:
        Whether warming was successful
    """
    try:
        from courses.models import Chapter
        from courses.serializers import ChapterGlobalSerializer
        from common.utils.cache import get_standard_cache_key, set_cache

        chapter = Chapter.objects.filter(pk=chapter_pk, course_id=course_pk).first()
        if not chapter:
            logger.warning(f"Chapter {chapter_pk} not found")
            return False

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            pk=chapter_pk,
            parent_pks={"course_pk": course_pk},
            is_separated=True,
            separated_type="GLOBAL",
        )

        serializer = ChapterGlobalSerializer(chapter)
        set_cache(cache_key, serializer.data, timeout=DEFAULT_GLOBAL_TTL)
        logger.debug(f"Warmed chapter {chapter_pk} (GLOBAL layer)")
        return True

    except Exception as e:
        logger.warning(f"Failed to warm chapter {chapter_pk}: {e}")
        return False


def _warm_problems_global_by_chapter(
    chapter_pk: int, course_pk: int, limit: int = 10
) -> bool:
    """On-demand warm a chapter's problem list GLOBAL cache

    Args:
        chapter_pk: Chapter primary key
        course_pk: Course primary key (parent)
        limit: Number of problems to warm (default: 10)

    Returns:
        Whether warming was successful
    """
    try:
        from courses.models import Problem
        from courses.serializers import ProblemGlobalSerializer
        from common.utils.cache import get_standard_cache_key, set_cache

        problems = Problem.objects.filter(chapter_id=chapter_pk).order_by("id")[:limit]

        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ProblemViewSet",
            parent_pks={"chapter_pk": chapter_pk},
            is_separated=True,
            separated_type="GLOBAL",
        )

        serializer = ProblemGlobalSerializer(problems, many=True)
        set_cache(cache_key, serializer.data, timeout=DEFAULT_GLOBAL_TTL)
        logger.debug(f"Warmed problem list for chapter {chapter_pk} (GLOBAL layer)")
        return True

    except Exception as e:
        logger.warning(f"Failed to warm problems for chapter {chapter_pk}: {e}")
        return False


@shared_task(bind=True, max_retries=3, time_limit=600)
def warm_separated_global_startup(self):
    """Startup warming: Warm GLOBAL layer cache for courses, chapters and problems

    Called on application startup:
    1. Warm course list and details for first 100 courses
    2. Warm chapter lists for first 100 courses
    3. Warm problem lists for first 1000 chapters (10 problems each)

    Timeout: 10 minutes
    Uses distributed lock to prevent duplicate execution
    """
    start_time = time.time()
    warmed_count = 0
    lock_key = get_warming_lock_key("startup", "global_separated")

    if not acquire_warming_lock(lock_key, timeout=600):
        logger.info("Startup warming (separated global) already in progress, skipping")
        return {"status": "skipped", "reason": "already_running"}

    try:
        logger.info("Starting separated global cache warming (startup)...")

        warmed_count += _warm_courses_list(course_limit=100)

        warmed_count += _warm_courses_detail(course_limit=100)

        warmed_count += _warm_chapters_global(course_limit=100)

        warmed_count += _warm_problems_global(
            chapter_limit=1000, problems_per_chapter=10
        )

        duration = time.time() - start_time
        record_warming_stats("startup", warmed_count, duration)

        logger.info(
            f"Startup warming (separated global) completed: {warmed_count} items in {duration:.2f}s"
        )
        return {"status": "success", "count": warmed_count, "duration": duration}

    except Exception as e:
        logger.error(f"Startup warming (separated global) failed: {e}")
        raise self.retry(exc=e, countdown=60)
    finally:
        release_warming_lock(lock_key)


@shared_task(bind=True, max_retries=3)
def warm_separated_global_scheduled(self):
    """Scheduled warming: Refresh high hit-rate GLOBAL layer cache

    Runs hourly via Celery Beat:
    1. Refresh chapter lists with hit rate > 30%
    2. Refresh problem lists with hit rate > 30%

    Uses distributed lock to prevent duplicate execution
    """
    start_time = time.time()
    warmed_count = 0
    lock_key = get_warming_lock_key("scheduled", "global_separated")

    if not acquire_warming_lock(lock_key, timeout=600):
        logger.info(
            "Scheduled warming (separated global) already in progress, skipping"
        )
        return {"status": "skipped", "reason": "already_running"}

    try:
        logger.info("Starting separated global cache warming (scheduled)...")

        warmed_count += _warm_high_priority_chapters_global()

        warmed_count += _warm_high_priority_problems_global()

        duration = time.time() - start_time
        record_warming_stats("scheduled", warmed_count, duration)

        logger.info(
            f"Scheduled warming (separated global) completed: {warmed_count} items in {duration:.2f}s"
        )
        return {"status": "success", "count": warmed_count, "duration": duration}

    except Exception as e:
        logger.error(f"Scheduled warming (separated global) failed: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        release_warming_lock(lock_key)


@shared_task(bind=True, max_retries=2)
def warm_separated_global_on_demand(
    self, cache_key: str, view_name: str, pk: int, parent_pks: dict
):
    """On-demand warming: Warm specific GLOBAL layer cache

    Triggered when a cache miss occurs, asynchronously warms the cache.

    Args:
        cache_key: The cache key that was accessed
        view_name: ViewSet name (ChapterViewSet, ProblemViewSet)
        pk: Primary key of the entity
        parent_pks: Parent keys (e.g., course_pk, chapter_pk)
    """
    lock_key = get_warming_lock_key("on_demand", f"{view_name}_{pk}")

    if not acquire_warming_lock(lock_key, timeout=60):
        logger.debug(f"On-demand warming already in progress for {cache_key}")
        return {"status": "skipped", "reason": "already_running"}

    try:
        start_time = time.time()
        logger.debug(f"Starting on-demand warming for {cache_key}")

        warmed = False

        if view_name == "ChapterViewSet" and pk:
            course_pk = parent_pks.get("course_pk")
            if course_pk:
                warmed = _warm_chapter_global_by_pk(pk, course_pk)

        elif view_name == "ProblemViewSet" and pk:
            chapter_pk = parent_pks.get("chapter_pk")
            course_pk = parent_pks.get("course_pk")
            if chapter_pk and course_pk:
                warmed = _warm_problems_global_by_chapter(chapter_pk, course_pk)

        duration = time.time() - start_time
        record_warming_stats("on_demand", 1 if warmed else 0, duration)

        return {"status": "success", "warmed": warmed}

    except Exception as e:
        logger.warning(f"On-demand warming failed for {cache_key}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        release_warming_lock(lock_key)


@shared_task
def cache_performance_summary():
    """Cache performance summary task

    Periodically generates cache performance summary logs:
    - Global statistics (total requests, hit rate, avg duration)
    - Per-endpoint statistics
    - Top 5 slowest endpoints
    - Top 5 endpoints with lowest hit rates
    - Active alerts (low hit rate, high penetration, slow operations)

    This task runs every 60 seconds via Celery Beat.
    """
    try:
        from common.utils.logging import _cache_performance_logger

        _cache_performance_logger.log_performance_summary()

        _cache_performance_logger.reset_stats()

        logger.debug("Cache performance summary logged and stats reset")

    except Exception as e:
        logger.error(f"Failed to generate cache performance summary: {e}")
