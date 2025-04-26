from rest_framework import serializers
from .models import (
    Hero,
    Location,
    TransportOptionSection,
    TransportOption,
    VisaSection
)
from utils.api.mixins.translation import TranslationMixin


class HeroSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = ['title', 'description']


class LocationSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['title', 'description', 'map_iframe']


class TransportOptionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TransportOption
        fields = ['title', 'description', 'icon']


class TransportOptionSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    options = TransportOptionSerializer(many=True, read_only=True)
    class Meta:
        model = TransportOptionSection
        fields = ['title', 'description', 'options']


class VisaSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = VisaSection
        fields = ['title', 'description', 'content']
