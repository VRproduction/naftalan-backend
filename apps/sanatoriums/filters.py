import django_filters
from .models import Sanatorium, RoomType

class SanatoriumFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    location = django_filters.CharFilter(field_name='location__name')
    location_type = django_filters.CharFilter(field_name='location__location_type')
    facilities = django_filters.CharFilter(method='filter_facilities')
    room_types = django_filters.CharFilter(method='filter_room_types')

    class Meta:
        model = Sanatorium
        fields = ['min_price', 'max_price', 'min_rating', 'location', 'location_type', 'facilities', 'room_types']

    def filter_facilities(self, queryset, name, value):
        facility_ids = value.split(',')
        return queryset.filter(facilities__id__in=facility_ids)

    def filter_room_types(self, queryset, name, value):
        room_type_ids = value.split(',')
        return queryset.filter(room_types__id__in=room_type_ids)

class RoomTypeFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    sanatorium = django_filters.CharFilter(field_name='sanatorium__id')

    class Meta:
        model = RoomType
        fields = ['min_price', 'max_price', 'sanatorium'] 