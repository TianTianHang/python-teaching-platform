"""
Views for file management API
"""
import hashlib
import logging
import urllib.parse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseNotModified, FileResponse
from django.utils.encoding import smart_str
from django.db.models import Q
from django.db import transaction
import os

from common.utils.cache import get_cache, invalidate_dir_cache, set_cache
from common.mixins.cache_mixin import CacheListMixin, CacheRetrieveMixin, InvalidateCacheMixin
from .models import FileEntry, Folder
from .serializers import (
    FileEntrySerializer, FileUploadSerializer, FileEntryUpdateSerializer,
    FolderSerializer, UnifiedPathSerializer, MoveCopyPathSerializer
)
from file_management.utils.path_utils import resolve_path_to_object, list_path_contents, get_folder_by_path, get_file_by_path, parse_destination_path, parse_upload_path
from .permissions import IsOwnerOrStaff, IsOwnerOrReadOnly
from file_management.utils.file_operations import (
    handle_file_move_copy,
    handle_folder_move_copy,
    validate_move_operation,
    download_file_by_path,
    generate_dir_etag
)

logger = logging.getLogger(__name__)



class FolderViewSet(CacheListMixin, CacheRetrieveMixin, InvalidateCacheMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing folders.
    Allows creation, listing, updating, and deletion of folders.
    Uses project standard caching strategy.
    """
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsOwnerOrStaff]
    pagination_class = None
    cache_prefix = "file_management"
    def get_queryset(self):
        """
        Optionally restricts returned folders based on authenticated user
        or public folders.
        """
        queryset = Folder.objects.all()

        # Non-staff users can only see their own folders
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)

        return queryset.select_related('owner', 'parent').prefetch_related('parent__owner')

    def perform_create(self, serializer):
        # Set owner to current user if not staff user
        if not self.request.user.is_staff:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        # Permission handled by IsOwnerOrStaff permission class
        serializer.save()

    def perform_destroy(self, instance):
        # Permission handled by IsOwnerOrStaff permission class
        # Recursively delete all subfolders and files
        # We'll delete child folders and files separately to maintain proper cleanup
        self._delete_folder_contents(instance)
        instance.delete()

    def _delete_folder_contents(self, folder):
        """Recursively delete folder contents"""
        # Delete all files in this folder
        for file_entry in folder.files.all():
            file_entry.delete()

        # Recursively delete subfolders
        for subfolder in folder.children.all():
            self._delete_folder_contents(subfolder)
            subfolder.delete()

    @action(detail=True, methods=['get'])
    def contents(self, request, pk=None):
        """
        Get contents of a specific folder (files and subfolders).
        """
        folder = self.get_object()
        # Permission handled by IsOwnerOrStaff permission class

        # Get files and subfolders in this folder
        files = FileEntry.objects.filter(folder=folder)
        subfolders = Folder.objects.filter(parent=folder)

        # Serialize the data
        files_serializer = FileEntrySerializer(files, many=True, context={'request': request})
        folders_serializer = FolderSerializer(subfolders, many=True, context={'request': request})

        return Response({
            'folder': FolderSerializer(folder, context={'request': request}).data,
            'files': files_serializer.data,
            'folders': folders_serializer.data
        })



class FileEntryViewSet(CacheListMixin, CacheRetrieveMixin, InvalidateCacheMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing file entries.
    Allows upload, download, listing, updating, and deletion of files.
    Uses project standard caching strategy.
    """
    queryset = FileEntry.objects.all()
    serializer_class = FileEntrySerializer
    pagination_class = None
    parser_classes = (MultiPartParser, FormParser)
    cache_prefix = "file_management"

    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        """
        Override permissions for specific actions requiring stricter control.
        """
        if self.action in ['upload', 'destroy', 'update', 'partial_update']:
            return [IsOwnerOrStaff()]
        if self.action == 'download':
            return [IsOwnerOrReadOnly()]
        return [permission() for permission in self.permission_classes]

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

        return queryset.select_related('owner', 'folder').prefetch_related('folder__owner')

    def create(self, request, *args, **kwargs):
        """
        Handle file uploads - alias for upload action
        """
        return self.upload(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
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

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download a file.
        Checks permissions based on file privacy settings.
        """
        file_entry = self.get_object()
        # Permission handled by IsOwnerOrReadOnly
        # Special handling for public files
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

            # For local storage, use FileResponse for streaming
            if file_entry.storage_backend == 'local':
                if os.path.exists(file_path):
                    # Use FileResponse to stream the file instead of loading it entirely into memory
                    response = FileResponse(
                        open(file_path, 'rb'),
                        as_attachment=True,
                        filename=smart_str(file_entry.name)
                    )
                    # Set content type if available
                    if file_entry.mime_type:
                        response['Content-Type'] = file_entry.mime_type
                    return response
                else:
                    raise Http404("File not found on disk")
            else:
                # For cloud storage, redirect to the cloud storage URL
                if hasattr(file_obj, 'url'):
                    return Response({'redirect_url': file_obj.url}, status=status.HTTP_302_FOUND)
                else:
                    # Fallback: stream from cloud storage
                    response = FileResponse(
                        file_obj.open(),
                        as_attachment=True,
                        filename=smart_str(file_entry.name)
                    )
                    if file_entry.mime_type:
                        response['Content-Type'] = file_entry.mime_type
                    return response
        except FileNotFoundError as e:
            logger.warning(f"File not found during download: {e}")
            return Response(
                {'error': f'File not found: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            logger.warning(f"Permission denied during download: {e}")
            return Response(
                {'error': f'Permission denied: {str(e)}'},
                status=status.HTTP_403_FORBIDDEN
            )
        except OSError as e:
            logger.error(f"OS error during file download: {e}")
            return Response(
                {'error': f'Storage error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"Unexpected error during file download: {e}")
            return Response(
                {'error': 'Internal server error during download'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Delete a file entry and the physical file.
        """
        instance = self.get_object()
        # Permission handled by IsOwnerOrStaff permission class
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        Update file metadata (name, privacy, storage backend, folder).
        Does not allow updating the file itself - for that, user should delete and re-upload.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Permission handled by IsOwnerOrStaff permission class

        serializer = FileEntryUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class UnifiedFileFolderViewSet(viewsets.ViewSet):
    """
    Unified viewset for path-based file and folder operations.
    Allows unified handling of files and folders using paths instead of PKs.
    """
    permission_classes = [IsOwnerOrStaff]
    parser_classes = (MultiPartParser, FormParser)
    TTL=30

    def check_ownership_or_staff(self, obj, request):
        """
        Check if user is owner or staff.
        Raises PermissionDenied if not.
        """
        if hasattr(obj, 'owner') and obj.owner != request.user and not request.user.is_staff:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")
        return True
    def list(self, request):
        """
        List contents of a given path.
        If no path provided, lists root level folders.
        """
        path = request.query_params.get('path', '/')
         # 构造唯一缓存 key：包含用户和路径
        cache_key_raw = f"dir_cache:user:{request.user.id}:path:{path}"
        # 避免 key 中有非法字符（如空格、中文等）
        cache_key = "file_dir:" + hashlib.md5(cache_key_raw.encode()).hexdigest()
        # 尝试从缓存读取
        cached_data = get_cache(cache_key)
        
        if cached_data :
            files_data = cached_data['files']
            folders_data = cached_data['folders']
            full_path = cached_data['path']
        else:
            try:
                result = list_path_contents(path, request.user)

                # Serialize the results
                files_serializer = FileEntrySerializer(result['files'], many=True, context={'request': request})
                folders_serializer = FolderSerializer(result['folders'], many=True, context={'request': request})
                files_data = files_serializer.data
                folders_data = folders_serializer.data
                full_path = result['path']
                response_data = {
                    'path': result['path'],
                    'files': files_serializer.data,
                    'folders': folders_serializer.data
                }
                set_cache(cache_key,response_data,timeout=self.TTL)
            except FileNotFoundError as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
            except PermissionError as e:
                return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                logger.exception(f"Unexpected error in list_path_contents: {e}")
                return Response(
                    {'error': 'Internal server error while listing path contents'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
  

        etag = generate_dir_etag(files_data, folders_data)
        if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
        if if_none_match == f'"{etag}"':
            return HttpResponseNotModified()
        response = Response({
            'path': full_path,
            'files': files_data,
            'folders': folders_data
        })
        response['ETag'] = f'"{etag}"'
        response['Cache-Control'] = 'no-cache'  # 告诉浏览器不要本地缓存，但可协商
        return response
    
    
    
    def retrieve(self, request, pk=None, full_path=None):
        """
        Get a file or folder by path. With 'download=1' query parameter, downloads the file.
        With 'delete=1' query parameter, deletes the file or folder.
        Path is provided as 'full_path' parameter from custom URL pattern.
        """
        # Use full_path from the custom URL pattern, fallback to pk
        path = full_path or pk
        if path:
            # URL decode the path to handle any encoded characters
            decoded_path = urllib.parse.unquote(path)
            # Ensure it starts with a slash
            path = '/' + decoded_path if not decoded_path.startswith('/') else decoded_path
        else:
            path = '/'
        
      

        # Check if this is a download request
        if request.query_params.get('download'):
            return self.download_file(request, pk=None, full_path=path)

        try:
            obj, obj_type = resolve_path_to_object(path, request.user)
            
            if obj_type == 'file':
                serializer = FileEntrySerializer(obj, context={'request': request})
                return Response({
                    'type': 'file',
                    'data': serializer.data
                })
            elif obj_type == 'folder':
                serializer = FolderSerializer(obj, context={'request': request})
                return Response({
                    'type': 'folder',
                    'data': serializer.data
                })
        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.exception(f"Unexpected error in path resolution: {e}")
            return Response(
                {'error': 'Internal server error while resolving path'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def delete_path(self, request, pk=None, full_path=None):
        """
        Delete a file or folder by path.
        Path is provided as 'full_path' parameter from custom URL pattern or method parameter.
        """
        # Use provided path, or extract from the full_path parameter
        if not full_path and pk:
            # URL decode the pk to handle any encoded characters
            decoded_pk = urllib.parse.unquote(pk)
            # Ensure it starts with a slash
            full_path = '/' + decoded_pk if not decoded_pk.startswith('/') else decoded_pk
        elif full_path and not full_path.startswith('/'):
            full_path = '/' + full_path

        path = full_path or '/'

        try:
            # Resolve the path to determine if it's a file or folder
            obj, obj_type = resolve_path_to_object(path, request.user)

            # Check permissions - user must be owner or staff
            self.check_ownership_or_staff(obj, request)

            # If it's a file, delete it
            if obj_type == 'file':
                obj.delete()
                fresh_path = obj.folder.get_full_path() if obj.folder is not None else '/'
                invalidate_dir_cache(request.user.id, fresh_path)
                return Response(
                    {'message': f'File "{obj.name}" successfully deleted'},
                    status=status.HTTP_204_NO_CONTENT
                )
            # If it's a folder, delete it (this will recursively delete contents)
            elif obj_type == 'folder':
                # The delete method in the model handles recursive deletion
                obj.delete()
                fresh_path = obj.parent.get_full_path() if obj.parent is not None else '/'
                invalidate_dir_cache(request.user.id, fresh_path)
                return Response(
                    {'message': f'Folder "{obj.name}" and all its contents successfully deleted'},
                    status=status.HTTP_204_NO_CONTENT
                )

        except FileNotFoundError as e:
            logger.warning(f"File not found during deletion: {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            logger.warning(f"Permission denied during deletion: {e}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.exception(f"Unexpected error during deletion: {e}")
            return Response(
                {'error': 'Internal server error during deletion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='upload', permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def upload_file(self, request):
        """
        Upload a file to a specific path.
        Path is provided as query parameter.
        """
        path = request.query_params.get('path', '/')
        if not path:
            return Response({'error': 'Path parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use extracted utility for path parsing
            target_folder_path, filename = parse_upload_path(path)

            # Get the destination folder
            if target_folder_path == '/' or target_folder_path == '':
                destination_folder = None
            else:
                destination_folder = get_folder_by_path(target_folder_path, request.user)


            uploaded_file = request.FILES.get('file')  # assuming field name is 'file'
            if not uploaded_file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            # Use parsed filename from path if provided, otherwise use uploaded file's name
            if not filename:
                filename = uploaded_file.name
            try:
                existing_file = FileEntry.objects.get(name=filename, folder=destination_folder, owner=request.user)
                is_update = True
            except FileEntry.DoesNotExist:
                existing_file = None
                is_update = False

            # Initialize serializer
            serializer = FileUploadSerializer(
                instance=existing_file,  # pass instance for update if exists
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                # Set the destination folder
                if 'folder' not in serializer.validated_data:
                    serializer.validated_data['folder'] = destination_folder

                # If folder is provided in the data, check if it's different from path
                if 'folder' in request.data:
                    # Use folder from request data
                    file_entry = serializer.save()
                else:
                    # Use path-derived folder
                    file_entry = serializer.save(folder=destination_folder)

                response_serializer = FileEntrySerializer(file_entry, context={'request': request})
                invalidate_dir_cache(request.user.id, target_folder_path if target_folder_path!='' else '/')
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except FileNotFoundError as e:
            logger.warning(f"Path not found during file upload: {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            logger.warning(f"Permission denied during file upload: {e}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except OSError as e:
            logger.error(f"OS error during file upload: {e}")
            return Response(
                {'error': f'Storage error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"Unexpected error during file upload: {e}")
            return Response(
                {'error': 'Internal server error during upload'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def download_file(self, request, pk=None, full_path=None):
        """
        Download a file by path.
        Path is provided as 'full_path' parameter from custom URL pattern or method parameter.
        """
        # Use provided path, or extract from the full_path parameter
        if not full_path and pk:
            # URL decode the pk to handle any encoded characters
            decoded_pk = urllib.parse.unquote(pk)
            # Ensure it starts with a slash
            full_path = '/' + decoded_pk if not decoded_pk.startswith('/') else decoded_pk
        elif full_path and not full_path.startswith('/'):
            full_path = '/' + full_path

        path = full_path or '/'

        try:
            # This should be a file path
            file_entry = get_file_by_path(path, request.user)

            # Check permissions for non-public files
            if not file_entry.is_public:
                self.check_ownership_or_staff(file_entry, request)

            # Use extracted utility for file download
            return download_file_by_path(file_entry, request)
        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='create-folder', permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def create_folder(self, request):
        """
        Create a folder at a specific path.
        """
        serializer = UnifiedPathSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        path = serializer.validated_data['path']

        try:
            # Use extracted utility for path parsing
            parent_folder_path, folder_name = parse_upload_path(path)

            if not folder_name:
                return Response({'error': 'Cannot create root folder'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the parent folder
            if parent_folder_path == '/' or parent_folder_path == '':
                parent_folder = None
            else:
                parent_folder = get_folder_by_path(parent_folder_path, request.user)

            # Check if folder already exists
            existing_folder = Folder.objects.filter(
                name=folder_name,
                parent=parent_folder,
                owner=request.user
            ).first()

            if existing_folder:
                return Response(
                    {'error': 'Folder with this name already exists at the specified path'},
                    status=status.HTTP_409_CONFLICT
                )

            # Create the new folder
            new_folder = Folder.objects.create(
                name=folder_name,
                parent=parent_folder,
                owner=request.user
            )

            folder_serializer = FolderSerializer(new_folder, context={'request': request})

            invalidate_dir_cache(request.user.id, parent_folder.get_full_path() if parent_folder else '/')
            return Response(folder_serializer.data, status=status.HTTP_201_CREATED)

        except FileNotFoundError as e:
            logger.warning(f"Parent folder not found during folder creation: {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            logger.warning(f"Permission denied during folder creation: {e}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            logger.warning(f"Invalid input during folder creation: {e}")
            return Response(
                {'error': f'Invalid input: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Unexpected error during folder creation: {e}")
            return Response(
                {'error': 'Internal server error during folder creation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def move_copy(self, request):
        """
        Move or copy a file or folder from source path to destination path.
        The destination path indicates where to place the source item.
        For example:
        - Move /folder1/file.txt to /folder2/ moves the file into folder2
        - Move /folder1/file.txt to /folder2/newname.txt renames and moves the file
        """
        serializer = MoveCopyPathSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        source_path = serializer.validated_data['source_path']
        destination_path = serializer.validated_data['destination_path']
        operation = serializer.validated_data['operation']

        try:
            # Resolve source object
            source_obj, source_type = resolve_path_to_object(source_path, request.user)

            # Parse destination to get folder and final name
            dest_folder, final_dest_name = parse_destination_path(
                destination_path, request.user, source_obj.name
            )

            # Validate the operation
            validate_move_operation(source_obj, dest_folder, operation, source_type)

            # If source is a file, perform file move/copy
            if source_type == 'file':
                return handle_file_move_copy(source_obj, dest_folder, operation, request, final_dest_name)
            # If source is a folder, perform folder move/copy
            elif source_type == 'folder':
                return handle_folder_move_copy(source_obj, dest_folder, operation, request, final_dest_name)
            else:
                return Response(
                    {'error': 'Source path must point to a file or folder'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except FileNotFoundError as e:
            logger.warning(f"Source or destination not found during move/copy: {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            logger.warning(f"Permission denied during move/copy: {e}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            logger.warning(f"Invalid move/copy operation: {e}")
            return Response(
                {'error': f'Invalid operation: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Unexpected error during move/copy: {e}")
            return Response(
                {'error': 'Internal server error during move/copy'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )