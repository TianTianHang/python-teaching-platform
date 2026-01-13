from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    """
    Custom User model.
    Extends AbstractUser to allow future extensions.
    """
    
    # Add custom fields here later if needed
    #avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    st_number = models.CharField(
        verbose_name="学号",
        max_length=20,          
        unique=True,            
        blank=False,           
        null=True 
    )
    avatar =  models.TextField(
        verbose_name="头像",          
        unique=False,            
        blank=False,           
        null=True 
    )
    
    def __str__(self):
        return f'{self.st_number}-{self.username}'
    


class MembershipType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 如 "Premium"
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(help_text="订阅有效天数")
    is_active = models.BooleanField(default=True,help_text="是否启用会员类型")
    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=self.membership_type.duration_days)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} - {self.membership_type.name}"