"""日志工具类"""

import logging
import uuid
import time
import json as json_module
from typing import Dict, Any, Optional, Union, Any as TypingAny
import pythonjsonlogger.jsonlogger as jsonlogger
from ..exceptions import BaseAPIException


class DetailedFormatter(logging.Formatter):
    """自定义日志格式化器，将 extra 字段以易读格式输出"""

    def format(self, record: logging.LogRecord) -> str:
        # 先调用父类方法格式化基本日志信息
        result = super().format(record)

        # 如果有 extra 字段，格式化输出
        if hasattr(record, 'params') or hasattr(record, 'headers') or \
           hasattr(record, 'method') or hasattr(record, 'path') or \
           hasattr(record, 'user_id') or hasattr(record, 'status_code') or \
           hasattr(record, 'duration_ms') or hasattr(record, 'request_id'):

            extra_parts = []

            # 常见字段
            if hasattr(record, 'request_id'):
                extra_parts.append(f"request_id={record.request_id}")
            if hasattr(record, 'method'):
                extra_parts.append(f"method={record.method}")
            if hasattr(record, 'path'):
                extra_parts.append(f"path={record.path}")
            if hasattr(record, 'user_id') and record.user_id is not None:
                extra_parts.append(f"user_id={record.user_id}")
            if hasattr(record, 'status_code'):
                extra_parts.append(f"status_code={record.status_code}")
            if hasattr(record, 'duration_ms'):
                extra_parts.append(f"duration_ms={record.duration_ms:.2f}")

            # 复杂字段（需要格式化）
            if hasattr(record, 'params') and record.params:
                params_str = self._format_complex_data(record.params)
                extra_parts.append(f"params={params_str}")
            if hasattr(record, 'headers') and record.headers:
                headers_str = self._format_complex_data(record.headers)
                extra_parts.append(f"headers={headers_str}")
            if hasattr(record, 'ip_address'):
                extra_parts.append(f"ip={record.ip_address}")
            if hasattr(record, 'response_size'):
                extra_parts.append(f"size={record.response_size}")

            if extra_parts:
                result = f"{result} | {' '.join(extra_parts)}"

        return result

    def _format_complex_data(self, data: Any, max_length: int = 200) -> str:
        """格式化复杂数据结构"""
        try:
            json_str = json_module.dumps(data, ensure_ascii=False, default=str)
            if len(json_str) > max_length:
                json_str = json_str[:max_length] + "..."
            return json_str
        except Exception:
            return str(data)[:max_length]


