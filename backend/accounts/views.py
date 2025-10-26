from tokenize import TokenError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    LogoutSerializer,
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
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

