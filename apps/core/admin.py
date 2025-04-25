from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline, TranslationTabularInline

from .models import Currency

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