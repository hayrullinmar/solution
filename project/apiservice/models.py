import os
from django.db import models
from django.contrib.postgres.fields import JSONField

from .validators import JSONSchemaValidator


ORDER_JSON_FIELD_SCHEMA = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "required": [
        "id",
        "price",
        "items",
        "address",
        "client",
        "point_id"
    ],
    "properties": {
        "id": {
            "$id": "#/properties/id",
            "type": "integer"
        },
        "price": {
            "$id": "#/properties/price",
            "type": "integer"
        },
        "items": {
            "$id": "#/properties/items",
            "type": "array",
            "items": {
                "$id": "#/properties/items/items",
                "type": "object",
                "required": [
                    "name",
                    "quantity",
                    "unit_price"
                ],
                "properties": {
                    "name": {
                        "$id": "#/properties/items/items/properties/name",
                        "type": "string",
                        "pattern": "^(.*)$"
                    },
                    "quantity": {
                        "$id": "#/properties/items/items/properties/quantity",
                        "type": "integer"
                    },
                    "unit_price": {
                        "$id": "#/properties/items/items/properties/unit_price",
                        "type": "integer"
                    }
                }
            }
        },
        "address": {
            "$id": "#/properties/address",
            "type": "string",
            "pattern": "^(.*)$"
        },
        "client": {
            "$id": "#/properties/client",
            "type": "object",
            "required": [
                "name",
                "phone"
            ],
            "properties": {
                "name": {
                    "$id": "#/properties/client/properties/name",
                    "type": "string",
                    "pattern": "^(.*)$"
                },
                "phone": {
                    "$id": "#/properties/client/properties/phone",
                    "type": "integer"
                }
            }
        },
        "point_id": {
            "$id": "#/properties/point_id",
            "type": "integer"
        }
    }
}

CHECK_TYPE_CHOICES = (
    ('kitchen', 'Кухня'),
    ('client', 'Клиент')
)


class Printer(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    api_key = models.CharField(max_length=256, unique=True)

    check_type = models.CharField(choices=CHECK_TYPE_CHOICES,
                                  default='kitchen',
                                  verbose_name='Тип чека',
                                  max_length=128)
    point_id = models.IntegerField()

    def __str__(self):
        return self.name


class Check(models.Model):
    type = models.CharField(choices=CHECK_TYPE_CHOICES,
                            verbose_name='Тип чека',
                            max_length=128)
    order = JSONField(default=dict, validators=[JSONSchemaValidator(limit_value=ORDER_JSON_FIELD_SCHEMA)])

    printer_id = models.ForeignKey(Printer,
                                   verbose_name="Принтер",
                                   on_delete=models.PROTECT)

    order_id = models.PositiveIntegerField(unique=True)

    STATUS_TYPE_CHOICES = (
        ('new', 'Новый'),
        ('rendered', 'Конвертирован'),
        ('printed', 'Распечатан')
    )

    status = models.CharField(choices=STATUS_TYPE_CHOICES,
                              default='new',
                              verbose_name='Статус чека',
                              max_length=128)

    pdf_file = models.FileField(default=None, upload_to='pdf')

    def __str__(self):
        return str("Check {} for order № {}".format(self.id, self.order_id))

    def filename(self):
        return os.path.basename(self.pdf_file.name)
