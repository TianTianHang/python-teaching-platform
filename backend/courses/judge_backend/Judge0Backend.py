import time
from typing import Any, Dict, Optional

from django.conf import settings
import requests

from .CodeJudgingBackend import CodeJudgingBackend




class Judge0Backend(CodeJudgingBackend):
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
        self.base_url = getattr(settings, 'JUDGE0_BASE_URL', 'http://192.168.122.137:2358')
        self.headers = {'Content-Type': 'application/json'}

    def submit_code(
        self,
        source_code: str,
        language_id: int,
        stdin: str = "",
        expected_output: Optional[str] = None,
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 128,
    ) -> Dict[str, Any]:
        # Convert to Judge0 units: seconds and KB
        cpu_time_limit_sec = time_limit_ms / 1000.0
        memory_limit_kb = memory_limit_mb * 1024  # 1 MB = 1024 KB

        url = f"{self.base_url}/submissions"
        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin,
            "cpu_time_limit": cpu_time_limit_sec,
            "memory_limit": memory_limit_kb,
        }
        if expected_output is not None:
            payload["expected_output"] = expected_output

        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Judge0 submission failed: {response.status_code} - {response.text}")

    def get_result(self, token: str, timeout_sec: int = 30) -> Dict[str, Any]:
        start = time.time()
        while time.time() - start < timeout_sec:
            url = f"{self.base_url}/submissions/{token}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                status_id = data.get("status", {}).get("id", 0)
                if status_id >= 3:  # Final state
                    # Convert Judge0 output units to ms and MB
                    raw_time_sec = data.get("time")        # seconds or None
                    raw_memory_kb = data.get("memory")     # KB or None

                   # Convert time: str -> float -> ms
                    if raw_time_sec is not None:
                        try:
                            time_sec = float(raw_time_sec)
                            time_ms = time_sec * 1000.0
                        except (ValueError, TypeError):
                            time_ms = None
                    else:
                        time_ms = None

                    # Convert memory: str -> float -> MB
                    if raw_memory_kb is not None:
                        try:
                            memory_kb = float(raw_memory_kb)
                            memory_mb = round(memory_kb / 1024.0,2)
                        except (ValueError, TypeError):
                            memory_mb = None
                    else:
                        memory_mb = None
                   
                    return {
                        "status_id": status_id,
                        "stdout": data.get("stdout", "") or "",
                        "stderr": data.get("stderr", "") or "",
                        "time": time_ms,
                        "memory": memory_mb,
                    }
            time.sleep(0.5)

        raise TimeoutError("Judge0 result polling timed out")

    def get_language_id(self, language_name: str) -> int:
        return self.LANGUAGE_IDS.get(language_name.lower(), 71)