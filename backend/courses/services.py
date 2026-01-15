import logging
from typing import Dict, Any, Optional
from .judge_backend.Judge0Backend import Judge0Backend
from .judge_backend.CodeJudgingBackend import CodeJudgingBackend
from .models import Submission
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