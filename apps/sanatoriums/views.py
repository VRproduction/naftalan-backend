from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Subquery, OuterRef
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import (
    Location, Sanatorium, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage,
    Season, RoomType, RoomPrice, AgeGroup, ExtraBedPrice, TreatmentOption
    )
from .serializers import (
    LocationSerializer, SanatoriumSerializer, SanatoriumListSerializer, 
    NaftalanSanatoriumsPageSerializer, OtherCitiesSanatoriumsPageSerializer,
    CurrencySerializer, SeasonSerializer, RoomTypeSerializer, RoomPriceSerializer,
    AgeGroupSerializer, ExtraBedPriceSerializer, TreatmentOptionSerializer
)
from utils.api.pagination.page_number_pagination import CustomPageNumberPagination
from apps.core.models import Currency
from .filters import SanatoriumFilter, RoomTypeFilter, RoomPriceFilter


# Create your views here.

class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [SearchFilter]
    search_fields = ['region', 'country']


class CurrencyListView(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class SeasonListView(generics.ListAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date']


class AgeGroupListView(generics.ListAPIView):
    queryset = AgeGroup.objects.all()
    serializer_class = AgeGroupSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['min_age', 'max_age']


class TreatmentOptionListView(generics.ListAPIView):
    queryset = TreatmentOption.objects.all()
    serializer_class = TreatmentOptionSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']


class RoomTypeListView(generics.ListAPIView):
    serializer_class = RoomTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RoomTypeFilter
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        sanatorium_slug = self.request.query_params.get('sanatorium_slug', None)
        if sanatorium_slug:
            return RoomType.objects.filter(sanatorium__slug=sanatorium_slug)
        return RoomType.objects.all()


class RoomTypeDetailView(generics.RetrieveAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer


class RoomPriceListView(generics.ListAPIView):
    serializer_class = RoomPriceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomPriceFilter
    
    def get_queryset(self):
        return RoomPrice.objects.all()


class SanatoriumListView(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True)
    serializer_class = SanatoriumListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SanatoriumFilter
    search_fields = ['name', 'location__region', 'location__country']
    ordering_fields = ['name', 'rating', 'created_at', 'total_price']
    pagination_class = CustomPageNumberPagination
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='occupancy', description='Number of occupants', required=False, type=int),
            OpenApiParameter(name='children_ages', description='Ages of children, comma separated (e.g., 5,7,11)', required=False, type=str),
            OpenApiParameter(name='min_price', description='Minimum price filter', required=False, type=float),
            OpenApiParameter(name='max_price', description='Maximum price filter', required=False, type=float),
            OpenApiParameter(name='has_treatment', description='Filter by treatment availability', required=False, type=bool),
            OpenApiParameter(name='location_type', description='Filter by location type (e.g., naftalan, other)', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order by field (e.g., name, -rating, total_price, -total_price)', required=False, type=str),
        ],
        responses={200: SanatoriumListSerializer}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            
            # Check if we need to order by total_price
            ordering = self.request.query_params.get('ordering', None)
            
            # Store original ordering to handle after all other filters
            is_total_price_ordering = False
            total_price_ordering_desc = False
            
            if ordering:
                if ordering == 'total_price':
                    is_total_price_ordering = True
                    total_price_ordering_desc = False
                elif ordering == '-total_price':
                    is_total_price_ordering = True
                    total_price_ordering_desc = True
            
            # Process all other filters first
            location_type = self.request.query_params.get('location_type', None)
            if location_type:
                queryset = queryset.filter(location_type=location_type)
                
            # Get query parameters
            occupancy = self.request.query_params.get('occupancy', None)
            
            import logging
            logger = logging.getLogger(__name__)
            
            # Log for debugging
            logger.info(f"Query params - occupancy: {occupancy}")
            logger.info(f"Initial queryset count: {queryset.count()}")
            
            # Get children_ages if specified
            children_ages_param = self.request.query_params.get('children_ages', None)
            children_ages = []
            if children_ages_param:
                try:
                    children_ages = [int(age) for age in children_ages_param.split(',') if age.strip()]
                    logger.info(f"Children ages: {children_ages}")
                except (ValueError, TypeError) as e:
                    logger.error(f"Error in children_ages conversion: {str(e)}")
            
            # Handle occupancy and children filter together
            if occupancy or children_ages:
                # Start with all sanatoriums
                valid_sanatorium_ids = set()
                
                # Go through each sanatorium and check if it meets criteria
                for sanatorium in queryset:
                    for room_type in sanatorium.room_types.all():
                        # Check if room can accommodate the extra beds needed
                        # If max_extra_beds is None, it means unlimited capacity
                        max_extra_beds = room_type.max_extra_beds
                        
                        logger.debug(f"Checking room {room_type.id} in sanatorium {sanatorium.id} - max_extra_beds: {max_extra_beds}, children: {len(children_ages) if children_ages else 0}")
                        
                        # If children and max_extra_beds is not None, check capacity
                        if children_ages and max_extra_beds is not None and len(children_ages) > max_extra_beds:
                            logger.debug(f"Room {room_type.id} skipped - not enough extra beds (max: {max_extra_beds}, needed: {len(children_ages)})")
                            continue
                        
                        # Check if room has prices for specified occupancy
                        if occupancy:
                            try:
                                occupancy_int = int(occupancy)
                                room_has_occupancy = room_type.prices.filter(occupancy=occupancy_int).exists()
                                if not room_has_occupancy:
                                    continue
                            except (ValueError, TypeError):
                                continue
                        
                        # Check if room has extra bed prices for the specified children ages
                        if children_ages:
                            # First, check if the room has any extra bed prices configured at all
                            has_extra_bed_prices = room_type.extra_bed_prices.exists()
                            
                            if not has_extra_bed_prices:
                                logger.info(f"Room {room_type.id} skipped - no extra bed prices configured at all")
                                continue
                                
                            # Get all age groups available for this room
                            available_age_groups = set()
                            for extra_bed_price in room_type.extra_bed_prices.all():
                                if extra_bed_price.age_group:
                                    available_age_groups.add(extra_bed_price.age_group)
                                    
                            # If there are no age groups available, skip this room regardless of max_extra_beds
                            if not available_age_groups:
                                logger.info(f"Room {room_type.id} skipped - no age groups available in extra bed prices")
                                continue
                                
                            # If max_extra_beds is None, it means unlimited capacity, we still need age groups but don't check limits
                            
                            # Check if each child age fits into at least one age group
                            # We do this check for all cases now, regardless of max_extra_beds value
                            # All children must have a matching age group in the available age groups
                            all_ages_fit = True
                            for age in children_ages:
                                age_fits = False
                                for age_group in available_age_groups:
                                    if age_group.min_age <= age <= age_group.max_age:
                                        age_fits = True
                                        break
                                
                                if not age_fits:
                                    logger.info(f"Child age {age} doesn't fit any age group for room {room_type.id}")
                                    all_ages_fit = False
                                    break
                            
                            if not all_ages_fit:
                                logger.info(f"Room {room_type.id} skipped - not all children ages fit available age groups")
                                continue
                        
                        # If we get here, the room meets all criteria
                        valid_sanatorium_ids.add(sanatorium.id)
                        break  # Don't need to check other rooms in this sanatorium
                
                # Filter queryset by valid IDs
                if valid_sanatorium_ids:
                    queryset = queryset.filter(id__in=valid_sanatorium_ids)
                else:
                    queryset = queryset.none()  # Return empty queryset if no valid sanatoriums
                
                logger.info(f"After occupancy and children filter - count: {queryset.count()}")
                logger.info(f"Valid sanatorium IDs: {valid_sanatorium_ids}")
                
                # Alternatively, use a simpler approach with just occupancy filter if no children
                # This is the original approach and works fine without children
                if occupancy and not children_ages:
                    try:
                        occupancy_int = int(occupancy)
                        filtered_queryset = queryset.filter(room_types__prices__occupancy=occupancy_int).distinct()
                        if filtered_queryset.exists():
                            queryset = filtered_queryset
                            logger.info(f"Using simple occupancy filter - count: {queryset.count()}")
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error in occupancy conversion: {str(e)}")
                        pass
                    
            # Filter by min_price and max_price if specified
            min_price = self.request.query_params.get('min_price', None)
            max_price = self.request.query_params.get('max_price', None)
            
            if min_price:
                try:
                    min_price = float(min_price)
                    queryset = queryset.filter(room_types__prices__price__gte=min_price).distinct()
                except (ValueError, TypeError):
                    pass
                    
            if max_price:
                try:
                    max_price = float(max_price)
                    queryset = queryset.filter(room_types__prices__price__lte=max_price).distinct()
                except (ValueError, TypeError):
                    pass
            
            logger.info(f"Final queryset count: {queryset.count()}")
            
            # Handle total_price ordering after all filters
            if is_total_price_ordering and queryset.exists():
                from datetime import datetime
                
                # Get check-in and check-out dates for total price calculation
                check_in_str = self.request.query_params.get('check_in')
                check_out_str = self.request.query_params.get('check_out')
                
                if check_in_str and check_out_str:
                    try:
                        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                        
                        # Calculate number of nights
                        nights = (check_out - check_in).days
                        
                        if nights > 0:
                            # Calculate total price for each sanatorium and sort
                            sanatorium_total_prices = []
                            
                            for sanatorium in queryset:
                                # Instantiate the serializer to calculate min_price
                                serializer = self.get_serializer(sanatorium)
                                min_price = serializer.get_min_price(sanatorium)
                                
                                if min_price is not None:
                                    total_price = min_price * nights
                                    sanatorium_total_prices.append((sanatorium.id, total_price))
                            
                            # Sort by total price
                            sanatorium_total_prices.sort(key=lambda x: x[1], reverse=total_price_ordering_desc)
                            
                            # Extract sorted IDs
                            sorted_ids = [id for id, _ in sanatorium_total_prices]
                            
                            # Create preserved order
                            from django.db.models import Case, When, Value, IntegerField
                            
                            if sorted_ids:
                                preserved_order = Case(
                                    *[When(id=pk, then=Value(pos)) for pos, pk in enumerate(sorted_ids)],
                                    output_field=IntegerField()
                                )
                                queryset = queryset.filter(id__in=sorted_ids).order_by(preserved_order)
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error in total_price ordering: {str(e)}")
            
            return queryset
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in SanatoriumListView.get_queryset: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Sanatorium.objects.none()
    

class SanatoriumDetailView(generics.RetrieveAPIView):
    queryset = Sanatorium.objects.filter(is_active=True)
    serializer_class = SanatoriumSerializer
    lookup_field = 'slug'
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='occupancy', description='Number of occupants', required=False, type=int),
            OpenApiParameter(name='children_ages', description='Ages of children, comma separated (e.g., 5,7,11)', required=False, type=str),
            OpenApiParameter(name='min_price', description='Minimum price filter', required=False, type=float),
            OpenApiParameter(name='max_price', description='Maximum price filter', required=False, type=float),
            OpenApiParameter(name='has_treatment', description='Filter by treatment availability', required=False, type=bool),
            OpenApiParameter(name='location_type', description='Filter by location type (e.g., naftalan, other)', required=False, type=str),
        ],
        responses={200: SanatoriumSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class NaftalanSanatoriumsPageView(generics.RetrieveAPIView):
    serializer_class = NaftalanSanatoriumsPageSerializer

    def get_object(self):
        return NaftalanSanatoriumsPage.objects.first()

class OtherCitiesSanatoriumsPageView(generics.RetrieveAPIView):
    serializer_class = OtherCitiesSanatoriumsPageSerializer

    def get_object(self):
        return OtherCitiesSanatoriumsPage.objects.first()


class NaftalanSanatoriums(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True, location_type='naftalan')
    serializer_class = SanatoriumListSerializer


class OtherCitiesSanatoriums(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True, location_type='other_cities')
    serializer_class = SanatoriumListSerializer