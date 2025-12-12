"""
Views for file management API
"""
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
from django.db.models import Q
import os
from .models import FileEntry
from .serializers import FileEntrySerializer, FileUploadSerializer, FileEntryUpdateSerializer
from django.core.files.storage import default_storage
from django.conf import settings


class FileEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing file entries.
    Allows upload, download, listing, updating, and deletion of files.
    """
    queryset = FileEntry.objects.all()
    serializer_class = FileEntrySerializer
    pagination_class = None
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'upload':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated]
        else:
            # For retrieve, list - check if file is public or user owns it
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally restricts returned files based on authenticated user
        or public files.
        """
        queryset = FileEntry.objects.all()

        # Non-staff users can only see their own files or public files
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(owner=self.request.user) | Q(is_public=True)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Handle file uploads - alias for upload action
        """
        return self.upload(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload(self, request):
        """
        Upload a new file.
        Supports both local and cloud storage backends.
        """
        serializer = FileUploadSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            file_entry = serializer.save()
            response_serializer = FileEntrySerializer(file_entry, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_by_name(self, request):
        """
        Get file instance by name.
        Requires 'name' query parameter.
        """
        name = request.query_params.get('name', None)
        if not name:
            return Response(
                {'error': 'Name parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get files by name for the current user or all public files
        files = self.get_queryset().filter(name=name)

        if not files.exists():
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # If multiple files have the same name, return all of them
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def download(self, request, pk=None):
        """
        Download a file.
        Checks permissions based on file privacy settings.
        """
        file_entry = get_object_or_404(FileEntry, pk=pk)

        # Check permissions
        if not file_entry.is_public and file_entry.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to download this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not file_entry.file:
            raise Http404("File not found")

        # Open the file based on storage backend
        try:
            file_obj = file_entry.file
            file_path = file_obj.path if hasattr(file_obj, 'path') else file_obj.name

            # Determine content type
            content_type = file_entry.mime_type or 'application/octet-stream'

            # Create HTTP response
            response = HttpResponse(content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{smart_str(file_entry.name)}"'

            # For local storage, read the file content
            if file_entry.storage_backend == 'local':
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        response.content = f.read()
                else:
                    raise Http404("File not found on disk")
            else:
                # For cloud storage, we might need a different approach
                # For now, redirect to the cloud storage URL
                # Or implement direct streaming from cloud storage
                if hasattr(file_obj, 'url'):
                    return Response({'redirect_url': file_obj.url}, status=status.HTTP_302_FOUND)
                else:
                    with file_obj.open() as f:
                        response.content = f.read()

            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to download file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a file entry and the physical file.
        """
        instance = self.get_object()

        # Only owners and staff can delete files
        if instance.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to delete this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        Update file metadata (name, privacy, storage backend).
        Does not allow updating the file itself - for that, user should delete and re-upload.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Only owners and staff can update files
        if instance.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to update this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = FileEntryUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)



class UserFilesView(generics.ListAPIView):
    """
    Get all files owned by the current user
    """
    serializer_class = FileEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FileEntry.objects.filter(owner=self.request.user)