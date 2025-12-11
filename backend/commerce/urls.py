# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlipayNotifyView, CreatePaymentView, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('orders/<str:order_number>/pay/', CreatePaymentView.as_view(), name='create-payment'),                   
    path('payments/alipay/notify/', AlipayNotifyView.as_view(), name='alipay-notify')
    ] + router.urls  
