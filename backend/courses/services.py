import logging
from typing import Dict, Any, Optional
from django.core.cache import cache
from .judge_backend.Judge0Backend import Judge0Backend
from .judge_backend.CodeJudgingBackend import CodeJudgingBackend
from .models import Submission, Enrollment, Course, Chapter, CourseUnlockSnapshot
from common.decorators.logging_decorators import log_execution_time

logger = logging.getLogger(__name__)


def generate_judge0_code(user_code: str,solve_func:str,language:str) -> str:
    """
    将用户实现的函数代码包装成完整的可执行程序
    user_code: 用户提交的函数定义（字符串）
    """
    template = {"python":'''import sys
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
'''
    }
    
    return template[language].format(user_code=user_code.strip(),solve_func=solve_func.strip())

class CodeExecutorService:
    """
    Service class to handle code execution and submission management.
    Uses a pluggable judging backend (e.g., Judge0).
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
            1: 'pending',
            2: 'judging',
            3: 'accepted',
            4: 'wrong_answer',
            5: 'time_limit_exceeded',
            6: 'memory_limit_exceeded',
            7: 'runtime_error',
            8: 'compilation_error',
        }
        return mapping.get(status_id, 'internal_error')

    def _update_submission_with_result(
        self,
        submission: Submission,
        final_status: str,
        output: str,
        error: str,
        execution_time_ms: Optional[float],
        memory_used_mb: Optional[float]
    ):
        """
        Update the submission record in a consistent way.
        """
        submission.status = final_status
        submission.output = output
        submission.error = error
        submission.execution_time = execution_time_ms
        submission.memory_used = memory_used_mb
        submission.save()

    @log_execution_time(threshold_ms=5000)
    def run_all_test_cases(self, user, problem, code: str, language: str = 'python') -> Submission:
        """
        Run submitted code against all test cases of a problem.
        """
        logger.info("Code execution started", extra={
            'user_id': user.id,
            'problem_id': problem.id,
            'language': language,
            'code_length': len(code)
        })

        submission = Submission.objects.create(
            user=user,
            problem=problem,
            code=code,
            language=language,
            status='pending'
        )

        try:
            algorithm_problem = problem.algorithm_info
            test_cases = algorithm_problem.test_cases.all()

            if not test_cases.exists():
                self._update_submission_with_result(
                    submission=submission,
                    final_status='compilation_error',
                    output="",
                    error="No test cases available for this problem",
                    execution_time_ms=None,
                    memory_used_mb=None
                )
                return submission

            language_id = self.backend.get_language_id(language)
            solve_func = algorithm_problem.solution_name.get(language, 'solve')

            all_passed = True
            max_time_ms = 0.0
            max_memory_mb = 0.0
            final_output = ""
            final_error = ""

            for test_case in test_cases:
                # Generate full executable code
                exec_code = generate_judge0_code(
                    user_code=code.strip(),
                    solve_func=solve_func,
                    language=language
                )

                # Submit to judging backend
                logger.debug(f"Running test case {test_case.id}", extra={
                    'test_case_id': test_case.id,
                    'time_limit': algorithm_problem.time_limit,
                    'memory_limit': algorithm_problem.memory_limit
                })

                submit_resp = self.backend.submit_code(
                    source_code=exec_code,
                    language_id=language_id,
                    stdin=test_case.input_data,
                    expected_output=test_case.expected_output,
                    time_limit_ms=algorithm_problem.time_limit,      # ms
                    memory_limit_mb=algorithm_problem.memory_limit   # MB
                )

                # Mark as judging
                submission.status = 'judging'
                submission.save()

                # Wait for result
                result = self.backend.get_result(submit_resp['token'], timeout_sec=30)

                status_id = result['status_id']
                stdout = result['stdout'] or ""
                stderr = result['stderr'] or ""
                time_ms = result['time']          # already in ms
                memory_mb = result['memory']      # already in MB

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
                logger.info(f"Test case {test_case.id} completed", extra={
                    'test_case_id': test_case.id,
                    'status': test_status,
                    'execution_time_ms': time_ms,
                    'memory_used_mb': memory_mb
                })

                # Check if this test case failed
                if status_id != 3:  # Not accepted
                    all_passed = False
                    final_status = self._map_status_id(status_id)
                    # Optionally break on first failure, or continue to collect all results
                    # Here we continue to run all test cases
                else:
                    final_status = 'accepted'

            # Finalize submission status
            final_status = 'accepted' if all_passed else final_status

            logger.info("Code execution completed", extra={
                'submission_id': submission.id,
                'status': final_status,
                'execution_time_ms': max_time_ms if max_time_ms > 0 else None,
                'memory_used_mb': max_memory_mb if max_memory_mb > 0 else None,
                'test_cases_count': test_cases.count(),
                'all_passed': all_passed
            })

            self._update_submission_with_result(
                submission=submission,
                final_status=final_status,
                output=final_output.rstrip(),
                error=final_error.rstrip(),
                execution_time_ms=max_time_ms if max_time_ms > 0 else None,
                memory_used_mb=max_memory_mb if max_memory_mb > 0 else None
            )

        except Exception as e:
            logger.error(f"Code execution failed", extra={
                'user_id': user.id,
                'problem_id': problem.id,
                'error': str(e)
            }, exc_info=True)

            self._update_submission_with_result(
                submission=submission,
                final_status='internal_error',
                output="",
                error=str(e),
                execution_time_ms=None,
                memory_used_mb=None
            )

        return submission

    @log_execution_time(threshold_ms=3000)
    def run_freely(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Execute arbitrary user code without test cases (e.g., "Run Code" feature).
        Returns standardized result dict.
        """
        logger.info("Free code execution started", extra={
            'language': language,
            'code_length': len(code)
        })

        try:
            language_id = self.backend.get_language_id(language)

            submit_resp = self.backend.submit_code(
                source_code=code,
                language_id=language_id,
                stdin="",
                time_limit_ms=2000,    # 2 seconds
                memory_limit_mb=128    # 128 MB
            )

            result = self.backend.get_result(submit_resp['token'], timeout_sec=30)

            final_result = {
                'status': self._map_status_id(result['status_id']),
                'stdout': result['stdout'] or '',
                'stderr': result['stderr'] or '',
                'execution_time': result['time'],      # ms
                'memory_used': result['memory'],       # MB
            }

            logger.info("Free code execution completed", extra={
                'status': final_result['status'],
                'execution_time': final_result['execution_time'],
                'memory_used': final_result['memory_used']
            })

            return final_result

        except Exception as e:
            logger.error(f"Free code execution failed", extra={
                'language': language,
                'error': str(e)
            }, exc_info=True)

            return {
                'status': 'internal_error',
                'stdout': '',
                'stderr': str(e),
                'execution_time': None,
                'memory_used': None,
            }


