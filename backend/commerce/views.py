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
from .models import Order, MembershipType
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import CreatePaymentSerializer, OrderCreateSerializer, OrderDetailSerializer

import logging
from common.utils.logging import AuditLogger

logger = logging.getLogger('commerce.views')
audit_logger = AuditLogger()


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
        membership_type_id = request.data.get('membership_type')
        ip_address = request.META.get('REMOTE_ADDR')

        logger.info(f"Order creation attempt", extra={
            'user_id': request.user.id,
            'username': request.user.username,
            'membership_type_id': membership_type_id,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
        })

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()  # 已在 serializer 中处理 user 和 amount

            logger.info(f"Order created successfully", extra={
                'user_id': request.user.id,
                'order_number': order.order_number,
                'membership_type': order.membership_type.name if order.membership_type else None,
                'amount': str(order.amount),
                'ip_address': ip_address
            })

            audit_logger.log_data_change(
                change_type='create',
                model_name='Order',
                object_id=order.order_number,
                user_id=request.user.id,
                changes={
                    'membership_type': order.membership_type.name if order.membership_type else None,
                    'amount': str(order.amount),
                    'status': order.status
                }
            )

            output_serializer = OrderDetailSerializer(order)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Order creation failed", extra={
                'user_id': request.user.id,
                'membership_type_id': membership_type_id,
                'error': str(e),
                'error_type': type(e).__name__ if isinstance(e, Exception) else type(e).__name__
            }, exc_info=True)
            raise

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
        ip_address = request.META.get('REMOTE_ADDR')

        logger.info(f"Order cancellation attempt", extra={
            'user_id': request.user.id,
            'order_number': order.order_number,
            'current_status': order.status,
            'ip_address': ip_address
        })

        if order.status != 'pending':
            logger.warning(f"Order cancellation failed - invalid status", extra={
                'user_id': request.user.id,
                'order_number': order.order_number,
                'status': order.status,
                'ip_address': ip_address
            })
            return Response(
                {"detail": "只有待支付的订单可以取消。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 记录取消时间
            order.cancelled_at = timezone.now()
            order.status = 'cancelled'
            order.save(update_fields=['status', 'cancelled_at'])

            logger.info(f"Order cancelled successfully", extra={
                'user_id': request.user.id,
                'order_number': order.order_number,
                'cancelled_at': order.cancelled_at.isoformat(),
                'ip_address': ip_address
            })

            audit_logger.log_data_change(
                change_type='update',
                model_name='Order',
                object_id=order.order_number,
                user_id=request.user.id,
                changes={
                    'status': 'cancelled',
                    'cancelled_at': order.cancelled_at.isoformat()
                }
            )

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Order cancellation failed", extra={
                'user_id': request.user.id,
                'order_number': order.order_number,
                'error': str(e),
                'error_type': type(e).__name__
            }, exc_info=True)
            return Response(
                {"detail": "订单取消失败，请稍后重试。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 禁用不支持的操作
    def update(self, request, *args, **kwargs):
        return Response({"detail": "订单不允许修改。"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "订单不允许修改。"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "订单不允许删除。"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePaymentSerializer

    def post(self, request, order_number):
        ip_address = request.META.get('REMOTE_ADDR')

        logger.info(f"Payment creation request", extra={
            'user_id': request.user.id,
            'order_number': order_number,
            'ip_address': ip_address
        })

        # 获取订单（更简洁）
        try:
            order = get_object_or_404(
                Order,
                order_number=order_number,
                user=request.user,
                status='pending'
            )

            logger.debug(f"Order verified for payment", extra={
                'user_id': request.user.id,
                'order_number': order.order_number,
                'membership_type': order.membership_type.name if order.membership_type else None,
                'amount': str(order.amount)
            })

        except Exception as e:
            logger.error(f"Order verification failed for payment", extra={
                'user_id': request.user.id,
                'order_number': order_number,
                'error': str(e)
            }, exc_info=True)
            return Response({"error": "订单不存在或状态不允许支付。"}, status=status.HTTP_404_NOT_FOUND)

        # 使用序列化器验证输入
        serializer = CreatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Payment validation failed", extra={
                'user_id': request.user.id,
                'order_number': order_number,
                'validation_errors': serializer.errors
            })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment_method = serializer.validated_data['payment_method']

        try:
            logger.info(f"Creating payment with method: {payment_method}", extra={
                'user_id': request.user.id,
                'order_number': order_number,
                'payment_method': payment_method,
                'membership_type': order.membership_type.name if order.membership_type else None,
                'amount': str(order.amount)
            })

            gateway = get_payment_gateway(payment_method)
            payment_info = gateway.create_payment(order)

            logger.info(f"Payment created successfully", extra={
                'user_id': request.user.id,
                'order_number': order_number,
                'payment_method': payment_method,
                'payment_gateway_gateway': 'alipay',  # 假设目前只有支付宝
                'ip_address': ip_address
            })

            audit_logger.log_payment_operation(
                operation='payment_created',
                order_number=order.order_number,
                user_id=request.user.id,
                amount=float(order.amount),
                payment_method=payment_method,
                status='pending_payment'
            )

            return Response(payment_info)

        except Exception as e:
            logger.error(f"Payment creation failed", extra={
                'user_id': request.user.id,
                'order_number': order_number,
                'payment_method': payment_method,
                'error': str(e),
                'error_type': type(e).__name__
            }, exc_info=True)
            return Response(
                {"error": "支付初始化失败，请稍后重试。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class AlipayNotifyView(APIView):
    """
    支付宝异步回调（必须公网可访问，且不能有登录限制）
    """
    authentication_classes = []
    permission_classes = []

    @transaction.atomic
    def post(self, request):
        # 记录所有支付宝回调，无论成功失败
        logger.info(f"Alipay webhook received", extra={
            'callback_data': dict(request.POST),
            'ip_address': request.META.get('REMOTE_ADDR')
        })

        try:
            gateway = get_payment_gateway("alipay")
            result = gateway.handle_callback(request.POST.dict())

            if result["success"]:
                logger.info(f"Alipay webhook processed successfully", extra={
                    'order_number': result.get('order_number'),
                    'transaction_id': result.get('transaction_id'),
                    'success': True
                })

                handle_payment_callback.delay(result['order_number'], result['transaction_id'])

                audit_logger.log_payment_operation(
                    operation='payment_completed',
                    order_number=result.get('order_number'),
                    user_id=result.get('user_id'),  # 如果有的话
                    amount=result.get('amount'),
                    payment_method='alipay',
                    status='paid'
                )

                return HttpResponse("success")
            else:
                logger.warning(f"Alipay webhook processing failed", extra={
                    'order_number': result.get('order_number'),
                    'error': result.get('error'),
                    'success': False,
                    'raw_data': result.get('raw_data', {})
                })

                audit_logger.log_payment_operation(
                    operation='payment_failed',
                    order_number=result.get('order_number'),
                    user_id=result.get('user_id'),
                    amount=result.get('amount'),
                    payment_method='alipay',
                    status='failed'
                )

                return HttpResponse("failure")

        except Exception as e:
            logger.error(f"Alipay webhook processing error", extra={
                'error': str(e),
                'error_type': type(e).__name__,
                'request_data': dict(request.POST),
                'ip_address': request.META.get('REMOTE_ADDR')
            }, exc_info=True)

            audit_logger.log_payment_operation(
                operation='webhook_error',
                order_number=request.POST.get('out_trade_no'),
                user_id=None,
                amount=None,
                payment_method='alipay',
                status='error'
            )

            return HttpResponse("failure")