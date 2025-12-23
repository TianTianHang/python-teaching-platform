"""
Utility functions for path-based file and folder operations
"""
from pathlib import PurePath

from common.utils.cache import delete_cache_pattern, get_cache, set_cache
from .models import FileEntry, Folder
from django.shortcuts import get_object_or_404
from django.db.models import Q


def resolve_path_to_object(path, user, include_files=True, include_folders=True):
    """
    Resolve a path to a file or folder object.
    
    Args:
        path (str): Path to resolve (e.g., '/folder/subfolder/file.txt' or '/folder/subfolder/')
        user: Django user object for permission checking
        include_files (bool): Whether to include files in the search
        include_folders (bool): Whether to include folders in the search
    
    Returns:
        tuple: (object, type) where object is the FileEntry or Folder instance,
               and type is 'file' or 'folder'
    """
    normalized_path = path.strip('/')
    
    if not normalized_path:
        raise FileNotFoundError("Root path '/' cannot be resolved to a file or folder object")

    path_parts = normalized_path.split('/')

    # Special case: single component (e.g., '/file.txt' or '/docs')
    if len(path_parts) == 1:
        part = path_parts[0]

        # First, try to find a file in root (parent=None for files means root)
        if include_files:
            file_query = FileEntry.objects.filter(folder=None, name=part)
            potential_file = file_query.first()
            if potential_file:
                # Permission check for file
                if not user.is_staff and potential_file.owner != user and not potential_file.is_public:
                    raise PermissionError(f"You do not have permission to access this file at '{path}'")
                return potential_file, 'file'

        # Then, try to find a top-level folder
        if include_folders:
            folder_query = Folder.objects.filter(parent=None, name=part)
            if not user.is_staff:
                folder_query = folder_query.filter(owner=user)
            potential_folder = folder_query.first()
            if potential_folder:
                return potential_folder, 'folder'

        # Not found
        raise FileNotFoundError(f"Path '{path}' does not exist")

    
    cache_key = f"folder_by_path:{user.id}:/{'/'.join(path_parts[:-1])}"
    folder_id = get_cache(cache_key)
    if folder_id is not None:
        try:
            # 直接通过 ID 获取对象（1 次 DB 查询，但可接受；或进一步缓存完整对象）
            current_folder = Folder.objects.get(id=folder_id)
            # 再做一次权限检查（防止缓存时用户权限已变更）
            if not user.is_staff and current_folder.owner_id != user.id:
                raise PermissionError(f"No permission to access '{path}'")
        except Folder.DoesNotExist:
            # 缓存了无效 ID，清除它
            delete_cache_pattern(cache_key)
            
    # 缓存未命中
    if current_folder is None:
        # Multi-component path: navigate hierarchy
        # Start from root folder (first component must be a folder)
        first_part = path_parts[0]
        folder_query = Folder.objects.filter(parent=None, name=first_part)
        if not user.is_staff:
            folder_query = folder_query.filter(owner=user)
        try:
            current_folder = folder_query.get()
        except Folder.DoesNotExist:
            raise FileNotFoundError(f"Folder '{path}' does not exist")
        # Traverse intermediate folders
        for i in range(1, len(path_parts) - 1):
            part = path_parts[i]
            next_folder = Folder.objects.filter(parent=current_folder, name=part).first()
            if next_folder is None:
                raise FileNotFoundError(f"Folder '{path}' does not exist")
            if not user.is_staff and next_folder.owner != user:
                raise PermissionError(f"You do not have permission to access this folder at '{path}'")
            current_folder = next_folder
        set_cache(cache_key,current_folder,timeout=300)
    # Last component: could be file or folder
    last_part = path_parts[-1]

    # Try folder first
    if include_folders:
        potential_folder = Folder.objects.filter(parent=current_folder, name=last_part).first()
        if potential_folder:
            if not user.is_staff and potential_folder.owner != user:
                raise PermissionError(f"You do not have permission to access this folder at '{path}'")
            return potential_folder, 'folder'

    # Then try file
    if include_files:
        potential_file = FileEntry.objects.filter(folder=current_folder, name=last_part).first()
        if potential_file:
            if not user.is_staff and potential_file.owner != user and not potential_file.is_public:
                raise PermissionError(f"You do not have permission to access this file at '{path}'")
            return potential_file, 'file'

    raise FileNotFoundError(f"Path '{path}' does not exist")


def list_path_contents(path, user):
    """
    List contents of a path (files and folders).
    
    Args:
        path (str): Path to list contents for
        user: Django user object for permission checking
    
    Returns:
        dict: Dictionary containing files and folders at the given path
    """
    if path == '/' or path.strip('/') == '':
        # List root level folders
        folders = Folder.objects.filter(parent=None)
        files = FileEntry.objects.filter(folder=None)
        if not user.is_staff:
            folders = folders.filter(owner=user)
        return {
            'files': list(files),
            'folders': list(folders),
            'path': '/'
        }
    
    # Ensure path ends with '/' to indicate it's a directory
    if not path.endswith('/'):
        path = path + '/'
    
    # Resolve the path to an object (should be a folder)
    obj, obj_type = resolve_path_to_object(path.rstrip('/'), user, include_files=False, include_folders=True)
    
    if obj_type != 'folder':
        raise FileNotFoundError(f"Path '{path}' does not point to a folder")
    
    # List contents of this folder
    files = FileEntry.objects.filter(folder=obj)
    if not user.is_staff:
        files = files.filter(Q(owner=user) | Q(is_public=True))
    
    subfolders = Folder.objects.filter(parent=obj)
    if not user.is_staff:
        subfolders = subfolders.filter(owner=user)
    
    return {
        'files': list(files),
        'folders': list(subfolders),
        'path': path.rstrip('/')
    }


def get_folder_by_path(path, user):
    """
    Get a folder by its path.
    
    Args:
        path (str): Path to the folder
        user: Django user object for permission checking
    
    Returns:
        Folder: Folder instance
    """
    obj, obj_type = resolve_path_to_object(path, user, include_files=False, include_folders=True)
    if obj_type != 'folder':
        raise FileNotFoundError(f"No folder exists at path '{path}'")
    return obj


def get_file_by_path(path, user):
    """
    Get a file by its path.
    
    Args:
        path (str): Path to the file
        user: Django user object for permission checking
    
    Returns:
        FileEntry: FileEntry instance
    """
    obj, obj_type = resolve_path_to_object(path, user, include_files=True, include_folders=False)
    if obj_type != 'file':
        raise FileNotFoundError(f"No file exists at path '{path}'")
    # Permission check already handled in resolve_path_to_object
    return obj