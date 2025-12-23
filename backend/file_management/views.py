"""
Views for file management API
"""
import hashlib
import json
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.utils.encoding import smart_str
from django.db.models import Q
import os

from common.utils.cache import get_cache, invalidate_dir_cache, set_cache
from .models import FileEntry, Folder
from .serializers import (
    FileEntrySerializer, FileUploadSerializer, FileEntryUpdateSerializer,
    FolderSerializer, UnifiedPathSerializer, MoveCopyPathSerializer
)
from .path_utils import resolve_path_to_object, list_path_contents, get_folder_by_path, get_file_by_path
from rest_framework.parsers import JSONParser

def generate_unique_name(name, parent_folder, is_file=True):
    """
    Generate a unique name to prevent conflicts when copying/moving files or folders.

    Args:
        name (str): Original name
        parent_folder: Parent folder object (None for root)
        is_file (bool): True if it's a file, False if it's a folder

    Returns:
        str: Unique name that doesn't conflict with existing items
    """
    if is_file:
        # For files, separate name and extension to maintain extension
        if '.' in name:
            name_part, ext = name.rsplit('.', 1)
            ext = f".{ext}"
        else:
            name_part = name
            ext = ""

        original_name_part = name_part
    else:
        # For folders, no extension to worry about
        original_name_part = name

    counter = 1
    new_name = name

    # Check for conflicts in the destination folder
    while True:
        if is_file:
            if parent_folder is None:
                # Looking in root: check for existing files with same name
                existing = FileEntry.objects.filter(folder=None, name=new_name).exists()
            else:
                existing = FileEntry.objects.filter(folder=parent_folder, name=new_name).exists()
        else:
            if parent_folder is None:
                # Looking in root: check for existing folders with same name
                existing = Folder.objects.filter(parent=None, name=new_name).exists()
            else:
                existing = Folder.objects.filter(parent=parent_folder, name=new_name).exists()

        if not existing:
            break

        # Generate new name with counter
        if is_file:
            new_name = f"{original_name_part} ({counter}){ext}"
        else:
            new_name = f"{original_name_part} ({counter})"

        counter += 1

    return new_name


class FolderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing folders.
    Allows creation, listing, updating, and deletion of folders.
    """
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    def get_queryset(self):
        """
        Optionally restricts returned folders based on authenticated user
        or public folders.
        """
        queryset = Folder.objects.all()

        # Non-staff users can only see their own folders
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)

        return queryset

    def perform_create(self, serializer):
        # Set owner to current user if not staff user
        if not self.request.user.is_staff:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        # Ensure user can only update their own folders (unless staff)
        folder = self.get_object()
        if folder.owner != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You do not have permission to update this folder.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure user can only delete their own folders (unless staff)
        if instance.owner != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You do not have permission to delete this folder.")

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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def contents(self, request, pk=None):
        """
        Get contents of a specific folder (files and subfolders).
        """
        folder = self.get_object()

        # Check permissions
        if folder.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to access this folder.'},
                status=status.HTTP_403_FORBIDDEN
            )

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
        elif self.action == 'move_copy':
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
        Update file metadata (name, privacy, storage backend, folder).
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


class UnifiedFileFolderViewSet(viewsets.ViewSet):
    """
    Unified viewset for path-based file and folder operations.
    Allows unified handling of files and folders using paths instead of PKs.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    TTL=30
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
                return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

      
        def generate_dir_etag(files_data, folders_data):
            # 提取文件的关键字段：(id, name)
            files_key = sorted(
                (f['id'], f['name']) for f in files_data
            )
            # 提取文件夹的关键字段：(id, name)
            folders_key = sorted(
                (f['id'], f['name']) for f in folders_data
            )
            content = {
                'files': files_key,
                'folders': folders_key
            }
            etag_str = json.dumps(content, sort_keys=True)
            return hashlib.md5(etag_str.encode()).hexdigest()
        
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
            import urllib.parse
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
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_path(self, request, pk=None, full_path=None):
        """
        Delete a file or folder by path.
        Path is provided as 'full_path' parameter from custom URL pattern or method parameter.
        """
        # Use provided path, or extract from the full_path parameter
        if not full_path and pk:
            # URL decode the pk to handle any encoded characters
            import urllib.parse
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
            if hasattr(obj, 'owner') and obj.owner != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'You do not have permission to delete this item.'},
                    status=status.HTTP_403_FORBIDDEN
                )

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
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'Unexpected error during deletion: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='upload', permission_classes=[permissions.IsAuthenticated])
    def upload_file(self, request):
        """
        Upload a file to a specific path.
        Path is provided as query parameter.
        """
        path = request.query_params.get('path', '/')
        if not path:
            return Response({'error': 'Path parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # If path ends with '/', treat it as a folder path
            if path.endswith('/'):
                target_folder_path = path.rstrip('/')
            else:
                # Split path to separate folder and filename
                path_parts = path.strip('/').split('/')
                target_folder_path = '/' + '/'.join(path_parts[:-1]) if len(path_parts) > 1 else '/'

            # Get the destination folder
            if target_folder_path == '/' or target_folder_path == '':
                destination_folder = None
            else:
                destination_folder = get_folder_by_path(target_folder_path, request.user)
                
                
            uploaded_file = request.FILES.get('file')  # assuming field name is 'file'
            if not uploaded_file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)        
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
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def download_file(self, request, pk=None, full_path=None):
        """
        Download a file by path.
        Path is provided as 'full_path' parameter from custom URL pattern or method parameter.
        """
        # Use provided path, or extract from the full_path parameter
        if not full_path and pk:
            # URL decode the pk to handle any encoded characters
            import urllib.parse
            decoded_pk = urllib.parse.unquote(pk)
            # Ensure it starts with a slash
            full_path = '/' + decoded_pk if not decoded_pk.startswith('/') else decoded_pk
        elif full_path and not full_path.startswith('/'):
            full_path = '/' + full_path

        path = full_path or '/'

        try:
            # This should be a file path
            file_entry = get_file_by_path(path, request.user)

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
                    # TODO 远程文件逻辑，暂时假定返回一个url
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
        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='create-folder', permission_classes=[permissions.IsAuthenticated])
    def create_folder(self, request):
        """
        Create a folder at a specific path.
        """
        serializer = UnifiedPathSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        path = serializer.validated_data['path']

        try:
            # Split path to parent folder path and new folder name
            path_parts = path.strip('/').split('/')
            if len(path_parts) == 1:  # Root level folder
                parent_folder = None
                folder_name = path_parts[0]
            elif len(path_parts) == 0 or (len(path_parts) == 1 and path_parts[0] == ''):
                return Response({'error': 'Cannot create root folder'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                parent_path = '/' + '/'.join(path_parts[:-1])
                folder_name = path_parts[-1]

                # Get the parent folder
                parent_folder = get_folder_by_path(parent_path, request.user) if parent_path != '/' else None

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
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
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

            # Determine destination folder and destination name
            normalized_dest_path = destination_path.rstrip('/')
            dest_path_parts = normalized_dest_path.split('/')
            dest_name = dest_path_parts[-1] if dest_path_parts and dest_path_parts[-1] else ''

            # If destination path ends with /, it's definitely a folder
            # Otherwise, we need to determine if last part is a folder name or new filename
            if destination_path.endswith('/'):
                # Definitely a folder destination
                dest_folder_path = destination_path.rstrip('/')
                if dest_folder_path == '':
                    dest_folder_path = '/'
                dest_folder = get_folder_by_path(dest_folder_path, request.user) if dest_folder_path != '/' else None
                final_dest_name = source_obj.name  # Keep original name when moving into folder
            else:
                # Need to check if destination is a folder or a new name
                try:
                    # Try to treat destination as a folder first
                    dest_folder = get_folder_by_path(destination_path, request.user)
                    # If successful, it's a folder - keep original name
                    final_dest_name = source_obj.name
                except FileNotFoundError:
                    # Destination is not a folder, so it's a new name
                    # Get parent folder instead
                    parent_path = '/'.join(dest_path_parts[:-1]) if len(dest_path_parts) > 1 else '/'
                    dest_folder = get_folder_by_path(parent_path, request.user) if parent_path != '/' and parent_path!='' else None
                    final_dest_name = dest_name

            # If source is a file, perform file move/copy
            if source_type == 'file':
                return self._handle_file_move_copy(source_obj, dest_folder, operation, request, final_dest_name)
            # If source is a folder, perform folder move/copy
            elif source_type == 'folder':
                return self._handle_folder_move_copy(source_obj, dest_folder, operation, request, final_dest_name)
            else:
                return Response(
                    {'error': 'Source path must point to a file or folder'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_file_move_copy(self, file_obj, destination_folder, operation, request, new_name=None):
        """Handle move/copy for file objects"""
        # Determine the final name based on the operation and destination
        if new_name:
            final_name = new_name
        else:
            final_name = file_obj.name  # Use original name if no new name is specified

        # If copying, ensure the name is unique in the destination folder to avoid conflicts
        if operation == 'copy':
            final_name = generate_unique_name(final_name, destination_folder, is_file=True)
        else:  # move operation
            # For move, if destination already has a file with the same name, generate a unique name
            # only if source and destination are the same and it's the same file
            if destination_folder == file_obj.folder and file_obj.name == final_name:
               return Response({
                'message': 'File successfully moved',
                'file': FileEntrySerializer(file_obj, context={'request': request}).data,
                'original_folder': FolderSerializer(file_obj.folder, context={'request': request}).data ,
                'new_folder': FolderSerializer(file_obj.folder, context={'request': request}).data
            })
 
        if operation == 'move':
            # Move the file: update the folder reference
            original_folder = file_obj.folder
            file_obj.folder = destination_folder
            # Update name if different
            if final_name != file_obj.name:
                file_obj.name = final_name
            file_obj.save()
            invalidate_dir_cache(request.user.id, original_folder.get_full_path() if original_folder else '/') 
            invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')
            return Response({
                'message': 'File successfully moved',
                'file': FileEntrySerializer(file_obj, context={'request': request}).data,
                'original_folder': FolderSerializer(original_folder, context={'request': request}).data if original_folder else None,
                'new_folder': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
            })
        else:  # copy
            # Copy the file by creating a new entry
            from django.forms.models import model_to_dict

            file_data = model_to_dict(file_obj)
            file_data.pop('id', None)  # Remove ID to create new instance
            file_data.pop('created_at', None)
            file_data.pop('updated_at', None)
            # Fix: Make sure the owner is properly referenced as a User object
            file_data['owner'] = file_obj.owner
            file_data['folder'] = destination_folder
            file_data['file'] = file_obj.file  # Reference the same file
            file_data['name'] = final_name  # Use the unique name

            copied_file = FileEntry.objects.create(**file_data)
            invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')
            return Response({
                'message': 'File successfully copied',
                'file': FileEntrySerializer(copied_file, context={'request': request}).data,
                'destination_folder': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
            })

    def _handle_folder_move_copy(self, folder_obj, destination_folder, operation, request, new_name=None):
        """Handle move/copy for folder objects"""
        # Determine the final name based on the operation and destination
        if new_name:
            final_name = new_name
        else:
            final_name = folder_obj.name  # Use original name if no new name is specified

        # If copying, ensure the name is unique in the destination folder to avoid conflicts
        if operation == 'copy':
            final_name = generate_unique_name(final_name, destination_folder, is_file=False)
        else:  # move operation
            # For move, if destination already has a folder with the same name, generate a unique name
            # only if source and destination are the same and it's the same folder
            if destination_folder == folder_obj.parent and folder_obj.name == final_name:
                return Response({
                    'message': 'Folder successfully moved',
                    'result': None
                })

        if operation == 'move':
            result = self._move_folder(folder_obj, destination_folder, request, final_name)
            source_folder_path = folder_obj.parent.get_full_path() if folder_obj.parent else '/'
            invalidate_dir_cache(request.user.id, source_folder_path)
            invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')
            return Response({
                'message': 'Folder successfully moved',
                'result': result
            })
        else:  # copy
            result = self._copy_folder(folder_obj, destination_folder, request, final_name)
            invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')
            return Response({
                'message': 'Folder successfully copied',
                'result': result
            })

    def _move_folder(self, folder, destination_folder, request, new_name=None):
        """Move a folder to a new location"""
        if destination_folder and destination_folder.id == folder.id:
            raise ValueError("Cannot move folder to itself")

        # Check for circular reference when moving
        if destination_folder:
            current = destination_folder
            visited = set()
            while current:
                if current.id in visited:
                    break
                if current.id == folder.id:
                    raise ValueError("Cannot move folder to its own descendant")
                visited.add(current.id)
                current = current.parent

        original_parent = folder.parent
        folder.parent = destination_folder
        # Update name if different
        if new_name and new_name != folder.name:
            folder.name = new_name
        folder.save()

        return {
            'moved_folder': FolderSerializer(folder, context={'request': request}).data,
            'original_parent': FolderSerializer(original_parent, context={'request': request}).data if original_parent else None,
            'new_parent': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
        }

    def _copy_folder(self, folder, destination_folder, request, new_name=None):
        """Copy a folder to a new location (including all contents)"""
        from django.forms.models import model_to_dict

        # Create new folder
        folder_data = model_to_dict(folder)
        folder_data.pop('id', None)  # Remove ID to create new instance
        folder_data.pop('created_at', None)
        folder_data.pop('updated_at', None)
        # Fix: Make sure the owner is properly referenced as a User object
        folder_data['owner'] = folder.owner
        folder_data['parent'] = destination_folder
        # Update name if different
        if new_name:
            folder_data['name'] = new_name

        new_folder = Folder.objects.create(**folder_data)

        # Copy all files in the folder
        for file_entry in folder.files.all():
            file_data = model_to_dict(file_entry)
            file_data.pop('id', None)  # Remove ID to create new instance
            file_data.pop('created_at', None)
            file_data.pop('updated_at', None)
            # Fix: Make sure the owner is properly referenced as a User object
            file_data['owner'] = file_entry.owner
            file_data['folder'] = new_folder
            file_data['file'] = file_entry.file  # Copy the file reference
            FileEntry.objects.create(**file_data)

        # Recursively copy subfolders
        for subfolder in folder.children.all():
            self._copy_folder(subfolder, new_folder, request)

        return {
            'copied_folder': FolderSerializer(new_folder, context={'request': request}).data,
            'destination_folder': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
        }