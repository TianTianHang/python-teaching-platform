from celery import shared_task
from accounts.models import Subscription
from commerce.models import Order
from django.utils import timezone
from django.db import transaction

@shared_task(bind=True, max_retries=3)
def handle_payment_callback(self, order_number,transaction_id):
    """
    异步处理支付成功后的逻辑
    """
    try:
        with transaction.atomic():
            order = Order.objects.get(order_number=order_number)
            if order.status == 'pending':
                order.status = 'paid'
                order.transaction_id = transaction_id
                order.paid_at = timezone.now()
                order.save()
                create_subscription_from_order.delay(order_number)
            return f"Order {order_number} processed successfully"

    except Order.DoesNotExist:
        # 订单不存在，记录日志
        print(f"Order {order_number} not found")
        return "Order not found"
    except Exception as exc:
        # 重试机制：3 次，每次间隔 2^retry * 60 秒
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
@shared_task(bind=True, max_retries=3)
def create_subscription_from_order(self, order_number):
    """
    根据已支付的订单创建订阅
    """
    try:
        with transaction.atomic():
            # 1. 获取已支付的订单
            order = Order.objects.select_for_update().get(
                order_number=order_number,
                status='paid'
            )
            # 4. 创建新订阅
            subscription = Subscription.objects.create(
                user=order.user,
                membership_type=order.membership_type,
                start_date=timezone.now(),
            )
            return f"New subscription created: {subscription}"

    except Order.DoesNotExist:
        return f"Paid order {order_number} not found"
    except Exception as exc:
        # 记录错误日志（可接入 Sentry 或 logging）
        print(f"Error creating subscription for {order_number}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))