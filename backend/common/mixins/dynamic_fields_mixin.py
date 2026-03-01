# mixins/dynamic_fields_mixin.py
"""
Dynamic Fields Mixin for ViewSets and Serializers

Provides reusable functionality for excluding fields from API responses
via the 'exclude' query parameter.
"""
from rest_framework import serializers
from typing import Set, Any, Dict


class DynamicFieldsMixin:
    """
    ViewSet mixin that supports dynamic field exclusion via 'exclude' query parameter.

    This mixin should be used together with DynamicFieldsSerializerMixin on the serializer.

    Usage:
        class MyViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
            serializer_class = MySerializer

        class MySerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
            class Meta:
                fields = ['id', 'name', 'description']

    Then clients can request:
        GET /api/my-resources/?exclude=description
    """

    def get_exclude_fields(self) -> Set[str]:
        """
        Parse and validate the 'exclude' query parameter.

        Returns:
            Set of field names to exclude from the response

        Raises:
            ValidationError: When exclude parameter contains invalid field names
        """
        exclude_param = self.request.query_params.get('exclude', '')

        # Split and clean field names
        if not exclude_param or not exclude_param.strip():
            return set()

        exclude_fields = set(f.strip() for f in exclude_param.split(',') if f.strip())

        # Validate field names
        if exclude_fields:
            serializer_class = self.get_serializer_class()
            valid_fields = self._get_serializable_fields(serializer_class)
            invalid_fields = exclude_fields - valid_fields

            if invalid_fields:
                raise serializers.ValidationError({
                    'exclude': f'Invalid fields: {", ".join(sorted(invalid_fields))}'
                })

        return exclude_fields

    def _get_serializable_fields(self, serializer_class) -> Set[str]:
        """
        Get all valid field names from a serializer class.

        Args:
            serializer_class: The serializer class to inspect

        Returns:
            Set of valid field names
        """
        # Instantiate serializer with no data to get fields
        # Use empty context to avoid issues
        serializer = serializer_class(context={})

        # Get all field names including SerializerMethodField
        fields = set()
        for field_name, field_obj in serializer.fields.items():
            fields.add(field_name)

        return fields

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Add exclude_fields to serializer context.

        Returns:
            Serializer context dict with exclude_fields added
        """
        context = super().get_serializer_context()

        # Add exclude_fields and re-raise validation errors
        context['exclude_fields'] = self.get_exclude_fields()

        return context