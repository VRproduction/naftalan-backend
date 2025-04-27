from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

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
    
    class Meta:
        model = RoomPrice
        fields = ['id', 'season', 'occupancy', 'with_treatment', 'treatment_option', 'price', 'currency']


class ExtraBedPriceSerializer(TranslationMixin, serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    age_group = AgeGroupSerializer(read_only=True)
    treatment_option = TreatmentOptionSerializer(read_only=True)
    
    class Meta:
        model = ExtraBedPrice
        fields = ['id', 'season', 'age_group', 'with_treatment', 'treatment_option', 'price', 'currency']


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

class SanatoriumListSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True, source='sanatoiruim')
    images = SanatoriumImageSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_price_currency = serializers.SerializerMethodField()

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'location', 'location_type',
            'short_description', 'rating', 'min_price', 'min_price_currency',
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
        
        min_price = None
        
        # If we have a current season, get minimum price from that season
        if current_season:
            for room_type in obj.room_types.all():
                room_prices = room_type.prices.filter(season=current_season)
                if room_prices.exists():
                    for price in room_prices:
                        if min_price is None or price.price < min_price:
                            min_price = price.price
                            self._min_price_currency = price.currency
        
        # If no current season or no prices found, get minimum price from all seasons
        if min_price is None:
            for room_type in obj.room_types.all():
                room_prices = room_type.prices.all()
                if room_prices.exists():
                    for price in room_prices:
                        if min_price is None or price.price < min_price:
                            min_price = price.price
                            self._min_price_currency = price.currency
        
        return min_price

    def get_min_price_currency(self, obj):
        if hasattr(self, '_min_price_currency') and self._min_price_currency:
            return CurrencySerializer(self._min_price_currency).data
        return None

class SanatoriumSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    images = SanatoriumImageSerializer(many=True, read_only=True)
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True, source='sanatoiruim')
    room_types = RoomTypeSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    similar_sanatoriums = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_price_currency = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'description', 'treatments', 'location', 'location_type',
            'map_iframe', 'address',
            'rating', 'facilities', 'room_types', 'reviews',
            'in_home', 'created_at', 'updated_at', 'images', 'similar_sanatoriums', 'min_price', 'min_price_currency', 'seo'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'min_price', 'min_price_currency']


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
        
        min_price = None
        
        # If we have a current season, get minimum price from that season
        if current_season:
            for room_type in obj.room_types.all():
                room_prices = room_type.prices.filter(season=current_season)
                if room_prices.exists():
                    for price in room_prices:
                        if min_price is None or price.price < min_price:
                            min_price = price.price
                            self._min_price_currency = price.currency
        
        # If no current season or no prices found, get minimum price from all seasons
        if min_price is None:
            for room_type in obj.room_types.all():
                room_prices = room_type.prices.all()
                if room_prices.exists():
                    for price in room_prices:
                        if min_price is None or price.price < min_price:
                            min_price = price.price
                            self._min_price_currency = price.currency
        
        return min_price

    def get_min_price_currency(self, obj):
        if hasattr(self, '_min_price_currency') and self._min_price_currency:
            return CurrencySerializer(self._min_price_currency).data
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