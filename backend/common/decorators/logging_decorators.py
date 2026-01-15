"""日志装饰器"""

import functools
import time
import logging
import inspect
from typing import Callable, Any, Optional, Union
from django.http import HttpRequest, HttpResponse
from django.db.models import Model
from ..utils.logging import get_logger, PerformanceLogger, AuditLogger

logger = get_logger('common.decorators.logging_decorators')


def log_execution_time(threshold_ms: Optional[int] = None):
    """性能监控装饰器

    Args:
        threshold_ms: 性能警告阈值（毫秒），超过此值会记录警告日志
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求 ID（如果存在）
            request_id = None
            if args and isinstance(args[0], HttpRequest):
                request_id = getattr(args[0], 'id', None)

            perf_logger = PerformanceLogger(request_id=request_id)
            perf_logger.start_timer(func.__name__)

            try:
                result = func(*args, **kwargs)
                duration_ms = perf_logger.end_timer(threshold_ms)

                # 记录性能信息
                if duration_ms is not None:
                    logger.info(f"Function execution completed", extra={
                        'function': func.__name__,
                        'duration_ms': duration_ms,
                        'status': 'success',
                        'threshold_ms': threshold_ms
                    })

                return result

            except Exception as e:
                perf_logger.end_timer(threshold_ms)

                # 记录异常
                logger.error(f"Function execution failed", extra={
                    'function': func.__name__,
                    'error': str(e),
                    'status': 'failed'
                }, exc_info=True)

                raise

        return wrapper
    return decorator


def log_exceptions(default_return=None):
    """异常捕获装饰器

    Args:
        default_return: 异常发生时的返回值
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求 ID（如果存在）
            request_id = None
            if args and isinstance(args[0], HttpRequest):
                request_id = getattr(args[0], 'id', None)

            func_logger = get_logger('teaching_platform.api', request_id)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录异常信息
                func_logger.error(f"Exception in {func.__name__}: {str(e)}", extra={
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                    'request_id': request_id
                }, exc_info=True)

                if default_return is not None:
                    return default_return

                raise

        return wrapper
    return decorator


def audit_log(action_type: str):
    """审计日志装饰器

    Args:
        action_type: 操作类型（如 'login', 'logout', 'create_order'）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求 ID（如果存在）
            request_id = None
            user_id = None
            resource_id = None

            if args and isinstance(args[0], HttpRequest):
                request_id = getattr(args[0], 'id', None)
                user_id = getattr(args[0].user, 'id', None)
            elif args:
                # 尝试从第一个参数获取用户信息
                first_arg = args[0]
                if hasattr(first_arg, 'user'):
                    user_id = getattr(first_arg.user, 'id', None)
                elif hasattr(first_arg, 'id'):
                    resource_id = getattr(first_arg, 'id', None)

            # 创建审计日志记录器
            audit_logger = AuditLogger(request_id)

            # 记录操作开始
            audit_logger.log_sensitive_operation(
                operation=action_type,
                user_id=user_id,
                resource_type=func.__class__.__name__,
                resource_id=resource_id,
                details={
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
            )

            try:
                result = func(*args, **kwargs)

                # 记录操作成功
                if hasattr(result, 'id') and isinstance(result, Model):
                    audit_logger.log_sensitive_operation(
                        operation=f"{action_type}_success",
                        user_id=user_id,
                        resource_type=func.__class__.__name__,
                        resource_id=str(result.id),
                        details={'status': 'success'}
                    )

                return result

            except Exception as e:
                # 记录操作失败
                audit_logger.log_sensitive_operation(
                    operation=f"{action_type}_failure",
                    user_id=user_id,
                    resource_type=func.__class__.__name__,
                    resource_id=resource_id,
                    details={
                        'status': 'failed',
                        'error': str(e)
                    }
                )

                raise

        return wrapper
    return decorator


def log_api_call(include_params: bool = False, include_response: bool = False):
    """API 调用日志装饰器

    Args:
        include_params: 是否包含请求参数
        include_response: 是否包含响应数据
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求 ID（如果存在）
            request_id = None
            if args and isinstance(args[0], HttpRequest):
                request_id = getattr(args[0], 'id', None)

            api_logger = get_logger('teaching_platform.api', request_id)

            # 记录 API 调用开始
            start_time = time.time()

            log_data = {
                'event': 'api_call_start',
                'function': func.__name__,
                'request_id': request_id
            }

            if include_params and len(args) > 0 and isinstance(args[0], HttpRequest):
                log_data['method'] = args[0].method
                log_data['path'] = args[0].path
                log_data['user_id'] = getattr(args[0].user, 'id', None)
                log_data['params'] = dict(args[0].GET) if args[0].GET else None

            api_logger.info(f"API call started: {func.__name__}", extra=log_data)

            try:
                result = func(*args, **kwargs)

                # 计算执行时间
                duration_ms = (time.time() - start_time) * 1000

                # 记录 API 调用成功
                log_data = {
                    'event': 'api_call_success',
                    'function': func.__name__,
                    'duration_ms': duration_ms,
                    'request_id': request_id
                }

                if include_response and hasattr(result, 'status_code'):
                    log_data['response_status'] = result.status_code
                elif include_response and isinstance(result, dict):
                    log_data['response_size'] = len(str(result))

                api_logger.info(f"API call completed: {func.__name__}", extra=log_data)

                return result

            except Exception as e:
                # 计算执行时间
                duration_ms = (time.time() - start_time) * 1000

                # 记录 API 调用失败
                api_logger.error(f"API call failed: {func.__name__}", extra={
                    'event': 'api_call_error',
                    'function': func.__name__,
                    'duration_ms': duration_ms,
                    'error': str(e),
                    'request_id': request_id
                }, exc_info=True)

                raise

        return wrapper
    return decorator


