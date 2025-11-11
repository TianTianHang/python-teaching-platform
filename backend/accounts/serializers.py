# backend/accounts/serializers.py
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from .models import User

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    st_number = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'st_number')

    def validate_st_number(self, value):
        if User.objects.filter(st_number=value).exists():
            raise serializers.ValidationError("该学号已被注册")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            st_number=validated_data['st_number']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims (optional)
        token['username'] = user.username
        token['st_number'] = user.st_number
        return token
    def validate(self, attrs):
        # attrs 包含 'username' 和 'password'，但我们要允许 'username' 实际是学号
        login_input = attrs.get("username")
        password = attrs.get("password")

        # 尝试根据 username 或 st_number 获取用户
        try:
            # 先按 username 查
            user = User.objects.get(username=login_input)
        except User.DoesNotExist:
            try:
                # 再按 st_number 查
                user = User.objects.get(st_number=login_input)
            except User.DoesNotExist:
                raise ValidationError("用户不存在", code="user_not_found")

        # 验证密码
        if not user.check_password(password):
            raise ValidationError("密码错误", code="password_incorrect")

        # 检查用户是否激活（可选）
        if not user.is_active:
            raise ValidationError("用户已被禁用", code="user_inactive")

        # 调用父类逻辑生成 token
        data = super().validate({"username": user.username, "password": password})
        # 可选：返回额外信息
        data.update({
            "user_id": user.id,
            "username": user.username,
            "st_number": user.st_number,
            
        })
        return data
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="The refresh token to be blacklisted.",
        write_only=True
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','st_number', 'avatar', 'email')  # 按需添加字段，如 first_name 等
        read_only_fields = ('id', 'st_number')  # 防止意外修改
    def update(self, instance, validated_data):
        # 只允许更新非敏感字段
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码错误。")
        return value

    def validate_new_password(self, value):
        # 可选：启用 Django 内置密码验证器（如长度、常见密码等）
        validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user