from rest_framework import serializers
from utils.api.mixins.translation import TranslationMixin
from .models import About, History, TimelinePunkt, ModernPunkt, Treatment, TreatmentProcess, TreatmentCategory, TreatmentBenefit, TreatmentPage


class AboutSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = About
        fields = ['banner_image', 'banner_title', 'banner_description', 'content', 'reservation_image', 'reservation_title', 'reservation_description'  ]


class TimelinePunktSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TimelinePunkt
        fields = ['year', 'title', 'description']


class ModernPunktSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = ModernPunkt
        fields = ['icon', 'title', 'description']


class HistorySerializer(TranslationMixin, serializers.ModelSerializer):
    timeline_punkts = TimelinePunktSerializer(many=True, read_only=True)
    modern_punkts = ModernPunktSerializer(many=True, read_only=True)
    class Meta:
        model = History
        fields = ['hero_section_title', 'hero_section_content', 'hero_section_image', 'introduction_title', 'introduction_content', 'timeline_section_title', 'timeline_section_description', 'scientific_section_title', 'scientific_section_content', 'scientific_section_image', 'soviet_section_title', 'soviet_section_content', 'soviet_section_image', 'modern_section_title', 'modern_section_description', 'timeline_punkts', 'modern_punkts']


class TreatmentPageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentPage
        fields = ['hero_title', 'hero_description', 'main_title', 'main_content', 'main_image', 'category_section_title', 'category_section_description', 'process_section_title', 'process_section_description', 'contact_section_title', 'contact_section_description']


class TreatmentCategorySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentCategory
        fields = ['title', 'id']


class TreatmentBenefitSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentBenefit
        fields = ['title', 'priority']
    

class TreatmentSerializer(TranslationMixin, serializers.ModelSerializer):
    category = TreatmentCategorySerializer()
    benefits = TreatmentBenefitSerializer(many=True, read_only=True)
    class Meta:
        model = Treatment
        fields = ['title', 'content', 'image', 'category', 'benefits']


class TreatmentProcessSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentProcess
        fields = ['title', 'content', 'priority']

