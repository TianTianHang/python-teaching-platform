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

    This class collects cache performance metrics using Redis and provides:
    - Real-time statistics per endpoint (hits, misses, null_values, duration, slow_operations)
    - Periodic performance summary logs (every 60 seconds)
    - Performance anomaly detection and alerts (low hit rate, high penetration rate, slow operations)
    - Alert suppression to prevent alert fatigue (5-minute window)
    - Cross-process data sharing (Django and Celery processes can access the same stats)

    Statistics are stored in Redis Hash and aggregated per endpoint.

    Storage:
        Redis Keys: cache:perf:stats:{endpoint}
        Fields: hits, misses, null_values, total_duration_ms, slow_operations
        TTL: 300 seconds (auto-cleanup)

        Alert suppression: cache:perf:alerts:{endpoint}
        Fields: {alert_type}: timestamp
        TTL: 300 seconds

    Public Methods:
        record_cache_operation(endpoint, operation_type, duration_ms, is_slow):
            Record a single cache operation and update statistics.

        get_endpoint_stats(endpoint) -> Dict[str, Any]:
            Get statistics for a single endpoint.

        get_all_endpoint_stats() -> Dict[str, Dict[str, Any]]:
            Get statistics for all endpoints.

        get_global_stats() -> Dict[str, Any]:
            Get aggregated global statistics across all endpoints.

        reset_stats():
            Reset all statistics to zero (delete all Redis keys).

        check_low_hit_rate(endpoint, threshold=0.8) -> Optional[Dict[str, Any]]:
            Check if endpoint has low hit rate below threshold.

        check_high_penetration_rate(endpoint, threshold=0.1) -> Optional[Dict[str, Any]]:
            Check if endpoint has high penetration rate above threshold.

        check_slow_operations(endpoint, threshold_ms=100.0) -> Optional[Dict[str, Any]]:
            Check if endpoint has high slow operation rate.

        log_performance_summary():
            Log periodic performance summary with all statistics and alerts.

    Example:
        >>> logger = CachePerformanceLogger()
        >>> logger.record_cache_operation('CourseViewSet', 'hit', duration_ms=2.5)
        >>> logger.record_cache_operation('CourseViewSet', 'miss', duration_ms=50.0)
        >>> stats = logger.get_endpoint_stats('CourseViewSet')
        >>> print(stats['hit_rate'])  # 0.5

    Configuration:
        Alert thresholds are configured in settings.py:
        CACHE_PERFORMANCE_ALERT_THRESHOLDS = {
            'low_hit_rate': 0.8,              # Alert if hit rate < 80%
            'high_penetration_rate': 0.1,     # Alert if penetration rate > 10%
            'slow_operation_ms': 100,         # Slow operation threshold in ms
            'high_error_rate': 0.05,          # Alert if error rate > 5%
        }

        Redis configuration:
        CACHE_STATS_KEY_PREFIX = "cache:perf:stats"
        CACHE_ALERTS_KEY_PREFIX = "cache:perf:alerts"
        CACHE_STATS_TTL = 300  # seconds
    """

    def __init__(self):
        self._logger = logging.getLogger('teaching_platform.cache')
        # Get configuration from settings
        from django.conf import settings
        self._stats_key_prefix = getattr(settings, 'CACHE_STATS_KEY_PREFIX', 'cache:perf:stats')
        self._alerts_key_prefix = getattr(settings, 'CACHE_ALERTS_KEY_PREFIX', 'cache:perf:alerts')
        self._stats_ttl = getattr(settings, 'CACHE_STATS_TTL', 300)  # 5 minutes default

    def record_cache_operation(
        self,
        endpoint: str,
        operation_type: str,
        duration_ms: Optional[float] = None,
        is_slow: bool = False
    ):
        """
        Record a cache operation and update statistics in Redis.

        Args:
            endpoint: The endpoint/view name
            operation_type: One of 'hit', 'miss', 'null_value'
            duration_ms: Operation duration in milliseconds (optional)
            is_slow: Whether this operation exceeded the slow threshold
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            # Use a pipeline for atomic operations
            pipe = redis_conn.pipeline(transaction=True)

            # Redis key for this endpoint
            key = f"{self._stats_key_prefix}:{endpoint}"

            # Increment counters
            if operation_type == 'hit':
                pipe.hincrby(key, 'hits', 1)
            elif operation_type == 'miss':
                pipe.hincrby(key, 'misses', 1)
            elif operation_type == 'null_value':
                pipe.hincrby(key, 'null_values', 1)

            # Add duration if provided
            if duration_ms is not None:
                pipe.hincrbyfloat(key, 'total_duration_ms', duration_ms)

            # Increment slow operations counter
            if is_slow:
                pipe.hincrby(key, 'slow_operations', 1)

            # Set TTL to auto-cleanup
            pipe.expire(key, self._stats_ttl)

            # Execute all commands atomically
            pipe.execute()

        except Exception as e:
            # Don't let stats recording errors affect cache operations
            self._logger.debug(f"Failed to record cache stats: {e}")

    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """
        Get statistics for a single endpoint from Redis.

        Args:
            endpoint: The endpoint name

        Returns:
            Dictionary with hits, misses, null_values, hit_rate, avg_duration_ms, etc.
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            key = f"{self._stats_key_prefix}:{endpoint}"
            stats = redis_conn.hgetall(key)

            if not stats:
                # No stats for this endpoint yet
                return {
                    'endpoint': endpoint,
                    'hits': 0,
                    'misses': 0,
                    'null_values': 0,
                    'total_requests': 0,
                    'total_operations': 0,
                    'hit_rate': None,
                    'miss_rate': None,
                    'penetration_rate': None,
                    'avg_duration_ms': None,
                    'slow_operations': 0,
                    'slow_operation_rate': None,
                }

            # Redis returns bytes, convert to int/float
            hits = int(stats.get(b'hits', 0))
            misses = int(stats.get(b'misses', 0))
            null_values = int(stats.get(b'null_values', 0))
            total_duration_ms = float(stats.get(b'total_duration_ms', 0))
            slow_operations = int(stats.get(b'slow_operations', 0))
            total_operations = int(stats.get(b'total_operations', 0))

            # Use total_operations if available, otherwise fall back to old calculation
            # This provides backward compatibility with existing data
            if total_operations > 0:
                total_requests = total_operations
            else:
                total_requests = hits + misses + null_values

            return {
                'endpoint': endpoint,
                'hits': hits,
                'misses': misses,
                'null_values': null_values,
                'total_requests': total_requests,
                'total_operations': total_operations,  # NEW: expose total_operations
                'hit_rate': self._calculate_hit_rate(hits, total_requests),
                'miss_rate': self._calculate_miss_rate(hits, total_requests),
                'penetration_rate': self._calculate_penetration_rate(
                    null_values, total_requests
                ),
                'avg_duration_ms': self._calculate_avg_duration(
                    total_duration_ms, total_requests
                ),
                'slow_operations': slow_operations,
                'slow_operation_rate': self._calculate_slow_rate(
                    slow_operations, total_requests
                )
            }
        except Exception as e:
            self._logger.debug(f"Failed to get endpoint stats: {e}")
            return {
                'endpoint': endpoint,
                'hits': 0,
                'misses': 0,
                'null_values': 0,
                'total_requests': 0,
                'total_operations': 0,
                'hit_rate': None,
                'miss_rate': None,
                'penetration_rate': None,
                'avg_duration_ms': None,
                'slow_operations': 0,
                'slow_operation_rate': None,
            }

    def get_all_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all endpoints from Redis.

        Returns:
            Dictionary mapping endpoint names to their statistics
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            # Scan for all keys matching the pattern
            pattern = f"{self._stats_key_prefix}:*"
            all_stats = {}

            for key in redis_conn.scan_iter(match=pattern, count=100):
                # Extract endpoint name from key
                key_str = key.decode() if isinstance(key, bytes) else key
                endpoint = key_str.split(':')[-1]

                # Get stats for this endpoint
                stats = self.get_endpoint_stats(endpoint)
                if stats.get('total_requests', 0) > 0:
                    all_stats[endpoint] = stats

            return all_stats
        except Exception as e:
            self._logger.debug(f"Failed to get all endpoint stats: {e}")
            return {}

    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get aggregated statistics across all endpoints from Redis.

        Returns:
            Dictionary with global hit_rate, avg_duration_ms, total_requests, etc.
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            # Scan for all keys matching the pattern
            pattern = f"{self._stats_key_prefix}:*"
            total_hits = 0
            total_misses = 0
            total_null_values = 0
            total_duration_ms = 0.0
            total_slow_operations = 0
            endpoint_count = 0

            total_operations = 0
            for key in redis_conn.scan_iter(match=pattern, count=100):
                stats = redis_conn.hgetall(key)
                if stats:
                    total_hits += int(stats.get(b'hits', 0))
                    total_misses += int(stats.get(b'misses', 0))
                    total_null_values += int(stats.get(b'null_values', 0))
                    total_duration_ms += float(stats.get(b'total_duration_ms', 0))
                    total_slow_operations += int(stats.get(b'slow_operations', 0))
                    total_operations += int(stats.get(b'total_operations', 0))
                    endpoint_count += 1

            # Use total_operations if available, otherwise fall back to old calculation
            # This provides backward compatibility with existing data
            if total_operations > 0:
                total_requests = total_operations
            else:
                total_requests = total_hits + total_misses + total_null_values

            return {
                'total_requests': total_requests,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'total_null_values': total_null_values,
                'total_operations': total_operations,  # NEW: expose total_operations
                'hit_rate': self._calculate_hit_rate(total_hits, total_requests),
                'miss_rate': self._calculate_miss_rate(total_hits, total_requests),
                'penetration_rate': self._calculate_penetration_rate(total_null_values, total_requests),
                'avg_duration_ms': self._calculate_avg_duration(total_duration_ms, total_requests),
                'total_slow_operations': total_slow_operations,
                'slow_operation_rate': self._calculate_slow_rate(total_slow_operations, total_requests),
                'endpoint_count': endpoint_count
            }
        except Exception as e:
            self._logger.debug(f"Failed to get global stats: {e}")
            return {
                'total_requests': 0,
                'total_hits': 0,
                'total_misses': 0,
                'total_null_values': 0,
                'total_operations': 0,
                'hit_rate': None,
                'miss_rate': None,
                'penetration_rate': None,
                'avg_duration_ms': None,
                'total_slow_operations': 0,
                'slow_operation_rate': None,
                'endpoint_count': 0
            }

    def reset_stats(self):
        """Reset all statistics by deleting all Redis keys."""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            # Scan for all keys matching the pattern and delete them
            pattern = f"{self._stats_key_prefix}:*"
            keys_to_delete = []

            for key in redis_conn.scan_iter(match=pattern, count=100):
                keys_to_delete.append(key)

                # Delete in batches to avoid blocking
                if len(keys_to_delete) >= 100:
                    redis_conn.delete(*keys_to_delete)
                    keys_to_delete = []

            # Delete remaining keys
            if keys_to_delete:
                redis_conn.delete(*keys_to_delete)

        except Exception as e:
            self._logger.debug(f"Failed to reset stats: {e}")

    def _calculate_hit_rate(self, hits: int, total_requests: int) -> Optional[float]:
        """Calculate hit rate using total_requests as denominator."""
        if total_requests == 0:
            return None
        return hits / total_requests

    def _calculate_miss_rate(self, hits: int, total_requests: int) -> Optional[float]:
        """Calculate miss rate using total_requests as denominator."""
        if total_requests == 0:
            return None
        return (total_requests - hits) / total_requests

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

    def check_low_hit_rate(self, endpoint: str, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        Check if endpoint has low hit rate.

        Args:
            endpoint: The endpoint name
            threshold: Hit rate threshold (default 0.8)

        Returns:
            Alert dict if hit rate is below threshold, None otherwise
        """
        stats = self.get_endpoint_stats(endpoint)
        if not stats or stats['hit_rate'] is None:
            return None

        if stats['hit_rate'] < threshold:
            return {
                'type': 'low_hit_rate',
                'endpoint': endpoint,
                'value': stats['hit_rate'],
                'threshold': threshold,
                'severity': 'WARNING'
            }
        return None

    def check_high_penetration_rate(self, endpoint: str, threshold: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Check if endpoint has high penetration rate.

        Args:
            endpoint: The endpoint name
            threshold: Penetration rate threshold (default 0.1)

        Returns:
            Alert dict if penetration rate is above threshold, None otherwise
        """
        stats = self.get_endpoint_stats(endpoint)
        if not stats or stats['penetration_rate'] is None:
            return None

        if stats['penetration_rate'] > threshold:
            return {
                'type': 'high_penetration_rate',
                'endpoint': endpoint,
                'value': stats['penetration_rate'],
                'threshold': threshold,
                'null_value_count': stats['null_values'],
                'total_requests': stats['total_requests'],
                'severity': 'WARNING'
            }
        return None

    def check_high_error_rate(self, endpoint: str, threshold: float = 0.05) -> Optional[Dict[str, Any]]:
        """
        Check if endpoint has high error rate.

        Args:
            endpoint: The endpoint name
            threshold: Error rate threshold (default 0.05)

        Returns:
            Alert dict if error rate is above threshold, None otherwise
        """
        # Note: Error tracking would need to be implemented in record_cache_operation
        # For now, return None as we don't have error tracking yet
        return None

    def check_slow_operations(self, endpoint: str, threshold_ms: float = 100.0) -> Optional[Dict[str, Any]]:
        """
        Check if endpoint has high slow operation rate.

        Args:
            endpoint: The endpoint name
            threshold_ms: Slow operation threshold in ms (default 100ms)

        Returns:
            Alert dict if slow operation rate is high, None otherwise
        """
        stats = self.get_endpoint_stats(endpoint)
        if not stats or stats['slow_operation_rate'] is None:
            return None

        # Alert if more than 20% of operations are slow
        if stats['slow_operation_rate'] > 0.2:
            return {
                'type': 'high_slow_operation_rate',
                'endpoint': endpoint,
                'slow_rate': stats['slow_operation_rate'],
                'slow_threshold_ms': threshold_ms,
                'avg_duration_ms': stats['avg_duration_ms'],
                'severity': 'WARNING'
            }
        return None

    def _should_suppress_alert(self, endpoint: str, alert_type: str, suppress_seconds: int = 300) -> bool:
        """
        Check if alert should be suppressed (5 minute window) using Redis.

        Args:
            endpoint: The endpoint name
            alert_type: Type of alert
            suppress_seconds: Suppression window in seconds (default 300 = 5 minutes)

        Returns:
            True if alert should be suppressed, False otherwise
        """
        import time
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            # Redis key for alert suppression
            key = f"{self._alerts_key_prefix}:{endpoint}"
            field = alert_type

            now = time.time()
            last_alert_bytes = redis_conn.hget(key, field)

            if last_alert_bytes:
                last_alert = float(last_alert_bytes)
                if (now - last_alert) < suppress_seconds:
                    return True

            # Update last alert time
            pipe = redis_conn.pipeline(transaction=True)
            pipe.hset(key, field, now)
            pipe.expire(key, suppress_seconds)
            pipe.execute()

            return False
        except Exception as e:
            self._logger.debug(f"Failed to check alert suppression: {e}")
            return False

    def log_performance_summary(self):
        """
        Log periodic performance summary with alerts.

        Generates a structured JSON log entry containing:
        - Global statistics
        - Per-endpoint statistics
        - Top 5 slowest endpoints
        - Top 5 endpoints with lowest hit rates
        - Active alerts
        """
        try:
            from django.conf import settings

            # Get thresholds from settings
            thresholds = getattr(settings, 'CACHE_PERFORMANCE_ALERT_THRESHOLDS', {
                'low_hit_rate': 0.8,
                'high_penetration_rate': 0.1,
                'slow_operation_ms': 100,
                'high_error_rate': 0.05
            })

            # Get all statistics
            global_stats = self.get_global_stats()
            all_endpoints = self.get_all_endpoint_stats()

            # Get top 5 slowest endpoints
            sorted_by_duration = sorted(
                [e for e in all_endpoints.values() if e.get('avg_duration_ms') is not None],
                key=lambda x: x['avg_duration_ms'],
                reverse=True
            )[:5]

            # Get top 5 endpoints with lowest hit rates
            sorted_by_hit_rate = sorted(
                [e for e in all_endpoints.values() if e.get('hit_rate') is not None],
                key=lambda x: x['hit_rate']
            )[:5]

            # Collect alerts
            alerts = []
            for endpoint in all_endpoints.keys():
                # Check low hit rate
                alert = self.check_low_hit_rate(endpoint, thresholds['low_hit_rate'])
                if alert and not self._should_suppress_alert(endpoint, 'low_hit_rate'):
                    alerts.append(alert)

                # Check high penetration rate
                alert = self.check_high_penetration_rate(endpoint, thresholds['high_penetration_rate'])
                if alert and not self._should_suppress_alert(endpoint, 'high_penetration_rate'):
                    alerts.append(alert)

                # Check slow operations
                alert = self.check_slow_operations(endpoint, thresholds['slow_operation_ms'])
                if alert and not self._should_suppress_alert(endpoint, 'high_slow_operation_rate'):
                    alerts.append(alert)

            # Log the summary
            self._logger.info(
                "Cache performance summary",
                extra={
                    'event': 'cache_performance_summary',
                    'period': '60s',
                    'global': global_stats,
                    'endpoints': all_endpoints,
                    'top_slow_endpoints': sorted_by_duration,
                    'top_low_hit_rate_endpoints': sorted_by_hit_rate,
                    'alerts': alerts
                }
            )

            # Log individual alerts
            for alert in alerts:
                self._logger.warning(
                    f"Cache performance alert: {alert['type']}",
                    extra={
                        'event': 'cache_performance_alert',
                        **alert
                    }
                )

        except Exception as e:
            self._logger.error(f"Failed to generate performance summary: {e}")


# Global instance for cache performance logging
_cache_performance_logger = CachePerformanceLogger()