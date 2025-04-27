from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline, TranslationTabularInline
from django.utils.translation import gettext_lazy as _

from .models import Currency, SiteSettings, SEO, PageType, WorkingHours, DayOfWeek

class TranslationMedia:
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Currency)
class CurrencyAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'symbol'),
        }),
    )

class WorkingHoursInline(TranslationTabularInline):
    model = WorkingHours
    extra = 0
    fields = ('day', 'is_working_day', 'opening_time', 'closing_time', 'lunch_start', 'lunch_end', 'note', 'order')
    ordering = ('order', 'day')

@admin.register(WorkingHours)
class WorkingHoursAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('day', 'get_site_name', 'is_working_day', 'display_hours', 'order')
    list_filter = ('is_working_day', 'site_settings')
    search_fields = ('note',)
    list_editable = ('order', 'is_working_day')
    
    fieldsets = (
        (None, {
            'fields': ('site_settings', 'day', 'order'),
        }),
        (_('İş saatları'), {
            'fields': ('is_working_day', 'opening_time', 'closing_time'),
        }),
        (_('Nahar fasiləsi'), {
            'fields': ('lunch_start', 'lunch_end'),
            'classes': ('collapse',),
        }),
        (_('Əlavə məlumat'), {
            'fields': ('note',),
        }),
    )
    
    def get_site_name(self, obj):
        return obj.site_settings.site_name
    get_site_name.short_description = _('Sayt')
    get_site_name.admin_order_field = 'site_settings__site_name'
    
    def display_hours(self, obj):
        if not obj.is_working_day:
            return _('İstirahət günü')
        
        if obj.opening_time and obj.closing_time:
            return f"{obj.opening_time.strftime('%H:%M')} - {obj.closing_time.strftime('%H:%M')}"
        return "-"
    display_hours.short_description = _('Saatlar')

@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('site_name', 'contact_email', 'contact_phone', 'updated_at')
    inlines = [WorkingHoursInline]
    
    fieldsets = (
        (_('Əsas Məlumatlar'), {
            'fields': ('site_name', 'site_tagline', 'site_description'),
        }),
        (_('Əlaqə Məlumatları'), {
            'fields': (
                'contact_email', 'contact_email_secondary',
                'contact_phone', 'contact_phone_secondary',
                'whatsapp_number', 'telegram_username',
            ),
        }),
        (_('Yer Məlumatları'), {
            'fields': ('address', 'map_latitude', 'map_longitude', 'map_zoom'),
            'description': _('İş saatları üçün aşağıdakı "İş saatları" bölməsindən istifadə edin'),
        }),
        (_('Şirkət Məlumatları'), {
            'fields': ('company_name', 'tax_number', 'foundation_year'),
            'classes': ('collapse',),
        }),
        (_('Vizual Elementlər'), {
            'fields': ('logo', 'logo_dark', 'footer_logo', 'favicon', 'mobile_app_icon'),
        }),
        (_('Rəng və Dizayn'), {
            'fields': ('primary_color', 'secondary_color', 'accent_color'),
            'classes': ('collapse',),
        }),
        (_('Alt Bölmə'), {
            'fields': ('footer_text', 'copyright_text', 'show_social_in_footer'),
            'classes': ('collapse',),
        }),
        (_('Sosial Media'), {
            'fields': (
                'social_facebook', 'social_instagram', 'social_twitter', 
                'social_youtube', 'social_linkedin', 'social_tiktok', 'social_pinterest'
            ),
        }),
        (_('SEO'), {
            'fields': ('default_meta_title', 'default_meta_description', 'default_meta_keywords', 'default_og_image'),
        }),
        (_('Analitika və İzləmə'), {
            'fields': (
                'google_analytics_id', 'google_tag_manager_id', 
                'google_site_verification', 'facebook_pixel_id'
            ),
            'classes': ('collapse',),
        }),
        (_('reCAPTCHA'), {
            'fields': ('recaptcha_site_key', 'recaptcha_secret_key'),
            'classes': ('collapse',),
        }),
        (_('Cookie və Məxfilik'), {
            'fields': ('cookie_policy_popup', 'cookie_popup_text', 'privacy_policy_page', 'terms_page'),
            'classes': ('collapse',),
        }),
        (_('Haqqımızda Bölməsi'), {
            'fields': ('about_short',),
        }),
        (_('Əlavə Parametrlər'), {
            'fields': ('maintenance_mode', 'maintenance_message', 'show_language_selector', 'default_language'),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        # Allow only one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(SEO)
class SEOAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('get_page_display', 'meta_title', 'no_index', 'updated_at')
    list_filter = ('page_type', 'no_index', 'no_follow')
    search_fields = ('meta_title', 'meta_description', 'meta_keywords', 'page_slug')
    
    fieldsets = (
        (_('Səhifə Məlumatları'), {
            'fields': ('page_type', 'page_slug'),
        }),
        (_('Meta Məlumatlar'), {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
        }),
        (_('Open Graph'), {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',),
        }),
        (_('Əlavə SEO Seçimləri'), {
            'fields': ('no_index', 'no_follow', 'canonical_url', 'structured_data'),
            'classes': ('collapse',),
        }),
    )
    
    def get_page_display(self, obj):
        if obj.page_type == PageType.CUSTOM:
            return f"{obj.get_page_type_display()}: {obj.page_slug}"
        return obj.get_page_type_display()
    get_page_display.short_description = _('Səhifə')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['page_slug'].help_text = _('Yalnız "Fərdi səhifə" seçildikdə istifadə olunur')
        return form
    
    def save_model(self, request, obj, form, change):
        # If page type is not custom, clear the slug
        if obj.page_type != PageType.CUSTOM:
            obj.page_slug = None
        super().save_model(request, obj, form, change)