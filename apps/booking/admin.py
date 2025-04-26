from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from .models import Booking, GuestDetail, ExtraBedBooking, BookingNote
import nested_admin

# Common Media class for admin panels
class TranslationMedia:
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }

# Inline admin classes
class GuestDetailInline(nested_admin.NestedTabularInline):
    model = GuestDetail
    extra = 1
    fields = ('first_name', 'last_name', 'gender', 'date_of_birth', 'age_category', 'is_main_guest')
    verbose_name = "Qonaq məlumatları"
    verbose_name_plural = "Qonaqlar"

class ExtraBedBookingInline(nested_admin.NestedTabularInline):
    model = ExtraBedBooking
    extra = 0
    fields = ('quantity', 'for_adult', 'with_treatment', 'treatment_option', 'price_per_night')
    verbose_name = "Əlavə çarpayı"
    verbose_name_plural = "Əlavə çarpayılar"

class BookingNoteInline(nested_admin.NestedStackedInline):
    model = BookingNote
    extra = 1
    fields = ('note',)
    verbose_name = "Qeyd"
    verbose_name_plural = "Qeydlər"

@admin.register(Booking)
class BookingAdmin(nested_admin.NestedModelAdmin):
    list_display = ('booking_reference', 'first_name', 'last_name', 'sanatorium', 'room_type', 
                   'check_in_date', 'check_out_date', 'status', 'total_price', 'currency')
    list_filter = ('status', 'sanatorium', 'room_type', 'check_in_date', 'with_treatment', 'season')
    search_fields = ('booking_reference', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')
    date_hierarchy = 'check_in_date'
    
    inlines = [
        GuestDetailInline,
        ExtraBedBookingInline,
        BookingNoteInline
    ]
    
    fieldsets = (
        ('Şəxsi məlumatlar', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Rezervasiya məlumatları', {
            'fields': ('booking_reference', 'sanatorium', 'room_type', 'season', 
                      'check_in_date', 'check_out_date', 'adults', 'children')
        }),
        ('Müalicə məlumatları', {
            'fields': ('with_treatment', 'treatment_option')
        }),
        ('Qiymət və Status', {
            'fields': ('total_price', 'currency', 'status')
        }),
        ('Xüsusi istəklər', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
        ('Meta məlumatlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Eğer yeni bir kayıtsa ve referans numarası yoksa, oluştur
        if not change and not obj.booking_reference:
            import random
            import string
            
            # Rastgele 10 karakterlik benzersiz bir referans oluştur
            chars = string.ascii_uppercase + string.digits
            reference = ''.join(random.choice(chars) for _ in range(10))
            
            while Booking.objects.filter(booking_reference=reference).exists():
                reference = ''.join(random.choice(chars) for _ in range(10))
            
            obj.booking_reference = reference
        
        # Eğer sezon belirtilmemişse, giriş tarihine göre belirle
        if not obj.season:
            from apps.sanatoriums.models import Season
            season = Season.objects.filter(
                start_date__lte=obj.check_in_date,
                end_date__gte=obj.check_in_date
            ).first()
            if season:
                obj.season = season
                
        super().save_model(request, obj, form, change)