def get_logger(name: str, request_id: Optional[str] = None) -> logging.Logger:
    """
    获取配置好的 logger，支持请求 ID 追踪

    Args:
        name: logger 名称
        request_id: 请求 ID（可选）

    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)

    # 返回 logger，request_id 会在每次调用日志时通过 extra 传递
    return logger


class RequestLogger:
    """请求日志记录器"""

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.logger = get_logger('teaching_platform.api', self.request_id)
        self.start_time = time.time()

    def log_request(
        self,
        method: str,
        path: str,
        user_id: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None
    ):
        """记录请求信息"""
        # 脱敏处理
        sanitized_params = self._sanitize_params(params) if params else None
        sanitized_headers = self._sanitize_headers(headers) if headers else None

        self.logger.info("HTTP request received", extra={
            'event': 'request_received',
            'method': method,
            'path': path,
            'user_id': user_id,
            'params': sanitized_params,
            'headers': sanitized_headers,
            'ip_address': ip_address,
            'request_id': self.request_id,
            'start_time': time.time()
        })

    def log_response(
        self,
        status_code: int,
        duration_ms: float,
        response_size: Optional[int] = None,
        error: Optional[str] = None
    ):
        """记录响应信息"""
        self.logger.info("HTTP response sent", extra={
            'event': 'response_sent',
            'status_code': status_code,
            'duration_ms': duration_ms,
            'response_size': response_size,
            'error': error,
            'request_id': self.request_id
        })

    def log_error(
        self,
        error: Union[Exception, str],
        context: Optional[Dict[str, Any]] = None
    ):
        """记录错误信息"""
        error_msg = str(error) if isinstance(error, Exception) else error
        error_type = type(error).__name__ if isinstance(error, Exception) else type(error)

        self.logger.error(f"Request error: {error_msg}", extra={
            'event': 'request_error',
            'error_type': error_type,
            'error_message': error_msg,
            'context': context or {},
            'request_id': self.request_id
        }, exc_info=isinstance(error, Exception))

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """脱敏敏感参数"""
        sensitive_fields = {'password', 'token', 'Authorization', 'api_key', 'secret'}
        sanitized = {}

        for key, value in params.items():
            if key.lower() in sensitive_fields:
                sanitized[key] = '******'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, dict):
                        sanitized_list.append(self._sanitize_params(item))
                    else:
                        # 简单字符串或基本类型，直接检查是否包含敏感信息
                        if isinstance(item, str) and any(field in item.lower() for field in sensitive_fields):
                            sanitized_list.append('******')
                        else:
                            sanitized_list.append(item)
                sanitized[key] = sanitized_list
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """脱敏敏感头部"""
        sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        sanitized = {}

        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = '******'
            else:
                sanitized[key] = value

        return sanitized


class PerformanceLogger:
    """性能监控器"""

    def __init__(self, logger_name: str = 'teaching_platform.performance', request_id: Optional[str] = None):
        self.logger = get_logger(logger_name, request_id)
        self.start_time = time.time()

    def start_timer(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """开始计时"""
        self.operation = operation
        self.logger.debug(f"Performance timer started: {operation}", extra={
            'event': 'timer_start',
            'operation': operation,
            'start_time': time.time(),
            'details': details or {}
        })

    def end_timer(self, threshold_ms: Optional[int] = None, additional_info: Optional[Dict[str, Any]] = None):
        """结束计时"""
        if not hasattr(self, 'operation'):
            return

        duration_ms = (time.time() - self.start_time) * 1000

        log_data = {
            'event': 'timer_end',
            'operation': self.operation,
            'duration_ms': duration_ms,
            'threshold_ms': threshold_ms
        }

        if additional_info:
            log_data.update(additional_info)

        if threshold_ms and duration_ms > threshold_ms:
            self.logger.warning(f"Slow operation detected: {self.operation} took {duration_ms:.2f}ms", extra=log_data)
        else:
            self.logger.info(f"Operation completed: {self.operation} took {duration_ms:.2f}ms", extra=log_data)

        return duration_ms


class AuditLogger:
    """审计日志记录器"""

    def __init__(self, request_id: Optional[str] = None):
        self.logger = get_logger('teaching_platform.security', request_id)

    def log_auth_success(
        self,
        user_id: Optional[int],
        username: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str] = None,
        action: str = 'login_success'
    ):
        """记录认证成功事件"""
        self.logger.info(f"Authentication successful: {action}", extra={
            'event': 'auth_success',
            'action': action,
            'user_id': user_id,
            'username': username,
            'ip_address': ip_address,
            'user_agent': user_agent
        })

    def log_auth_failure(
        self,
        username: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str] = None,
        reason: Optional[str] = None,
        action: str = 'login_failure'
    ):
        """记录认证失败事件"""
        self.logger.warning(f"Authentication failed: {action}", extra={
            'event': 'auth_failure',
            'action': action,
            'username': username,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'reason': reason
        })

    def log_sensitive_operation(
        self,
        operation: str,
        user_id: Optional[int],
        resource_type: Optional[str],
        resource_id: Optional[str],
        details: Optional[Dict[str, Any]] = None
    ):
        """记录敏感操作事件"""
        self.logger.info(f"Sensitive operation performed: {operation}", extra={
            'event': 'sensitive_operation',
            'operation': operation,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {}
        })

    def log_data_change(
        self,
        change_type: str,  # create, update, delete
        model_name: str,
        object_id: Optional[str],
        user_id: Optional[int],
        changes: Optional[Dict[str, Any]] = None
    ):
        """记录数据变更事件"""
        self.logger.info(f"Data {change_type} operation", extra={
            'event': 'data_change',
            'change_type': change_type,
            'model_name': model_name,
            'object_id': object_id,
            'user_id': user_id,
            'changes': changes or {}
        })

    def log_payment_operation(
        self,
        operation: str,
        order_number: str,
        user_id: Optional[int],
        amount: Optional[float],
        payment_method: Optional[str] = None,
        status: Optional[str] = None
    ):
        """记录支付相关操作"""
        self.logger.info(f"Payment operation: {operation}", extra={
            'event': 'payment_operation',
            'operation': operation,
            'order_number': order_number,
            'user_id': user_id,
            'amount': amount,
            'payment_method': payment_method,
            'status': status
        })

    def log_file_operation(
        self,
        operation: str,
        file_id: Optional[str],
        file_path: Optional[str],
        user_id: Optional[int],
        file_size: Optional[int] = None,
        file_type: Optional[str] = None
    ):
        """记录文件操作事件"""
        self.logger.info(f"File operation: {operation}", extra={
            'event': 'file_operation',
            'operation': operation,
            'file_id': file_id,
            'file_path': file_path,
            'user_id': user_id,
            'file_size': file_size,
            'file_type': file_type
        })


def setup_json_formatter(date_format: str = '%Y-%m-%d %H:%M:%S') -> TypingAny:
    """设置 JSON 格式化器"""
    return jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt=date_format
    )


class CachePerformanceLogger:
    """
    Cache performance statistics collector and logger.

    Collects cache performance metrics in memory and provides:
    - Real-time statistics per endpoint
    - Periodic performance summary logs
    - Performance anomaly detection and alerts

    Statistics are aggregated per endpoint and reset after each summary log.
    """

    def __init__(self):
        from collections import defaultdict
        self._stats = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'null_values': 0,
            'total_duration_ms': 0.0,
            'slow_operations': 0,
        })
        self._last_alert_time = defaultdict(dict)  # endpoint -> alert_type -> timestamp
        self._logger = logging.getLogger('teaching_platform.cache')

    def record_cache_operation(
        self,
        endpoint: str,
        operation_type: str,
        duration_ms: Optional[float] = None,
        is_slow: bool = False
    ):
        """
        Record a cache operation and update statistics.

        Args:
            endpoint: The endpoint/view name
            operation_type: One of 'hit', 'miss', 'null_value'
            duration_ms: Operation duration in milliseconds (optional)
            is_slow: Whether this operation exceeded the slow threshold
        """
        try:
            stats = self._stats[endpoint]

            if operation_type == 'hit':
                stats['hits'] += 1
            elif operation_type == 'miss':
                stats['misses'] += 1
            elif operation_type == 'null_value':
                stats['null_values'] += 1

            if duration_ms is not None:
                stats['total_duration_ms'] += duration_ms

            if is_slow:
                stats['slow_operations'] += 1
        except Exception as e:
            # Don't let stats recording errors affect cache operations
            self._logger.debug(f"Failed to record cache stats: {e}")

    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """
        Get statistics for a single endpoint.

        Args:
            endpoint: The endpoint name

        Returns:
            Dictionary with hits, misses, null_values, hit_rate, avg_duration_ms, etc.
        """
        stats = self._stats.get(endpoint)
        if not stats:
            return {}

        total_requests = stats['hits'] + stats['misses'] + stats['null_values']

        return {
            'endpoint': endpoint,
            'hits': stats['hits'],
            'misses': stats['misses'],
            'null_values': stats['null_values'],
            'total_requests': total_requests,
            'hit_rate': self._calculate_hit_rate(stats['hits'], stats['misses']),
            'miss_rate': self._calculate_miss_rate(stats['hits'], stats['misses']),
            'penetration_rate': self._calculate_penetration_rate(
                stats['null_values'], total_requests
            ),
            'avg_duration_ms': self._calculate_avg_duration(
                stats['total_duration_ms'], total_requests
            ),
            'slow_operations': stats['slow_operations'],
            'slow_operation_rate': self._calculate_slow_rate(
                stats['slow_operations'], total_requests
            )
        }

    def get_all_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all endpoints.

        Returns:
            Dictionary mapping endpoint names to their statistics
        """
        return {
            endpoint: self.get_endpoint_stats(endpoint)
            for endpoint in self._stats.keys()
        }

    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get aggregated statistics across all endpoints.

        Returns:
            Dictionary with global hit_rate, avg_duration_ms, total_requests, etc.
        """
        total_hits = sum(s['hits'] for s in self._stats.values())
        total_misses = sum(s['misses'] for s in self._stats.values())
        total_null_values = sum(s['null_values'] for s in self._stats.values())
        total_duration_ms = sum(s['total_duration_ms'] for s in self._stats.values())
        total_slow_operations = sum(s['slow_operations'] for s in self._stats.values())

        total_requests = total_hits + total_misses + total_null_values

        return {
            'total_requests': total_requests,
            'total_hits': total_hits,
            'total_misses': total_misses,
            'total_null_values': total_null_values,
            'hit_rate': self._calculate_hit_rate(total_hits, total_misses),
            'miss_rate': self._calculate_miss_rate(total_hits, total_misses),
            'penetration_rate': self._calculate_penetration_rate(total_null_values, total_requests),
            'avg_duration_ms': self._calculate_avg_duration(total_duration_ms, total_requests),
            'total_slow_operations': total_slow_operations,
            'slow_operation_rate': self._calculate_slow_rate(total_slow_operations, total_requests),
            'endpoint_count': len(self._stats)
        }

    def reset_stats(self):
        """Reset all statistics to zero."""
        self._stats.clear()

    def _calculate_hit_rate(self, hits: int, misses: int) -> Optional[float]:
        """Calculate hit rate from hits and misses."""
        total = hits + misses
        if total == 0:
            return None
        return hits / total

    def _calculate_miss_rate(self, hits: int, misses: int) -> Optional[float]:
        """Calculate miss rate from hits and misses."""
        total = hits + misses
        if total == 0:
            return None
        return misses / total

    def _calculate_penetration_rate(self, null_values: int, total_requests: int) -> Optional[float]:
        """Calculate cache penetration rate."""
        if total_requests == 0:
            return None
        return null_values / total_requests

    def _calculate_avg_duration(self, total_duration_ms: float, total_requests: int) -> Optional[float]:
        """Calculate average operation duration."""
        if total_requests == 0:
            return None
        return total_duration_ms / total_requests

    def _calculate_slow_rate(self, slow_operations: int, total_requests: int) -> Optional[float]:
        """Calculate slow operation rate."""
        if total_requests == 0:
            return None
        return slow_operations / total_requests


# Global instance for cache performance logging
_cache_performance_logger = CachePerformanceLogger()