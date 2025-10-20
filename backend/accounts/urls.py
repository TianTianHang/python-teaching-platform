# backend/accounts/urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView,TokenVerifyView
urlpatterns = [
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),
    path('auth/me', views.MeView.as_view(), name='me'),
    path('auth/refresh', TokenRefreshView.as_view(), name='refresh'),
    path('auth/verify', TokenVerifyView.as_view(), name='verify'),
]