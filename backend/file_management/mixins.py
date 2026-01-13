"""
Mixin classes for file management API.
"""

import os
import logging
from django.db import models
from django.http import FileResponse, Http404, HttpResponse, HttpResponseNotModified
from django.utils.encoding import smart_str
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

logger = logging.getLogger(__name__)


class FileDownloadMixin:
    """
    文件下载 Mixin，提供统一的文件下载逻辑。

    特点：
    - 使用 FileResponse 流式传输，避免内存溢出
    - 统一的权限检查
    - 支持本地存储和云存储
    - 正确处理文件类型和编码
    """

    def _handle_file_download(self, file_entry, request):
        """
        处理文件下载逻辑。

        Args:
            file_entry: FileEntry 实例
            request: HTTP 请求对象

        Returns:
            FileResponse 或 Response

        Raises:
            Http404: 文件不存在
            PermissionDenied: 没有权限
        """
        # 检查文件是否存在
        if not file_entry.file:
            raise Http404("File not found")

        # 检查权限
        if (not file_entry.is_public and
            file_entry.owner != request.user and
            not request.user.is_staff):
            raise PermissionDenied("No permission to download this file")

        # 获取文件对象
        file_obj = file_entry.file

        # 获取文件路径（本地存储）或 URL（云存储）
        try:
            if hasattr(file_obj, 'path'):
                file_path = file_obj.path
                is_local = file_entry.storage_backend == 'local'
            else:
                file_path = file_obj.name if hasattr(file_obj, 'name') else None
                is_local = False
        except Exception:
            # 如果无法获取路径，尝试直接使用 URL
            if hasattr(file_obj, 'url'):
                return {'redirect_url': file_obj.url, 'local': False}
            raise Http404("File not accessible")

        # 根据存储后端处理下载
        if is_local and file_path and os.path.exists(file_path):
            # 本地存储：使用 FileResponse 流式传输
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=smart_str(file_entry.name)
            )

            # 设置内容类型
            if file_entry.mime_type:
                response['Content-Type'] = file_entry.mime_type

            return {'response': response, 'local': True}
        elif hasattr(file_obj, 'url'):
            # 云存储：返回重定向 URL
            return {'redirect_url': file_obj.url, 'local': False}
        else:
            # 备选方案：直接流式传输
            try:
                response = FileResponse(
                    file_obj.open(),
                    as_attachment=True,
                    filename=smart_str(file_entry.name)
                )
                if file_entry.mime_type:
                    response['Content-Type'] = file_entry.mime_type
                return {'response': response, 'local': False}
            except Exception as e:
                logger.error(f"Error streaming file {file_entry.id}: {str(e)}")
                raise Http404("Failed to access file from storage")

    def _handle_range_request(self, file_path, request, response):
        """
        处理 Range 请求（支持断点续传）。

        Args:
            file_path: 文件路径
            request: HTTP 请求对象
            response: HTTP 响应对象

        Returns:
            bool: 是否成功处理 Range 请求
        """
        if 'HTTP_RANGE' not in request.META:
            return False

        # 解析 Range 头
        range_header = request.META['HTTP_RANGE']
        if not range_header.startswith('bytes='):
            return False

        # 获取文件大小
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            return False

        # 解析范围
        try:
            range_spec = range_header[6:]  # 移除 'bytes='
            if '-' in range_spec:
                start_str, end_str = range_spec.split('-', 1)
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1

                # 验证范围
                if start >= file_size or end >= file_size or start > end:
                    return False

                # 设置响应头
                content_length = end - start + 1
                response.status_code = status.HTTP_206_PARTIAL_CONTENT
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Content-Length'] = content_length

                # 截取文件内容
                with open(file_path, 'rb') as f:
                    f.seek(start)
                    response.content = f.read(content_length)

                return True
        except ValueError:
            return False

        return False


class CacheInvalidateMixin:
    """
    缓存失效 Mixin，为文件管理操作提供缓存失效功能。
    """

    def _invalidate_folder_cache(self, folder):
        """
        失效指定文件夹的缓存。

        Args:
            folder: Folder 实例
        """
        from common.utils.cache import delete_cache
        import os

        path = folder.get_full_path()
        cache_key = f"file_dir:{folder.owner.id}:{path}"
        delete_cache(cache_key)
        logger.debug(f"Invalidated cache for folder: {path}")

    def _invalidate_parent_cache(self, parent_folder):
        """
        失效父文件夹的缓存。

        Args:
            parent_folder: 父文件夹实例
        """
        # 递归失效所有父文件夹的缓存
        current = parent_folder
        while current:
            self._invalidate_folder_cache(current)
            current = current.parent

    def _invalidate_user_cache(self, user):
        """
        失效用户相关的所有缓存。

        Args:
            user: User 实例
        """
        from common.utils.cache import delete_cache

        # 删除用户目录的缓存
        cache_key = f"file_dir:{user.id}:/"
        delete_cache(cache_key)
        logger.debug(f"Invalidated cache for user: {user.id}")


class UserQuotaMixin:
    """
    用户存储配额 Mixin，提供配额检查功能。
    """

    def check_user_quota(self, user, file_size):
        """
        检查用户是否有足够的存储空间。

        Args:
            user: User 实例
            file_size: 文件大小（字节）

        Returns:
            tuple: (is_allowed, message, current_usage, limit)
        """
        from django.conf import settings
        from .models import FileEntry

        # 获取当前使用量
        current_usage = FileEntry.objects.filter(owner=user).aggregate(
            total=models.Sum('file_size')
        )['total'] or 0

        # 检查是否超过限制
        if current_usage + file_size > settings.MAX_USER_STORAGE_QUOTA:
            return (
                False,
                f"存储空间不足。当前使用: {current_usage // 1024 // 1024}MB，"
                f"限制: {settings.MAX_USER_STORAGE_QUOTA // 1024 // 1024}MB",
                current_usage,
                settings.MAX_USER_STORAGE_QUOTA
            )

        return (True, "", current_usage, settings.MAX_USER_STORAGE_QUOTA)