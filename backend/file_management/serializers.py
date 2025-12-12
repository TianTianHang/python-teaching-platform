"""
Serializers for file management API
"""
from rest_framework import serializers
from .models import FileEntry, FileStorageBackend
from accounts.serializers import UserSerializer


class FileEntrySerializer(serializers.ModelSerializer):
    """Serializer for FileEntry model"""
    owner = UserSerializer(read_only=True)
    download_url = serializers.SerializerMethodField()
    formatted_file_size = serializers.SerializerMethodField()

    class Meta:
        model = FileEntry
        fields = [
            'id', 'name', 'file', 'file_size', 'formatted_file_size',
            'mime_type', 'storage_backend', 'owner', 'is_public',
            'created_at', 'updated_at', 'download_url'
        ]
        read_only_fields = ['id', 'file_size', 'mime_type', 'owner', 'created_at', 'updated_at']

    def get_download_url(self, obj):
        """Generate download URL for the file"""
        if obj.file:
            return obj.file.url
        return None

    def get_formatted_file_size(self, obj):
        """Format file size in human readable format"""
        size = obj.file_size

        # Convert bytes to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file upload"""
    file = serializers.FileField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = FileEntry
        fields = ['name', 'file', 'is_public', 'storage_backend']
        extra_kwargs = {
            'name': {'required': False},
            'storage_backend': {'required': False}
        }

    def create(self, validated_data):
        # If name not provided, use the original file name
        if not validated_data.get('name'):
            validated_data['name'] = validated_data['file'].name

        # Set the owner to the current user
        validated_data['owner'] = self.context['request'].user

        return super().create(validated_data)


class FileEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating file entry properties"""
    class Meta:
        model = FileEntry
        fields = ['name', 'is_public', 'storage_backend']