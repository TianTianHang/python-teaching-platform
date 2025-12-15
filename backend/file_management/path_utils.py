"""
Utility functions for path-based file and folder operations
"""
from pathlib import PurePath
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
    if path == '/' or path == '':
        # Return root folders for the user
        folders = Folder.objects.filter(parent=None)
        if not user.is_staff:
            folders = folders.filter(owner=user)
        return folders, 'folder_list'
    
    # Normalize path and split into components
    normalized_path = path.strip('/')
    if not normalized_path:
        # Root path
        folders = Folder.objects.filter(parent=None)
        if not user.is_staff:
            folders = folders.filter(owner=user)
        return folders, 'folder_list'
    
    path_parts = normalized_path.split('/')
    
    # Start from the root level with the first part
    current_folder = None
    
    # Find the first folder in the path
    first_folder_query = Folder.objects.filter(name=path_parts[0], parent=None)
    if not user.is_staff:
        first_folder_query = first_folder_query.filter(owner=user)
    
    try:
        current_folder = first_folder_query.get()
    except Folder.DoesNotExist:
        raise FileNotFoundError(f"Folder '{path}' does not exist")
    
    # Navigate through the remaining path components
    for i in range(1, len(path_parts)):
        part = path_parts[i]
        
        # Check if this is the last part and it might be a file
        if i == len(path_parts) - 1:
            # First check if it's a subfolder
            potential_folder = Folder.objects.filter(
                parent=current_folder,
                name=part
            ).first()
            
            if potential_folder:
                return potential_folder, 'folder'
            
            # Then check if it's a file
            if include_files:
                potential_file = FileEntry.objects.filter(
                    folder=current_folder,
                    name=part
                ).first()
                
                # Apply permissions for files
                if potential_file:
                    if not user.is_staff and potential_file.owner != user and not potential_file.is_public:
                        raise PermissionError(f"You do not have permission to access this file at '{path}'")
                    return potential_file, 'file'
        
        # If it's not the last part or not found as file, treat as folder
        next_folder = Folder.objects.filter(
            parent=current_folder,
            name=part
        ).first()
        
        if next_folder is None:
            raise FileNotFoundError(f"Folder '{path}' does not exist")
        
        # Apply permissions for folders
        if not user.is_staff and next_folder.owner != user:
            raise PermissionError(f"You do not have permission to access this folder at '{path}'")
        
        current_folder = next_folder
    
    return current_folder, 'folder'


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
        if not user.is_staff:
            folders = folders.filter(owner=user)
        return {
            'files': [],
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