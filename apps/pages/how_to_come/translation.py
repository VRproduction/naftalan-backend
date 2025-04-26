from modeltranslation.translator import TranslationOptions,register
from .models import (
    Hero,
    Location,
    TransportOptionSection,
    TransportOption,
    VisaSection
)

@register(Hero)
class HeroTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Location)
class LocationTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(TransportOptionSection)
class TransportOptionSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(TransportOption)
class TransportOptionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(VisaSection)
class VisaSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'content')
