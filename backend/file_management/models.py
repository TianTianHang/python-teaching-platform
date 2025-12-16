from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import os

from file_management.storages import CustomMinioStorage, CustomS3Storage


User = get_user_model()


def file_upload_path(instance, filename):
    """
    Define the upload path for files.
    Organizes files by user ID and date.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join(
        'uploads',
        str(instance.owner.id if instance.owner else 'anonymous'),
        str(timezone.now().year),
        str(timezone.now().month),
        filename
    )


class FileStorageBackend(models.TextChoices):
    LOCAL = 'local', 'Local Storage'
    S3 = 's3', 'Amazon S3'
    MINIO = 'minio', 'MinIO (S3 Compatible)'

def get_storage_backend(backend_type=FileStorageBackend.LOCAL):
    """
    Factory function to return the appropriate storage backend.

    Args:
        backend_type (str): Type of storage backend ('local', 's3', 'minio')

    Returns:
        Storage backend instance
    """
    if backend_type == FileStorageBackend.S3:
        return CustomS3Storage()
    elif backend_type == FileStorageBackend.MINIO:
        return CustomMinioStorage()
    else:  # Default to local storage
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage(location=settings.MEDIA_ROOT)

class Folder(models.Model):
    """
    Model to represent folders in a hierarchical file system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Folder name")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='folders',
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name="Parent folder"
    )
    is_public = models.BooleanField(default=False, help_text="Allow public access to the folder and its contents")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Folder'
        verbose_name_plural = 'Folders'
        unique_together = ['name', 'parent', 'owner']  # A folder name must be unique within a parent folder

    def __str__(self):
        return f"{self.name} (Folder)"

    def clean(self):
        # Prevent a folder from being its own parent
        if self.parent and self.parent.id == self.id:
            raise ValidationError("A folder cannot be its own parent.")

        # Prevent circular reference by checking if the parent is actually a descendant of this folder
        if self.parent:
            current = self.parent
            visited = set()
            while current:
                if current.id in visited:
                    raise ValidationError("Circular reference detected in folder hierarchy.")
                if current.id == self.id:
                    raise ValidationError("Circular reference detected in folder hierarchy.")
                visited.add(current.id)
                current = current.parent

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_path(self):
        """Get the full path of the folder from root."""
        path_parts = []
        current = self
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return "/" + "/".join(path_parts)

    def get_children(self):
        """Get all child files and folders."""
        files = FileEntry.objects.filter(folder=self)
        folders = Folder.objects.filter(parent=self)
        return {
            'files': files,
            'folders': folders
        }

    def get_descendants(self):
        """Recursively get all descendant folders."""
        descendants = []
        for child_folder in self.children.all():
            descendants.append(child_folder)
            descendants.extend(child_folder.get_descendants())
        return descendants

    def get_contents_recursive(self):
        """Get all files and folders recursively."""
        contents = {
            'files': FileEntry.objects.filter(folder=self),
            'folders': Folder.objects.filter(parent=self)
        }

        # Recursively add contents of child folders
        for child_folder in contents['folders']:
            child_contents = child_folder.get_contents_recursive()
            contents['files'] = contents['files'] | child_contents['files']
            contents['folders'] = contents['folders'] | child_contents['folders']

        return contents


class FileEntry(models.Model):
    """
    Model to represent uploaded files with folder support.
    Supports both local and object storage backends.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Original file name")
    file = models.FileField(upload_to=file_upload_path, max_length=500)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    storage_backend = models.CharField(
        max_length=20,
        choices=FileStorageBackend.choices,
        default=FileStorageBackend.LOCAL
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        null=True,
        blank=True
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        related_name='files',
        null=True,
        blank=True,
        verbose_name="Parent folder"
    )
    is_public = models.BooleanField(default=False, help_text="Allow public access to the file")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'File Entry'
        verbose_name_plural = 'File Entries'
        unique_together = ['name', 'folder', 'owner']  # A file name must be unique within a folder

    def __str__(self):
        if self.folder:
            return f"{self.name} in {self.folder.name} ({self.get_storage_backend_display()})"
        return f"{self.name} ({self.get_storage_backend_display()})"

    def clean(self):
        if self.file_size <= 0:
            raise ValidationError("File size must be greater than zero.")

        if self.mime_type and '/' not in self.mime_type:
            raise ValidationError("Invalid MIME type format.")

        # Ensure the folder belongs to the same owner as the file (if both have owners)
        if self.folder and self.owner and self.folder.owner != self.owner:
            raise ValidationError("File and folder must belong to the same user.")

    def save(self, *args, **kwargs):
        # Set file size automatically if not provided
        if not self.file_size and self.file:
            try:
                self.file_size = self.file.size
            except AttributeError:
                pass

        # Set MIME type automatically if not provided
        if not self.mime_type and self.file:
            import mimetypes
            self.mime_type, _ = mimetypes.guess_type(self.file.name)
        self.file.storage =get_storage_backend(self.storage_backend)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete to also remove the actual file from storage.
        """
        # Delete the actual file from storage
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def get_full_path(self):
        """Get the full path of the file from root."""
        path_parts = [self.name]
        if self.folder:
            path_parts.insert(0, self.folder.get_full_path()[1:])  # Remove leading slash
        return "/" + "/".join(path_parts)
