from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import Package, PackageInclusion, PackageOrder

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

class PackageInclusionInline(TranslationMedia, TranslationTabularInline):
    model = PackageInclusion
    extra = 0

@admin.register(Package)
class PackageAdmin(TranslationMedia, TranslationAdmin):
    list_display = ('name', 'sanatorium', 'duration', 'original_price', 'discounted_price', 'currency', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured', 'sanatorium', 'currency')
    search_fields = ('name', 'sanatorium__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PackageInclusionInline, ]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sanatorium', 'duration', 'occupancy')
        }),
        ('Qiymət və Endirim', {
            'fields': ('original_price', 'currency', 'discount_type', 'discount_value')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'in_home')
        }),
        ('Tarix', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PackageOrder)
class PackageOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'package', 'check_in', 'check_out', 'status', 'total_price', 'currency', 'created_at')
    list_filter = ('status', 'package', 'currency', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'package__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_editable = ('status',)
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('package', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Tarixlər', {
            'fields': ('check_in', 'check_out')
        }),
        ('Nəfər Sayı', {
            'fields': ('adults', 'children')
        }),
        ('Qiymət və Status', {
            'fields': ('total_price', 'currency', 'status')
        }),
        ('Əlavə Məlumat', {
            'fields': ('notes',)
        }),
        ('Tarix', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

