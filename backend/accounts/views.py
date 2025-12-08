from tokenize import TokenError
from rest_framework import status,generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.utils import timezone
from .models import MembershipType, User
from .serializers import (
    ChangePasswordSerializer,
    LogoutSerializer,
    MembershipTypeSerializer,
    RegisterUserSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer  # ← 关键！Browsable API 会读这个

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer  # ← 关键！Browsable API 会读这个

    def post(self, request):
        # 可选：用 serializer 做基础验证（推荐）
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"refresh": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "An error occurred while logging out."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
    
class UserListView(generics.ListAPIView):
    """
    管理员查看所有用户
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # 仅管理员可访问
    
class ChangePasswordView(generics.UpdateAPIView):
    """
    修改当前用户的密码
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "密码已成功更新。"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MembershipTypeListView(ListAPIView):
    """
    列出所有启用的会员类型（公开接口）
    """
    queryset = MembershipType.objects.filter(is_active=True).order_by('duration_days')
    serializer_class = MembershipTypeSerializer
    permission_classes = [AllowAny]  # 无需登录即可查看