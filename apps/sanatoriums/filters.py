import django_filters
from .models import Sanatorium, RoomType, RoomPrice, AgeGroup
from django.db.models import Q, Min, Max

class SanatoriumFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    location = django_filters.CharFilter(field_name='location__id')
    location_type = django_filters.CharFilter(field_name='location__location_type')
    facilities = django_filters.CharFilter(method='filter_facilities')
    room_types = django_filters.CharFilter(method='filter_room_types')
    occupancy = django_filters.NumberFilter(method='filter_occupancy')
    min_occupancy = django_filters.NumberFilter(method='filter_min_occupancy')
    max_occupancy = django_filters.NumberFilter(method='filter_max_occupancy')
    children_ages = django_filters.CharFilter(method='filter_children_ages')
    check_in = django_filters.DateFilter(method='filter_check_in')
    check_out = django_filters.DateFilter(method='filter_check_out')

    class Meta:
        model = Sanatorium
        fields = ['min_price', 'max_price', 'min_rating', 'location', 'location_type', 
                 'facilities', 'room_types', 'occupancy', 'min_occupancy', 'max_occupancy',
                 'children_ages', 'check_in', 'check_out']

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
        
    def filter_children_ages(self, queryset, name, value):
        """
        Filter sanatoriums that can accommodate children of specified ages.
        This filter doesn't actually filter the queryset, but makes the children_ages 
        parameter available for price calculations in the serializer.
        """
        # The actual filtering is done in the serializer
        return queryset

    def filter_check_in(self, queryset, name, value):
        return queryset
    
    def filter_check_out(self, queryset, name, value):
        return queryset

class RoomTypeFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    sanatorium = django_filters.CharFilter(field_name='sanatorium__id')
    occupancy = django_filters.NumberFilter(method='filter_occupancy')
    min_occupancy = django_filters.NumberFilter(method='filter_min_occupancy')
    max_occupancy = django_filters.NumberFilter(method='filter_max_occupancy')
    min_extra_beds = django_filters.NumberFilter(field_name='max_extra_beds', lookup_expr='gte')

    class Meta:
        model = RoomType
        fields = ['min_price', 'max_price', 'sanatorium', 'occupancy', 'min_occupancy', 'max_occupancy',
                 'min_extra_beds']
    
    def filter_occupancy(self, queryset, name, value):
        return queryset.filter(prices__occupancy=value).distinct()
        
    def filter_min_occupancy(self, queryset, name, value):
        return queryset.filter(prices__occupancy__gte=value).distinct()
        
    def filter_max_occupancy(self, queryset, name, value):
        return queryset.filter(prices__occupancy__lte=value).distinct()

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