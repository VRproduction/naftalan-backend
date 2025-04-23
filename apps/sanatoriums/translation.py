from modeltranslation.translator import translator, TranslationOptions
from .models import Location, Sanatorium, Facility, RoomType, Review, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage

class LocationTranslationOptions(TranslationOptions):
    fields = ('region', 'country')

class SanatoriumTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description', 'treatments', 'address')

class FacilityTranslationOptions(TranslationOptions):
    fields = ('name',)

class RoomTypeTranslationOptions(TranslationOptions):
    fields = ('name',)

class ReviewTranslationOptions(TranslationOptions):
    fields = ('full_name', 'content',)

class NaftalanSanatoriumsPageTranslationOptions(TranslationOptions):
    fields = ('hero_section_title', 'hero_section_description', 'main_section_title', 'main_section_description', 'sanatoriums_section_title', 'sanatoriums_section_description', 'contact_section_title', 'contact_section_description',)

class OtherCitiesSanatoriumsPageTranslationOptions(TranslationOptions):
    fields = ('hero_section_title', 'hero_section_description', 'main_section_title', 'main_section_description', 'sanatoriums_section_title', 'sanatoriums_section_description', 'contact_section_title', 'contact_section_description',)

# Register models for translation
translator.register(Location, LocationTranslationOptions)
translator.register(Sanatorium, SanatoriumTranslationOptions)
translator.register(Facility, FacilityTranslationOptions)
translator.register(RoomType, RoomTypeTranslationOptions)
translator.register(Review, ReviewTranslationOptions)
translator.register(NaftalanSanatoriumsPage, NaftalanSanatoriumsPageTranslationOptions)
translator.register(OtherCitiesSanatoriumsPage, OtherCitiesSanatoriumsPageTranslationOptions)
