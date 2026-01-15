import logging
from tokenize import TokenError
from rest_framework import status,generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, DestroyAPIView
from django.utils import timezone
from django.db import transaction

from common.decorators.logging_decorators import audit_log
from .models import MembershipType, User
from .serializers import (
    ChangePasswordSerializer,
    LogoutSerializer,
    MembershipTypeSerializer,
    RegisterUserSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
   
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        ip_address = self._get_client_ip(request)

        logger.info(f"Login attempt", extra={
            'username': username,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
        })

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            logger.info(f"Login successful", extra={
                'username': username,
                'ip_address': ip_address,
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            })
        else:
            logger.warning(f"Login failed", extra={
                'username': username,
                'ip_address': ip_address,
                'status_code': response.status_code
            })

        return response

    def _get_client_ip(self, request):
        """获取客户端真实 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer  # ← 关键！Browsable API 会读这个

    @transaction.atomic
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        ip_address = self._get_client_ip(request)

        logger.info(f"Registration attempt", extra={
            'username': username,
            'email': email,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
        })

        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            logger.info(f"User registered successfully", extra={
                'username': username,
                'email': email,
                'user_id': user.id,
                'ip_address': ip_address
            })

            # Auto-login after register: return tokens
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            return Response(
                {
                    "user": RegisterUserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )

        logger.warning(f"Registration failed", extra={
            'username': username,
            'email': email,
            'ip_address': ip_address,
            'validation_errors': serializer.errors
        })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_client_ip(self, request):
        """获取客户端真实 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer  # ← 关键！Browsable API 会读这个

    def post(self, request):
        user_id = getattr(request.user, 'id', None)
        ip_address = self._get_client_ip(request)

        logger.info(f"Logout attempt", extra={
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
        })

        # 可选：用 serializer 做基础验证（推荐）
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Logout failed - invalid data", extra={
                'user_id': user_id,
                'ip_address': ip_address,
                'validation_errors': serializer.errors
            })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"Logout successful", extra={
                'user_id': user_id,
                'ip_address': ip_address
            })

            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except TokenError:
            logger.warning(f"Logout failed - invalid token", extra={
                'user_id': user_id,
                'ip_address': ip_address,
                'refresh_token': refresh_token[:20] + '...' if refresh_token else None
            })
            return Response(
                {"refresh": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Logout failed - exception", extra={
                'user_id': user_id,
                'ip_address': ip_address,
                'error': str(exc),
                'refresh_token': refresh_token[:20] + '...' if refresh_token else None
            }, exc_info=True)
            return Response(
                {"detail": "An error occurred while logging out."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_client_ip(self, request):
        """获取客户端真实 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer  # ← 关键！Browsable API 会读这个

    def get(self, request):
        """
        获取当前登录用户的信息。
        """
        user = request.user
        # 预加载有效订阅（end_date > now）
        from .models import Subscription
        try:
            active_sub = Subscription.objects.get(
                user=user,
                end_date__gt=timezone.now()
            )
            user.active_subscription = active_sub  # 动态附加属性
        except Subscription.DoesNotExist:
            user.active_subscription = None
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserUpdateView(generics.UpdateAPIView):
    """
    允许用户更新自己的信息（除密码外）
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # 只能修改自己

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class UserListView(generics.ListAPIView):
    """
    管理员查看所有用户
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # 仅管理员可访问

class UserDeleteView(DestroyAPIView):
    """
    管理员删除用户
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # 仅管理员可访问

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class ChangePasswordView(generics.UpdateAPIView):
    """
    修改当前用户的密码
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        user = request.user
        ip_address = self._get_client_ip(request)

        logger.info(f"Password change attempt", extra={
            'user_id': user.id,
            'username': user.username,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
        })

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            logger.info(f"Password changed successfully", extra={
                'user_id': user.id,
                'username': user.username,
                'ip_address': ip_address
            })

            return Response({"detail": "密码已成功更新。"}, status=status.HTTP_200_OK)

        logger.warning(f"Password change failed - validation error", extra={
            'user_id': user.id,
            'username': user.username,
            'ip_address': ip_address,
            'validation_errors': serializer.errors
        })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_client_ip(self, request):
        """获取客户端真实 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class MembershipTypeListView(ListAPIView):
    """
    列出所有启用的会员类型（公开接口）
    """
    queryset = MembershipType.objects.filter(is_active=True).order_by('duration_days')
    serializer_class = MembershipTypeSerializer
    permission_classes = [AllowAny]  # 无需登录即可查看