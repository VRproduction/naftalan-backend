from modeltranslation.translator import register, TranslationOptions
from .models import Package, PackageInclusion

@register(Package)
class PackageTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('az',)

@register(PackageInclusion)
class PackageInclusionTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('az',)
