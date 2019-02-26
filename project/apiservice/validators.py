from jsonschema import validate
from django.core.validators import BaseValidator


class JSONSchemaValidator(BaseValidator):
    def compare(self, a, b):
        return validate(a, b)
