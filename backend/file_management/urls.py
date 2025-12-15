"""
URL patterns for file management API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileEntryViewSet, FolderViewSet, UnifiedFileFolderViewSet

# Create router for ViewSets
router = DefaultRouter()

# Register the other viewsets
router.register(r'files', FileEntryViewSet, basename='fileentry')
router.register(r'folders', FolderViewSet, basename='folder')

# Register the path viewset without the default routes that conflict with nested paths
urlpatterns = [
    # Standard routes for files and folders
    path('', include(router.urls)),
    # Custom routes for the path-based operations that handle nested paths properly
    path('path/', UnifiedFileFolderViewSet.as_view({'get': 'list', 'post': 'create_folder'}), name='path-list'),
    path('path/upload/', UnifiedFileFolderViewSet.as_view({'post': 'upload_file'}), name='path-upload'),
    path('path/create-folder/', UnifiedFileFolderViewSet.as_view({'post': 'create_folder'}), name='path-create-folder'),
    path('path/move_copy/', UnifiedFileFolderViewSet.as_view({'post': 'move_copy'}), name='path-move-copy'),
    # Custom route for nested paths - retrieve/download based on query parameters
    path('path/<path:full_path>/', UnifiedFileFolderViewSet.as_view({'get': 'retrieve'}), name='path-retrieve'),
    # Additional endpoints can be added here as needed
    # path('upload/', FileUploadView.as_view(), name='file-upload'),
    # path('download/<uuid:pk>/', FileDownloadView.as_view(), name='file-download'),
]