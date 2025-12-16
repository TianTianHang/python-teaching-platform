"""
Custom storage classes for file management system.
Supports local storage and S3-compatible object storage services.
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import os




class LocalMediaStorage:
    """Placeholder class for local media storage"""
    pass


class CustomS3Storage(S3Boto3Storage):
    """Custom S3 storage with specific configuration"""
    def __init__(self, **kwargs):
        # Override any default settings if needed
        kwargs['bucket_name'] = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        kwargs['location'] = getattr(settings, 'AWS_LOCATION', 'media')
        kwargs['file_overwrite'] = False  # Prevent overwriting files
        # Set S3-specific settings for compatibility with MinIO or other S3-compatible services
        if hasattr(settings, 'AWS_S3_ENDPOINT_URL') and settings.AWS_S3_ENDPOINT_URL:
            kwargs['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL
        if hasattr(settings, 'AWS_S3_REGION_NAME') and settings.AWS_S3_REGION_NAME:
            kwargs['region_name'] = settings.AWS_S3_REGION_NAME
        if hasattr(settings, 'AWS_S3_USE_SSL'):
            kwargs['use_ssl'] = settings.AWS_S3_USE_SSL
        if hasattr(settings, 'AWS_S3_VERIFY'):
            kwargs['verify'] = settings.AWS_S3_VERIFY
        super().__init__(**kwargs)


class CustomMinioStorage(S3Boto3Storage):
    """Custom MinIO storage with specific configuration for S3 compatibility"""
    def __init__(self, **kwargs):
        # MinIO is S3-compatible, so we configure S3Boto3Storage for MinIO
        kwargs['bucket_name'] = getattr(settings, 'MINIO_BUCKET_NAME', 'file-management')
        kwargs['endpoint_url'] = getattr(settings, 'MINIO_ENDPOINT_URL', 'http://localhost:9000')
        kwargs['access_key'] = getattr(settings, 'MINIO_ACCESS_KEY', '')
        kwargs['secret_key'] = getattr(settings, 'MINIO_SECRET_KEY', '')
        kwargs['region_name'] = getattr(settings, 'MINIO_REGION_NAME', '')
        kwargs['use_ssl'] = getattr(settings, 'MINIO_USE_SSL', False)
        kwargs['verify'] = getattr(settings, 'MINIO_VERIFY', True)
        kwargs['file_overwrite'] = False  # Prevent overwriting files
        # Set proper ACL for MinIO
        kwargs.setdefault('default_acl', 'public-read')
        super().__init__(**kwargs)

