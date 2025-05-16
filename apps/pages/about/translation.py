from modeltranslation.translator import TranslationOptions,register
from .models import About, History, TimelinePunkt, ModernPunkt, TreatmentPage, Treatment, TreatmentBenefit, TreatmentProcess, TreatmentCategory, Indication, Contraindications


@register(About)
class AboutTranslationOptions(TranslationOptions):
    fields = ('banner_title', 'banner_description', 'content', 'reservation_title', 'reservation_description')


@register(History)
class HistoryTranslationOptions(TranslationOptions):
    fields = ('hero_section_title', 'hero_section_content', 'hero_section_image', 'introduction_title', 'introduction_content', 'timeline_section_title', 'timeline_section_description', 'scientific_section_title', 'scientific_section_content', 'scientific_section_image', 'soviet_section_title', 'soviet_section_content', 'soviet_section_image', 'modern_section_title', 'modern_section_description')


@register(TimelinePunkt)
class TimelinePunktTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(ModernPunkt)
class ModernPunktTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(TreatmentPage)
class TreatmentPageTranslationOptions(TranslationOptions):
    fields = ('hero_title', 'hero_description', 'main_title', 'main_content', 'category_section_title', 'category_section_description', 'process_section_title', 'process_section_description', 'contact_section_title', 'contact_section_description')


@register(TreatmentCategory)
class TreatmentCategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Treatment)
class TreatmentTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(TreatmentBenefit)
class TreatmentBenefitTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(TreatmentProcess)
class TreatmentProcessTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(Indication)
class IndicationTranslationOptions(TranslationOptions):
    fields = ('content',)


@register(Contraindications)
class ContraindicationsTranslationOptions(TranslationOptions):
    fields = ('content',)