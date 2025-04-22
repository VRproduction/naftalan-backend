from modeltranslation.translator import TranslationOptions,register
from .models import (
    AboutSection,
    AboutPunkt,
    SanatoriesSection,
    TreatmentsSection,
    PackagesSection,
    CustomerCommentsSection,
    CustomerComments,
    FAQSection,
    FAQ,
    BlogSection,
    ContactSection
)


@register(AboutSection)
class AboutSectionTranslationOptions(TranslationOptions):
    fields = ('sub_title', 'title', 'section_description', 'content_title')


@register(AboutPunkt)
class AboutPunktTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(SanatoriesSection)
class SanatoriesSectionTranslationOptions(TranslationOptions):
    fields = ('sub_title', 'title', 'section_description')


@register(TreatmentsSection)
class TreatmentsSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'section_description')


@register(PackagesSection)
class PackagesSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'section_description')


@register(CustomerCommentsSection)
class CustomerCommentsSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'section_description')


@register(CustomerComments)
class CustomerCommentsTranslationOptions(TranslationOptions):
    fields = ('full_name', 'address', 'comment')


@register(FAQSection)
class FAQSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'section_description')


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(BlogSection)
class BlogSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'section_description')


@register(ContactSection)
class ContactSectionTranslationOptions(TranslationOptions):
    fields = ('left_section_title', 'left_section_description', 'right_section_title', 'right_section_description')
