from django.contrib import admin

from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from .models import About, History, TimelinePunkt, ModernPunkt, Treatment, TreatmentPage,TreatmentBenefit, TreatmentProcess, TreatmentCategory, Indication, Contraindications



@admin.register(About)
class AboutAdmin(TranslationAdmin):
    fieldsets = (
        ('Banner', {'fields': ('banner_image', 'banner_title', 'banner_description')}),
        ('Kontent', {'fields': ('content',)}),
        ('Rezervasiya', {'fields': ('reservation_image', 'reservation_title', 'reservation_description')})
    )

    def has_add_permission(self, request):
        return not About.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class TimelinePunktInline(TranslationStackedInline):
    model = TimelinePunkt
    extra = 1

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class ModernPunktInline(TranslationStackedInline):
    model = ModernPunkt
    extra = 1

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(History)
class HistoryAdmin(TranslationAdmin):
    inlines = [TimelinePunktInline, ModernPunktInline]
    fieldsets = (
        ('Hero', {'fields': ('hero_section_title', 'hero_section_content', 'hero_section_image')}),
        ('Giriş', {'fields': ('introduction_title', 'introduction_content')}),
        ('Xronologiya', {'fields': ('timeline_section_title', 'timeline_section_description')}),
        ('Elmi', {'fields': ('scientific_section_title', 'scientific_section_content', 'scientific_section_image')}),
        ('Sovet dövrü', {'fields': ('soviet_section_title', 'soviet_section_content', 'soviet_section_image')}),
        ('Müasir dövr', {'fields': ('modern_section_title', 'modern_section_description')})
    )

    def has_add_permission(self, request):
        return not History.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(TreatmentPage)
class TreatmentPageAdmin(TranslationAdmin):
    fieldsets = (
        ('Giriş', {'fields': ('hero_title', 'hero_description')}),
        ('Əsas', {'fields': ('main_title', 'main_content', 'main_image')}),
        ('Kategoriyalar', {'fields': ('category_section_title', 'category_section_description')}),
        ('Proses', {'fields': ('process_section_title', 'process_section_description')}),
        ('Kontakt', {'fields': ('contact_section_title', 'contact_section_description')})
    )

    def has_add_permission(self, request):
        return not TreatmentPage.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class TreatmentBenefitInline(TranslationStackedInline):
    model = TreatmentBenefit
    extra = 1

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Treatment)
class TreatmentAdmin(TranslationAdmin):
    inlines = [TreatmentBenefitInline, ]
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(TreatmentProcess)
class TreatmentProcessAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(TreatmentCategory)
class TreatmentCategoryAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Indication)
class IndicationAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }
    
    def has_add_permission(self, request):
        return not Indication.objects.exists()

@admin.register(Contraindications)
class ContraindicationsAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }
    
    def has_add_permission(self, request):
        return not Contraindications.objects.exists()
