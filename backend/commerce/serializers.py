from accounts.models import MembershipType
from rest_framework import serializers

from accounts.serializers import MembershipTypeSerializer, SubscriptionSerializer
from commerce.payment.registry import PAYMENT_GATEWAYS
from .models import Order

# ----------------------------
# 订单创建（用户下单）
# ----------------------------

class OrderCreateSerializer(serializers.ModelSerializer):
    # 用户只能选择 membership_type.id，不能传其他敏感字段
    membership_type = serializers.PrimaryKeyRelatedField(
        queryset=MembershipType.objects.filter(is_active=True)  # 假设你有 is_active 字段，没有可去掉 filter
    )
    
    class Meta:
        model = Order
        fields = ['membership_type']
        # 其他字段如 order_number, status, amount 等由后端自动计算或设置


    def validate_membership_type(self, value):
        if not value:
            raise serializers.ValidationError("请选择有效的会员类型。")
        return value


    def create(self, validated_data):
        user = self.context['request'].user
        membership_type = validated_data['membership_type']

        # 检查是否已有未支付的相同会员类型订单
        existing_order = Order.objects.filter(
            user=user,
            membership_type=membership_type,
            status='pending'
        ).first()

        if existing_order:
            return existing_order  # 返回已有pending订单，避免重复创建
        # 自动填充金额（防止前端篡改价格）
        order = Order.objects.create(
            user=user,
            membership_type=membership_type,
            amount=membership_type.price,  # 关键：价格以服务端为准！
            status='pending'
        )
        return order


    
# ----------------------------
# 订单详情 / 列表（只读）
# ----------------------------
class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")  # 显示 username
    membership_type = MembershipTypeSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'user',
            'membership_type',
            'status',
            'amount',
            'created_at',
            'paid_at',
            'cancelled_at',
            'subscription',
            'transaction_id',
        ]
        read_only_fields = fields


class CreatePaymentSerializer(serializers.Serializer):

    payment_method = serializers.ChoiceField(
        choices=list(PAYMENT_GATEWAYS.keys()),
        default="alipay",
        help_text="支付方式"
    )