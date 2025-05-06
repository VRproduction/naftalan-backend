import django_filters
from .models import Sanatorium, RoomType, RoomPrice, AgeGroup
from django.db.models import Q, Min, Max

class SanatoriumFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='min_price_value', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='min_price_value', lookup_expr='lte')
    min_total_price = django_filters.NumberFilter(method='filter_min_total_price')
    max_total_price = django_filters.NumberFilter(method='filter_max_total_price')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    ratings = django_filters.CharFilter(method='filter_ratings')
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
        fields = ['min_price', 'max_price', 'min_total_price', 'max_total_price', 
                 'min_rating', 'ratings', 'location', 'location_type', 
                 'facilities', 'room_types', 'occupancy', 'min_occupancy', 'max_occupancy',
                 'children_ages', 'check_in', 'check_out']

    def filter_min_total_price(self, queryset, name, value):
        """
        Filter by minimum total price. 
        Since total_price is calculated in the serializer based on the stay duration,
        we need to estimate the filter by adjusting for the number of nights.
        """
        if not value:
            return queryset
            
        try:
            # Get check-in and check-out dates to calculate number of nights
            from datetime import datetime
            check_in_str = self.request.query_params.get('check_in')
            check_out_str = self.request.query_params.get('check_out')
            
            if check_in_str and check_out_str:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                nights = (check_out - check_in).days
                
                if nights > 0:
                    # Adjust the min_price filter based on number of nights
                    min_price_per_night = float(value) / nights
                    return queryset.filter(min_price_value__gte=min_price_per_night)
            
            # If no dates provided or calculation failed, use the value directly
            return queryset.filter(min_price_value__gte=float(value))
        except (ValueError, TypeError, ZeroDivisionError):
            return queryset
            
    def filter_max_total_price(self, queryset, name, value):
        """
        Filter by maximum total price.
        Since total_price is calculated in the serializer based on the stay duration,
        we need to estimate the filter by adjusting for the number of nights.
        """
        if not value:
            return queryset
            
        try:
            # Get check-in and check-out dates to calculate number of nights
            from datetime import datetime
            check_in_str = self.request.query_params.get('check_in')
            check_out_str = self.request.query_params.get('check_out')
            
            if check_in_str and check_out_str:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                nights = (check_out - check_in).days
                
                if nights > 0:
                    # Adjust the max_price filter based on number of nights
                    max_price_per_night = float(value) / nights
                    return queryset.filter(min_price_value__lte=max_price_per_night)
            
            # If no dates provided or calculation failed, use the value directly
            return queryset.filter(min_price_value__lte=float(value))
        except (ValueError, TypeError, ZeroDivisionError):
            return queryset
            
    def filter_ratings(self, queryset, name, value):
        """
        Filter sanatoriums by a list of ratings values.
        Expects a comma-separated list of rating values (e.g., "3,4,5").
        """
        if not value:
            return queryset
            
        try:
            ratings = [float(r.strip()) for r in value.split(',') if r.strip()]
            if ratings:
                return queryset.filter(rating__in=ratings)
        except (ValueError, TypeError):
            pass
            
        return queryset

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