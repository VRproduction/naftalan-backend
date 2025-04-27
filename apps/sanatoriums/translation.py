from modeltranslation.translator import translator, TranslationOptions
from .models import (
    Location, Sanatorium, Facility, RoomType, Review, 
    NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage,
    Season, TreatmentOption, AgeGroup
)

class LocationTranslationOptions(TranslationOptions):
    fields = ('region', 'country')

class SanatoriumTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description', 'treatments', 'address', 'meta_title', 'meta_description', 'meta_keywords')

class FacilityTranslationOptions(TranslationOptions):
    fields = ('name',)

class RoomTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class ReviewTranslationOptions(TranslationOptions):
    fields = ('full_name', 'content',)

class NaftalanSanatoriumsPageTranslationOptions(TranslationOptions):
    fields = ('hero_section_title', 'hero_section_description', 'main_section_title', 'main_section_description', 'sanatoriums_section_title', 'sanatoriums_section_description', 'contact_section_title', 'contact_section_description',)

class OtherCitiesSanatoriumsPageTranslationOptions(TranslationOptions):
    fields = ('hero_section_title', 'hero_section_description', 'main_section_title', 'main_section_description', 'sanatoriums_section_title', 'sanatoriums_section_description', 'contact_section_title', 'contact_section_description',)


class SeasonTranslationOptions(TranslationOptions):
    fields = ('name',)

class TreatmentOptionTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class AgeGroupTranslationOptions(TranslationOptions):
    fields = ('name',)

# Register models for translation
translator.register(Location, LocationTranslationOptions)
translator.register(Sanatorium, SanatoriumTranslationOptions)
translator.register(Facility, FacilityTranslationOptions)
translator.register(RoomType, RoomTypeTranslationOptions)
translator.register(Review, ReviewTranslationOptions)
translator.register(NaftalanSanatoriumsPage, NaftalanSanatoriumsPageTranslationOptions)
translator.register(OtherCitiesSanatoriumsPage, OtherCitiesSanatoriumsPageTranslationOptions)
translator.register(Season, SeasonTranslationOptions)
translator.register(TreatmentOption, TreatmentOptionTranslationOptions)
translator.register(AgeGroup, AgeGroupTranslationOptions)
# from modeltranslation.translator import register, TranslationOptions
# from .models import (Currency
# )

# @register(Currency)
# class CurrencyTranslationOptions(TranslationOptions):
#     fields = ('name',)