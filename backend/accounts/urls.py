# backend/accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]