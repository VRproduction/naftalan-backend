from django_filters import FilterSet
from .models import Blog
from django_filters import rest_framework as filters
from django.db.models import Q


class BlogFilter(FilterSet):
    search = filters.CharFilter(field_name='title', lookup_expr='icontains')
    tags = filters.CharFilter(method='filter_by_tags')
    class Meta:
        model = Blog
        fields = ['category', 'tags', 'is_popular', 'is_featured', 'search']

    def filter_by_tags(self, queryset, name, value):
        if value:
            tag_ids = value.split(',')
            query = Q()
            for tag_id in tag_ids:
                query |= Q(tags__id=tag_id)  # Use | to match any of the tags
            return queryset.filter(query).distinct()  # Add distinct() to remove duplicates
        return queryset