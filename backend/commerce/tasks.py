import logging
from celery import shared_task
from accounts.models import Subscription
from commerce.models import Order
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def handle_payment_callback(self, order_number,transaction_id):
    """
    异步处理支付成功后的逻辑
    """
    logger.info(f"Payment callback task started", extra={
        'order_number': order_number,
        'transaction_id': transaction_id,
        'task_id': self.request.id
    })

    try:
        with transaction.atomic():
            order = Order.objects.get(order_number=order_number)
            if order.status == 'pending':
                order.status = 'paid'
                order.transaction_id = transaction_id
                order.paid_at = timezone.now()
                order.save()

                logger.info(f"Order marked as paid", extra={
                    'order_number': order_number,
                    'transaction_id': transaction_id,
                    'paid_at': order.paid_at.isoformat()
                })

                create_subscription_from_order.delay(order_number)

                logger.info(f"Payment callback task completed successfully", extra={
                    'order_number': order_number,
                    'transaction_id': transaction_id
                })

            return f"Order {order_number} processed successfully"

    except Order.DoesNotExist:
        # 订单不存在，记录日志
        logger.error(f"Order not found during payment callback", extra={
            'order_number': order_number,
            'transaction_id': transaction_id,
            'task_id': self.request.id
        })
        return "Order not found"

    except Exception as exc:
        # 重试机制：3 次，每次间隔 2^retry * 60 秒
        logger.warning(f"Payment callback failed, retrying", extra={
            'order_number': order_number,
            'transaction_id': transaction_id,
            'retry_count': self.request.retries,
            'max_retries': 3,
            'error': str(exc)
        }, exc_info=True)

        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
@shared_task(bind=True, max_retries=3)
def create_subscription_from_order(self, order_number):
    """
    根据已支付的订单创建订阅
    """
    logger.info(f"Subscription creation task started", extra={
        'order_number': order_number,
        'task_id': self.request.id
    })

    try:
        with transaction.atomic():
            # 1. 获取已支付的订单
            order = Order.objects.select_for_update().get(
                order_number=order_number,
                status='paid'
            )

            logger.debug(f"Paid order retrieved", extra={
                'order_number': order_number,
                'user_id': order.user.id,
                'membership_type': order.membership_type.name if order.membership_type else None
            })

            # 4. 创建新订阅
            subscription = Subscription.objects.create(
                user=order.user,
                membership_type=order.membership_type,
                start_date=timezone.now(),
            )

            logger.info(f"Subscription created successfully", extra={
                'order_number': order_number,
                'subscription_id': subscription.id,
                'user_id': order.user.id,
                'membership_type': order.membership_type.name if order.membership_type else None,
                'start_date': subscription.start_date.isoformat()
            })

            return f"New subscription created: {subscription}"

    except Order.DoesNotExist:
        logger.error(f"Paid order not found during subscription creation", extra={
            'order_number': order_number,
            'task_id': self.request.id
        })
        return f"Paid order {order_number} not found"

    except Exception as exc:
        # 记录错误日志（可接入 Sentry 或 logging）
        logger.error(f"Subscription creation failed, retrying", extra={
            'order_number': order_number,
            'retry_count': self.request.retries,
            'max_retries': 3,
            'error': str(exc)
        }, exc_info=True)

        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))