import django_filters
from .models import Sanatorium, RoomType, RoomPrice

class SanatoriumFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    location = django_filters.CharFilter(field_name='location__name')
    location_type = django_filters.CharFilter(field_name='location__location_type')
    facilities = django_filters.CharFilter(method='filter_facilities')
    room_types = django_filters.CharFilter(method='filter_room_types')
    occupancy = django_filters.NumberFilter(method='filter_occupancy')
    min_occupancy = django_filters.NumberFilter(method='filter_min_occupancy')
    max_occupancy = django_filters.NumberFilter(method='filter_max_occupancy')

    class Meta:
        model = Sanatorium
        fields = ['min_price', 'max_price', 'min_rating', 'location', 'location_type', 
                 'facilities', 'room_types', 'occupancy', 'min_occupancy', 'max_occupancy']

    def filter_facilities(self, queryset, name, value):
        facility_ids = value.split(',')
        return queryset.filter(facilities__id__in=facility_ids)

    def filter_room_types(self, queryset, name, value):
        room_type_ids = value.split(',')
        return queryset.filter(room_types__id__in=room_type_ids)
        
    def filter_occupancy(self, queryset, name, value):
        return queryset.filter(room_types__prices__occupancy=value).distinct()
        
    def filter_min_occupancy(self, queryset, name, value):
        return queryset.filter(room_types__prices__occupancy__gte=value).distinct()
        
    def filter_max_occupancy(self, queryset, name, value):
        return queryset.filter(room_types__prices__occupancy__lte=value).distinct()

class RoomTypeFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    sanatorium = django_filters.CharFilter(field_name='sanatorium__id')

    class Meta:
        model = RoomType
        fields = ['min_price', 'max_price', 'sanatorium'] 

class RoomPriceFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    occupancy = django_filters.NumberFilter(field_name='occupancy', lookup_expr='exact')
    min_occupancy = django_filters.NumberFilter(field_name='occupancy', lookup_expr='gte')
    max_occupancy = django_filters.NumberFilter(field_name='occupancy', lookup_expr='lte')
    with_treatment = django_filters.BooleanFilter(field_name='with_treatment')
    room_type = django_filters.CharFilter(field_name='room_type__id')
    sanatorium = django_filters.CharFilter(field_name='room_type__sanatorium__id')

    class Meta:
        model = RoomPrice
        fields = ['min_price', 'max_price', 'occupancy', 'min_occupancy', 'max_occupancy', 
                 'with_treatment', 'room_type', 'sanatorium'] 