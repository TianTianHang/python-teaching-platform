# payment/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePaymentGateway(ABC):
    """
    所有支付网关必须实现的接口
    """

    @abstractmethod
    def create_payment(self, order) -> Dict[str, Any]:
        """
        创建支付请求，返回前端所需数据（如跳转 URL 或表单）
        :param order: your_app.models.Order 实例
        :return: dict with keys like 'pay_url', 'method', 'raw_response'
        """
        pass

    @abstractmethod
    def handle_callback(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理异步/同步回调，验证签名并返回标准化结果
        :param request_data: 原始回调参数（GET/POST）
        :return: {
            'success': bool,
            'order_number': str,
            'transaction_id': str,
            'amount': Decimal,
            'raw_data': dict
        }
        """
        pass

    @abstractmethod
    def verify_signature(self, data: Dict[str, Any]) -> bool:
        """验证回调签名"""
        pass