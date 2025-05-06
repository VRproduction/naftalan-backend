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

import logging
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
    serializer_class = SanatoriumListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SanatoriumFilter
    search_fields = ['name', 'location__region', 'location__country']
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """
        Tüm sanatoriumları getir ve ön işlem yap
        """
        try:
            # Queryset'i oluştur
            queryset = Sanatorium.objects.filter(is_active=True)
            
            # Diğer filtreleme işlemleri...
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
                        logger.debug(f"Checking room {room_type.id} in sanatorium {sanatorium.id}")
                        
                        # Check if room can accommodate the extra beds needed based on max_extra_beds
                        max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                        
                        # Öncelikle basic capacity kontrolü yap
                        if children_ages and max_extra_beds < len(children_ages):
                            logger.debug(f"Room {room_type.id} skipped - max_extra_beds {max_extra_beds} < children {len(children_ages)}")
                            continue
                        
                        # Occupancy kontrolü
                        if occupancy:
                            try:
                                occupancy_int = int(occupancy)
                                # Occupancy değeri fiyatlar içinde var mı kontrol et
                                if not room_type.prices.filter(occupancy=occupancy_int).exists():
                                    logger.debug(f"Room {room_type.id} skipped - no price for occupancy {occupancy_int}")
                                    continue
                            except (ValueError, TypeError):
                                continue
                        
                        # Çocuklar için extra bed gerekiyorsa
                        if children_ages:
                            # Extra bed fiyatları var mı kontrol et
                            has_extra_bed_prices = room_type.extra_bed_prices.exists()
                            
                            # Eğer oda için max_extra_beds tanımlanmışsa ve > 0 ise, 
                            # ama extra_bed_prices tanımlanmamışsa, bu durumda yaş kontrolü yapmadan odayı kabul et
                            if max_extra_beds > 0 and not has_extra_bed_prices:
                                logger.info(f"Room {room_type.id} accepted - has max_extra_beds={max_extra_beds} but no extra bed prices configured")
                                valid_sanatorium_ids.add(sanatorium.id)
                                break
                            
                            # Eğer extra_bed_prices varsa, yaş kontrolü yap
                            if has_extra_bed_prices:
                                # Get all age groups available for this room
                                available_age_groups = set()
                                for extra_bed_price in room_type.extra_bed_prices.all():
                                    if extra_bed_price.age_group:
                                        available_age_groups.add(extra_bed_price.age_group)
                                
                                # Eğer hiç yaş grubu tanımlanmamışsa ama max_extra_beds > 0 ise, odayı kabul et
                                if not available_age_groups and max_extra_beds > 0:
                                    logger.info(f"Room {room_type.id} accepted - has extra_bed_prices but no age groups defined")
                                    valid_sanatorium_ids.add(sanatorium.id)
                                    break
                                
                                # Eğer yaş grupları tanımlanmışsa, çocuk yaşlarının en az birinin bu gruplara uyduğunu kontrol et
                                # Tüm çocukların uyduğu zorunluluğunu kaldırıyoruz, en az 1 çocuk uygunsa kabul edeceğiz
                                if available_age_groups:
                                    matching_ages_count = 0
                                    for age in children_ages:
                                        for age_group in available_age_groups:
                                            if age_group.min_age <= age <= age_group.max_age:
                                                matching_ages_count += 1
                                                break
                                    
                                    # En az 1 çocuk yaş grubuna uyuyorsa, odayı kabul et
                                    if matching_ages_count > 0:
                                        logger.info(f"Room {room_type.id} accepted - {matching_ages_count} of {len(children_ages)} children fit age groups")
                                        valid_sanatorium_ids.add(sanatorium.id)
                                        break
                                    else:
                                        logger.info(f"Room {room_type.id} skipped - no children fit available age groups")
                                        continue
                        
                        # Buraya kadar geldiyse, tüm kriterler OK
                        valid_sanatorium_ids.add(sanatorium.id)
                        break  # Sonraki odaları kontrol etmeye gerek yok
                
                # Filter queryset by valid IDs
                if valid_sanatorium_ids:
                    queryset = queryset.filter(id__in=valid_sanatorium_ids)
                else:
                    queryset = queryset.none()  # Return empty queryset if no valid sanatoriums
                
                logger.info(f"After occupancy and children filter - count: {queryset.count()}")
                logger.info(f"Valid sanatorium IDs: {valid_sanatorium_ids}")
            
            # Filter by min_price and max_price if specified
            min_price = self.request.query_params.get('min_price', None)
            max_price = self.request.query_params.get('max_price', None)
            
            # Önce min_price'ı hesaplamak için alt sorgu oluştur
            from django.db.models import Min, OuterRef, Subquery
            
            # Fiyatlara göre sıralama - Oda fiyatlarından en düşük olanı bul
            room_prices = RoomPrice.objects.filter(
                room_type__sanatorium=OuterRef('id')
            ).order_by('price').values('price')[:1]
            
            # min_price_value'yu queryset'e ekle ve ona göre sırala
            queryset = queryset.annotate(
                min_price_value=Subquery(room_prices)
            )
            
            # min_price ve max_price filtreleri uygula
            if min_price:
                try:
                    min_price = float(min_price)
                    queryset = queryset.filter(min_price_value__gte=min_price).distinct()
                except (ValueError, TypeError):
                    pass
                    
            if max_price:
                try:
                    max_price = float(max_price)
                    queryset = queryset.filter(min_price_value__lte=max_price).distinct()
                except (ValueError, TypeError):
                    pass
            
            # min_price'a göre sırala
            queryset = queryset.order_by('min_price_value')
            
            logger = logging.getLogger(__name__)
            logger.info(f"Final queryset ordered by min_price: {[s.id for s in queryset[:10]]}")
            
            return queryset
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in SanatoriumListView.get_queryset: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Sanatorium.objects.none()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='occupancy', description='Number of occupants', required=False, type=int),
            OpenApiParameter(name='children_ages', description='Ages of children, comma separated (e.g., 5,7,11)', required=False, type=str),
            OpenApiParameter(name='min_price', description='Minimum price per night filter', required=False, type=float),
            OpenApiParameter(name='max_price', description='Maximum price per night filter', required=False, type=float),
            OpenApiParameter(name='min_total_price', description='Minimum total price for entire stay', required=False, type=float),
            OpenApiParameter(name='max_total_price', description='Maximum total price for entire stay', required=False, type=float),
            OpenApiParameter(name='min_rating', description='Minimum rating filter', required=False, type=float),
            OpenApiParameter(name='ratings', description='Filter by specific ratings, comma separated (e.g., 3,4,5)', required=False, type=str),
            OpenApiParameter(name='has_treatment', description='Filter by treatment availability', required=False, type=bool),
            OpenApiParameter(name='location_type', description='Filter by location type (e.g., naftalan, other)', required=False, type=str),
            OpenApiParameter(name='check_in', description='Check-in date (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='check_out', description='Check-out date (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='ordering', description='Sıralama alanı. Desteklenen değerler: total_price, total_discount_price. Azalan sıra için - ekleyin.', required=False, type=str),
        ],
        responses={200: SanatoriumListSerializer}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Fiyata göre manuel sıralama
        ordering = request.query_params.get('ordering', 'total_discount_price')  # Varsayılan olarak total_discount_price
        
        # Sonuçları manuel olarak sırala
        if 'results' in response.data and response.data['results']:
            reverse_sort = ordering.startswith('-')
            sort_field = ordering[1:] if reverse_sort else ordering
            
            # Hangi alana göre sıralama yapacağız?
            if sort_field in ['total_price', 'total_discount_price']:
                logger = logging.getLogger(__name__)
                logger.info(f"Sorting by {ordering}")
                
                # Key fonksiyonu tanımla
                def get_sort_key(item):
                    if sort_field == 'total_discount_price':
                        value = item.get('total_discount_price')
                        if value is None:
                            value = item.get('total_price')  # Total discount price yoksa total price kullan
                    else:
                        value = item.get(sort_field)
                        
                    # None değerler için sonsuz değer döndür (sıralamada en sona kalsın)
                    if value is None:
                        return float('inf')
                    
                    # Sayıya dönüştürmeyi dene
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return float('inf')
                
                # Herhangi bir sorunu görmek için sıralama öncesi değerleri yazdır
                try:
                    logger.info(f"Before sorting - IDs: {[item.get('id') for item in response.data['results']]}")
                    logger.info(f"Before sorting - Values: {[(item.get('id'), get_sort_key(item)) for item in response.data['results'][:5]]}")
                except Exception as e:
                    logger.error(f"Error logging before sorting: {str(e)}")
                
                # Sıralama yap
                try:
                    sorted_results = sorted(
                        response.data['results'],
                        key=get_sort_key,
                        reverse=reverse_sort
                    )
                    
                    # Sıralama sonrası değerleri yazdır
                    logger.info(f"After sorting - IDs: {[item.get('id') for item in sorted_results]}")
                    logger.info(f"After sorting - Values: {[(item.get('id'), get_sort_key(item)) for item in sorted_results[:5]]}")
                    
                    # Sıralanmış sonuçları response'a yerleştir
                    response.data['results'] = sorted_results
                except Exception as e:
                    logger.error(f"Error during sorting: {str(e)}")
            else:
                logger.info(f"No custom sorting applied. Using ordering: {ordering}")
        
        return response


class SanatoriumDetailView(generics.RetrieveAPIView):
    queryset = Sanatorium.objects.filter(is_active=True)
    serializer_class = SanatoriumSerializer
    lookup_field = 'slug'
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='occupancy', description='Number of occupants', required=False, type=int),
            OpenApiParameter(name='children_ages', description='Ages of children, comma separated (e.g., 5,7,11)', required=False, type=str),
            OpenApiParameter(name='min_price', description='Minimum price per night filter', required=False, type=float),
            OpenApiParameter(name='max_price', description='Maximum price per night filter', required=False, type=float),
            OpenApiParameter(name='min_total_price', description='Minimum total price for entire stay', required=False, type=float),
            OpenApiParameter(name='max_total_price', description='Maximum total price for entire stay', required=False, type=float),
            OpenApiParameter(name='min_rating', description='Minimum rating filter', required=False, type=float),
            OpenApiParameter(name='ratings', description='Filter by specific ratings, comma separated (e.g., 3,4,5)', required=False, type=str),
            OpenApiParameter(name='check_in', description='Check-in date (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='check_out', description='Check-out date (YYYY-MM-DD)', required=False, type=str),
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