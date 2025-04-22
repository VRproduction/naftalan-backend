from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline, TranslationStackedInline
from .models import (
    Location, Sanatorium, SanatoriumImage, 
    Facility, SanatoriumFacility,
    RoomType, RoomImage, Review
)

import nested_admin

# Common Media class for all TranslationAdmin
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

        


# Inline admin classes
class SanatoriumImageInline(nested_admin.NestedTabularInline):
    model = SanatoriumImage
    extra = 1
    fields = ('image', 'is_main', 'priority')
    verbose_name = "Şəkil"
    verbose_name_plural = "Şəkillər"

class SanatoriumFacilityInline(nested_admin.NestedTabularInline):
    model = SanatoriumFacility
    extra = 1
    verbose_name = "Xidmət"
    verbose_name_plural = "Xidmətlər"

class ReviewInline(nested_admin.NestedStackedInline,  TranslationStackedInline,  TranslationMedia):
    model = Review
    extra = 1
    verbose_name = "Rəy"
    verbose_name_plural = "Müştəri rəyləri"


class RoomImageInline(nested_admin.NestedTabularInline):
    model = RoomImage
    extra = 1
    fields = ('image', 'priority')
    verbose_name = "Otaq şəkli"
    verbose_name_plural = "Otaq şəkilləri"


class RoomTypeInline(nested_admin.NestedStackedInline, TranslationStackedInline,  TranslationMedia):
    model = RoomType
    extra = 0
    inlines = [RoomImageInline]
    verbose_name = "Otaq növü"
    verbose_name_plural = "Otaq növləri"

# Admin classes with translation
@admin.register(Location)
class LocationAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('region', 'country')
    search_fields = ('region', 'country')
    list_filter = ('country',)
    
    fieldsets = (
        (None, {
            'fields': ('region', 'country'),
        }),
    )

@admin.register(Sanatorium)
class SanatoriumAdmin(nested_admin.NestedModelAdmin, TranslationAdmin, TranslationMedia):
    list_display = ('name', 'location', 'rating', 'price', 'is_active')
    list_filter = ('is_active', 'location', 'rating')
    search_fields = ('name', 'description', 'address')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        SanatoriumImageInline, 
        SanatoriumFacilityInline,
        RoomTypeInline,
        ReviewInline
    ]
    
    fieldsets = (
        ('Əsas məlumatlar', {
            'fields': ('name', 'slug', 'location', 'location_type', 'short_description', 'is_active', 'in_home'),
        }),
        ('Təsvir', {
            'fields': ('description', 'treatments'),
        }),
        ('Qiymət və Reytinq', {
            'fields': ('price', 'rating'),
        }),
        ('Ünvan məlumatları', {
            'fields': ('address', 'map_iframe'),
        }),
    )

@admin.register(Facility)
class FacilityAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name', 'icon')
    search_fields = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'icon'),
        }),
    )

