import logging
from typing import Dict, Any, Optional
from django.core.cache import cache
from .judge_backend.Judge0Backend import Judge0Backend
from .judge_backend.CodeJudgingBackend import CodeJudgingBackend
from .models import (
    Submission,
    Enrollment,
    Course,
    Chapter,
    CourseUnlockSnapshot,
    ProblemUnlockSnapshot,
    JudgingQueueStats,
)
from common.decorators.logging_decorators import log_execution_time
from common.services import BusinessCacheService
from common.utils.cache import get_standard_cache_key, CacheInvalidator

logger = logging.getLogger(__name__)


def generate_judge0_code(user_code: str, solve_func: str, language: str) -> str:
    """
    将用户实现的函数代码包装成完整的可执行程序
    user_code: 用户提交的函数定义（字符串）
    """
    template = {
        "python": """import sys
import json

{user_code}

if __name__ == "__main__":
    input_data = sys.stdin.read().strip()
    if not input_data:
        sys.exit(0)
    try:
        args = json.loads(input_data)
    except json.JSONDecodeError:
        # 如果不是 JSON，当作单行字符串处理（兼容简单题目）
        args = input_data.split(", ")

    if isinstance(args, list):
        result = {solve_func}(*args)
    elif isinstance(args, dict):
        result = {solve_func}(**args)
    else:
        result = {solve_func}(args)

    if isinstance(result, (dict, list, tuple, bool)) or result is None:
        print(json.dumps(result))
    else:
        print(result)
"""
    }

    return template[language].format(
        user_code=user_code.strip(), solve_func=solve_func.strip()
    )


