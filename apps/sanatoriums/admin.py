from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline, TranslationStackedInline
from .models import (
    Location, Sanatorium, SanatoriumImage, 
    Facility, SanatoriumFacility,
    RoomType, RoomImage, Review
)

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
class SanatoriumImageInline(admin.TabularInline):
    model = SanatoriumImage
    extra = 1
    fields = ('image', 'is_main', 'priority')
    verbose_name = "Şəkil"
    verbose_name_plural = "Şəkillər"

class SanatoriumFacilityInline(admin.TabularInline):
    model = SanatoriumFacility
    extra = 1
    verbose_name = "Xidmət"
    verbose_name_plural = "Xidmətlər"

class RoomTypeInline(TranslationStackedInline, TranslationMedia):
    model = RoomType
    extra = 0
    verbose_name = "Otaq növü"
    verbose_name_plural = "Otaq növləri"

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ('image', 'priority')
    verbose_name = "Otaq şəkli"
    verbose_name_plural = "Otaq şəkilləri"


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
class SanatoriumAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name', 'location', 'rating', 'price', 'is_active')
    list_filter = ('is_active', 'location', 'rating')
    search_fields = ('name', 'description', 'address')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        SanatoriumImageInline, 
        SanatoriumFacilityInline,
        RoomTypeInline,
    ]
    
    fieldsets = (
        ('Əsas məlumatlar', {
            'fields': ('name', 'slug', 'location', 'location_type', 'short_description', 'is_active'),
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

@admin.register(RoomType)
class RoomTypeAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name', 'sanatorium')
    list_filter = ('sanatorium',)
    search_fields = ('name', 'sanatorium__name')
    inlines = [RoomImageInline]
    
    fieldsets = (
        (None, {
            'fields': ('sanatorium', 'name'),
        }),
    )

@admin.register(Review)
class ReviewAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('sanatorium', 'user', 'rating', 'date', 'is_published')
    list_filter = ('rating', 'is_published', 'date')
    search_fields = ('sanatorium__name', 'user__username', 'content')
    
    fieldsets = (
        ('Rəy məlumatları', {
            'fields': ('sanatorium', 'user', 'rating', 'content', 'is_published'),
        }),
    )

# Regular admin classes
@admin.register(SanatoriumImage)
class SanatoriumImageAdmin(admin.ModelAdmin):
    list_display = ('sanatorium', 'is_main', 'priority')
    list_filter = ('is_main', 'sanatorium')
    search_fields = ('sanatorium__name',)
    
    fieldsets = (
        (None, {
            'fields': ('sanatorium', 'image', 'is_main', 'priority'),
        }),
    )

@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'priority')
    list_filter = ('room_type__sanatorium',)
    search_fields = ('room_type__name',)
    
    fieldsets = (
        (None, {
            'fields': ('room_type', 'image', 'priority'),
        }),
    )

# Register the remaining models
admin.site.register(SanatoriumFacility)
