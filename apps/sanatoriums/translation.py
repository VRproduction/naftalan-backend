from modeltranslation.translator import translator, TranslationOptions
from .models import Location, Sanatorium, Facility, RoomType, Review

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

# Register models for translation
translator.register(Location, LocationTranslationOptions)
translator.register(Sanatorium, SanatoriumTranslationOptions)
translator.register(Facility, FacilityTranslationOptions)
translator.register(RoomType, RoomTypeTranslationOptions)
translator.register(Review, ReviewTranslationOptions)
