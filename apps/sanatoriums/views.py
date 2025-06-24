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
    LocationSerializer, SanatoriumSerializer, SanatoriumSearchSerializer,
    NaftalanSanatoriumsPageSerializer, OtherCitiesSanatoriumsPageSerializer,
    CurrencySerializer, SeasonSerializer, RoomTypeSerializer, RoomPriceSerializer,
    AgeGroupSerializer, ExtraBedPriceSerializer, TreatmentOptionSerializer, SanatoriumListSerializer,
    SanatoriumSerializer, SanatoriumRoomDetailSerializer
)
from utils.api.pagination.page_number_pagination import CustomPageNumberPagination
from apps.core.models import Currency
from .filters import SanatoriumFilter, RoomTypeFilter, RoomPriceFilter

import logging
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

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


# Ortak arama/filtre fonksiyonu
def filter_sanatorium_queryset(queryset, request, single_instance=None):
    """
    queryset: Sanatorium queryset (veya tek bir instance içeren queryset)
    request: DRF request
    single_instance: Eğer sadece bir sanatoryum kontrol edilecekse, instance olarak verilir
    """
    logger = logging.getLogger(__name__)
    def _get_int_query_param(key):
        value = request.query_params.get(key)
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    def _get_float_query_param(key):
        value = request.query_params.get(key)
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    def _get_int_list_query_param(key):
        value = request.query_params.get(key)
        if not value:
            return []
        try:
            return [int(age) for age in value.split(',') if age.strip()]
        except (ValueError, TypeError):
            return []

    occupancy = _get_int_query_param('occupancy')
    children_ages = _get_int_list_query_param('children_ages')
    min_price = _get_float_query_param('min_price')
    max_price = _get_float_query_param('max_price')

    logger.info(f"Query params - occupancy: {occupancy}, children_ages: {children_ages}")
    logger.info(f"Initial queryset count: {queryset.count()}")

    # Uygunluk kontrolü
    def is_valid_sanatorium(sanatorium):
        # Kural: Bir sanatoryum, tüm kriterlere uyan en az bir odaya sahipse geçerlidir.

        # Kriter 1 & 2: Doluluk & Çocuklar
        if occupancy or children_ages:
            room_is_available = False
            for room_type in sanatorium.room_types.all():
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else 0
                if children_ages and max_extra_beds < len(children_ages):
                    continue

                # YENİ: occupancy >= aranan occupancy ve oda max_capacity >= aranan occupancy olmalı
                if occupancy:
                    max_capacity = room_type.max_capacity if room_type.max_capacity is not None else None
                    if max_capacity is not None and occupancy > max_capacity:
                        continue
                    if not room_type.prices.filter(occupancy__gte=occupancy).exists():
                        continue

                # Çocuk yaş gereksinimlerini ekstra yatak fiyatlarına göre kontrol et
                if children_ages:
                    if not room_type.extra_bed_prices.exists():
                        # Bu odada ekstra yatak fiyatı tanımlanmamış. Kullanıcı geçerli sayılmasını istiyor.
                        pass
                    else:
                        # Ekstra yatak fiyatları var, bu yüzden eşleşen bir yaş grubu bulmalıyız.
                        available_age_groups = {
                            ebp.age_group for ebp in room_type.extra_bed_prices.all() if ebp.age_group
                        }
                        # Fiyatlar var ama belirli yaş grupları yoksa, bu herkes için geçerli demektir.
                        if available_age_groups:
                            is_match = any(
                                any(ag.min_age <= child_age <= ag.max_age for ag in available_age_groups)
                                for child_age in children_ages
                            )
                            if not is_match:
                                continue # Hiçbir çocuk yaş grubuna uymuyor, bu yüzden bu oda uygun değil.

                # Bu noktaya ulaştıysak, bu oda doluluk/çocuklar için geçerlidir.
                room_is_available = True
                break # Geçerli bir oda bulundu, diğerlerini kontrol etmeye gerek yok.
            
            if not room_is_available:
                return False # Bu sanatoryumda doluluk/çocuk kriterlerini karşılayan oda yok.

        # Kriter 3: Fiyat Aralığı (tüm sanatoryum için)
        min_price_value = RoomPrice.objects.filter(room_type__sanatorium=sanatorium.id).order_by('price').values_list('price', flat=True).first()

        if min_price_value is None:
            return False # Sanatoryumun hiç fiyatı yok.
        
        if min_price is not None and min_price_value < min_price:
            return False
            
        if max_price is not None and min_price_value > max_price:
            return False

        # Tüm kontrollerden geçti
        return True

    # Tek bir instance için kontrol
    if single_instance is not None:
        return single_instance

    # Liste için filtreleme
    valid_ids = [s.id for s in queryset if is_valid_sanatorium(s)]
    queryset = queryset.filter(id__in=valid_ids)
    logger.info(f"After filter - count: {queryset.count()}")
    logger.info(f"Valid sanatorium IDs: {valid_ids}")
    return queryset


