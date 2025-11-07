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