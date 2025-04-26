from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline, TranslationTabularInline
from .models import (
    Hero,
    Location,
    TransportOptionSection,
    TransportOption,
    VisaSection
)
# Register your models here.
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


@admin.register(Hero)
class HeroAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')

    fieldsets = (
        (None, {
            'fields': ('title', 'description'),
        }),
    )

    def has_add_permission(self, request):
        return not Hero.objects.exists()


@admin.register(Location)
class LocationAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'map_iframe'),
        }),
    )
    

    def has_add_permission(self, request):
        return not Location.objects.exists()


class TransportOptionInline(TranslationStackedInline, TranslationMedia):
    model = TransportOption
    extra = 0


@admin.register(TransportOptionSection)
class TransportOptionSectionAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    inlines = [TransportOptionInline, ]
    fieldsets = (
        (None, {
            'fields': ('title', 'description'),
        }),
    )

    def has_add_permission(self, request):
        return not TransportOptionSection.objects.exists()


@admin.register(VisaSection)
class VisaSectionAdmin(TranslationAdmin, TranslationMedia):
    def has_add_permission(self, request):
        return not VisaSection.objects.exists()
