from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import Blog, BlogCategory, BlogTag


@admin.register(BlogCategory)
class BlogCategoryAdmin(TranslationAdmin):
    list_display = ('title',)

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }
        

@admin.register(BlogTag)
class BlogTagAdmin(TranslationAdmin):
    list_display = ('title',)

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Blog)
class BlogAdmin(TranslationAdmin):
    def image_display(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 100px; height: auto;" />')
        return "Şəkil yoxdur"
    image_display.short_description = 'Şəkil'
    
    def view_count_display(self, obj):
        return format_html('<span style="color: #{};">{}</span>',
                          '1E88E5' if obj.view_count > 100 else '4CAF50',
                          obj.view_count)
    view_count_display.short_description = 'Baxış sayı'
    
    def get_in_home(self, obj):
        if obj.in_home:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    get_in_home.short_description = 'Ana səhifədə'
    
    list_display = ('title', 'updated', 'image_display')
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('title', 'description', 'category', 'tags', 'short_description', 'image', 'image_display', 'in_home', 'is_popular', 'is_featured', 'date')
        }),
        ('SEO Məlumatları', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Əlavə SEO Parametrləri', {
            'fields': ('canonical_url', 'no_index', 'no_follow'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('image_display',)
    search_fields = ('title', 'short_description')
    filter_horizontal = ('tags',)
    
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }
    

class BlogCategoryAdmin(TranslationAdmin):
    list_display = ('title',)