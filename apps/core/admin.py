from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline, TranslationTabularInline
from django.utils.translation import gettext_lazy as _

from .models import Currency, SiteSettings, SEO, PageType, WorkingHours, DayOfWeek, ContactEmail, ContactPhone

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
    ordering = ('code',)
    
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
    list_display = ('site_name', 'company_name', 'contact_email', 'contact_phone')
    inlines = [WorkingHoursInline]
    
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('site_name', 'site_tagline', 'site_description')
        }),
        ('Əlaqə Məlumatları', {
            'fields': ('whatsapp_number', 'telegram_username')
        }),
        ('Şirkət Məlumatları', {
            'fields': ('company_name', 'tax_number', 'foundation_year')
        }),
        ('Vizual Elementlər', {
            'fields': ('logo', 'logo_dark', 'footer_logo', 'favicon', 'mobile_app_icon')
        }),
        ('Rənglər', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Alt Mətn', {
            'fields': ('footer_text', 'copyright_text', 'copyright_link', 'show_social_in_footer')
        }),
        ('Sosial Media', {
            'fields': (
                'social_facebook', 'social_instagram', 'social_twitter',
                'social_youtube', 'social_linkedin', 'social_tiktok',
                'social_pinterest'
            )
        }),
        ('SEO', {
            'fields': (
                'default_meta_title', 'default_meta_description',
                'default_meta_keywords', 'default_og_image'
            )
        }),
        ("Ünvan", {
            'fields': (
                'address', 'map_latitude',
                'map_longitude', 'map_zoom',
                'map_src'
            )
        }),
        ('Analitika', {
            'fields': (
                'google_analytics_id', 'google_tag_manager_id',
                'google_site_verification', 'facebook_pixel_id'
            )
        }),
        ('reCAPTCHA', {
            'fields': ('recaptcha_site_key', 'recaptcha_secret_key')
        }),
        ('Cookie & Məxfilik', {
            'fields': (
                'cookie_policy_popup', 'cookie_popup_text',
                'privacy_policy_page', 'terms_page'
            )
        }),
        ('Haqqımızda', {
            'fields': ('about_short',)
        }),
        ('Sistem', {
            'fields': (
                'maintenance_mode', 'maintenance_message',
                'show_language_selector', 'default_language'
            )
        }),
        ('Tarix', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def contact_email(self, obj):
        primary_email = obj.contact_emails.filter(is_primary=True).first()
        return primary_email.email if primary_email else '-'
    contact_email.short_description = 'Əsas E-poçt'

    def contact_phone(self, obj):
        primary_phone = obj.contact_phones.filter(is_primary=True).first()
        return primary_phone.phone if primary_phone else '-'
    contact_phone.short_description = 'Əsas Telefon'

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

@admin.register(ContactEmail)
class ContactEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_primary', 'priority', 'created_at')
    list_filter = ('is_primary',)
    search_fields = ('email',)
    ordering = ('-is_primary', 'priority', '-created_at')
    list_editable = ('is_primary', 'priority')
    fieldsets = (
        (None, {
            'fields': ('email', 'is_primary', 'priority')
        }),
        ('Tarix', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.site_settings_id:
            obj.site_settings = SiteSettings.objects.first()
        super().save_model(request, obj, form, change)

@admin.register(ContactPhone)
class ContactPhoneAdmin(admin.ModelAdmin):
    list_display = ('phone', 'is_primary', 'priority', 'created_at')
    list_filter = ('is_primary',)
    search_fields = ('phone',)
    ordering = ('-is_primary', 'priority', '-created_at')
    list_editable = ('is_primary', 'priority')
    fieldsets = (
        (None, {
            'fields': ('phone', 'is_primary', 'priority')
        }),
        ('Tarix', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.site_settings_id:
            obj.site_settings = SiteSettings.objects.first()
        super().save_model(request, obj, form, change)