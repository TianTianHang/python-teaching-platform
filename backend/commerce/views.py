from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from commerce.tasks import handle_payment_callback
from commerce.payment.registry import get_payment_gateway
from .models import Order
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import CreatePaymentSerializer, OrderCreateSerializer, OrderDetailSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    订单视图集
    - create: 创建订单（购买会员）
    - list: 查看我的订单列表
    - retrieve: 查看订单详情
    - 不支持 update / partial_update / destroy
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]  # 使用默认全局权限（IsAuthenticated）

    def get_queryset(self):
        # 用户只能看到自己的订单
        return Order.objects.filter(user=self.request.user).select_related(
            'membership_type', 'subscription'
        ).order_by('-created_at')
        
        
    # 使用不同的serialize类
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer
    def get_object(self):
        """
        支持通过 pk（数字）或 order_number（字符串）获取订单。
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field  # 默认是 'pk'
        lookup_value = self.kwargs[lookup_url_kwarg]

        # 先尝试按主键（整数）查找
        if lookup_value.isdigit():
            obj = get_object_or_404(queryset, pk=lookup_value)
        else:
            # 否则按 order_number 查找
            obj = get_object_or_404(queryset, order_number=lookup_value)
        # 可选：检查对象权限（DRF 会自动调用 check_object_permissions）
        self.check_object_permissions(self.request, obj)
        return obj
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        创建订单：用户选择 membership_type，系统生成待支付订单
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()  # 已在 serializer 中处理 user 和 amount
        output_serializer = OrderDetailSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='cancel')
    @transaction.atomic
    def cancel(self, request, pk=None):
        """
        用户主动取消待支付订单。
        仅当订单状态为 'pending' 时允许取消。
        """
        order = self.get_object()  # 自动应用 get_queryset，确保是当前用户的订单
        if order.status != 'pending':
            return Response(
                {"detail": "只有待支付的订单可以取消。"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # 可选：记录取消时间（如果你在模型中加了 cancelled_at 字段）
        order.cancelled_at = timezone.now()
        order.save(update_fields=['status', 'cancelled_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 禁用不支持的操作
    def update(self, request, *args, **kwargs):
        return Response({"detail": "订单不允许修改。"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "订单不允许修改。"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "订单不允许删除。"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

import logging
logger = logging.getLogger(__name__)
class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePaymentSerializer
    def post(self, request, order_number):
        # 获取订单（更简洁）
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user,
            status='pending'
        )

        # 使用序列化器验证输入
        serializer = CreatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        payment_method = serializer.validated_data['payment_method']
        try:
            gateway = get_payment_gateway(payment_method)
            payment_info = gateway.create_payment(order)
            return Response(payment_info)
        except Exception as e:
            # 建议记录日志
            logger.error(f"Payment creation failed: {e}", exc_info=True)
            return Response({"error": "支付初始化失败，请稍后重试。"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AlipayNotifyView(APIView):
    """
    支付宝异步回调（必须公网可访问，且不能有登录限制）
    """
    authentication_classes = []
    permission_classes = []


    @transaction.atomic
    def post(self, request):
        gateway = get_payment_gateway("alipay")
        result = gateway.handle_callback(request.POST.dict())

        if result["success"]:
            handle_payment_callback.delay(result['order_number'],result['transaction_id'])
        else:
            logger.warning(f"Payment failed: {result}")

        return HttpResponse("failure")