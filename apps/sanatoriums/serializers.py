from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import (
    Location, Sanatorium, SanatoriumImage, 
    Facility, SanatoriumFacility,
    RoomType, RoomImage, Review, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage
)
from utils.api.mixins.translation import TranslationMixin

class LocationSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'region', 'country']

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

class RoomTypeSerializer(TranslationMixin, serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = RoomType
        fields = ['id', 'name', 'images']

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

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'location', 'location_type',
            'short_description', 'rating', 'price',
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

    

class SanatoriumSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    images = SanatoriumImageSerializer(many=True, read_only=True)
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True, source='sanatoiruim')
    room_types = RoomTypeSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    similar_sanatoriums = serializers.SerializerMethodField()

    
    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'description', 'treatments', 'location', 'location_type',
            'map_iframe', 'address',
            'price', 'rating', 'facilities', 'room_types', 'reviews',
            'in_home', 'created_at', 'updated_at', 'images', 'similar_sanatoriums'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


    @extend_schema_field(SanatoriumListSerializer(many=True))
    def get_similar_sanatoriums(self, obj):
        queryset = Sanatorium.objects.filter(
            location_type=obj.location_type
        ).exclude(id=obj.id)[:3]
        return SanatoriumListSerializer(queryset, many=True, context=self.context).data



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