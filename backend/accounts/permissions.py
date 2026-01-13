
from rest_framework.permissions import BasePermission
from django.utils import timezone
from .models import Subscription


class IsSubscriptionActive(BasePermission):
    """

    仅允许拥有有效订阅的认证用户访问。

    """
    def has_permission(self, request, view):
        # 必须是已认证用户
        if not request.user or not request.user.is_authenticated:
            return False

        # 检查是否存在至少一个有效的、未过期的活跃订阅
        return Subscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gte=timezone.now()
        ).exists()
        