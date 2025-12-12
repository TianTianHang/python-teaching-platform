"""
URL patterns for file management API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileEntryViewSet, UserFilesView

# Create router for FileEntryViewSet
router = DefaultRouter()
router.register(r'files', FileEntryViewSet, basename='fileentry')

urlpatterns = [
    # API endpoints for file management
    path('', include(router.urls)),
    
    # Endpoint to get current user's files
    path('user-files/', UserFilesView.as_view(), name='user-files'),
    
    # Additional endpoints can be added here as needed
    # path('upload/', FileUploadView.as_view(), name='file-upload'),
    # path('download/<uuid:pk>/', FileDownloadView.as_view(), name='file-download'),
]