"""
Fixed version of the serializers.py file with proper handling of child ages
that don't match any available age group
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample
import logging
from apps.sanatoriums.pricing_helper import get_price_details, get_extra_bed_price_details

from .models import (
    Location, Sanatorium, SanatoriumImage, 
    Facility, SanatoriumFacility,
    RoomType, RoomImage, Review, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage,
    Season, RoomPrice, AgeGroup, ExtraBedPrice, TreatmentOption
)
from utils.api.mixins.translation import TranslationMixin

from apps.core.models import Currency


class SEOSerializer(serializers.ModelSerializer):
    """SEO məlumatları üçün ayrı serializer"""
    og_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Sanatorium
        fields = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image',
                 'canonical_url', 'no_index', 'no_follow')
    
    def get_og_image(self, obj):
        """OG Image üçün tam URL qaytarır"""
        request = self.context.get('request')
        if obj.og_image and hasattr(obj.og_image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.og_image.url)
            return obj.og_image.url
        return None

class LocationSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'region', 'country']


class CurrencySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']


class SeasonSerializer(TranslationMixin, serializers.ModelSerializer):
    is_current = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Season
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']


class TreatmentOptionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentOption
        fields = ['id', 'name', 'description']


class AgeGroupSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        fields = ['id', 'name', 'min_age', 'max_age']


class FacilitySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name', 'icon']

class SanatoriumImageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = SanatoriumImage
        fields = ['id', 'image', 'is_main', 'priority']

class RoomImageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'priority']


class RoomPriceSerializer(TranslationMixin, serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    treatment_option = TreatmentOptionSerializer(read_only=True)
    discounted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomPrice
        fields = ['id', 'season', 'occupancy', 'with_treatment', 'treatment_option', 'price', 'currency',
                 'discount_type', 'discount_value', 'discounted_price']
    
    def get_discounted_price(self, obj):
        return obj.discounted_price


class ExtraBedPriceSerializer(TranslationMixin, serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    age_group = AgeGroupSerializer(read_only=True)
    treatment_option = TreatmentOptionSerializer(read_only=True)
    discounted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ExtraBedPrice
        fields = ['id', 'season', 'age_group', 'with_treatment', 'treatment_option', 'price', 'currency',
                 'discount_type', 'discount_value', 'discounted_price']
    
    def get_discounted_price(self, obj):
        return obj.discounted_price


class RoomTypeSerializer(TranslationMixin, serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    prices = RoomPriceSerializer(many=True, read_only=True)
    extra_bed_prices = ExtraBedPriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = RoomType
        fields = ['id', 'name', 'description', 'min_capacity', 'max_capacity', 'max_extra_beds', 'size', 'images', 'prices', 'extra_bed_prices']

class ReviewSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'full_name', 'sanatorium', 'rating', 'content', 'date']
        read_only_fields = [ 'created_at']

class SanatoriumFacilitySerializer(TranslationMixin, serializers.ModelSerializer):
    facility = FacilitySerializer(read_only=True)
    
    class Meta:
        model = SanatoriumFacility
        fields = ['id', 'facility']

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Sanatorium list',
            summary='List of sanatoriums',
            description='This is a list of sanatoriums',
            value={
                'id': 1,
                'name': 'Sanatorium 1',
                'slug': 'sanatorium-1',
                'location': {
                    'id': 1,
                    'region': 'Baku',
                    'country': 'Azerbaijan'
                },
                'location_type': 'city',
                'short_description': 'Short description',
                'rating': 4.5,
                'min_price': 100.0,
                'min_price_currency': {
                    'id': 1,
                    'code': 'AZN',
                    'name': 'Azerbaijani Manat',
                    'symbol': '₼'
                },
                'total_price': 200.0,
                'min_price_details': {
                    'selected_room': 'Room 1',
                    'occupancy': 2,
                    'children_ages': [5, 10],
                    'season': 'Summer',
                    'season_type': 'current',
                    'base_price': 100.0,
                    'base_price_currency': 'AZN',
                    'extra_bed_prices': [
                        {
                            'child_age': 5,
                            'price_added': 20.0,
                            'is_default': False
                        },
                        {
                            'child_age': 10,
                            'price_added': 30.0,
                            'is_default': False
                        }
                    ],
                    'total_price': 200.0,
                    'room_capacity': {
                        'min': 2,
                        'max': 4
                    },
                    'max_extra_beds': 2,
                    'with_treatment': True,
                    'treatment_option': 'Treatment 1'
                },
                'is_active': True,
                'in_home': True,
                'main_image': {
                    'id': 1,
                    'image': 'image.jpg',
                    'is_main': True,
                    'priority': 1
                },
                'facilities': [
                    {
                        'id': 1,
                        'facility': {
                            'id': 1,
                            'name': 'Facility 1',
                            'icon': 'icon.jpg'
                        }
                    }
                ],
                'images': [
                    {
                        'id': 1,
                        'image': 'image.jpg',
                        'is_main': True,
                        'priority': 1
                    }
                ]
            }
        )
    ]
)
class SanatoriumListSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True)
    images = SanatoriumImageSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_price_currency = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    min_price_details = serializers.SerializerMethodField()

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'location', 'location_type',
            'short_description', 'rating', 'min_price', 'min_price_currency', 'total_price', 'min_price_details',
            'is_active', 'in_home', 'main_image', 'facilities', 'images'
        ]
    
    def get_main_image(self, obj):
        request = self.context.get('request')
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return SanatoriumImageSerializer(main_image, context={'request': request}).data
        
        # If no main image, return the first image from the list
        first_image = obj.images.first()
        if first_image:
            return SanatoriumImageSerializer(first_image, context={'request': request}).data
        
        return None

    def get_min_price(self, obj):
        # Get the current season prices for rooms
        from datetime import date
        today = date.today()
        current_season = Season.objects.filter(start_date__lte=today, end_date__gte=today).first()
        
        # Get occupancy from request query params
        request = self.context.get('request')
        occupancy = None
        if request and request.query_params.get('occupancy'):
            try:
                occupancy = int(request.query_params.get('occupancy'))
            except (ValueError, TypeError):
                pass
        
        # Get children ages from request query params
        children_ages = []
        if request and request.query_params.get('children_ages'):
            try:
                children_ages = [int(age) for age in request.query_params.get('children_ages').split(',') if age.strip()]
            except (ValueError, TypeError):
                pass
        
        # Logging for debugging purposes
        logger = logging.getLogger(__name__)
        logger.debug(f"Calculating min price for sanatorium {obj.id} with occupancy {occupancy} and children ages {children_ages}")

        min_price = None
        min_room_type = None
        min_price_season = None
        selected_price = None
        
        # If we have a current season, get minimum price from that season
        if current_season:
            for room_type in obj.room_types.all():
                # Check if the room can accommodate the extra beds needed
                # Handle case where max_extra_beds may be None
                # Eğer max_extra_beds None ise, sınırsız ek yatak kapasitesi olarak değerlendirilmeli
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                if children_ages and len(children_ages) > max_extra_beds:
                    continue
                
                # Filter prices by occupancy if specified
                if occupancy:
                    room_prices = room_type.prices.filter(season=current_season, occupancy=occupancy)
                else:
                    room_prices = room_type.prices.filter(season=current_season)
                
                if room_prices.exists():
                    for price in room_prices:
                        room_price = price.price
                        if min_price is None or room_price < min_price:
                            min_price = room_price
                            self._min_price_currency = price.currency
                            min_room_type = room_type
                            min_price_season = current_season
                            selected_price = price
        
        # If no current season or no prices found, get minimum price from all seasons
        if min_price is None:
            for room_type in obj.room_types.all():
                # Check if the room can accommodate the extra beds needed
                # Handle case where max_extra_beds may be None
                # Eğer max_extra_beds None ise, sınırsız ek yatak kapasitesi olarak değerlendirilmeli
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                if children_ages and len(children_ages) > max_extra_beds:
                    continue
                
                # Filter prices by occupancy if specified
                if occupancy:
                    room_prices = room_type.prices.filter(occupancy=occupancy)
                else:
                    room_prices = room_type.prices.all()
                
                if room_prices.exists():
                    for price in room_prices:
                        room_price = price.price
                        if min_price is None or room_price < min_price:
                            min_price = room_price
                            self._min_price_currency = price.currency
                            min_room_type = room_type
                            min_price_season = price.season
                            selected_price = price
        
        # Add extra bed prices if there are children
        extra_bed_price_details = []
        if min_price is not None and min_room_type is not None and children_ages:
            # İlk olarak geçerli sezon fiyatlarını kontrol edelim (eğer sezon varsa)
            extra_bed_prices = None
            
            if min_price_season is not None:
                extra_bed_prices = min_room_type.extra_bed_prices.filter(season=min_price_season)
                
                # Belirli sezon için fiyat yoksa standart fiyatları deneyelim
                if not extra_bed_prices.exists():
                    extra_bed_prices = min_room_type.extra_bed_prices.filter(is_standard=True)
            else:
                # Sezon yoksa standart fiyatları deneyelim
                extra_bed_prices = min_room_type.extra_bed_prices.filter(is_standard=True)
            
            # Standart fiyatlar da yoksa tüm fiyatları deneyelim
            if not extra_bed_prices.exists():
                extra_bed_prices = min_room_type.extra_bed_prices.all()
                
            # Uygun fiyatlar bulunduysa her çocuk için işlem yapalım
            if extra_bed_prices.exists():
                for age in children_ages:
                    # Çocuk için uygun yaş grubu arama
                    age_group_found = False
                    
                    for extra_bed_price in extra_bed_prices:
                        age_group = extra_bed_price.age_group
                        if age_group.min_age <= age <= age_group.max_age:
                            min_price += extra_bed_price.price
                            age_group_found = True
                            
                            # Add extra bed price details
                            extra_bed_price_detail = get_extra_bed_price_details(
                                room_type=min_room_type, 
                                child_age=age, 
                                extra_bed_price=extra_bed_price, 
                                price_added=extra_bed_price.price, 
                                is_default=False
                            )
                            extra_bed_price_details.append(extra_bed_price_detail)
                            break
                    
                    # Eğer çocuk için yaş grubu bulunamadıysa, fiyata ekleme yapma
                    if not age_group_found:
                        logger.debug(f"No matching age group found for child age {age} - no price added")
        
        # Create detailed price information using the helper function
        if min_room_type and selected_price:
            is_current_season = (min_price_season == current_season)
            self._min_price_details = get_price_details(
                sanatorium=obj,
                room_type=min_room_type,
                price=selected_price,
                is_current_season=is_current_season,
                season=min_price_season,
                min_price=min_price,
                occupancy=occupancy,
                children_ages=children_ages
            )
        
        return min_price

    def get_total_price(self, obj):
        """Calculate total price based on check-in and check-out dates"""
        from datetime import datetime
        
        request = self.context.get('request')
        if not request:
            return None
            
        # Get check-in and check-out dates
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        
        if not check_in_str or not check_out_str:
            return None
            
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            
            # Calculate number of nights
            nights = (check_out - check_in).days
            if nights <= 0:
                return None
                
            # Get base price (including extra beds if applicable)
            base_price = self.get_min_price(obj)
            if base_price is None:
                return None
                
            # Calculate total price based on nights
            total_price = base_price * nights
            return total_price
            
        except (ValueError, TypeError):
            return None

    def get_min_price_currency(self, obj):
        if hasattr(self, '_min_price_currency') and self._min_price_currency:
            return CurrencySerializer(self._min_price_currency).data
        return None
        
    def get_min_price_details(self, obj):
        """Returns detailed information about how the minimum price is calculated"""
        # Call get_min_price first to ensure price details are calculated
        if not hasattr(self, '_min_price_details'):
            self.get_min_price(obj)
            
        if hasattr(self, '_min_price_details'):
            return self._min_price_details
            
        return None

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Sanatorium detail',
            summary='Detail of a sanatorium',
            description='Complete information about a specific sanatorium',
            value={
                'id': 1,
                'name': 'Chinar Hotel & Spa Naftalan',
                'slug': 'chinar-hotel-spa-naftalan',
                'description': 'Chinar Hotel & Spa Naftalan is a luxury hotel located in the heart of Naftalan city, famous for its healing oil treatments.',
                'treatments': 'The hotel offers various treatments including Naftalan oil baths, mud therapy, and other balneological procedures.',
                'location': {
                    'id': 1,
                    'region': 'Naftalan',
                    'country': 'Azerbaijan'
                },
                'location_type': 'naftalan',
                'map_iframe': '<iframe src="https://maps.google.com/maps?q=40.6461,46.8311&z=15&output=embed"></iframe>',
                'address': 'Naftalan city, Azerbaijan',
                'rating': 4.8,
                'facilities': [
                    {
                        'id': 1,
                        'facility': {
                            'id': 1,
                            'name': 'Swimming Pool',
                            'icon': 'pool-icon.svg'
                        }
                    },
                    {
                        'id': 2,
                        'facility': {
                            'id': 2,
                            'name': 'Spa Center',
                            'icon': 'spa-icon.svg'
                        }
                    }
                ],
                'room_types': [
                    {
                        'id': 1,
                        'name': 'Standard Room',
                        'description': 'Comfortable standard room with all necessary amenities',
                        'min_capacity': 1,
                        'max_capacity': 2,
                        'max_extra_beds': 1,
                        'size': 25,
                        'images': [
                            {
                                'id': 1,
                                'image': 'room1.jpg',
                                'priority': 1
                            }
                        ],
                        'prices': [
                            {
                                'id': 1,
                                'season': {
                                    'id': 1,
                                    'name': 'Summer 2023',
                                    'start_date': '2023-06-01',
                                    'end_date': '2023-08-31',
                                    'is_current': True
                                },
                                'occupancy': 2,
                                'with_treatment': True,
                                'treatment_option': {
                                    'id': 1,
                                    'name': 'Naftalan Oil Bath',
                                    'description': 'Traditional naftalan oil treatment'
                                },
                                'price': 150.0,
                                'currency': {
                                    'id': 1,
                                    'code': 'AZN',
                                    'name': 'Azerbaijani Manat',
                                    'symbol': '₼'
                                },
                                'discount_type': 'percentage',
                                'discount_value': 10,
                                'discounted_price': 135.0
                            }
                        ],
                        'extra_bed_prices': [
                            {
                                'id': 1,
                                'season': {
                                    'id': 1,
                                    'name': 'Summer 2023',
                                    'start_date': '2023-06-01',
                                    'end_date': '2023-08-31',
                                    'is_current': True
                                },
                                'age_group': {
                                    'id': 1,
                                    'name': 'Children 3-11',
                                    'min_age': 3,
                                    'max_age': 11
                                },
                                'with_treatment': False,
                                'treatment_option': None,
                                'price': 50.0,
                                'currency': {
                                    'id': 1,
                                    'code': 'AZN',
                                    'name': 'Azerbaijani Manat',
                                    'symbol': '₼'
                                },
                                'discount_type': None,
                                'discount_value': None,
                                'discounted_price': 50.0
                            }
                        ]
                    }
                ],
                'reviews': [
                    {
                        'id': 1,
                        'full_name': 'Ali Mammadov',
                        'sanatorium': 1,
                        'rating': 5,
                        'content': 'Great hotel with excellent service',
                        'date': '2023-07-15'
                    }
                ],
                'in_home': True,
                'created_at': '2023-01-01T12:00:00Z',
                'updated_at': '2023-05-10T15:30:00Z',
                'images': [
                    {
                        'id': 1,
                        'image': 'hotel-main.jpg',
                        'is_main': True,
                        'priority': 1
                    },
                    {
                        'id': 2,
                        'image': 'hotel-pool.jpg',
                        'is_main': False,
                        'priority': 2
                    }
                ],
                'similar_sanatoriums': [
                    {
                        'id': 2,
                        'name': 'Qarabag Resort & Spa',
                        'slug': 'qarabag-resort-spa',
                        'location': {
                            'id': 1,
                            'region': 'Naftalan',
                            'country': 'Azerbaijan'
                        },
                        'location_type': 'naftalan',
                        'short_description': 'Premium resort with comprehensive treatment facilities',
                        'rating': 4.5,
                        'min_price': 120.0,
                        'min_price_currency': {
                            'id': 1,
                            'code': 'AZN',
                            'name': 'Azerbaijani Manat',
                            'symbol': '₼'
                        },
                        'total_price': 840.0,
                        'min_price_details': {
                            'room_type': 'Double Room',
                            'occupancy': 2,
                            'with_treatment': True,
                            'price_per_night': 120.0,
                            'nights': 7,
                            'discount_applied': True,
                            'discount_type': 'percentage',
                            'discount_value': 10
                        },
                        'is_active': True,
                        'in_home': True,
                        'main_image': {
                            'id': 3,
                            'image': 'qarabag-main.jpg',
                            'is_main': True,
                            'priority': 1
                        },
                        'facilities': []
                    }
                ],
                'min_price': 135.0,
                'min_price_currency': {
                    'id': 1,
                    'code': 'AZN',
                    'name': 'Azerbaijani Manat',
                    'symbol': '₼'
                },
                'total_price': 945.0,
                'min_price_details': {
                    'room_type': 'Standard Room',
                    'occupancy': 2,
                    'with_treatment': True,
                    'price_per_night': 135.0,
                    'nights': 7,
                    'discount_applied': True,
                    'discount_type': 'percentage',
                    'discount_value': 10
                },
                'seo': {
                    'meta_title': 'Chinar Hotel & Spa Naftalan - Luxury Hotel with Naftalan Oil Treatments',
                    'meta_description': 'Discover the healing properties of Naftalan oil in our luxury hotel. Book your stay today for a rejuvenating experience.',
                    'meta_keywords': 'naftalan, spa, hotel, azerbaijan, treatment, healing oil',
                    'og_title': 'Chinar Hotel & Spa - Premium Naftalan Treatments',
                    'og_description': 'Experience the best of Naftalan oil treatments in our luxury hotel.',
                    'og_image': 'https://example.com/images/chinar-og.jpg',
                    'canonical_url': 'https://example.com/sanatoriums/chinar-hotel-spa-naftalan',
                    'no_index': False,
                    'no_follow': False
                }
            }
        )
    ]
)
class SanatoriumSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    images = SanatoriumImageSerializer(many=True, read_only=True)
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True)
    room_types = RoomTypeSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    similar_sanatoriums = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_price_currency = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    min_price_details = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'description', 'treatments', 'location', 'location_type',
            'map_iframe', 'address',
            'rating', 'facilities', 'room_types', 'reviews',
            'in_home', 'created_at', 'updated_at', 'images', 'similar_sanatoriums', 
            'min_price', 'min_price_currency', 'total_price', 'min_price_details', 'seo'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'min_price', 'min_price_currency', 'total_price', 'min_price_details']


    @extend_schema_field(SEOSerializer)
    def get_seo(self, obj):
        """SEO məlumatlarını ayrı bir obyekt kimi qaytarır"""
        serializer = SEOSerializer(obj, context=self.context)
        return serializer.data
    
    @extend_schema_field(SanatoriumListSerializer(many=True))
    def get_similar_sanatoriums(self, obj):
        queryset = Sanatorium.objects.filter(
            location_type=obj.location_type
        ).exclude(id=obj.id)[:3]
        return SanatoriumListSerializer(queryset, many=True, context=self.context).data

    def get_min_price(self, obj):
        # Get the current season prices for rooms
        from datetime import date
        today = date.today()
        current_season = Season.objects.filter(start_date__lte=today, end_date__gte=today).first()
        
        # Get occupancy from request query params
        request = self.context.get('request')
        occupancy = None
        if request and request.query_params.get('occupancy'):
            try:
                occupancy = int(request.query_params.get('occupancy'))
            except (ValueError, TypeError):
                pass
        
        # Get children ages from request query params
        children_ages = []
        if request and request.query_params.get('children_ages'):
            try:
                children_ages = [int(age) for age in request.query_params.get('children_ages').split(',') if age.strip()]
            except (ValueError, TypeError):
                pass

        # Logging for debugging purposes
        logger = logging.getLogger(__name__)
        logger.debug(f"Calculating min price for sanatorium {obj.id} with occupancy {occupancy} and children ages {children_ages}")
        
        min_price = None
        min_room_type = None
        min_price_season = None
        selected_price = None
        
        # Fiyat oluşturma detaylarını takip etmek için değişkenler
        self._price_details = {
            'selected_room': None,
            'occupancy': occupancy,
            'children_ages': children_ages,
            'season': None,
            'season_type': None,  # Hangi tip sezon kullanıldı (current, standard, any)
            'base_price': None,
            'base_price_currency': None,
            'extra_bed_prices': [],
            'total_price': None,
            'room_capacity': None,
            'max_extra_beds': None,
            'with_treatment': None,
            'treatment_option': None
        }
        
        # If we have a current season, get minimum price from that season
        if current_season:
            for room_type in obj.room_types.all():
                # Check if the room can accommodate the extra beds needed
                # Handle case where max_extra_beds may be None
                # Eğer max_extra_beds None ise, sınırsız ek yatak kapasitesi olarak değerlendirilmeli
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                if children_ages and len(children_ages) > max_extra_beds:
                    continue
                
                # Filter prices by occupancy if specified
                if occupancy:
                    room_prices = room_type.prices.filter(season=current_season, occupancy=occupancy)
                else:
                    room_prices = room_type.prices.filter(season=current_season)
                
                if room_prices.exists():
                    for price in room_prices:
                        room_price = price.price
                        if min_price is None or room_price < min_price:
                            min_price = room_price
                            self._min_price_currency = price.currency
                            min_room_type = room_type
                            min_price_season = current_season
                            selected_price = price
        
        # If no current season or no prices found, get minimum price from all seasons
        if min_price is None:
            for room_type in obj.room_types.all():
                # Check if the room can accommodate the extra beds needed
                # Handle case where max_extra_beds may be None
                # Eğer max_extra_beds None ise, bu sınırsız ek yatak anlamına gelir (sınırlama yok)
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                if children_ages and len(children_ages) > max_extra_beds:
                    continue
                
                # Filter prices by occupancy if specified
                if occupancy:
                    room_prices = room_type.prices.filter(occupancy=occupancy)
                else:
                    room_prices = room_type.prices.all()
                
                if room_prices.exists():
                    for price in room_prices:
                        room_price = price.price
                        if min_price is None or room_price < min_price:
                            min_price = room_price
                            self._min_price_currency = price.currency
                            min_room_type = room_type
                            min_price_season = price.season
                            selected_price = price
        
        # Fiyat detaylarını güncelle
        if min_room_type and min_price_season:
            self._price_details.update({
                'selected_room': min_room_type.name,
                'season': min_price_season.name if min_price_season else None,
                'season_type': 'current' if min_price_season == current_season else 'other',
                'base_price': min_price,
                'base_price_currency': self._min_price_currency.code if self._min_price_currency else None,
                'room_capacity': {
                    'min': min_room_type.min_capacity,
                    'max': min_room_type.max_capacity
                },
                'max_extra_beds': min_room_type.max_extra_beds,
                'with_treatment': selected_price.with_treatment if selected_price and hasattr(selected_price, 'with_treatment') else None,
                'treatment_option': selected_price.treatment_option.name if selected_price and hasattr(selected_price, 'treatment_option') and selected_price.treatment_option else None
            })
        
        # Add extra bed prices if there are children
        extra_bed_price_details = []
        if min_price is not None and min_room_type is not None and children_ages:
            # İlk olarak geçerli sezon fiyatlarını kontrol edelim (eğer sezon varsa)
            extra_bed_prices = None
            
            if min_price_season is not None:
                extra_bed_prices = min_room_type.extra_bed_prices.filter(season=min_price_season)
                
                # Belirli sezon için fiyat yoksa standart fiyatları deneyelim
                if not extra_bed_prices.exists():
                    extra_bed_prices = min_room_type.extra_bed_prices.filter(is_standard=True)
            else:
                # Sezon yoksa standart fiyatları deneyelim
                extra_bed_prices = min_room_type.extra_bed_prices.filter(is_standard=True)
            
            # Standart fiyatlar da yoksa tüm fiyatları deneyelim
            if not extra_bed_prices.exists():
                extra_bed_prices = min_room_type.extra_bed_prices.all()
                
            # Uygun fiyatlar bulunduysa her çocuk için işlem yapalım
            if extra_bed_prices.exists():
                for age in children_ages:
                    # Çocuk için uygun yaş grubu arama
                    age_group_found = False
                    
                    for extra_bed_price in extra_bed_prices:
                        age_group = extra_bed_price.age_group
                        if age_group.min_age <= age <= age_group.max_age:
                            min_price += extra_bed_price.price
                            age_group_found = True
                            
                            # Add extra bed price details
                            extra_bed_price_detail = get_extra_bed_price_details(
                                room_type=min_room_type, 
                                child_age=age, 
                                extra_bed_price=extra_bed_price, 
                                price_added=extra_bed_price.price, 
                                is_default=False
                            )
                            extra_bed_price_details.append(extra_bed_price_detail)
                            break
                    
                    # Eğer çocuk için yaş grubu bulunamadıysa, fiyata ekleme yapma
                    if not age_group_found:
                        logger.debug(f"No matching age group found for child age {age} - no price added")
        
        # Update the price details with extra bed prices and total price
        self._price_details['extra_bed_prices'] = extra_bed_price_details
        self._price_details['total_price'] = min_price
        
        # Create detailed price information using the helper function
        if min_room_type and selected_price:
            is_current_season = (min_price_season == current_season)
            self._min_price_details = get_price_details(
                sanatorium=obj,
                room_type=min_room_type,
                price=selected_price,
                is_current_season=is_current_season,
                season=min_price_season,
                min_price=min_price,
                occupancy=occupancy,
                children_ages=children_ages
            )
        
        return min_price

   
    def get_total_price(self, obj):
        """Calculate total price based on check-in and check-out dates"""
        from datetime import datetime
        
        request = self.context.get('request')
        if not request:
            return None
            
        # Get check-in and check-out dates
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        
        if not check_in_str or not check_out_str:
            return None
            
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            
            # Calculate number of nights
            nights = (check_out - check_in).days
            if nights <= 0:
                return None
                
            # Get base price (including extra beds if applicable)
            base_price = self.get_min_price(obj)
            if base_price is None:
                return None
                
            # Calculate total price based on nights
            total_price = base_price * nights
            return total_price
            
        except (ValueError, TypeError):
            return None

    def get_min_price_currency(self, obj):
        if hasattr(self, '_min_price_currency') and self._min_price_currency:
            return CurrencySerializer(self._min_price_currency).data
        return None
        
    def get_min_price_details(self, obj):
        """Returns detailed information about how the minimum price is calculated"""
        # Call get_min_price first to ensure price details are calculated
        if not hasattr(self, '_min_price_details'):
            self.get_min_price(obj)
            
        if hasattr(self, '_min_price_details'):
            return self._min_price_details
            
        return None

class ReviewCreateSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['sanatorium', 'full_name', 'rating', 'content']
        extra_kwargs = {
            'sanatorium': {'write_only': True}
        }


class NaftalanSanatoriumsPageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = NaftalanSanatoriumsPage
        fields = ['id', 'hero_section_title', 'hero_section_description',
                  'main_section_title', 'main_section_description', 'main_section_image',
                  'sanatoriums_section_title', 'sanatoriums_section_description',
                  'contact_section_title', 'contact_section_description']


class OtherCitiesSanatoriumsPageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = OtherCitiesSanatoriumsPage
        fields = ['id', 'hero_section_title', 'hero_section_description',
                  'main_section_title', 'main_section_description', 'main_section_image',
                  'sanatoriums_section_title', 'sanatoriums_section_description',
                  'contact_section_title', 'contact_section_description']
