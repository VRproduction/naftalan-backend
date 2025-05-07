from rest_framework import serializers
from .models import (
    AboutPunkt,
    AboutSection,
    ContactSection,
    CustomerComments,
    CustomerCommentsSection,
    HeroSlider,
    PackagesSection,
    SanatoriesSection,
    TreatmentsSection,
    FAQSection,
    FAQ,
    BlogSection,
    ContactSection,
)
from utils.api.mixins.translation import TranslationMixin
from apps.sanatoriums.serializers import SanatoriumSearchSerializer


class HeroSliderSerializer(TranslationMixin, serializers.ModelSerializer):
    sanatorium = SanatoriumSearchSerializer()
    class Meta:
        model = HeroSlider
        fields = ['sanatorium',]


class AboutPunktSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = AboutPunkt
        fields = ['icon', 'title', 'description']


class AboutSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    punkts = AboutPunktSerializer(many=True)
    class Meta:
        model = AboutSection
        fields = ['sub_title', 'title', 'section_description', 'image', 'content_title', 'punkts']


class SanatoriesSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = SanatoriesSection
        fields = ['sub_title', 'title', 'section_description']


class TreatmentsSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentsSection
        fields = ['title', 'section_description']  


class PackagesSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = PackagesSection
        fields = ['title', 'section_description']


class CustomerCommentsSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomerCommentsSection
        fields = ['title', 'section_description']


class CustomerCommentsSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomerComments
        fields = ['full_name', 'address', 'rating', 'comment', 'priority']


class FAQSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = FAQSection
        fields = ['title', 'section_description']


class FAQSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'priority']


class BlogSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = BlogSection
        fields = ['title', 'section_description']


class ContactSectionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = ContactSection
        fields = ['left_section_title', 'left_section_description', 'right_section_title', 'right_section_description']