from modeltranslation.translator import register, TranslationOptions
from .models import (Currency, SiteSettings, SEO, WorkingHours
)

@register(Currency)
class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = (
        'site_name', 
        'site_tagline', 
        'site_description',
        'address', 
        'working_hours',
        'company_name',
        'footer_text',
        'copyright_text',
        'default_meta_title', 
        'default_meta_description',
        'default_meta_keywords',
        'cookie_popup_text',
        'about_short',
        'maintenance_message'
    )

@register(SEO)
class SEOTranslationOptions(TranslationOptions):
    fields = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description')

@register(WorkingHours)
class WorkingHoursTranslationOptions(TranslationOptions):
    fields = ('note',)