from rest_framework import serializers
from utils.api.mixins.translation import TranslationMixin
from .models import SiteSettings, SEO, Currency, WorkingHours, ContactEmail, ContactPhone



class CurrencySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'code', 'name', 'symbol')

class WorkingHoursSerializer(TranslationMixin, serializers.ModelSerializer):
    """Serializer for working hours"""
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    class Meta:
        model = WorkingHours
        fields = (
            'id', 'day', 'day_display', 'is_working_day', 'opening_time', 
            'closing_time', 'lunch_start', 'lunch_end', 'note', 'order'
        )

class ContactEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEmail
        fields = ['id', 'email', 'is_primary', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ContactPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPhone
        fields = ['id', 'phone', 'is_primary', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class SiteSettingsSerializer(TranslationMixin, serializers.ModelSerializer):
    """Serializer for site-wide settings"""
    working_hours = WorkingHoursSerializer(source='working_hours_set', many=True, read_only=True)
    contact_emails = ContactEmailSerializer(many=True, read_only=True)
    contact_phones = ContactPhoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = SiteSettings
        fields = (
            # Basic Site Info
            'site_name', 'site_tagline', 'site_description',
            
            # Contact Info
            'contact_emails', 'contact_phones', 'working_hours',
            'whatsapp_number', 'telegram_username',
            
            # Location
            'address', 'map_latitude', 'map_longitude', 'map_zoom', 
            
            # Company Info
            'company_name', 'tax_number', 'foundation_year',
            
            # Visual Assets
            'logo', 'logo_dark', 'footer_logo', 'favicon', 'mobile_app_icon',
            
            # Colors
            'primary_color', 'secondary_color', 'accent_color',
            
            # Footer
            'footer_text', 'copyright_text', 'show_social_in_footer',
            
            # Social
            'social_facebook', 'social_instagram', 'social_twitter', 
            'social_youtube', 'social_linkedin', 'social_tiktok', 'social_pinterest',
            
            # SEO
            'default_meta_title', 'default_meta_description', 'default_meta_keywords', 
            'default_og_image',
            
            # Analytics
            'google_analytics_id', 'google_tag_manager_id', 'google_site_verification',
            'facebook_pixel_id',
            
            # Cookie & Privacy
            'cookie_policy_popup', 'cookie_popup_text', 'privacy_policy_page', 'terms_page',
            
            # About
            'about_short',
            
            # System
            'maintenance_mode', 'maintenance_message', 'show_language_selector',
            'default_language',
            
            # Additional fields
            'created_at', 'updated_at'
        )
        read_only_fields = ['created_at', 'updated_at']

class SEOSerializer(TranslationMixin, serializers.ModelSerializer):
    """Serializer for SEO data"""
    class Meta:
        model = SEO
        fields = (
            'meta_title', 'meta_description', 'meta_keywords', 
            'og_title', 'og_description', 'og_image', 
            'no_index', 'no_follow', 'canonical_url', 'structured_data'
        )

class SEOByPageTypeSerializer(serializers.Serializer):
    """Serializer for retrieving SEO data by page type"""
    page_type = serializers.CharField(required=True)
    page_slug = serializers.SlugField(required=False, allow_null=True) 