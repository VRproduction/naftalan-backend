from django.contrib import admin

from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from .models import (HeroSlider, AboutSection, AboutPunkt, SanatoriesSection,
                     TreatmentsSection, PackagesSection, CustomerCommentsSection,
                     CustomerComments, FAQ, FAQSection, BlogSection,
                     ContactSection)


admin.site.register(HeroSlider)


class AboutPunktInline(TranslationStackedInline):
    model = AboutPunkt
    extra = 0

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(AboutSection)
class AboutSectionAdmin(TranslationAdmin):
    inlines = [AboutPunktInline]

    def has_add_permission(self, request, obj=None):
        return not AboutSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(SanatoriesSection)
class SanatoriesSectionAdmin(TranslationAdmin):
    def has_add_permission(self, request, obj=None):
        return not SanatoriesSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(TreatmentsSection)
class TreatmentsSectionAdmin(TranslationAdmin):
    def has_add_permission(self, request, obj=None):
        return not TreatmentsSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(PackagesSection)
class PackagesSectionAdmin(TranslationAdmin):
    def has_add_permission(self, request, obj=None):
        return not PackagesSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(CustomerCommentsSection)
class CustomerCommentsSectionAdmin(TranslationAdmin):
    def has_add_permission(self, request, obj=None):
        return not CustomerCommentsSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(CustomerComments)
class CustomerCommentsAdmin(TranslationAdmin):
    list_display = ('full_name', 'address', 'rating', 'priority')

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(FAQSection)
class FAQSectionAdmin(TranslationAdmin):
    def has_add_permission(self, request, obj=None):
        return not FAQSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(FAQ)
class FAQAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(BlogSection)
class BlogSectionAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }
    
    def has_add_permission(self, request, obj=None):
        return not BlogSection.objects.exists()


@admin.register(ContactSection)
class ContactSectionAdmin(TranslationAdmin):

    fieldsets = (
        ('Sol bölum', {'fields': ('left_section_title', 'left_section_description')}),
        ('Sağ bölum', {'fields': ('right_section_title', 'right_section_description')}),
    )

    def has_add_permission(self, request, obj=None):
        return not ContactSection.objects.exists()

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }