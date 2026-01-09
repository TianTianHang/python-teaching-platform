"""
Permission classes for file management API.
"""

from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """
    自定义权限类：只有对象的所有者或管理员可以访问。

    对于对象级别的权限，默认拒绝访问。
    只有当对象的所有者是当前用户，或者当前用户是管理员时才允许访问。
    """

    def has_permission(self, request, view):
        """
        判断是否有权限（用于列表/创建操作）。
        只有认证用户才能访问。
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        判断是否有对象级别的权限。

        Args:
            request: HTTP 请求对象
            view: 视图对象
            obj: 要检查的对象（Folder 或 FileEntry）

        Returns:
            bool: 是否有权限
        """
        # 对象的所有者是当前用户
        is_owner = obj.owner == request.user

        # 当前用户是管理员
        is_staff = request.user.is_staff

        return is_owner or is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限类：对象的所有者可以完全访问，其他用户只能读取。
    """

    def has_permission(self, request, view):
        """
        判断是否有权限。
        - 安全方法（GET、HEAD、OPTIONS）：允许所有用户
        - 其他方法（POST、PUT、DELETE、PATCH）：只允许认证用户
        """
        # 允许只读方法
        if request.method in permissions.SAFE_METHODS:
            return True
        # 允许认证用户进行其他操作
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        判断是否有对象级别的权限。

        - 允许所有用户使用 GET、HEAD、OPTIONS 方法（只读）
        - 只有对象的所有者可以使用其他方法（修改、删除等）
        """
        # 允许只读方法
        if request.method in permissions.SAFE_METHODS:
            return True

        # 允许对象所有者进行任何操作
        return obj.owner == request.user