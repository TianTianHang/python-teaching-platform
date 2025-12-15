"""
Serializers for file management API
"""
from rest_framework import serializers
from .models import FileEntry, FileStorageBackend, Folder
from accounts.serializers import UserSerializer


class FolderSerializer(serializers.ModelSerializer):
    """Serializer for Folder model"""
    owner = UserSerializer(read_only=True)
    children_count = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'owner', 'parent', 'is_public',
            'created_at', 'updated_at', 'children_count', 'path'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        """Return the count of child files and folders"""
        files_count = obj.files.count()
        folders_count = obj.children.count()
        return {
            'files': files_count,
            'folders': folders_count,
            'total': files_count + folders_count
        }

    def get_path(self, obj):
        """Return the full path of the folder"""
        return obj.get_full_path()

    def validate_parent(self, value):
        """Validate that the parent folder belongs to the same owner"""
        request = self.context.get('request')
        if value and request and request.user != value.owner and not request.user.is_staff:
            raise serializers.ValidationError("You do not have permission to use this parent folder.")
        return value

    def validate(self, attrs):
        """Validate folder creation"""
        request = self.context.get('request')
        if request and not request.user.is_staff:
            # Ensure folder belongs to current user when created
            if 'owner' not in attrs or not attrs['owner']:
                attrs['owner'] = request.user

        parent = attrs.get('parent')
        if parent:
            # Prevent circular reference by checking if the parent is actually a descendant of this folder
            instance = getattr(self, 'instance', None)
            if instance:
                # For updates, check if we're trying to set parent to a descendant
                if parent == instance:
                    raise serializers.ValidationError({"parent": "A folder cannot be its own parent."})

                # Check for circular reference
                current = parent
                visited = set()
                while current:
                    if current.id in visited:
                        raise serializers.ValidationError({"parent": "Circular reference detected in folder hierarchy."})
                    if current.id == instance.id:
                        raise serializers.ValidationError({"parent": "Circular reference detected in folder hierarchy."})
                    visited.add(current.id)
                    current = current.parent

        return super().validate(attrs)


class FileEntrySerializer(serializers.ModelSerializer):
    """Serializer for FileEntry model"""
    owner = UserSerializer(read_only=True)
    download_url = serializers.SerializerMethodField()
    formatted_file_size = serializers.SerializerMethodField()
    folder_name = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = FileEntry
        fields = [
            'id', 'name', 'file', 'file_size', 'formatted_file_size',
            'mime_type', 'storage_backend', 'owner', 'folder', 'folder_name',
            'is_public', 'created_at', 'updated_at', 'download_url', 'path'
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

    def get_folder_name(self, obj):
        """Return the name of the parent folder"""
        if obj.folder:
            return obj.folder.name
        return None

    def get_path(self, obj):
        """Return the full path of the file"""
        return obj.get_full_path()

    def validate_folder(self, value):
        """Validate that the folder belongs to the same owner"""
        request = self.context.get('request')
        if value and request and request.user != value.owner and not request.user.is_staff:
            raise serializers.ValidationError("You do not have permission to use this folder.")
        return value


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file upload with folder support"""
    file = serializers.FileField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FileEntry
        fields = ['name', 'file', 'is_public', 'storage_backend', 'folder']
        extra_kwargs = {
            'name': {'required': False},
            'storage_backend': {'required': False},
            'folder': {'required': False}
        }

    def validate_folder(self, value):
        """Validate that the folder belongs to the same owner as the uploading user"""
        request = self.context.get('request')
        if value and request and request.user != value.owner and not request.user.is_staff:
            raise serializers.ValidationError("You do not have permission to upload to this folder.")
        return value

    def create(self, validated_data):
        # If name not provided, use the original file name
        if not validated_data.get('name'):
            validated_data['name'] = validated_data['file'].name

        # Set the owner to the current user
        validated_data['owner'] = self.context['request'].user

        return super().create(validated_data)


class FileEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating file entry properties"""
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FileEntry
        fields = ['name', 'is_public', 'storage_backend', 'folder']

    def validate_folder(self, value):
        """Validate that the folder belongs to the same owner"""
        if value and self.instance and self.instance.owner != value.owner and not self.instance.owner.is_staff:
            raise serializers.ValidationError("You do not have permission to move file to this folder.")
        return value


class MoveCopyFileSerializer(serializers.Serializer):
    """Serializer for moving/copying files"""
    destination_folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    operation = serializers.ChoiceField(choices=['move', 'copy'])

    def validate_destination_folder(self, value):
        """Validate that the destination folder belongs to the same owner"""
        request = self.context.get('request')
        if request and request.user != value.owner and not request.user.is_staff:
            raise serializers.ValidationError("You do not have permission to use this destination folder.")
        return value


class MoveCopyFolderSerializer(serializers.Serializer):
    """Serializer for moving/copying folders"""
    destination_folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all(), required=False, allow_null=True)
    operation = serializers.ChoiceField(choices=['move', 'copy'])

    def validate_destination_folder(self, value):
        """Validate that the destination folder belongs to the same owner"""
        request = self.context.get('request')
        if value and request and request.user != value.owner and not request.user.is_staff:
            raise serializers.ValidationError("You do not have permission to use this destination folder.")
        return value

    def validate(self, attrs):
        """Additional validation for folder operations"""
        folder_id = self.context.get('folder_id')
        destination_folder = attrs.get('destination_folder')

        if folder_id and destination_folder:
            # Prevent moving/copying a folder into itself or one of its descendants
            try:
                source_folder = Folder.objects.get(id=folder_id)

                # Check if destination is same as source
                if source_folder.id == destination_folder.id:
                    raise serializers.ValidationError({"destination_folder": "Cannot move/copy folder to itself."})

                # Check if destination is a descendant of source (for move operations)
                if attrs['operation'] == 'move':
                    current = destination_folder
                    visited = set()
                    while current:
                        if current.id in visited:
                            break
                        if current.id == source_folder.id:
                            raise serializers.ValidationError({"destination_folder": "Cannot move folder to its own descendant."})
                        visited.add(current.id)
                        current = current.parent

            except Folder.DoesNotExist:
                pass

        return attrs


class UnifiedPathSerializer(serializers.Serializer):
    """Unified serializer for path-based operations"""
    path = serializers.CharField(max_length=1000, help_text="Path to file or folder (e.g., '/folder/subfolder/file.txt')")

    def validate_path(self, value):
        """Validate the path format"""
        if not value.startswith('/'):
            raise serializers.ValidationError("Path must start with '/'")
        return value


class MoveCopyPathSerializer(serializers.Serializer):
    """Serializer for path-based move/copy operations"""
    source_path = serializers.CharField(max_length=1000, help_text="Source path to file or folder")
    destination_path = serializers.CharField(max_length=1000, help_text="Destination path for file or folder")
    operation = serializers.ChoiceField(choices=['move', 'copy'])

    def validate_source_path(self, value):
        """Validate source path format"""
        if not value.startswith('/'):
            raise serializers.ValidationError("Source path must start with '/'")
        return value

    def validate_destination_path(self, value):
        """Validate destination path format"""
        if not value.startswith('/'):
            raise serializers.ValidationError("Destination path must start with '/'")
        return value

    def validate(self, attrs):
        """Additional validation for move/copy operations"""
        source_path = attrs['source_path']
        destination_path = attrs['destination_path']

        # Prevent moving/copying to itself
        if source_path == destination_path:
            raise serializers.ValidationError({
                'destination_path': 'Source and destination paths cannot be the same.'
            })

        return attrs