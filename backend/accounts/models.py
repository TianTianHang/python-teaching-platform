from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    """
    Custom User model.
    Extends AbstractUser to allow future extensions.
    """
    # Add custom fields here later if needed
    # e.g., avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.username