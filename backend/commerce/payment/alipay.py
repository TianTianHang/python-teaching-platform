# payment/alipay.py
import logging
from decimal import Decimal
from django.conf import settings
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel

from commerce.models import Order
from .base import BasePaymentGateway

logger = logging.getLogger(__name__)


class AlipayGateway(BasePaymentGateway):
    def __init__(self):
        # 初始化客户端配置
        config = AlipayClientConfig()
        config.server_url = (
            "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
            if settings.ALIPAY_DEBUG
            else "https://openapi.alipay.com/gateway.do"
        )
        config.app_id = settings.ALIPAY_APPID
        config.app_private_key = self._read_key(settings.ALIPAY_PRIVATE_KEY_PATH)
        config.alipay_public_key = self._read_key(settings.ALIPAY_PUBLIC_KEY_PATH)

        self.client = DefaultAlipayClient(alipay_client_config=config, logger=logger)

    def _read_key(self, path: str) -> str:
        """读取密钥文件内容"""
        with open(path, "r") as f:
            return f.read().strip()

    def create_payment(self, order:Order):
        """
        创建电脑网站支付（alipay.trade.page.pay）
        返回前端跳转 URL
        """
        logger.info(f"Creating Alipay payment", extra={
            'order_number': order.order_number,
            'user_id': getattr(order, 'user', None).id if hasattr(order, 'user') and order.user else None,
            'amount': float(order.amount),
            'membership_type': order.membership_type.name if order.membership_type else None,
            'debug_mode': settings.ALIPAY_DEBUG
        })

        model = AlipayTradePagePayModel()
        model.out_trade_no = order.order_number
        model.total_amount = str(order.amount)  # Fix: convert to string instead of int
        if order.membership_type:
            model.subject = f"会员订阅 - {order.membership_type.name}"
        else:
            model.subject = "普通商品"
        model.product_code = "FAST_INSTANT_TRADE_PAY"


        request = AlipayTradePagePayRequest(biz_model=model)
        request.return_url = settings.ALIPAY_RETURN_URL  # 同步回调（可选）
        request.notify_url = settings.ALIPAY_NOTIFY_URL  # 异步回调（必须）

        logger.debug(f"Alipay payment URLs configured", extra={
            'order_number': order.order_number,
            'notify_url': settings.ALIPAY_NOTIFY_URL,
            'return_url': settings.ALIPAY_RETURN_URL,
            'amount': str(order.amount),
            'subject': model.subject
        })
        try:
            # 获取完整跳转 URL（GET 请求）
            pay_url = self.client.page_execute(request, http_method="GET")

            logger.info(f"Alipay payment created successfully", extra={
                'order_number': order.order_number,
                'pay_url': pay_url[:100] + '...' if len(pay_url) > 100 else pay_url,  # Truncate long URL
                'amount': str(order.amount)
            })

            return {
                "method": "redirect",
                "pay_url": pay_url,
                "gateway": "alipay",
            }
        except Exception as e:
            logger.error(f"Alipay create payment failed", extra={
                'order_number': order.order_number,
                'amount': str(order.amount),
                'error': str(e),
                'error_type': type(e).__name__
            }, exc_info=True)
            raise

    def handle_callback(self, request_data: dict):
        """
        处理支付宝异步/同步回调
        官方 SDK 不直接提供验签方法，需手动调用 verify
        """
        logger.info(f"Received Alipay callback", extra={
            'order_number': request_data.get("out_trade_no"),
            'trade_status': request_data.get("trade_status"),
            'total_amount': request_data.get("total_amount"),
            'trade_no': request_data.get("trade_no"),
            'callback_type': 'async' if 'notify_url' in request_data else 'sync'
        })

        if not self.verify_signature(request_data):
            logger.error(f"Alipay signature verification failed", extra={
                'order_number': request_data.get("out_trade_no"),
                'trade_no': request_data.get("trade_no"),
                'sign': request_data.get("sign")[:20] + '...' if request_data.get("sign") else None,
                'sign_type': request_data.get("sign_type")
            })
            return {"success": False, "error": "Invalid signature"}

        logger.debug(f"Alipay signature verification successful", extra={
            'order_number': request_data.get("out_trade_no"),
            'trade_status': request_data.get("trade_status")
        })

        trade_status = request_data.get("trade_status")
        success_statuses = ["TRADE_SUCCESS", "TRADE_FINISHED"]

        result = {
            "success": trade_status in success_statuses,
            "order_number": request_data.get("out_trade_no"),
            "transaction_id": request_data.get("trade_no"),
            "amount": Decimal(request_data.get("total_amount", "0")),
            "trade_status": trade_status,
            "raw_data": request_data,
        }

        logger.info(f"Alipay callback processed successfully", extra={
            'order_number': result["order_number"],
            'success': result["success"],
            'trade_status': trade_status,
            'transaction_id': result["transaction_id"]
        })

        return result

    def verify_signature(self, data: dict) -> bool:
        """
        使用官方 SDK 验证支付宝回调签名
        注意：需要移除 sign_type 和 sign 字段后再验签
        """
        from alipay.aop.api.util.SignatureUtils import verify_with_rsa

        # 提取公钥（去除首尾标记）
        pub_key = self._format_public_key(settings.ALIPAY_PUBLIC_KEY_PATH)

        # 分离 sign 和待验签参数
        sign = data.get("sign")
        sign_type = data.get("sign_type", "RSA2")

        if not sign:
            logger.warning(f"No signature found in callback data", extra={
                'order_number': data.get("out_trade_no"),
                'sign_type': sign_type
            })
            return False

        # 构造待验签字符串（按 key 升序，排除 sign/sign_type）
        unsigned_items = [(k, v) for k, v in data.items() if k not in ("sign", "sign_type")]
        unsigned_items.sort(key=lambda x: x[0])
        unsigned_string = "&".join(f"{k}={v}" for k, v in unsigned_items)

        logger.debug(f"Verifying signature for order {data.get('out_trade_no')}", extra={
            'order_number': data.get("out_trade_no"),
            'sign_type': sign_type,
            'unsigned_string_length': len(unsigned_string),
            'sign_length': len(sign) if sign else 0
        })

        try:
            if sign_type == "RSA2":
                result = verify_with_rsa(pub_key, unsigned_string.encode('UTF-8','strict'), sign)
                logger.debug(f"Signature verification result: {result}", extra={
                    'order_number': data.get("out_trade_no"),
                    'verification_result': result
                })
                return result
            else:
                logger.error(f"Unsupported signature type: {sign_type}", extra={
                    'order_number': data.get("out_trade_no"),
                    'sign_type': sign_type
                })
                raise ValueError("Only RSA2 is supported")
        except Exception as e:
            logger.error(f"Signature verification error", extra={
                'order_number': data.get("out_trade_no"),
                'error': str(e),
                'error_type': type(e).__name__,
                'sign_type': sign_type
            }, exc_info=True)
            raise

    def _format_public_key(self, path: str) -> str:
        """格式化公钥为纯字符串（无 BEGIN/END）"""
        with open(path, "r") as f:
            content = f.read()
        return (
            content.replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "")
            .strip()
        )