class SanatoriumSearchView(generics.ListAPIView):
    serializer_class = SanatoriumSearchSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SanatoriumFilter
    search_fields = ['name', 'location__region', 'location__country']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Sanatorium.objects.filter(is_active=True)
        location_type = self.request.query_params.get('location_type')
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        queryset = filter_sanatorium_queryset(queryset, self.request)
        from django.db.models import OuterRef, Subquery
        room_prices = RoomPrice.objects.filter(
            room_type__sanatorium=OuterRef('id')
        ).order_by('price').values('price')[:1]
        queryset = queryset.annotate(min_price_value=Subquery(room_prices))
        queryset = queryset.filter(min_price_value__isnull=False)
        queryset = queryset.order_by('min_price_value')
        return queryset

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
        responses={200: SanatoriumSearchSerializer}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        ordering = request.query_params.get('ordering', 'total_discount_price')
        if 'results' in response.data and response.data['results']:
            reverse_sort = ordering.startswith('-')
            sort_field = ordering[1:] if reverse_sort else ordering
            if sort_field in ['total_price', 'total_discount_price']:
                logger = logging.getLogger(__name__)
                logger.info(f"Sorting by {ordering}")
                def get_sort_key(item):
                    value = item.get('total_discount_price') if sort_field == 'total_discount_price' else item.get(sort_field)
                    if sort_field == 'total_discount_price' and value is None:
                        value = item.get('total_price')
                    if value is None:
                        return float('inf')
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return float('inf')
                try:
                    logger.info(f"Before sorting - IDs: {[item.get('id') for item in response.data['results']]}")
                    logger.info(f"Before sorting - Values: {[(item.get('id'), get_sort_key(item)) for item in response.data['results'][:5]]}")
                except Exception as e:
                    logger.error(f"Error logging before sorting: {str(e)}")
                try:
                    sorted_results = sorted(
                        response.data['results'],
                        key=get_sort_key,
                        reverse=reverse_sort
                    )
                    logger.info(f"After sorting - IDs: {[item.get('id') for item in sorted_results]}")
                    logger.info(f"After sorting - Values: {[(item.get('id'), get_sort_key(item)) for item in sorted_results[:5]]}")
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
        instance = self.get_object()
        filter_sanatorium_queryset(Sanatorium.objects.filter(id=instance.id), request, single_instance=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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
    serializer_class = SanatoriumSearchSerializer


class OtherCitiesSanatoriums(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True, location_type='other_cities')
    serializer_class = SanatoriumSearchSerializer


class SanatoriumList(generics.ListAPIView):
    serializer_class = SanatoriumListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SanatoriumFilter
    
    def get_queryset(self):
        return Sanatorium.objects.filter(is_active=True)
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


def is_valid_room_for_search(room, occupancy, children_ages):
    # Oda kapasitesi kontrolü
    if occupancy:
        max_capacity = room.max_capacity if room.max_capacity is not None else None
        if max_capacity is not None and occupancy > max_capacity:
            return False
        # RoomPrice tablosunda uygun bir fiyat var mı?
        if not room.prices.filter(occupancy__gte=occupancy).exists():
            return False

    # Çocuk yaşları kontrolü
    if children_ages:
        if not room.extra_bed_prices.exists():
            # Ekstra yatak fiyatı tanımlı değilse, yine de geçerli say
            pass
        else:
            available_age_groups = {
                ebp.age_group for ebp in room.extra_bed_prices.all() if ebp.age_group
            }
            if available_age_groups:
                is_match = any(
                    any(ag.min_age <= child_age <= ag.max_age for ag in available_age_groups)
                    for child_age in children_ages
                )
                if not is_match:
                    return False
    return True


@extend_schema(
    parameters=[
        OpenApiParameter(name='check_in', description='Check-in date (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='check_out', description='Check-out date (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='occupancy', description='Number of occupants', required=False, type=int),
        OpenApiParameter(name='children_ages', description='Ages of children, comma separated (e.g., 5,7,11)', required=False, type=str),
    ]
)
class SanatoriumRoomDetailView(generics.RetrieveAPIView):
    serializer_class = SanatoriumRoomDetailSerializer
    lookup_url_kwarg = "room_pk"

    def get_queryset(self):
        sanatorium_pk = self.kwargs.get("sanatorium_pk")
        return RoomType.objects.filter(sanatorium_id=sanatorium_pk)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "request": self.request,
            "check_in": self.request.query_params.get("check_in"),
            "check_out": self.request.query_params.get("check_out"),
            "occupancy": self.request.query_params.get("occupancy"),
            "children_ages": self.request.query_params.get("children_ages", ""),
        })
        return context
    
    def get(self, request, *args, **kwargs):
        room = self.get_object()
        
        context = self.get_serializer_context()
        occupancy_str = context.get("occupancy")
        children_ages_str = context.get("children_ages", "")

        occupancy = int(occupancy_str) if occupancy_str and occupancy_str.isdigit() else 1
        children_ages = [int(age) for age in children_ages_str.split(',') if age.strip().isdigit()]

        is_valid = is_valid_room_for_search(room, occupancy, children_ages)
        
        if not is_valid:
            return Response(
                {"detail": "This room does not match the specified criteria (e.g., occupancy, children)."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().get(request, *args, **kwargs)


class SimilarSanatoriumsView(generics.ListAPIView):
    serializer_class = SanatoriumSearchSerializer
    pagination_class = CustomPageNumberPagination