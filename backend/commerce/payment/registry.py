# payment/registry.py
from .alipay import AlipayGateway
from .base import BasePaymentGateway

PAYMENT_GATEWAYS = {
    "alipay": AlipayGateway,
}

def get_payment_gateway(gateway_name: str) -> BasePaymentGateway:
    """
    工厂方法：根据名称获取支付网关实例
    """
    gateway_class = PAYMENT_GATEWAYS.get(gateway_name)
    if not gateway_class:
        raise ValueError(f"Unsupported payment gateway: {gateway_name}")
    return gateway_class()