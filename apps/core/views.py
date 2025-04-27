from django.shortcuts import render
from django.core.cache import cache
from django.db.models import Q
from rest_framework import generics, status, views, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample

from .models import SiteSettings, SEO, PageType, Currency, WorkingHours, DayOfWeek
from .serializers import (
    SiteSettingsSerializer, SEOSerializer, SEOByPageTypeSerializer, 
    CurrencySerializer, WorkingHoursSerializer
)

@extend_schema_view(
    list=extend_schema(
        description="Return a list of all currencies.",
        parameters=[
            OpenApiParameter(name="code", description="Filter by currency code", required=False, type=str),
            OpenApiParameter(name="search", description="Search by code or name", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by fields (prefix with '-' for descending): code, name", required=False, type=str)
        ]
    ),
    retrieve=extend_schema(
        description="Get details of a specific currency by its code."
    )
)
class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing currencies.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    lookup_field = 'code'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']

@extend_schema_view(
    list=extend_schema(
        description="Return a list of all working hours entries.",
        parameters=[
            OpenApiParameter(name="site_settings", description="Filter by site settings ID", required=False, type=int),
            OpenApiParameter(name="day", description="Filter by day of week", required=False, type=str),
            OpenApiParameter(name="is_working_day", description="Filter by working day status (true/false)", required=False, type=bool),
            OpenApiParameter(name="search", description="Search in notes", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by fields (prefix with '-' for descending): order, day", required=False, type=str)
        ]
    ),
    retrieve=extend_schema(
        description="Get details of a specific working hours entry."
    ),
    create=extend_schema(
        description="Create a new working hours entry."
    ),
    update=extend_schema(
        description="Update a working hours entry completely."
    ),
    partial_update=extend_schema(
        description="Update parts of a working hours entry."
    ),
    destroy=extend_schema(
        description="Delete a working hours entry."
    )
)
class WorkingHoursViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing working hours.
    """
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['site_settings', 'day', 'is_working_day']
    search_fields = ['note']
    ordering_fields = ['order', 'day']
    ordering = ['order', 'day']
    
    @extend_schema(
        description="Get a list of available days of the week",
        responses={200: OpenApiExample(
            'Example response',
            value=[
                {'value': 'monday', 'display': 'Bazar ertəsi'},
                {'value': 'tuesday', 'display': 'Çərşənbə axşamı'},
                # other days omitted for brevity
            ]
        )}
    )
    @action(detail=False, methods=['get'])
    def days(self, request):
        """Return the list of days of the week"""
        return Response([
            {'value': day[0], 'display': day[1]}
            for day in DayOfWeek.choices
        ])

class SiteSettingsRetrieveView(generics.RetrieveAPIView):
    """
    Generic view for retrieving site settings.
    Always returns the first/only settings object.
    """
    serializer_class = SiteSettingsSerializer
    
    def get_object(self):
        # Try to get from cache first
        settings = cache.get('site_settings')
        
        if not settings:
            try:
                settings = SiteSettings.objects.first()
                # Cache for 1 hour (3600 seconds)
                if settings:
                    cache.set('site_settings', settings, 3600)
            except SiteSettings.DoesNotExist:
                return None
                
        return settings
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"error": "Site settings not configured"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@extend_schema_view(
    get=extend_schema(
        description="List SEO entries with optional filtering.",
        parameters=[
            OpenApiParameter(name="page_type", description="Filter by page type (e.g. home, about, contact, custom)", required=False, type=str),
            OpenApiParameter(name="no_index", description="Filter by no_index status (true/false)", required=False, type=bool),
            OpenApiParameter(name="no_follow", description="Filter by no_follow status (true/false)", required=False, type=bool),
            OpenApiParameter(name="search", description="Search in meta_title, meta_description, meta_keywords, page_slug, og_title", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by fields (prefix with '-' for descending): id, page_type, created_at, updated_at", required=False, type=str)
        ]
    ),
    post=extend_schema(
        description="Create a new SEO entry."
    )
)
class SEOListCreateView(generics.ListCreateAPIView):
    """
    Generic view for listing and creating SEO entries.
    """
    queryset = SEO.objects.all()
    serializer_class = SEOSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['page_type', 'no_index', 'no_follow']
    search_fields = ['meta_title', 'meta_description', 'meta_keywords', 'page_slug', 'og_title']
    ordering_fields = ['id', 'page_type', 'created_at', 'updated_at']
    ordering = ['-updated_at']

@extend_schema_view(
    get=extend_schema(
        description="Get a specific SEO entry by ID."
    ),
    put=extend_schema(
        description="Update a specific SEO entry completely."
    ),
    patch=extend_schema(
        description="Update parts of a specific SEO entry."
    ),
    delete=extend_schema(
        description="Delete a specific SEO entry."
    )
)
class SEORetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic view for retrieving, updating and deleting SEO entries.
    """
    queryset = SEO.objects.all()
    serializer_class = SEOSerializer

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="page_type",
            description="The type of page to get SEO data for (e.g. home, about, contact, custom)",
            required=True,
            type=str,
            examples=[
                OpenApiExample(
                    'Home page',
                    value="home",
                ),
                OpenApiExample(
                    'About page',
                    value="about",
                ),
                OpenApiExample(
                    'Custom page',
                    value="custom",
                ),
            ]
        ),
        OpenApiParameter(
            name="page_slug",
            description="The slug of the custom page (required when page_type is 'custom')",
            required=False,
            type=str
        ),
    ],
    description="Get SEO data for a specific page type and slug."
)
class SEOByPageView(generics.GenericAPIView):
    """
    Generic API view to get SEO data for a specific page.
    """
    serializer_class = SEOSerializer
    
    def get(self, request, *args, **kwargs):
        # Get page type from query params
        validator = SEOByPageTypeSerializer(data=request.query_params)
        
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        
        page_type = validator.validated_data.get('page_type')
        page_slug = validator.validated_data.get('page_slug', None)
        
        # Validate page_type against choices
        valid_page_types = [choice[0] for choice in PageType.choices]
        if page_type not in valid_page_types:
            return Response(
                {"error": f"Invalid page_type. Valid options are: {', '.join(valid_page_types)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Query based on page type and slug
        query = Q(page_type=page_type)
        if page_type == PageType.CUSTOM:
            if not page_slug:
                return Response(
                    {"error": "page_slug is required for custom pages"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            query &= Q(page_slug=page_slug)
        
        try:
            seo = SEO.objects.get(query)
        except SEO.DoesNotExist:
            # If no specific SEO is found, try to get default site settings for basic meta data
            settings = SiteSettings.objects.first()
            if settings and settings.default_meta_title and settings.default_meta_description:
                return Response({
                    "meta_title": settings.default_meta_title,
                    "meta_description": settings.default_meta_description,
                    "meta_keywords": settings.default_meta_keywords if hasattr(settings, "default_meta_keywords") else None,
                    "no_index": False,
                    "no_follow": False
                })
            else:
                return Response(
                    {"error": f"SEO data not found for page_type: {page_type}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        serializer = self.get_serializer(seo)
        return Response(serializer.data)
