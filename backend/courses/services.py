import requests
import time
from typing import Dict, Any, Optional
from django.conf import settings
from .models import Submission, TestCase
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

class Judge0API:
    """
    Judge0 API wrapper for code execution
    """
    
    def __init__(self):
        # Get API key and base URL from settings, with defaults
        self.api_key = getattr(settings, 'JUDGE0_API_KEY', '')
        self.base_url = getattr(settings, 'JUDGE0_BASE_URL', 'http://192.168.122.137:2358')
        
        # Headers for API requests
        self.headers = {
            # 'X-RapidAPI-Host': 'judge0.p.rapidapi.com',
            # 'X-RapidAPI-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def submit_code(self, code: str, language_id: int, stdin: str = "", expected_output: str = None, 
                    time_limit: int = 2000, memory_limit: int = 128000) -> Dict[str, Any]:
        """
        Submit code to Judge0 API for execution
        
        Args:
            code: Source code to execute
            language_id: Judge0 language ID
            stdin: Input for the program
            expected_output: Expected output (for comparison)
            time_limit: Time limit in milliseconds
            memory_limit: Memory limit in KB
            
        Returns:
            Dict containing submission details
        """
        url = f"{self.base_url}/submissions"
        
        payload = {
            "source_code": code,
            "language_id": language_id,
            "stdin": stdin,
            "cpu_time_limit": time_limit / 1000.0,  # Convert to seconds
            "memory_limit": memory_limit * 1000,  # in KB
        }
        if expected_output is not None:
            payload['expected_output'] = expected_output
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error submitting code: {response.status_code} - {response.text}")
    
    def get_submission_status(self, token: str) -> Dict[str, Any]:
        """
        Get the status of a submission by its token
        
        Args:
            token: Submission token
            
        Returns:
            Dict containing submission status
        """
        url = f"{self.base_url}/submissions/{token}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error getting submission status: {response.status_code} - {response.text}")
    
    def wait_for_submission_result(self, token: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Poll for submission result until completed or timeout
        
        Args:
            token: Submission token
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dict containing final submission result
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_submission_status(token)
            
            # Check status - status_id 1 = In Queue, 2 = Processing, 3 = Accepted, etc.
            status_id = result.get('status', {}).get('id', 0)
            
            if status_id in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:  # Final states
                return result
            
            time.sleep(0.5)  # Wait 0.5 seconds before polling again
        
        raise Exception("Submission timeout")


class CodeExecutorService:
    """
    Service class to handle code execution and submission management
    """
    
    # Language ID mapping for Judge0
    LANGUAGE_IDS = {
        'python': 71,
        'c': 50,
        'cpp': 54,
        'java': 62,
        'javascript': 63,
        'go': 60,
        'rust': 78,
        'kotlin': 79,
        'swift': 82,
    }
    
    def __init__(self):
        self.judge0 = Judge0API()
    
    def execute_algorithm_problem_solution(self, user, problem, code: str, language: str = 'python') -> Submission:
        """
        Execute code for an algorithm problem and create a submission record
        
        Args:
            user: User submitting the code
            problem: Problem object being solved
            code: Source code submitted
            language: Programming language
            
        Returns:
            Submission object with execution results
        """
        # First, create a pending submission record
        submission = Submission.objects.create(
            user=user,
            problem=problem,
            code=code,
            language=language,
            status='pending'
        )
        
        try:
            # Get the algorithm problem details
            algorithm_problem = problem.algorithm_info
            test_cases = algorithm_problem.test_cases.all()
            
            # Default to Python if language not supported
            language_id = self.LANGUAGE_IDS.get(language.lower(), 71)
            
            # Use the first test case for execution (in a real system, you'd run all test cases)
            if test_cases.exists():
                first_test_case = test_cases.first()
                
                # Submit the code to Judge0
                submission_response = self.judge0.submit_code(
                    code=code,
                    language_id=language_id,
                    stdin=first_test_case.input_data,
                    expected_output=first_test_case.expected_output,
                    time_limit=algorithm_problem.time_limit, #ms
                    memory_limit=algorithm_problem.memory_limit #MB  
                )
                
                # Update submission with token
                token = submission_response['token']
                submission.status = 'judging'
                submission.save()
                
                # Wait for the result
                result = self.judge0.wait_for_submission_result(token)
                
                # Process the result and update submission
                self._update_submission_with_result(submission, result)
            else:
                # If no test cases, mark as compilation error
                submission.status = 'compilation_error'
                submission.error = "No test cases available for this problem"
                submission.save()
                
        except Exception as e:
            # Handle any errors during execution
            submission.status = 'internal_error'
            submission.error = str(e)
            submission.save()
        
        return submission
    
    def _update_submission_with_result(self, submission: Submission, result: Dict[str, Any]):
        """
        Update submission record with execution results
        
        Args:
            submission: Submission object to update
            result: Judge0 result dictionary
        """
        status_id = result.get('status', {}).get('id', 0)
        stdout = result.get('stdout', '')
        stderr = result.get('stderr', '')
        time = result.get('time', None)
        memory = result.get('memory', None)
        
        # Map Judge0 status IDs to our status
        status_mapping = {
            1: 'pending',      # In Queue
            2: 'judging',      # Processing
            3: 'accepted',     # Accepted
            4: 'wrong_answer', # Wrong Answer
            5: 'time_limit_exceeded',    # Time Limit Exceeded
            6: 'memory_limit_exceeded',  # Memory Limit Exceeded
            7: 'runtime_error',          # Runtime Error
            8: 'compilation_error',      # Compilation Error
            9: 'internal_error',         # Internal Error
            10: 'internal_error',        # Internal Error
            11: 'internal_error',        # Internal Error
            12: 'internal_error',        # Internal Error
        }
        
        submission.status = status_mapping.get(status_id, 'internal_error')
        submission.output = stdout if stdout else stderr
        submission.error = stderr if stderr and status_id in [7, 8] else ""
        
        if time is not None:
            submission.execution_time = float(time) * 1000  # Convert seconds to milliseconds
        if memory is not None:
            submission.memory_used = memory/1000 # Memory convert to MB
            
        submission.save()
    
    def run_all_test_cases(self, user, problem, code: str, language: str = 'python') -> Submission:
        """
        Run the submitted code against all test cases for the problem
        
        Args:
            user: User submitting the code
            problem: Problem object being solved
            code: Source code submitted
            language: Programming language
            
        Returns:
            Submission object with execution results
        """
        # First, create a pending submission record
        submission = Submission.objects.create(
            user=user,
            problem=problem,
            code=code,
            language=language,
            status='pending'
        )
        
        try:
            # Get the algorithm problem details
            algorithm_problem = problem.algorithm_info
            test_cases = algorithm_problem.test_cases.all()
            
            if not test_cases.exists():
                submission.status = 'compilation_error'
                submission.error = "No test cases available for this problem"
                submission.save()
                return submission
            
            # Default to Python if language not supported
            language_id = self.LANGUAGE_IDS.get(language.lower(), 71)
            solve_func = algorithm_problem.solution_name['python']
            all_passed = True
            max_time = 0
            max_memory = 0
            final_status = 'accepted'
            final_output = ""
            final_error = ""
            
            for test_case in test_cases:
                if not all_passed:  # If a previous test case failed, we can still run others to collect info
                    break
                

                exec_code = generate_judge0_code(user_code=code.strip(),solve_func=solve_func,language=language)
                # Submit the code to Judge0 for this test case
                submission_response = self.judge0.submit_code(
                    code=exec_code,
                    language_id=language_id,
                    stdin=test_case.input_data,
                    expected_output=test_case.expected_output,
                    time_limit=algorithm_problem.time_limit,
                    memory_limit=algorithm_problem.memory_limit  
                )
                
                # Update submission to judging status
                submission.status = 'judging'
                submission.save()
                
                # Wait for the result
                result = self.judge0.wait_for_submission_result(submission_response['token'])
                
                status_id = result.get('status', {}).get('id', 0)
                
                # If this test case fails, update the status
                if status_id != 3:  # Not accepted
                    all_passed = False
                    final_status = self._map_status_id(status_id)
                
                # Track max time and memory used
                time_taken = result.get('time')
                memory_used = result.get('memory')
                
                if time_taken is not None:
                    max_time = max(max_time, float(time_taken) * 1000)  # Convert to milliseconds
                
                if memory_used is not None:
                    max_memory = max(max_memory, memory_used/1000)
                
                # Get output and error
                stdout = result.get('stdout', '')
                stderr = result.get('stderr', '')
                #TODO return last test case if wrong
                if stdout:
                    final_output += f"Test case {test_case.id} output: {stdout}\n"
                if stderr:
                    final_error += f"Test case {test_case.id} error: {stderr}\n"
            
            # Update the submission with final results
            submission.status = final_status if not all_passed else 'accepted'
            submission.execution_time = max_time if max_time > 0 else None
            submission.memory_used = max_memory if max_memory > 0 else None
            submission.output = final_output
            submission.error = final_error
            submission.save()
            
        except Exception as e:
            # Handle any errors during execution
            submission.status = 'internal_error'
            submission.error = str(e)
            submission.save()
        
        return submission
    def run_freely(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        自由执行用户代码（不关联任何题目），适用于“运行代码”场景。
    
        Args:
            code (str): 用户提交的源代码
            language (str): 编程语言标识，如 'python', 'cpp', 'java' 等
        
        Returns:
            Dict[str, Any]: 包含执行结果的字典，字段包括：
                - status: 执行状态（如 'accepted', 'runtime_error' 等）
                - stdout: 标准输出
                - stderr: 标准错误
                - execution_time_ms: 执行时间（毫秒）
                - memory_used_kb: 内存使用量（KB）
        """
        # 1. 获取语言 ID，不支持的语言默认使用 Python (71)
        language_id = self.LANGUAGE_IDS.get(language.lower(), 71)

        try:
            # 2. 提交代码到 Judge0（无 stdin，无 expected_output）
            submission_response = self.judge0.submit_code(
                code=code,
                language_id=language_id,
                stdin="",               # 无标准输入
                time_limit=2000,        # 2000 毫秒 = 2 秒
                memory_limit=128     # 128 MB = 128 * 1000 KB
            )

            # 3. 等待执行结果（最多 30 秒）
            result = self.judge0.wait_for_submission_result(submission_response['token'])

            # 4. 解析结果
            status_id = result.get('status', {}).get('id', 0)
            stdout = result.get('stdout', '') or ""
            stderr = result.get('stderr', '') or ""
            time_sec = result.get('time')        # 单位：秒（float 或 None）
            memory_kb = result.get('memory')     # 单位：KB（int 或 None）

            # 5. 返回结构化结果
            return {
                'status': self._map_status_id(status_id),
                'stdout': stdout,
                'stderr': stderr,
                'execution_time': float(time_sec) * 1000 if time_sec is not None else None,
                'memory_used': memory_kb/1000,
            }

        except Exception as e:
            # 6. 捕获所有异常（网络错误、Judge0 错误、超时等）
            return {
                'status': 'internal_error',
                'stdout': '',
                'stderr': str(e),
                'execution_time': None,
                'memory_used': None,
            }
    def _map_status_id(self, status_id: int) -> str:
        """
        Map Judge0 status ID to our status
        
        Args:
            status_id: Judge0 status ID
            
        Returns:
            Our status string
        """
        status_mapping = {
            1: 'pending',      # In Queue
            2: 'judging',      # Processing
            3: 'accepted',     # Accepted
            4: 'wrong_answer', # Wrong Answer
            5: 'time_limit_exceeded',    # Time Limit Exceeded
            6: 'memory_limit_exceeded',  # Memory Limit Exceeded
            7: 'runtime_error',          # Runtime Error
            8: 'compilation_error',      # Compilation Error
            9: 'internal_error',         # Internal Error
            10: 'internal_error',        # Internal Error
            11: 'internal_error',        # Internal Error
            12: 'internal_error',        # Internal Error
        }
        
        return status_mapping.get(status_id, 'internal_error')