from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline, TranslationTabularInline
from .models import (
    Location, Sanatorium, SanatoriumImage, 
    Facility, SanatoriumFacility,
    RoomType, RoomImage, Review, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage,
    Season, RoomPrice, AgeGroup, ExtraBedPrice, TreatmentOption
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


class RoomPriceInline(nested_admin.NestedTabularInline):
    model = RoomPrice
    extra = 1
    verbose_name = "Qiymət"
    verbose_name_plural = "Qiymətlər"


class ExtraBedPriceInline(nested_admin.NestedTabularInline):
    model = ExtraBedPrice
    extra = 1
    verbose_name = "Əlavə çarpayı qiyməti"
    verbose_name_plural = "Əlavə çarpayı qiymətləri"


class RoomTypeInline(nested_admin.NestedStackedInline, TranslationStackedInline, TranslationMedia):
    model = RoomType
    extra = 0
    inlines = [RoomImageInline, RoomPriceInline, ExtraBedPriceInline]
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


@admin.register(Season)
class SeasonAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'start_date', 'end_date'),
        }),
    )


@admin.register(TreatmentOption)
class TreatmentOptionAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name',)
    search_fields = ('name', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
        }),
    )


@admin.register(AgeGroup)
class AgeGroupAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name', 'min_age', 'max_age')
    search_fields = ('name',)
    list_filter = ('min_age', 'max_age')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'min_age', 'max_age'),
        }),
    )


@admin.register(Sanatorium)
class SanatoriumAdmin(nested_admin.NestedModelAdmin, TranslationAdmin, TranslationMedia):
    list_display = ('name', 'location', 'rating', 'is_active')
    list_filter = ('is_active', 'location', 'rating', 'location_type')
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
        ('Reytinq', {
            'fields': ('rating',),
        }),
        ('Ünvan məlumatları', {
            'fields': ('address', 'map_iframe'),
        }),
    )


@admin.register(RoomType)
class RoomTypeAdmin(nested_admin.NestedModelAdmin, TranslationAdmin, TranslationMedia):
    list_display = ('name', 'sanatorium', 'min_capacity', 'max_capacity')
    list_filter = ('sanatorium', 'min_capacity', 'max_capacity')
    search_fields = ('name', 'description')
    inlines = [RoomImageInline, RoomPriceInline, ExtraBedPriceInline]
    
    fieldsets = (
        ('Əsas məlumatlar', {
            'fields': ('sanatorium', 'name', 'description'),
        }),
        ('Tutum məlumatları', {
            'fields': ('min_capacity', 'max_capacity', 'max_extra_beds', 'size'),
        }),
    )


@admin.register(RoomPrice)
class RoomPriceAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'season', 'occupancy', 'with_treatment', 'price', 'currency')
    list_filter = ('room_type__sanatorium', 'season', 'occupancy', 'with_treatment', 'currency')
    search_fields = ('room_type__name', 'room_type__sanatorium__name')


@admin.register(ExtraBedPrice)
class ExtraBedPriceAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'season', 'age_group', 'with_treatment', 'price', 'currency')
    list_filter = ('room_type__sanatorium', 'season', 'age_group', 'with_treatment', 'currency')
    search_fields = ('room_type__name', 'room_type__sanatorium__name', 'age_group__name')


@admin.register(Facility)
class FacilityAdmin(TranslationAdmin, TranslationMedia):
    list_display = ('name', 'icon')
    search_fields = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'icon'),
        }),
    )

@admin.register(NaftalanSanatoriumsPage)
class NaftalanSanatoriumsPageAdmin(TranslationAdmin, TranslationMedia):
    fieldsets = (
        ('Giriş', {
            'fields': ('hero_section_title', 'hero_section_description'),
        }),
        ('Əsas məlumatlar', {
            'fields': ('main_section_title', 'main_section_description', 'main_section_image'),
        }),
        ('Sanatoriumlar', {
            'fields': ('sanatoriums_section_title', 'sanatoriums_section_description'),
        }),
        ('Əlaqə', {
            'fields': ('contact_section_title', 'contact_section_description'),
        }),
    )

    def has_add_permission(self, request):
        return not NaftalanSanatoriumsPage.objects.exists()


@admin.register(OtherCitiesSanatoriumsPage)
class OtherCitiesSanatoriumsPageAdmin(TranslationAdmin, TranslationMedia):
    fieldsets = (
        ('Giriş', {
            'fields': ('hero_section_title', 'hero_section_description'),
        }),
        ('Əsas məlumatlar', {
            'fields': ('main_section_title', 'main_section_description', 'main_section_image'),
        }),
        ('Sanatoriumlar', {
            'fields': ('sanatoriums_section_title', 'sanatoriums_section_description'),
        }),
        ('Əlaqə', {
            'fields': ('contact_section_title', 'contact_section_description'),
        }),
    )

    def has_add_permission(self, request):
        return not OtherCitiesSanatoriumsPage.objects.exists()