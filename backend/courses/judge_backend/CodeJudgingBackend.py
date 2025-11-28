from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class CodeJudgingBackend(ABC):
    """
    Abstract base class for code judging backends.
    All judging services (e.g., Judge0, custom sandbox) must implement this interface.

    Units:
      - Time: milliseconds (ms)
      - Memory: megabytes (MB)
    """

    @abstractmethod
    def submit_code(
        self,
        source_code: str,
        language_id: int,
        stdin: str = "",
        expected_output: Optional[str] = None,
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 128,
    ) -> Dict[str, Any]:
        """
        Submit code for execution.

        Args:
            source_code: 用户提交的完整可执行代码
            language_id: 后端定义的语言 ID
            stdin: 标准输入（字符串）
            expected_output: 期望输出（用于自动判题，可选）
            time_limit_ms: 时间限制（毫秒）
            memory_limit_mb: 内存限制（MB）

        Returns:
            至少包含 'token' 字段的字典，用于后续查询结果
        """
        pass

    @abstractmethod
    def get_result(self, token: str, timeout_sec: int = 30) -> Dict[str, Any]:
        """
        Poll until execution completes and return standardized result.

        Returns:
            {
                'status_id': int,       # 判题状态 ID（3=Accepted, 4=Wrong Answer, etc.）
                'stdout': str,          # 程序标准输出
                'stderr': str,          # 程序标准错误
                'time': float,          # 执行时间（毫秒），可能为 None
                'memory': float,        # 内存使用量（MB），可能为 None
            }
        """
        pass

    @abstractmethod
    def get_language_id(self, language_name: str) -> int:
        """
        Map common language name to backend-specific ID.

        Example: 'python' → 71 (Judge0), or 1 (custom sandbox)
        """
        pass