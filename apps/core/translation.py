from modeltranslation.translator import register, TranslationOptions
from .models import (Currency
)

@register(Currency)
class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)