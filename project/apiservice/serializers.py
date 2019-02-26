from .models import Check
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class CheckSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Check
        fields = ('id', 'type', 'order', 'printer_id', 'order_id', 'status', 'pdf_file')
        extra_kwargs = {
            'type': {'write_only': True},
            'order': {'write_only': True},
            'printer_id': {'write_only': True},
            'status': {'write_only': True},
            'order_id': {'write_only': True},
        }



