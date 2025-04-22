from django.conf import settings

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter


class CustomAutoSchema(AutoSchema):
    global_params = [
        OpenApiParameter(
            name="Accept-Language",
            type=str,
            location=OpenApiParameter.HEADER,
            description="`az` or `en` or `ru`. The default value is az",
        ),
    ]

    def get_override_parameters(self):
        params = super().get_override_parameters()
        return params + self.global_params
    
    def get_response_serializer(self, path, method):
        # Orijinal serializer'ı alıyoruz
        serializer = super().get_response_serializer(path, method)

        # Eğer serializer varsa ve bir alanı çıkarmak istiyorsanız
        if serializer and hasattr(serializer, 'fields'):
            # id alanını çıkarıyoruz
            serializer.fields.pop('id', None)

        return serializer