class ChapterUnlockService:
    """
    章节解锁服务
    处理章节解锁状态的检查和查询
    """

    CACHE_TIMEOUT = 900  # 15分钟缓存
    UNLOCK_CACHE_PREFIX = "chapter_unlock"
    PREREQUISITE_PROGRESS_CACHE_PREFIX = "chapter_prerequisite_progress"

    @classmethod
    def _get_cache_key(cls, chapter_id, enrollment_id, prefix=None):
        """
        生成缓存键
        """
        if prefix is None:
            prefix = cls.UNLOCK_CACHE_PREFIX
        return f"{prefix}:{chapter_id}:{enrollment_id}"

    @classmethod
    def _set_cache(cls, key, value):
        """设置缓存"""
        cache.set(key, value, cls.CACHE_TIMEOUT)

    @classmethod
    def _get_cache(cls, key):
        """获取缓存"""
        return cache.get(key)

    @classmethod
    def _invalidate_cache(cls, chapter_id, enrollment_id=None):
        """
        使缓存失效
        """
        patterns_to_invalidate = []

        # 使当前章节的缓存失效
        patterns_to_invalidate.append(f"{cls.UNLOCK_CACHE_PREFIX}:{chapter_id}:*")
        patterns_to_invalidate.append(f"{cls.PREREQUISITE_PROGRESS_CACHE_PREFIX}:{chapter_id}:*")

        # 如果 enrollment_id 提供了，使其特定的缓存失效
        if enrollment_id:
            patterns_to_invalidate.append(f"{cls.UNLOCK_CACHE_PREFIX}:{chapter_id}:{enrollment_id}")
            patterns_to_invalidate.append(f"{cls.PREREQUISITE_PROGRESS_CACHE_PREFIX}:{chapter_id}:{enrollment_id}")

        from common.utils.cache import delete_cache_pattern
        for pattern in patterns_to_invalidate:
            delete_cache_pattern(pattern)

    @staticmethod
    def is_unlocked(chapter, enrollment):
        """
        检查章节对指定用户是否已解锁

        规则：
        1. 如果没有解锁条件，则已解锁
        2. 根据 unlock_condition_type 执行相应检查：
           - 'prerequisite': 只检查前置章节
           - 'date': 只检查解锁日期
           - 'all': 同时检查前置章节和解锁日期（默认）
        """
        # 首先尝试从缓存获取
        cache_key = ChapterUnlockService._get_cache_key(chapter.id, enrollment.id)
        cached_result = ChapterUnlockService._get_cache(cache_key)
        if cached_result is not None:
            return cached_result

        if not hasattr(chapter, 'unlock_condition') or chapter.unlock_condition is None:
            ChapterUnlockService._set_cache(cache_key, True)
            return True

        condition = chapter.unlock_condition
        unlock_type = condition.unlock_condition_type

        # 检查前置章节（仅当类型为 prerequisite 或 all）
        if unlock_type in ('prerequisite', 'all') and condition.prerequisite_chapters.exists():
            from .models import ChapterProgress

            prerequisite_ids = list(condition.prerequisite_chapters.values_list('id', flat=True))
            completed_count = ChapterProgress.objects.filter(
                enrollment=enrollment,
                chapter_id__in=prerequisite_ids,
                completed=True
            ).count()

            if completed_count != len(prerequisite_ids):
                ChapterUnlockService._set_cache(cache_key, False)
                return False

        # 检查解锁日期（仅当类型为 date 或 all）
        if unlock_type in ('date', 'all') and condition.unlock_date:
            from django.utils import timezone
            if timezone.now() < condition.unlock_date:
                ChapterUnlockService._set_cache(cache_key, False)
                return False

        result = True
        ChapterUnlockService._set_cache(cache_key, result)
        return result

    @staticmethod
    def get_unlock_status(chapter, enrollment):
        """
        获取章节解锁状态详情
        返回：是否解锁、缺少哪些前置章节、解锁倒计时等
        """
        # 首先尝试从缓存获取前置进度
        progress_cache_key = ChapterUnlockService._get_cache_key(
            chapter.id, enrollment.id,
            ChapterUnlockService.PREREQUISITE_PROGRESS_CACHE_PREFIX
        )
        cached_progress = ChapterUnlockService._get_cache(progress_cache_key)
        if cached_progress is not None:
            return cached_progress

        from .models import ChapterProgress
        from django.utils import timezone

        # 如果没有解锁条件，返回已解锁
        if not hasattr(chapter, 'unlock_condition') or chapter.unlock_condition is None:
            result = {
                'is_locked': False,
                'reason': None,
                'prerequisite_progress': None,
                'unlock_date': None,
                'time_until_unlock': None,
                'chapter': {
                    'id': chapter.id,
                    'title': chapter.title,
                    'order': chapter.order,
                    'course_title': chapter.course.title,
                },
            }
            ChapterUnlockService._set_cache(progress_cache_key, result)
            return result

        condition = chapter.unlock_condition
        unlock_type = condition.unlock_condition_type

        result = {
            'is_locked': False,
            'reason': None,
            'prerequisite_progress': None,
            'unlock_date': condition.unlock_date,
            'time_until_unlock': None,
            'chapter': {
                'id': chapter.id,
                'title': chapter.title,
                'order': chapter.order,
                'course_title': chapter.course.title,
            },
        }

        # 检查前置章节
        if unlock_type in ('prerequisite', 'all') and condition.prerequisite_chapters.exists():
            prerequisite_ids = list(condition.prerequisite_chapters.values_list('id', flat=True))
            completed_prerequisites = set(
                ChapterProgress.objects.filter(
                    enrollment=enrollment,
                    chapter_id__in=prerequisite_ids,
                    completed=True
                ).values_list('chapter_id', flat=True)
            )

            remaining_prerequisites = [
                {
                    'id': prereq.id,
                    'title': prereq.title,
                    'order': prereq.order,
                }
                for prereq in condition.prerequisite_chapters.all()
                if prereq.id not in completed_prerequisites
            ]

            result['prerequisite_progress'] = {
                'total': len(prerequisite_ids),
                'completed': len(completed_prerequisites),
                'remaining': remaining_prerequisites,
            }

            if len(completed_prerequisites) < len(prerequisite_ids):
                result['is_locked'] = True
                result['reason'] = 'prerequisite'

        # 检查解锁日期
        if unlock_type in ('date', 'all') and condition.unlock_date:
            now = timezone.now()
            if now < condition.unlock_date:
                result['is_locked'] = True
                if result['reason'] is None:
                    result['reason'] = 'date'
                elif result['reason'] == 'prerequisite':
                    result['reason'] = 'both'

                # 计算剩余时间
                delta = condition.unlock_date - now
                result['time_until_unlock'] = {
                    'days': delta.days,
                    'hours': delta.seconds // 3600,
                    'minutes': (delta.seconds % 3600) // 60,
                }

        # 缓存结果
        ChapterUnlockService._set_cache(progress_cache_key, result)
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
    def get_or_create_snapshot(enrollment: 'Enrollment') -> 'CourseUnlockSnapshot':
        """
        获取或创建快照

        如果快照不存在，创建并触发异步计算。
        返回快照对象（可能暂时是空的）。
        """
        snapshot, created = CourseUnlockSnapshot.objects.get_or_create(
            enrollment=enrollment,
            defaults={'course': enrollment.course}
        )

        if created:
            # 触发异步计算
            from .tasks import refresh_unlock_snapshot
            refresh_unlock_snapshot.delay(enrollment.id)

        return snapshot

    @staticmethod
    def mark_stale(enrollment: 'Enrollment'):
        """
        标记快照为过期

        当用户完成章节时调用。
        不立即重新计算，而是设置 is_stale=True。
        """
        try:
            snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)
            snapshot.is_stale = True
            snapshot.save(update_fields=['is_stale'])
        except CourseUnlockSnapshot.DoesNotExist:
            # 快照不存在，无需标记
            pass

    @staticmethod
    def get_unlock_status_hybrid(course: 'Course', enrollment: 'Enrollment') -> dict:
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
                course=course,
                enrollment=enrollment
            )

            if not snapshot.is_stale:
                # 快照新鲜，直接使用
                return {
                    'unlock_states': snapshot.unlock_states,
                    'source': 'snapshot',
                    'snapshot_version': snapshot.version
                }
            else:
                # 快照过期，触发异步刷新
                from .tasks import refresh_unlock_snapshot
                refresh_unlock_snapshot.delay(enrollment.id)

                # 返回旧数据（允许短暂不一致）
                return {
                    'unlock_states': snapshot.unlock_states,
                    'source': 'snapshot_stale',
                    'snapshot_version': snapshot.version
                }

        except CourseUnlockSnapshot.DoesNotExist:
            # 快照不存在，触发异步创建
            from .tasks import refresh_unlock_snapshot
            refresh_unlock_snapshot.delay(enrollment.id)

            # 降级到实时计算
            return UnlockSnapshotService._compute_realtime(course, enrollment)

    @staticmethod
    def _compute_realtime(course: 'Course', enrollment: 'Enrollment') -> dict:
        """
        实时计算解锁状态（降级策略）

        复用现有的 ChapterUnlockService.is_unlocked() 逻辑。
        """
        from .models import ChapterProgress
        from django.utils import timezone

        chapters = course.chapters.all()
        unlock_states = {}

        for chapter in chapters:
            # 使用 ChapterUnlockService 的 is_locked 方法
            is_locked = not ChapterUnlockService.is_unlocked(chapter, enrollment)

            # 获取锁定原因（逻辑同 recompute）
            if is_locked and hasattr(chapter, 'unlock_condition'):
                condition = chapter.unlock_condition
                unlock_type = condition.unlock_condition_type

                has_unmet_prereqs = False
                if unlock_type in ('prerequisite', 'all'):
                    prereq_ids = list(condition.prerequisite_chapters.values_list('id', flat=True))
                    completed_count = ChapterProgress.objects.filter(
                        enrollment=enrollment,
                        chapter_id__in=prereq_ids,
                        completed=True
                    ).count()
                    has_unmet_prereqs = completed_count < len(prereq_ids)

                is_before_date = False
                if unlock_type in ('date', 'all') and condition.unlock_date:
                    is_before_date = timezone.now() < condition.unlock_date

                if has_unmet_prereqs and is_before_date:
                    reason = 'both'
                elif has_unmet_prereqs:
                    reason = 'prerequisite'
                elif is_before_date:
                    reason = 'date'
                else:
                    reason = None
            else:
                reason = None

            unlock_states[str(chapter.id)] = {
                'locked': is_locked,
                'reason': reason
            }

        return {
            'unlock_states': unlock_states,
            'source': 'realtime'
        }