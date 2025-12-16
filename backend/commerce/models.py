from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.utils import timezone
import time
from accounts.models import MembershipType, Subscription, User

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
        ('failed', '支付失败'),
    ]
    order_number = models.CharField("订单号", max_length=32, unique=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    
    # 关联会员类型（当前场景）
    membership_type = models.ForeignKey(
        MembershipType, 
        on_delete=models.PROTECT, 
        null=True, blank=True,
        help_text="仅用于会员订阅类订单"
    )

    # 未来扩展预留：可用于普通商品等（可选）
    # product_type = models.CharField(max_length=50, choices=[('membership', '会员'), ('product', '商品')], default='membership')
    # generic_product_id = models.PositiveIntegerField(null=True, blank=True)  # 配合 ContentType 可做通用外键

    status = models.CharField("订单状态", max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    amount = models.DecimalField("订单金额", max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    paid_at = models.DateTimeField("支付时间", null=True, blank=True)
    cancelled_at = models.DateTimeField("取消时间", null=True, blank=True)
    # 关联生成的订阅（可选但推荐）
    subscription = models.OneToOneField(
        Subscription,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="支付成功后创建的订阅"
    )

    transaction_id = models.CharField("支付流水号", max_length=100, blank=True)  # 用于对账
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    @staticmethod

    def generate_order_number():
        # 方案：时间戳(秒) + 4位随机数
        # 示例：202512081145001234
        prefix = time.strftime("%Y%m%d%H%M%S")  # 14位：20251208114500
        rand_part = str(int(time.time() * 1000000) % 10000).zfill(4)  # 4位防冲突
        return f"ORD_{prefix}{rand_part}"
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username} - {self.membership_type.name if self.membership_type else 'N/A'}"