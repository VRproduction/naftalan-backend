from django.core.files.base import ContentFile
from rest_framework import serializers
import base64
import uuid


class Base64FileField(serializers.FileField):
    """
    Görseller veya diğer dosyalar için Base64 formatını destekleyen bir özel alan.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            # Base64 kodunu ve dosya türünü ayıkla
            format, filestr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(filestr), name=f'{uuid.uuid4()}.{ext}')
        return super().to_internal_value(data)