def log_model_operations(model_class):
    """模型操作日志装饰器工厂

    为 Django 模型的 save、delete 等方法添加日志记录
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 获取请求 ID（如果存在）
            request_id = None
            if hasattr(self, '_request_id'):
                request_id = self._request_id
            elif len(args) > 0 and hasattr(args[0], 'id'):
                request_id = getattr(args[0], 'id', None)

            model_logger = get_logger(f'teaching_platform.models.{model_class.__name__}', request_id)

            # 记录操作开始
            operation = func.__name__

            log_data = {
                'event': f'model_{operation}_start',
                'model': model_class.__name__,
                'object_id': getattr(self, 'pk', None),
                'request_id': request_id
            }

            model_logger.info(f"Model operation started: {operation}", extra=log_data)

            try:
                result = func(self, *args, **kwargs)

                # 记录操作成功
                log_data = {
                    'event': f'model_{operation}_success',
                    'model': model_class.__name__,
                    'object_id': getattr(self, 'pk', None),
                    'request_id': request_id
                }

                model_logger.info(f"Model operation completed: {operation}", extra=log_data)

                return result

            except Exception as e:
                # 记录操作失败
                model_logger.error(f"Model operation failed: {operation}", extra={
                    'event': f'model_{operation}_error',
                    'model': model_class.__name__,
                    'object_id': getattr(self, 'pk', None),
                    'error': str(e),
                    'request_id': request_id
                }, exc_info=True)

                raise

        return wrapper
    return decorator


def log_database_operation(operation_type: str = 'query'):
    """数据库操作日志装饰器

    Args:
        operation_type: 操作类型（'query', 'create', 'update', 'delete'）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求 ID（如果存在）
            request_id = None
            if args and hasattr(args[0], 'id'):
                request_id = getattr(args[0], 'id', None)

            db_logger = get_logger('teaching_platform.database', request_id)

            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                duration_ms = (time.time() - start_time) * 1000

                db_logger.debug(f"Database operation completed", extra={
                    'operation': operation_type,
                    'duration_ms': duration_ms,
                    'request_id': request_id
                })

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                db_logger.error(f"Database operation failed", extra={
                    'operation': operation_type,
                    'duration_ms': duration_ms,
                    'error': str(e),
                    'request_id': request_id
                }, exc_info=True)

                raise

        return wrapper
    return decorator