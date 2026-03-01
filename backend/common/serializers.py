# common/serializers.py
"""
Common serializers and serializer mixins
"""
from rest_framework import serializers
from typing import Set, Any, Dict


class DynamicFieldsSerializerMixin:
    """
    Serializer mixin that removes excluded fields from the response.

    This mixin should be used together with DynamicFieldsMixin on the ViewSet.

    Usage:
        class MySerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
            class Meta:
                fields = ['id', 'name', 'description']

    The ViewSet should pass 'exclude_fields' in the serializer context:
        context['exclude_fields'] = {'description'}
    """

    def to_representation(self, instance: Any) -> Dict[str, Any]:
        """
        Remove excluded fields from the serialized representation.

        Args:
            instance: The model instance being serialized

        Returns:
            Dictionary representation with excluded fields removed
        """
        # Get the base representation
        data = super().to_representation(instance)

        # Get exclude_fields from context
        exclude_fields = self.context.get('exclude_fields', set())

        # Remove excluded fields
        if exclude_fields:
            for field in exclude_fields:
                # Only remove if the field exists in data
                if field in data:
                    del data[field]

        return data