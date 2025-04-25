from modeltranslation.translator import translator, TranslationOptions
from .models import Booking, GuestDetail, ExtraBedBooking, BookingNote

class BookingTranslationOptions(TranslationOptions):
    fields = ('special_requests',)

class GuestDetailTranslationOptions(TranslationOptions):
    fields = ()  # No fields to translate here

class ExtraBedBookingTranslationOptions(TranslationOptions):
    fields = ()  # No fields to translate here

class BookingNoteTranslationOptions(TranslationOptions):
    fields = ('note',)

# Register models for translation
translator.register(Booking, BookingTranslationOptions)
translator.register(GuestDetail, GuestDetailTranslationOptions)
translator.register(ExtraBedBooking, ExtraBedBookingTranslationOptions)
translator.register(BookingNote, BookingNoteTranslationOptions) 