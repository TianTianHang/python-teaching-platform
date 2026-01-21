"""日志中间件"""

import uuid
import time
import logging
from typing import Callable, Any, Dict, Optional, Union
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.http.request import HttpRequest as DjangoHttpRequest
from django.http.response import HttpResponseBase as DjangoHttpResponse
from ..utils.logging import RequestLogger, get_logger

logger = get_logger('common.middleware.logging_middleware')


class LoggingMiddleware:
    """日志中间件"""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: DjangoHttpRequest) -> DjangoHttpResponse:
        """处理请求和响应"""
        # 生成请求 ID
        request.id = str(uuid.uuid4())

        # 创建请求日志记录器
        request_logger = RequestLogger(request.id)

        # 开始计时
        start_time = time.time()

        # 记录请求信息
        request_logger.log_request(
            method=request.method,
            path=request.path,
            user_id=getattr(request.user, 'id', None),
            params=self._get_request_params(request),
            headers=self._get_request_headers(request),
            ip_address=self._get_client_ip(request)
        )

        # 处理请求
        response = self.get_response(request)

        # 计算响应时间
        duration_ms = (time.time() - start_time) * 1000

        # 记录响应信息
        request_logger.log_response(
            status_code=response.status_code,
            duration_ms=duration_ms,
            response_size=len(response.content) if hasattr(response, 'content') else None
        )

        # 如果是 5xx 错误，额外记录错误
        if 500 <= response.status_code < 600:
            request_logger.log_error(
                error=f"Server error: {response.status_code}",
                context={
                    'path': request.path,
                    'method': request.method
                }
            )

        # 添加请求 ID 到响应头（如果还没有）
        if 'X-Request-ID' not in response:
            response['X-Request-ID'] = request.id

        return response

    def process_exception(self, request: DjangoHttpRequest, exception: Exception) -> Optional[DjangoHttpResponse]:
        """处理异常"""
        request_id = getattr(request, 'id', str(uuid.uuid4()))

        request_logger = RequestLogger(request_id)

        # 记录异常信息
        request_logger.log_error(
            error=exception,
            context={
                'path': request.path,
                'method': request.method,
                'user_id': getattr(request.user, 'id', None)
            }
        )

        # 如果还没有请求 ID，添加到请求中
        if not hasattr(request, 'id'):
            request.id = request_id

        # 返回一个友好的错误响应
        if not settings.DEBUG:
            return JsonResponse(
                {
                    'error': 'Internal server error',
                    'request_id': request.id
                },
                status=500
            )

        # 开发环境返回原始异常
        return None

    def _get_request_params(self, request: DjangoHttpRequest) -> Dict[str, Any]:
        """获取请求参数"""
        params = {}

        # 获取 GET 参数
        if request.GET:
            params.update(dict(request.GET))

        # 获取 POST 参数（排除文件）
        if request.method in ['POST', 'PUT', 'PATCH'] and request.POST:
            try:
                post_params = dict(request.POST)
            except Exception:
                post_params = {}
            # 处理文件上传，记录文件信息而不是文件内容
            for key, value in post_params.items():
                if hasattr(value, 'name'):  # 文件对象
                    post_params[key] = {
                        'type': 'file',
                        'name': value.name,
                        'size': value.size
                    }
                else:
                    post_params[key] = str(value)
            params.update(post_params)

        # 获取 JSON 请求体
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_type == 'application/json':
                try:
                    import json
                    body = request.body.decode('utf-8')
                    json_data = json.loads(body)
                    params.update({'body': json_data})
                except (json.JSONDecodeError, UnicodeDecodeError, Exception):
                    pass  # JSON 解析失败，跳过

        return params

    def _get_request_headers(self, request: DjangoHttpRequest) -> Dict[str, str]:
        """获取请求头部（已脱敏）"""
        headers = {}
        sensitive_headers = {
            'authorization', 'cookie', 'set-cookie', 'x-api-key',
            'x-auth-token', 'proxy-authorization'
        }

        for key, value in request.headers.items():
            if key.lower() in sensitive_headers:
                headers[key] = '******'
            else:
                headers[key] = value

        return headers

    def _get_client_ip(self, request: DjangoHttpRequest) -> Optional[str]:
        """获取客户端 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip