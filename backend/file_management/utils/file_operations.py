"""
File and folder operations utilities.
Provides high-level operations for file management like move, copy, delete.
"""
import hashlib
import json
import logging
from django.db import transaction
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.response import Response

from file_management.models import FileEntry, Folder
from file_management.serializers import FileEntrySerializer, FolderSerializer
from common.utils.cache import invalidate_dir_cache

logger = logging.getLogger(__name__)


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


def download_file_by_path(file_entry, request):
    """
    Download a file, handling different storage backends.

    Args:
        file_entry: FileEntry instance to download
        request: Request object for context

    Returns:
        Response object with file download or error

    Raises:
        Http404: If file not found on disk
    """
    from django.http import Http404, HttpResponse, FileResponse
    from django.utils.encoding import smart_str
    import os

    if not file_entry.file:
        raise Http404("File not found")

    try:
        file_obj = file_entry.file
        file_path = file_obj.path if hasattr(file_obj, 'path') else file_obj.name

        # For local storage, use FileResponse for streaming
        if file_entry.storage_backend == 'local':
            if os.path.exists(file_path):
                return FileResponse(
                    open(file_path, 'rb'),
                    as_attachment=True,
                    filename=smart_str(file_entry.name)
                )
            else:
                raise Http404("File not found on disk")
        else:
            # For cloud storage, redirect to the cloud storage URL
            if hasattr(file_obj, 'url'):
                return Response({'redirect_url': file_obj.url}, status=status.HTTP_302_FOUND)
            else:
                return FileResponse(
                    file_obj.open(),
                    as_attachment=True,
                    filename=smart_str(file_entry.name)
                )
    except Exception as e:
        logger.exception(f"Error during file download: {e}")
        raise


def validate_move_operation(source_obj, dest_folder, operation, source_type):
    """
    Validate that the move/copy operation is valid.

    Args:
        source_obj: The source file or folder object
        dest_folder: The destination folder object (None for root)
        operation: 'move' or 'copy'
        source_type: 'file' or 'folder'

    Raises:
        ValueError: If the operation is invalid (e.g., circular reference)
    """
    if source_type == 'folder' and operation == 'move' and dest_folder:
        # Check for circular reference when moving a folder
        if dest_folder.id == source_obj.id:
            raise ValueError("Cannot move folder to itself")

        # Check if destination is a descendant of source
        current = dest_folder
        visited = set()
        while current:
            if current.id in visited:
                break
            if current.id == source_obj.id:
                raise ValueError("Cannot move folder to its own descendant")
            visited.add(current.id)
            current = current.parent


@transaction.atomic
def handle_file_move_copy(file_obj, destination_folder, operation, request, new_name=None):
    """
    Handle move/copy for file objects.

    Args:
        file_obj: FileEntry instance to move/copy
        destination_folder: Folder instance (None for root)
        operation: 'move' or 'copy'
        request: Request object for serialization
        new_name: Optional new name for the file

    Returns:
        Response object with operation result
    """
    # generate_unique_name is defined in this module, no import needed

    # Determine the final name based on the operation and destination
    if new_name:
        final_name = new_name
    else:
        final_name = file_obj.name

    # If copying, ensure the name is unique in the destination folder
    if operation == 'copy':
        final_name = generate_unique_name(final_name, destination_folder, is_file=True)
    else:  # move operation
        if destination_folder == file_obj.folder and file_obj.name == final_name:
            return Response({
                'message': 'File successfully moved',
                'file': FileEntrySerializer(file_obj, context={'request': request}).data,
                'original_folder': FolderSerializer(file_obj.folder, context={'request': request}).data,
                'new_folder': FolderSerializer(file_obj.folder, context={'request': request}).data
            })

    if operation == 'move':
        original_folder = file_obj.folder
        file_obj.folder = destination_folder
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
        file_data = model_to_dict(file_obj)
        file_data.pop('id', None)
        file_data.pop('created_at', None)
        file_data.pop('updated_at', None)
        file_data['owner'] = file_obj.owner
        file_data['folder'] = destination_folder
        file_data['file'] = file_obj.file
        file_data['name'] = final_name

        copied_file = FileEntry.objects.create(**file_data)
        invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')

        return Response({
            'message': 'File successfully copied',
            'file': FileEntrySerializer(copied_file, context={'request': request}).data,
            'destination_folder': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
        })


@transaction.atomic
def handle_folder_move_copy(folder_obj, destination_folder, operation, request, new_name=None):
    """
    Handle move/copy for folder objects.

    Args:
        folder_obj: Folder instance to move/copy
        destination_folder: Destination Folder instance (None for root)
        operation: 'move' or 'copy'
        request: Request object for serialization
        new_name: Optional new name for the folder

    Returns:
        Response object with operation result
    """
    
    if new_name:
        final_name = new_name
    else:
        final_name = folder_obj.name

    if operation == 'copy':
        final_name = generate_unique_name(final_name, destination_folder, is_file=False)
    else:  # move operation
        if destination_folder == folder_obj.parent and folder_obj.name == final_name:
            return Response({
                'message': 'Folder successfully moved',
                'result': None
            })

    if operation == 'move':
        result = move_folder(folder_obj, destination_folder, request, final_name)
        source_folder_path = folder_obj.parent.get_full_path() if folder_obj.parent else '/'
        invalidate_dir_cache(request.user.id, source_folder_path)
        invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')

        return Response({
            'message': 'Folder successfully moved',
            'result': result
        })
    else:  # copy
        result = copy_folder_recursive(folder_obj, destination_folder, request, final_name)
        invalidate_dir_cache(request.user.id, destination_folder.get_full_path() if destination_folder else '/')

        return Response({
            'message': 'Folder successfully copied',
            'result': result
        })


def move_folder(folder, destination_folder, request, new_name=None):
    """
    Move a folder to a new location.
    Note: Validation (circular reference checks) should be done before calling.

    Args:
        folder: Folder instance to move
        destination_folder: Destination Folder instance (None for root)
        request: Request object for serialization
        new_name: Optional new name for the folder

    Returns:
        dict: Dictionary with moved folder info
    """
    original_parent = folder.parent
    folder.parent = destination_folder
    if new_name and new_name != folder.name:
        folder.name = new_name
    folder.save()

    return {
        'moved_folder': FolderSerializer(folder, context={'request': request}).data,
        'original_parent': FolderSerializer(original_parent, context={'request': request}).data if original_parent else None,
        'new_parent': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
    }


@transaction.atomic
def copy_folder_recursive(folder, destination_folder, request, new_name=None):
    """
    Copy a folder to a new location (including all contents).

    Args:
        folder: Folder instance to copy
        destination_folder: Destination Folder instance (None for root)
        request: Request object for serialization
        new_name: Optional new name for the folder

    Returns:
        dict: Dictionary with copied folder info
    """
    # Create new folder
    folder_data = model_to_dict(folder)
    folder_data.pop('id', None)
    folder_data.pop('created_at', None)
    folder_data.pop('updated_at', None)
    folder_data['owner'] = folder.owner
    folder_data['parent'] = destination_folder
    if new_name:
        folder_data['name'] = new_name

    new_folder = Folder.objects.create(**folder_data)

    # Copy all files in the folder
    for file_entry in folder.files.all():
        file_data = model_to_dict(file_entry)
        file_data.pop('id', None)
        file_data.pop('created_at', None)
        file_data.pop('updated_at', None)
        file_data['owner'] = file_entry.owner
        file_data['folder'] = new_folder
        file_data['file'] = file_entry.file
        FileEntry.objects.create(**file_data)

    # Recursively copy subfolders
    for subfolder in folder.children.all():
        copy_folder_recursive(subfolder, new_folder, request)

    return {
        'copied_folder': FolderSerializer(new_folder, context={'request': request}).data,
        'destination_folder': FolderSerializer(destination_folder, context={'request': request}).data if destination_folder else None
    }


def generate_dir_etag(files_data, folders_data):
    """
    Generate ETag for directory listing.

    Args:
        files_data: List of serialized file data
        folders_data: List of serialized folder data

    Returns:
        str: MD5 hash ETag
    """
    files_key = sorted((f['id'], f['name']) for f in files_data)
    folders_key = sorted((f['id'], f['name']) for f in folders_data)
    content = {
        'files': files_key,
        'folders': folders_key
    }
    etag_str = json.dumps(content, sort_keys=True)
    return hashlib.md5(etag_str.encode()).hexdigest()