class CodeExecutorService:
    """
    Service class to handle code execution and submission management.
    Uses a pluggable judging backend (e.g., Judge0).

    Supports both synchronous and asynchronous code execution modes.
    """

    def __init__(self, backend: Optional[CodeJudgingBackend] = None):
        """
        Initialize with a judging backend. Defaults to Judge0Backend if none provided.
        """
        self.backend = backend or Judge0Backend()

    def _map_status_id(self, status_id: int) -> str:
        """
        Map standardized status ID to human-readable status string.
        """
        mapping = {
            1: "pending",
            2: "judging",
            3: "accepted",
            4: "wrong_answer",
            5: "time_limit_exceeded",
            6: "memory_limit_exceeded",
            7: "runtime_error",
            8: "compilation_error",
        }
        return mapping.get(status_id, "internal_error")

    def _update_submission_with_result(
        self,
        submission: Submission,
        final_status: str,
        output: str,
        error: str,
        execution_time_ms: Optional[float],
        memory_used_mb: Optional[float],
    ):
        """
        Update the submission record in a consistent way.
        """
        submission.status = final_status
        submission.output = output
        submission.error = error
        submission.execution_time = execution_time_ms
        submission.memory_used = memory_used_mb
        submission.save(update_fields=[
            'status', 'output', 'error', 'execution_time', 'memory_used'
        ])

    def _execute_test_cases_internal(
        self,
        submission: Submission,
        problem,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Internal method to execute test cases for a submission.

        This is the core execution logic shared by both sync and async modes.

        Args:
            submission: The submission record (must be saved)
            problem: The problem being solved
            code: User's code
            language: Programming language

        Returns:
            Dict containing:
                - success: bool
                - status: str (final status)
                - output: str
                - error: str
                - execution_time_ms: Optional[float]
                - memory_used_mb: Optional[float]
                - test_cases_count: int
                - all_passed: bool
        """
        logger.info(
            "Code execution started",
            extra={
                "submission_id": submission.id,
                "user_id": submission.user_id,
                "problem_id": problem.id,
                "language": language,
                "code_length": len(code),
            },
        )

        try:
            algorithm_problem = problem.algorithm_info
            test_cases = algorithm_problem.test_cases.all()

            if not test_cases.exists():
                return {
                    "success": False,
                    "status": "compilation_error",
                    "output": "",
                    "error": "No test cases available for this problem",
                    "execution_time_ms": None,
                    "memory_used_mb": None,
                    "test_cases_count": 0,
                    "all_passed": False,
                }

            language_id = self.backend.get_language_id(language)
            solve_func = algorithm_problem.solution_name.get(language, "solve")

            all_passed = True
            max_time_ms = 0.0
            max_memory_mb = 0.0
            final_output = ""
            final_error = ""

            for test_case in test_cases:
                # Generate full executable code
                exec_code = generate_judge0_code(
                    user_code=code.strip(), solve_func=solve_func, language=language
                )

                # Submit to judging backend
                logger.debug(
                    f"Running test case {test_case.id}",
                    extra={
                        "submission_id": submission.id,
                        "test_case_id": test_case.id,
                        "time_limit": algorithm_problem.time_limit,
                        "memory_limit": algorithm_problem.memory_limit,
                    },
                )

                submit_resp = self.backend.submit_code(
                    source_code=exec_code,
                    language_id=language_id,
                    stdin=test_case.input_data,
                    expected_output=test_case.expected_output,
                    time_limit_ms=algorithm_problem.time_limit,  # ms
                    memory_limit_mb=algorithm_problem.memory_limit,  # MB
                )

                # Wait for result
                result = self.backend.get_result(submit_resp["token"], timeout_sec=30)

                status_id = result["status_id"]
                stdout = result["stdout"] or ""
                stderr = result["stderr"] or ""
                time_ms = result["time"]  # already in ms
                memory_mb = result["memory"]  # already in MB

                # Accumulate output/error for debugging
                final_output += f"Test case {test_case.id}: {stdout}\n"
                if stderr:
                    final_error += f"Test case {test_case.id} error: {stderr}\n"

                # Update max resources
                if time_ms is not None:
                    max_time_ms = max(max_time_ms, time_ms)
                if memory_mb is not None:
                    max_memory_mb = max(max_memory_mb, memory_mb)

                # Log test case result
                test_status = self._map_status_id(status_id)
                logger.info(
                    f"Test case {test_case.id} completed",
                    extra={
                        "submission_id": submission.id,
                        "test_case_id": test_case.id,
                        "status": test_status,
                        "execution_time_ms": time_ms,
                        "memory_used_mb": memory_mb,
                    },
                )

                # Check if this test case failed
                if status_id != 3:  # Not accepted
                    all_passed = False
                    final_status = self._map_status_id(status_id)
                    # Optionally break on first failure, or continue to collect all results
                    # Here we continue to run all test cases
                else:
                    final_status = "accepted"

            # Finalize submission status
            final_status = "accepted" if all_passed else final_status

            logger.info(
                "Code execution completed",
                extra={
                    "submission_id": submission.id,
                    "status": final_status,
                    "execution_time_ms": max_time_ms if max_time_ms > 0 else None,
                    "memory_used_mb": max_memory_mb if max_memory_mb > 0 else None,
                    "test_cases_count": test_cases.count(),
                    "all_passed": all_passed,
                },
            )

            return {
                "success": True,
                "status": final_status,
                "output": final_output.rstrip(),
                "error": final_error.rstrip(),
                "execution_time_ms": max_time_ms if max_time_ms > 0 else None,
                "memory_used_mb": max_memory_mb if max_memory_mb > 0 else None,
                "test_cases_count": test_cases.count(),
                "all_passed": all_passed,
            }

        except Exception as e:
            logger.error(
                f"Code execution failed",
                extra={
                    "submission_id": submission.id,
                    "error": str(e),
                },
                exc_info=True,
            )

            return {
                "success": False,
                "status": "internal_error",
                "output": "",
                "error": str(e),
                "execution_time_ms": None,
                "memory_used_mb": None,
                "test_cases_count": 0,
                "all_passed": False,
            }

    @log_execution_time(threshold_ms=5000)
    def run_all_test_cases(
        self, user, problem, code: str, language: str = "python"
    ) -> Submission:
        """
        Run submitted code against all test cases of a problem.

        This is the synchronous execution mode for backward compatibility.
        It creates a new submission and executes all test cases synchronously.

        Args:
            user: The user submitting the code
            problem: The problem to solve
            code: User's code
            language: Programming language (default: "python")

        Returns:
            Submission: The submission record with results
        """
        logger.info(
            "Synchronous code execution started",
            extra={
                "user_id": user.id,
                "problem_id": problem.id,
                "language": language,
                "code_length": len(code),
            },
        )

        submission = Submission.objects.create(
            user=user, problem=problem, code=code, language=language, status="pending"
        )

        # Execute test cases using internal method
        result = self._execute_test_cases_internal(
            submission=submission,
            problem=problem,
            code=code,
            language=language,
        )

        # Update submission with results
        self._update_submission_with_result(
            submission=submission,
            final_status=result["status"],
            output=result["output"],
            error=result["error"],
            execution_time_ms=result["execution_time_ms"],
            memory_used_mb=result["memory_used_mb"],
        )

        return submission

    def run_all_test_cases_async(
        self,
        submission: Submission,
        problem,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Run submitted code against all test cases in asynchronous mode.

        This method is designed to be called from Celery tasks.
        It updates the JudgingQueueStats with timing information.

        Args:
            submission: The submission record (must be saved with queue_stats)
            problem: The problem being solved
            code: User's code
            language: Programming language

        Returns:
            Dict containing execution results and timing information
        """
        from django.utils import timezone

        logger.info(
            "Asynchronous code execution started",
            extra={
                "submission_id": submission.id,
                "user_id": submission.user_id,
                "problem_id": problem.id,
                "language": language,
            },
        )

        queue_stats = None
        try:
            # Get queue stats
            queue_stats = submission.queue_stats
        except JudgingQueueStats.DoesNotExist:
            logger.error(
                f"Queue stats not found for submission {submission.id}",
                extra={"submission_id": submission.id},
            )
            # Update submission to failed state
            self._update_submission_with_result(
                submission=submission,
                final_status="internal_error",
                output="",
                error="Queue stats not found",
                execution_time_ms=None,
                memory_used_mb=None,
            )
            return {
                "success": False,
                "error": "Queue stats not found",
                "execution_seconds": 0,
            }

        # Mark as started and update timing
        now = timezone.now()
        queue_stats.status = "started"
        queue_stats.started_at = now

        # Calculate actual wait time
        if queue_stats.created_at:
            wait_seconds = int((now - queue_stats.created_at).total_seconds())
            queue_stats.queue_wait_seconds = wait_seconds

        queue_stats.save()

        # Execute test cases using internal method
        result = self._execute_test_cases_internal(
            submission=submission,
            problem=problem,
            code=code,
            language=language,
        )

        # Calculate execution time
        completed_at = timezone.now()
        execution_seconds = int((completed_at - now).total_seconds())

        # Update queue stats with final status
        queue_stats.completed_at = completed_at
        queue_stats.execution_seconds = execution_seconds

        if result["success"]:
            queue_stats.status = "success"
        else:
            queue_stats.status = "failed"
            queue_stats.error_message = result["error"][:1000]  # Limit error message length

        queue_stats.save()

        # Update submission with results
        self._update_submission_with_result(
            submission=submission,
            final_status=result["status"],
            output=result["output"],
            error=result["error"],
            execution_time_ms=result["execution_time_ms"],
            memory_used_mb=result["memory_used_mb"],
        )

        logger.info(
            "Asynchronous code execution completed",
            extra={
                "submission_id": submission.id,
                "status": result["status"],
                "execution_seconds": execution_seconds,
                "queue_wait_seconds": queue_stats.queue_wait_seconds,
                "test_cases_count": result["test_cases_count"],
                "all_passed": result["all_passed"],
            },
        )

        return {
            "success": result["success"],
            "status": result["status"],
            "execution_seconds": execution_seconds,
            "queue_wait_seconds": queue_stats.queue_wait_seconds,
        }

    @log_execution_time(threshold_ms=3000)
    def run_freely(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute arbitrary user code without test cases (e.g., "Run Code" feature).
        Returns standardized result dict.
        """
        logger.info(
            "Free code execution started",
            extra={"language": language, "code_length": len(code)},
        )

        try:
            language_id = self.backend.get_language_id(language)

            submit_resp = self.backend.submit_code(
                source_code=code,
                language_id=language_id,
                stdin="",
                time_limit_ms=2000,  # 2 seconds
                memory_limit_mb=128,  # 128 MB
            )

            result = self.backend.get_result(submit_resp["token"], timeout_sec=30)

            final_result = {
                "status": self._map_status_id(result["status_id"]),
                "stdout": result["stdout"] or "",
                "stderr": result["stderr"] or "",
                "execution_time": result["time"],  # ms
                "memory_used": result["memory"],  # MB
            }

            logger.info(
                "Free code execution completed",
                extra={
                    "status": final_result["status"],
                    "execution_time": final_result["execution_time"],
                    "memory_used": final_result["memory_used"],
                },
            )

            return final_result

        except Exception as e:
            logger.error(
                f"Free code execution failed",
                extra={"language": language, "error": str(e)},
                exc_info=True,
            )

            return {
                "status": "internal_error",
                "stdout": "",
                "stderr": str(e),
                "execution_time": None,
                "memory_used": None,
            }


class ChapterUnlockService:
    """
    章节解锁服务
    处理章节解锁状态的检查和查询
    """

    CACHE_TIMEOUT = 300  # 5分钟缓存

    @classmethod
    def _invalidate_cache(cls, chapter_id, enrollment_id=None, user_id=None):
        """
        使缓存失效（使用 CacheInvalidator）
        """
        if enrollment_id:
            # 特定 enrollment 的缓存
            CacheInvalidator.invalidate_viewset_list(
                prefix="courses",
                view_name="ChapterUnlockService",
                parent_pks={"chapter_pk": chapter_id, "enrollment_pk": enrollment_id},
            )
        else:
            # 所有 enrollment 的缓存
            CacheInvalidator.invalidate_viewset_list(
                prefix="courses",
                view_name="ChapterUnlockService",
                parent_pks={"chapter_pk": chapter_id},
            )

    @staticmethod
    def _compute_unlock_status(chapter, enrollment):
        """
        计算章节解锁状态（纯业务逻辑，无缓存）

        Returns:
            bool: 是否已解锁
        """
        if not hasattr(chapter, "unlock_condition") or chapter.unlock_condition is None:
            return True

        condition = chapter.unlock_condition
        unlock_type = condition.unlock_condition_type

        # 检查前置章节（仅当类型为 prerequisite 或 all）
        if (
            unlock_type in ("prerequisite", "all")
            and condition.prerequisite_chapters.exists()
        ):
            from .models import ChapterProgress

            prerequisite_ids = list(
                condition.prerequisite_chapters.values_list("id", flat=True)
            )
            completed_count = ChapterProgress.objects.filter(
                enrollment=enrollment, chapter_id__in=prerequisite_ids, completed=True
            ).count()

            if completed_count != len(prerequisite_ids):
                return False

        # 检查解锁日期（仅当类型为 date 或 all）
        if unlock_type in ("date", "all") and condition.unlock_date:
            from django.utils import timezone

            if timezone.now() < condition.unlock_date:
                return False

        return True

    @classmethod
    def is_unlocked(cls, chapter, enrollment):
        """
        检查章节对指定用户是否已解锁

        使用 BusinessCacheService 缓存解锁状态
        """
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={"chapter_pk": chapter.id, "enrollment_pk": enrollment.id},
            query_params={"type": "UNLOCK"},
        )

        result = BusinessCacheService.cache_result(
            cache_key=cache_key,
            fetcher=lambda: cls._compute_unlock_status(chapter, enrollment),
            timeout=cls.CACHE_TIMEOUT,
        )

        return result

    @staticmethod
    def _compute_unlock_status_detail(chapter, enrollment):
        """
        计算章节解锁状态详情（纯业务逻辑，无缓存）

        Returns:
            dict: 包含解锁状态详情的字典
        """
        from .models import ChapterProgress
        from django.utils import timezone

        # 如果没有解锁条件，返回已解锁
        if not hasattr(chapter, "unlock_condition") or chapter.unlock_condition is None:
            return {
                "is_locked": False,
                "reason": None,
                "prerequisite_progress": None,
                "unlock_date": None,
                "time_until_unlock": None,
                "chapter": {
                    "id": chapter.id,
                    "title": chapter.title,
                    "order": chapter.order,
                    "course_title": chapter.course.title,
                },
            }

        condition = chapter.unlock_condition
        unlock_type = condition.unlock_condition_type

        result = {
            "is_locked": False,
            "reason": None,
            "prerequisite_progress": None,
            "unlock_date": condition.unlock_date,
            "time_until_unlock": None,
            "chapter": {
                "id": chapter.id,
                "title": chapter.title,
                "order": chapter.order,
                "course_title": chapter.course.title,
            },
        }

        # 检查前置章节
        if (
            unlock_type in ("prerequisite", "all")
            and condition.prerequisite_chapters.exists()
        ):
            prerequisite_ids = list(
                condition.prerequisite_chapters.values_list("id", flat=True)
            )
            completed_prerequisites = set(
                ChapterProgress.objects.filter(
                    enrollment=enrollment,
                    chapter_id__in=prerequisite_ids,
                    completed=True,
                ).values_list("chapter_id", flat=True)
            )

            remaining_prerequisites = [
                {
                    "id": prereq.id,
                    "title": prereq.title,
                    "order": prereq.order,
                }
                for prereq in condition.prerequisite_chapters.all()
                if prereq.id not in completed_prerequisites
            ]

            result["prerequisite_progress"] = {
                "total": len(prerequisite_ids),
                "completed": len(completed_prerequisites),
                "remaining": remaining_prerequisites,
            }

            if len(completed_prerequisites) < len(prerequisite_ids):
                result["is_locked"] = True
                result["reason"] = "prerequisite"

        # 检查解锁日期
        if unlock_type in ("date", "all") and condition.unlock_date:
            now = timezone.now()
            if now < condition.unlock_date:
                result["is_locked"] = True
                if result["reason"] is None:
                    result["reason"] = "date"
                elif result["reason"] == "prerequisite":
                    result["reason"] = "both"

                # 计算剩余时间
                delta = condition.unlock_date - now
                result["time_until_unlock"] = {
                    "days": delta.days,
                    "hours": delta.seconds // 3600,
                    "minutes": (delta.seconds % 3600) // 60,
                }

        return result

    @classmethod
    def get_unlock_status(cls, chapter, enrollment):
        """
        获取章节解锁状态详情
        返回：是否解锁、缺少哪些前置章节、解锁倒计时等
        使用 BusinessCacheService 缓存结果
        """
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterUnlockService",
            parent_pks={"chapter_pk": chapter.id, "enrollment_pk": enrollment.id},
            query_params={"type": "PROGRESS"},
        )

        result = BusinessCacheService.cache_result(
            cache_key=cache_key,
            fetcher=lambda: cls._compute_unlock_status_detail(chapter, enrollment),
            timeout=cls.CACHE_TIMEOUT,
        )

        return result


class UnlockSnapshotService:
    """
    解锁状态快照服务

    职责：
    1. 管理快照的创建、查询、更新
    2. 实现混合查询策略（快照优先，stale 时降级）
    3. 提供快照刷新接口
    """

    @staticmethod
    def get_or_create_snapshot(enrollment: "Enrollment") -> "CourseUnlockSnapshot":
        """
        获取或创建快照

        如果快照不存在，创建并触发异步计算。
        返回快照对象（可能暂时是空的）。
        """
        snapshot, created = CourseUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment, defaults={"course": enrollment.course}
        )

        if created:
            # 触发异步计算
            from .tasks import refresh_unlock_snapshot

            refresh_unlock_snapshot.delay(enrollment.id)

        return snapshot

    @staticmethod
    def mark_stale(enrollment: "Enrollment"):
        """
        标记快照为过期

        当用户完成章节时调用。
        不立即重新计算，而是设置 is_stale=True。
        """
        try:
            snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)
            snapshot.is_stale = True
            snapshot.save(update_fields=["is_stale"])
        except CourseUnlockSnapshot.DoesNotExist:
            # 快照不存在，无需标记
            pass

    @staticmethod
    def get_unlock_status_hybrid(course: "Course", enrollment: "Enrollment") -> dict:
        """
        混合查询策略：优先使用快照，stale 时降级到实时计算

        返回格式：
        {
            'unlock_states': dict,  # {chapter_id: {'locked': bool, 'reason': str|null}}
            'source': 'snapshot' | 'snapshot_stale' | 'realtime'
        }

        策略：
        1. 尝试获取快照
        2. 如果快照存在且新鲜（is_stale=False），直接返回
        3. 如果快照过期，触发异步刷新，但先返回旧数据
        4. 如果快照不存在，触发异步创建，使用实时计算
        """
        try:
            snapshot = CourseUnlockSnapshot.objects.get(
                course=course, enrollment=enrollment
            )

            if not snapshot.is_stale:
                # 快照新鲜，直接使用
                return {
                    "unlock_states": snapshot.unlock_states,
                    "source": "snapshot",
                    "snapshot_version": snapshot.version,
                }
            else:
                # 快照过期，触发异步刷新
                from .tasks import refresh_unlock_snapshot

                refresh_unlock_snapshot.delay(enrollment.id)

                # 返回旧数据（允许短暂不一致）
                return {
                    "unlock_states": snapshot.unlock_states,
                    "source": "snapshot_stale",
                    "snapshot_version": snapshot.version,
                }

        except CourseUnlockSnapshot.DoesNotExist:
            # 快照不存在，触发异步创建
            from .tasks import refresh_unlock_snapshot

            refresh_unlock_snapshot.delay(enrollment.id)

            # 降级到实时计算
            return UnlockSnapshotService._compute_realtime(course, enrollment)

    @staticmethod
    def _compute_realtime(course: "Course", enrollment: "Enrollment") -> dict:
        """
        实时计算解锁状态（降级策略）

        预取 unlock_condition 和 prerequisite_chapters 避免 N+1 查询。
        内联解锁逻辑，计算后回填 ChapterUnlockService 缓存。
        """
        from .models import ChapterProgress
        from django.utils import timezone

        chapters = (
            course.chapters.select_related("unlock_condition")
            .prefetch_related("unlock_condition__prerequisite_chapters")
            .all()
        )
        unlock_states = {}

        chapter_progresses = ChapterProgress.objects.filter(
            enrollment=enrollment, chapter__course=course
        ).values("chapter_id", "completed")
        progress_map = {cp["chapter_id"]: cp["completed"] for cp in chapter_progresses}
        completed_chapter_ids = {
            cp["chapter_id"] for cp in chapter_progresses if cp["completed"]
        }

        for chapter in chapters:
            reason = None
            prerequisite_progress = None
            is_locked = False

            if hasattr(chapter, "unlock_condition") and chapter.unlock_condition:
                condition = chapter.unlock_condition
                unlock_type = condition.unlock_condition_type

                has_unmet_prereqs = False
                is_before_date = False

                if unlock_type in ("prerequisite", "all"):
                    prereq_chapters = list(condition.prerequisite_chapters.all())
                    if prereq_chapters:
                        prereq_ids = [p.id for p in prereq_chapters]
                        completed_count = sum(
                            1 for pid in prereq_ids if pid in completed_chapter_ids
                        )
                        total = len(prereq_ids)
                        has_unmet_prereqs = completed_count < total

                        remaining = [
                            {"id": p.id, "title": p.title, "order": p.order}
                            for p in prereq_chapters
                            if p.id not in completed_chapter_ids
                        ]
                        prerequisite_progress = {
                            "total": total,
                            "completed": completed_count,
                            "remaining": remaining,
                        }

                if unlock_type in ("date", "all") and condition.unlock_date:
                    is_before_date = timezone.now() < condition.unlock_date

                if has_unmet_prereqs and is_before_date:
                    reason = "both"
                    is_locked = True
                elif has_unmet_prereqs:
                    reason = "prerequisite"
                    is_locked = True
                elif is_before_date:
                    reason = "date"
                    is_locked = True

            is_completed = progress_map.get(chapter.id, False)
            if chapter.id not in progress_map:
                chapter_status = "not_started"
            elif is_completed:
                chapter_status = "completed"
            else:
                chapter_status = "in_progress"

            unlock_states[str(chapter.id)] = {
                "locked": is_locked,
                "reason": reason,
                "status": chapter_status,
                "prerequisite_progress": prerequisite_progress,
            }

        return {"unlock_states": unlock_states, "source": "realtime"}


class ProblemUnlockSnapshotService:
    """
    问题解锁状态快照服务

    职责：
    1. 管理问题快照的创建、查询、更新
    2. 实现混合查询策略（快照优先，stale 时降级）
    3. 提供快照刷新接口
    """

    @staticmethod
    def get_or_create_snapshot(enrollment: "Enrollment") -> "ProblemUnlockSnapshot":
        """
        获取或创建问题解锁快照

        如果快照不存在，创建并触发异步计算。
        返回快照对象（可能暂时是空的）。
        """
        snapshot, created = ProblemUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment, defaults={"course": enrollment.course}
        )

        if created:
            # 触发异步计算
            from .tasks import refresh_problem_unlock_snapshot

            refresh_problem_unlock_snapshot.delay(enrollment.id)

        return snapshot

    @staticmethod
    def mark_stale(enrollment: "Enrollment"):
        """
        标记问题快照为过期

        当用户解题进度更新时调用。
        不立即重新计算，而是设置 is_stale=True。
        """
        try:
            snapshot = ProblemUnlockSnapshot.objects.get(enrollment=enrollment)
            snapshot.is_stale = True
            snapshot.save(update_fields=["is_stale"])
        except ProblemUnlockSnapshot.DoesNotExist:
            # 快照不存在，无需标记
            pass

    @staticmethod
    def get_unlock_status_hybrid(course: "Course", enrollment: "Enrollment") -> dict:
        """
        混合查询策略：优先使用快照，stale 时降级到实时计算

        返回格式：
        {
            'unlock_states': dict,  # {problem_id: {'unlocked': bool, 'reason': str|null}}
            'source': 'snapshot' | 'snapshot_stale' | 'realtime'
        }

        策略：
        1. 尝试获取快照
        2. 如果快照存在且新鲜（is_stale=False），直接返回
        3. 如果快照过期，触发异步刷新，但先返回旧数据
        4. 如果快照不存在，触发异步创建，使用实时计算
        """
        try:
            snapshot = ProblemUnlockSnapshot.objects.get(
                course=course, enrollment=enrollment
            )

            if not snapshot.is_stale:
                # 快照新鲜，直接使用
                return {
                    "unlock_states": snapshot.unlock_states,
                    "source": "snapshot",
                    "snapshot_version": snapshot.version,
                }
            else:
                # 快照过期，触发异步刷新
                from .tasks import refresh_problem_unlock_snapshot

                refresh_problem_unlock_snapshot.delay(enrollment.id)

                # 返回旧数据（允许短暂不一致）
                return {
                    "unlock_states": snapshot.unlock_states,
                    "source": "snapshot_stale",
                    "snapshot_version": snapshot.version,
                }

        except ProblemUnlockSnapshot.DoesNotExist:
            # 快照不存在，触发异步创建
            from .tasks import refresh_problem_unlock_snapshot

            refresh_problem_unlock_snapshot.delay(enrollment.id)

            # 降级到实时计算
            return ProblemUnlockSnapshotService._compute_realtime(course, enrollment)

    @staticmethod
    def _compute_realtime(course: "Course", enrollment: "Enrollment") -> dict:
        """
        实时计算解锁状态（降级策略）

        复用现有的 ProblemUnlockCondition.is_unlocked() 逻辑。
        """
        from .models import ProblemProgress, Problem
        from django.utils import timezone

        problems = Problem.objects.filter(chapter__course=course).select_related(
            "chapter"
        )
        unlock_states = {}

        for problem in problems:
            if hasattr(problem, "unlock_condition"):
                condition = problem.unlock_condition
                unlock_type = condition.unlock_condition_type

                # 检查前置题目
                has_unmet_prereqs = False
                if unlock_type in ("prerequisite", "both"):
                    prereq_ids = list(
                        condition.prerequisite_problems.values_list("id", flat=True)
                    )
                    completed_count = ProblemProgress.objects.filter(
                        enrollment=enrollment,
                        problem_id__in=prereq_ids,
                        status="solved",
                    ).count()
                    has_unmet_prereqs = completed_count < len(prereq_ids)

                # 检查解锁日期
                is_before_date = False
                if unlock_type in ("date", "both") and condition.unlock_date:
                    is_before_date = timezone.now() < condition.unlock_date

                # 确定解锁状态
                is_unlocked = not (has_unmet_prereqs or is_before_date)

                # 确定原因
                if has_unmet_prereqs and is_before_date:
                    reason = "both"
                elif has_unmet_prereqs:
                    reason = "prerequisite"
                elif is_before_date:
                    reason = "date"
                else:
                    reason = None
            else:
                is_unlocked = True
                reason = None

            unlock_states[str(problem.id)] = {"unlocked": is_unlocked, "reason": reason}

        return {"unlock_states": unlock_states, "source": "realtime"}


# Batch user status retrieval functions for cache separation


def _compute_chapter_user_status(chapter_ids, user_id, course_id):
    """
    计算章节用户状态（纯业务逻辑，无缓存）
    """
    from .models import Enrollment, ChapterProgress, CourseUnlockSnapshot

    # 从数据库获取用户状态
    try:
        enrollment = Enrollment.objects.get(user_id=user_id, course_id=course_id)
    except Enrollment.DoesNotExist:
        # 未注册课程，返回默认状态
        return {
            str(ch_id): {"status": "not_started", "is_locked": True}
            for ch_id in chapter_ids
        }

    # 优先从快照获取解锁状态
    unlock_states = {}
    try:
        snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)
        unlock_states = snapshot.unlock_states
    except CourseUnlockSnapshot.DoesNotExist:
        # 如果快照不存在，触发异步创建
        from .tasks import refresh_unlock_snapshot

        refresh_unlock_snapshot.delay(enrollment.id)
        # 使用实时计算作为回退
        from .services import UnlockSnapshotService

        realtime_result = UnlockSnapshotService._compute_realtime(
            enrollment.course, enrollment
        )
        unlock_states = realtime_result["unlock_states"]

    # 获取章节进度
    progress_records = ChapterProgress.objects.filter(
        enrollment=enrollment, chapter_id__in=chapter_ids
    ).values("chapter_id", "completed")

    progress_map = {p["chapter_id"]: p["completed"] for p in progress_records}

    # 获取用户在课程中所有已完成的章节ID（用于 prerequisite_progress 计算）
    completed_chapter_ids = set(
        ChapterProgress.objects.filter(
            enrollment=enrollment, completed=True
        ).values_list("chapter_id", flat=True)
    )

    # 合并状态
    result = {}
    for ch_id in chapter_ids:
        ch_id_str = str(ch_id)
        is_completed = progress_map.get(ch_id, False)

        # 确定状态
        if ch_id not in progress_map:
            status = "not_started"
        elif is_completed:
            status = "completed"
        else:
            status = "in_progress"

        # 获取锁定状态（从快照或实时计算结果）
        unlock_state = unlock_states.get(ch_id_str, {})
        is_locked = unlock_state.get("locked", False)

        result[ch_id_str] = {"status": status, "is_locked": is_locked}

    # 添加已完成章节ID列表（用于 prerequisite_progress 计算）
    result["_meta"] = {"completed_chapter_ids": list(completed_chapter_ids)}

    return result


def get_chapter_user_status(chapter_ids, user_id, course_id):
    """
    批量获取章节用户状态

    Args:
        chapter_ids: 章节ID列表
        user_id: 用户ID
        course_id: 课程ID

    Returns:
        dict: 章节ID到用户状态的映射
    """
    cache_key = get_standard_cache_key(
        prefix="courses",
        view_name="business:ChapterStatus",
        parent_pks={"course_pk": course_id},
        query_params={"user_id": user_id},
    )

    result = BusinessCacheService.cache_result(
        cache_key=cache_key,
        fetcher=lambda: _compute_chapter_user_status(chapter_ids, user_id, course_id),
        timeout=300,
    )

    return result


def _compute_problem_user_status(problem_ids, user_id, chapter_id):
    """
    计算问题用户状态（纯业务逻辑，无缓存）
    """
    from .models import Enrollment, ProblemProgress, ProblemUnlockSnapshot, Chapter

    # 获取章节所属课程
    try:
        chapter = Chapter.objects.select_related("course").get(id=chapter_id)
        course_id = chapter.course_id
    except Chapter.DoesNotExist:
        # 章节不存在，返回默认状态
        return {
            str(p_id): {"status": "not_started", "is_unlocked": False}
            for p_id in problem_ids
        }

    # 从数据库获取用户状态
    try:
        enrollment = Enrollment.objects.get(user_id=user_id, course_id=course_id)
    except Enrollment.DoesNotExist:
        # 未注册课程，返回默认状态
        return {
            str(p_id): {"status": "not_started", "is_unlocked": False}
            for p_id in problem_ids
        }

    # 优先从快照获取解锁状态
    unlock_states = {}
    try:
        snapshot = ProblemUnlockSnapshot.objects.get(enrollment=enrollment)
        unlock_states = snapshot.unlock_states
    except ProblemUnlockSnapshot.DoesNotExist:
        # 如果快照不存在，触发异步创建
        from .tasks import refresh_problem_unlock_snapshot

        refresh_problem_unlock_snapshot.delay(enrollment.id)
        # 使用实时计算作为回退
        from .services import ProblemUnlockSnapshotService

        realtime_result = ProblemUnlockSnapshotService._compute_realtime(
            enrollment.course, enrollment
        )
        unlock_states = realtime_result["unlock_states"]

    # 获取问题进度
    progress_records = ProblemProgress.objects.filter(
        enrollment=enrollment, problem_id__in=problem_ids
    ).values("problem_id", "status")

    progress_map = {p["problem_id"]: p["status"] for p in progress_records}

    # 合并状态
    result = {}
    for p_id in problem_ids:
        p_id_str = str(p_id)

        # 获取进度状态
        status = progress_map.get(p_id, "not_started")

        # 获取解锁状态（从快照或实时计算结果）
        unlock_state = unlock_states.get(p_id_str, {})
        is_unlocked = unlock_state.get("unlocked", False)

        result[p_id_str] = {"status": status, "is_unlocked": is_unlocked}

    return result


def get_problem_user_status(problem_ids, user_id, chapter_id):
    """
    批量获取问题用户状态

    Args:
        problem_ids: 问题ID列表
        user_id: 用户ID
        chapter_id: 章节ID

    Returns:
        dict: 问题ID到用户状态的映射
    """
    cache_key = get_standard_cache_key(
        prefix="courses",
        view_name="business:ProblemStatus",
        parent_pks={"chapter_pk": chapter_id},
        query_params={"user_id": user_id},
    )

    result = BusinessCacheService.cache_result(
        cache_key=cache_key,
        fetcher=lambda: _compute_problem_user_status(problem_ids, user_id, chapter_id),
        timeout=300,
    )

    return result


# ============================================================================
# Async Code Judging System Configuration
# ============================================================================

CODE_JUDGING_CONFIG = {
    "max_queue_size": 18,  # Maximum number of tasks in queue
    "warning_threshold": 10,  # Warning threshold for queue size
    "soft_timeout_sec": 270,  # Soft timeout (4.5 minutes)
    "hard_timeout_sec": 300,  # Hard timeout (5 minutes)
    "queue_timeout_sec": 120,  # Maximum time in queue (2 minutes)
    "cache_timeout_sec": 30,  # Cache timeout for capacity info (30 seconds)
    "avg_judging_time_sec": 30,  # Average time per submission
    "max_retries": 3,  # Maximum retry attempts for failed tasks
}


# ============================================================================
# Judging Capacity Service
# ============================================================================

class JudgingCapacityService:
    """
    Service class to manage code judging queue capacity and status.

    Provides functionality to:
    - Calculate current queue capacity
    - Cache capacity information for performance
    - Estimate wait times for submissions
    - Check if system can accept new submissions
    """

    def __init__(self):
        """Initialize the capacity service."""
        self.config = CODE_JUDGING_CONFIG
        self.cache_prefix = "judging_capacity"

    def get_cache_key(self) -> str:
        """
        Get the cache key for capacity information.

        Returns:
            str: The cache key
        """
        return f"{self.cache_prefix}:current"

    def _calculate_capacity_from_db(self) -> Dict[str, Any]:
        """
        Calculate current capacity from database.

        Returns:
            Dict containing capacity information
        """
        from django.db.models import Q, Count

        # Count pending and started tasks
        pending_count = JudgingQueueStats.objects.filter(
            status__in=["pending", "started"]
        ).count()

        # Count only started (actively running) tasks
        running_count = JudgingQueueStats.objects.filter(
            status="started"
        ).count()

        total_capacity = self.config["max_queue_size"]
        available_slots = total_capacity - pending_count

        # Determine system status
        if pending_count >= total_capacity:
            status = "full"
        elif pending_count >= self.config["warning_threshold"]:
            status = "busy"
        else:
            status = "available"

        return {
            "pending_count": pending_count,
            "running_count": running_count,
            "total_capacity": total_capacity,
            "available_slots": max(0, available_slots),
            "status": status,
        }

    def get_current_capacity(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get current queue capacity information.

        Args:
            use_cache: Whether to use cached data (default: True)

        Returns:
            Dict containing:
                - pending_count: Number of pending/started tasks
                - running_count: Number of actively running tasks
                - total_capacity: Maximum queue size
                - available_slots: Number of available slots
                - status: System status (available/busy/full)
        """
        cache_key = self.get_cache_key()

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached capacity data: {cached_data}")
                return cached_data

        # Calculate from database
        capacity_data = self._calculate_capacity_from_db()

        # Cache the result
        if use_cache:
            cache.set(
                cache_key,
                capacity_data,
                timeout=self.config["cache_timeout_sec"]
            )
            logger.debug(
                f"Cached capacity data: {capacity_data}, "
                f"timeout={self.config['cache_timeout_sec']}s"
            )

        return capacity_data

    def invalidate_cache(self):
        """
        Invalidate the capacity cache.
        Call this after creating or completing a task.
        """
        cache_key = self.get_cache_key()
        cache.delete(cache_key)
        logger.debug(f"Invalidated capacity cache: {cache_key}")

    def can_accept_submission(self) -> tuple[bool, str]:
        """
        Check if the system can accept a new submission.

        Returns:
            Tuple of (can_accept, reason)
                - can_accept: True if submission can be accepted
                - reason: Human-readable reason
        """
        capacity = self.get_current_capacity()

        if capacity["status"] == "full":
            return False, "系统繁忙，请稍后再试"

        return True, ""

    def estimate_wait_time(self, position: int) -> int:
        """
        Estimate wait time for a submission at given queue position.

        Args:
            position: Queue position (1-indexed)

        Returns:
            Estimated wait time in seconds
        """
        if position <= 0:
            return 0

        avg_time = self.config["avg_judging_time_sec"]
        estimated_seconds = position * avg_time

        logger.info(
            f"Estimated wait time for position {position}: {estimated_seconds}s"
        )

        return estimated_seconds

    def get_queue_position(self, submission: Submission) -> Optional[int]:
        """
        Get the queue position for a submission.

        Args:
            submission: The submission to check

        Returns:
            Queue position (1-indexed) or None if not in queue
        """
        try:
            stats = submission.queue_stats
            if stats.status not in ["pending", "started"]:
                return None

            # Count how many pending tasks are ahead of this one
            position = JudgingQueueStats.objects.filter(
                status="pending",
                created_at__lt=stats.created_at
            ).count() + 1

            return position
        except JudgingQueueStats.DoesNotExist:
            return None

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for monitoring.

        Returns:
            Dict containing system status information
        """
        capacity = self.get_current_capacity()

        # Get additional statistics
        from django.db.models import Avg, Max, Min, Count
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        hour_ago = now - timedelta(hours=1)

        # Recent statistics
        recent_stats = JudgingQueueStats.objects.filter(
            completed_at__gte=hour_ago,
            status="success"
        ).aggregate(
            avg_wait_time=Avg("queue_wait_seconds"),
            avg_execution_time=Avg("execution_seconds"),
            max_wait_time=Max("queue_wait_seconds"),
            total_completed=Count("id")
        )

        return {
            "capacity": capacity,
            "recent_performance": {
                "avg_wait_time_seconds": recent_stats["avg_wait_time"] or 0,
                "avg_execution_time_seconds": recent_stats["avg_execution_time"] or 0,
                "max_wait_time_seconds": recent_stats["max_wait_time"] or 0,
                "total_completed_last_hour": recent_stats["total_completed"] or 0,
            },
            "config": {
                "max_queue_size": self.config["max_queue_size"],
                "warning_threshold": self.config["warning_threshold"],
                "avg_judging_time_seconds": self.config["avg_judging_time_sec"],
            },
        }
