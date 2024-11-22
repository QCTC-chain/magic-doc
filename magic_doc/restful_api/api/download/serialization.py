'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-11-21 20:53:27
LastEditors: shaxunyeman shaxunyeman@gmail.com
LastEditTime: 2024-11-22 18:36:51
FilePath: /magic-doc/magic_doc/restful_api/api/download/serialization.py
Description: 
'''
from marshmallow import Schema, fields, validates, ValidationError

class MagicPdfDownloadSchema(Schema):
    objectName = fields.Str(required=True)

    @validates('objectName')
    def validate_url(self, data, **kwargs):
        if not data:
            raise ValidationError('objectName cannot be empty')
        else:
            return data
