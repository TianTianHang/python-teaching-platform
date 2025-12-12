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

class FileEntry(models.Model):
    """
    Model to represent uploaded files.
    Supports both local and object storage backends.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Original file name",unique=True)
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
    is_public = models.BooleanField(default=False, help_text="Allow public access to the file")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'File Entry'
        verbose_name_plural = 'File Entries'

    def __str__(self):
        return f"{self.name} ({self.get_storage_backend_display()})"

    def clean(self):
        if self.file_size <= 0:
            raise ValidationError("File size must be greater than zero.")

        if self.mime_type and '/' not in self.mime_type:
            raise ValidationError("Invalid MIME type format.")

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
