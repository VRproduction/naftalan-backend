from django.conf import settings

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter, extend_schema_field, extend_schema
from drf_spectacular.extensions import OpenApiFilterExtension


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
    
    def get_filter_parameters(self):
        """Properly document filter, search and ordering parameters."""
        parameters = super().get_filter_parameters()
        
        view = self.view
        
        # Get filterset fields
        if hasattr(view, 'filterset_fields') and view.filterset_fields:
            for field_name in view.filterset_fields:
                if isinstance(field_name, str):
                    parameters.append(
                        OpenApiParameter(
                            name=field_name,
                            description=f"Filter by {field_name}",
                            required=False,
                            type=str,
                        )
                    )
        
        # Document search fields
        if hasattr(view, 'search_fields') and view.search_fields and 'rest_framework.filters.SearchFilter' in [f.__name__ for f in view.filter_backends]:
            parameters.append(
                OpenApiParameter(
                    name='search',
                    description=f"Search in fields: {', '.join(view.search_fields)}",
                    required=False,
                    type=str,
                )
            )
        
        # Document ordering fields
        if hasattr(view, 'ordering_fields') and view.ordering_fields and 'rest_framework.filters.OrderingFilter' in [f.__name__ for f in view.filter_backends]:
            parameters.append(
                OpenApiParameter(
                    name='ordering',
                    description=f"Order by fields (prefix with '-' for descending): {', '.join(view.ordering_fields)}",
                    required=False,
                    type=str,
                )
            )
        
        return parameters
    
    def get_response_serializer(self, path, method):
        # Orijinal serializer'ı alıyoruz
        serializer = super().get_response_serializer(path, method)

        # Eğer serializer varsa ve bir alanı çıkarmak istiyorsanız
        if serializer and hasattr(serializer, 'fields'):
            # id alanını çıkarıyoruz
            serializer.fields.pop('id', None)

        return serializer