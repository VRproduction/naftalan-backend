from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Booking, GuestDetail, ExtraBedBooking, BookingNote, BookingStatus
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
    extra = 0
    fields = ('first_name', 'last_name', 'gender', 'date_of_birth', 'age_category', 'is_main_guest')
    verbose_name = "Qonaq məlumatları"
    verbose_name_plural = "Qonaqlar"

class ExtraBedBookingInline(nested_admin.NestedTabularInline):
    model = ExtraBedBooking
    extra = 0
    fields = ('extra_bed_price', 'quantity', 'for_adult', 'with_treatment', 'treatment_option', 'price_per_night',)
    verbose_name = "Əlavə çarpayı"
    verbose_name_plural = "Əlavə çarpayılar"

class BookingNoteInline(nested_admin.NestedStackedInline):
    model = BookingNote
    extra = 1
    fields = ('note', 'created_by')
    readonly_fields = ('created_at', 'created_by')
    verbose_name = "Qeyd"
    verbose_name_plural = "Qeydlər"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Booking)
class BookingAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'booking_reference',
        'display_status',
        'first_name',
        'last_name',
        'sanatorium',
        'room_type',
        'created_at',
        'check_in_date',
        'check_out_date',
        'total_days',
        'total_price',
        'currency',
        'status_changed_at'
    )
    list_filter = ('status', 'sanatorium', 'room_type', 'check_in_date', 'with_treatment', 'season')
    search_fields = ('booking_reference', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at', 'status_changed_at', 'total_days')
    date_hierarchy = 'check_in_date'
    
    inlines = [
        GuestDetailInline,
        ExtraBedBookingInline,
        BookingNoteInline
    ]
    
    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_as_waiting_payment', 'mark_as_completed']
    
    @admin.display(description='Status', ordering='status')
    def display_status(self, obj):
        color = {
            'new': '#4285F4',  # blue
            'confirmed': '#34A853',  # green
            'cancelled': '#EA4335',  # red
            'completed': '#9C27B0',  # purple
            'waiting_payment': '#FBBC05',  # yellow
        }.get(obj.status, '#9E9E9E')  # gray default
        
        text_color = '#FFFFFF'  # white for most
        if obj.status == 'waiting_payment':
            text_color = '#000000'  # black for yellow background
            
        return format_html(
            '<span style="padding:4px 8px; background-color:{}; color:{}; border-radius:5px;">{}</span>',
            color,
            text_color,
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )
    
    @admin.display(description='Gecə sayı')
    def total_days(self, obj):
        if obj.check_in_date and obj.check_out_date:
            return (obj.check_out_date - obj.check_in_date).days
        return None

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        
        for instance in instances:
            if isinstance(instance, BookingNote) and not instance.created_by:
                instance.created_by = request.user
            instance.save()
            
        formset.save_m2m()
    
    def add_status_note(self, request, queryset, new_status, note_template):
        User = get_user_model()
        current_user = request.user if isinstance(request.user, User) else None
        
        for booking in queryset:
            booking.status = new_status
            booking.status_changed_at = timezone.now()
            booking.save()
            
            # Add a note
            BookingNote.objects.create(
                booking=booking,
                note=note_template.format(
                    status=dict(BookingStatus.choices)[new_status],
                    user=current_user.get_full_name() if current_user else "Admin"
                ),
                created_by=current_user
            )
    
    @admin.action(description=_("Təsdiqlənmiş kimi qeyd edin"))
    def mark_as_confirmed(self, request, queryset):
        self.add_status_note(
            request, queryset, 
            BookingStatus.CONFIRMED, 
            _("Rezervasiya statusu '{status}' olaraq dəyişdirildi. ({user} tərəfindən)")
        )
        self.message_user(request, _("Seçilmiş rezervasiyalar təsdiqləndi"))
    
    @admin.action(description=_("Ödəniş gözləyir kimi qeyd edin"))
    def mark_as_waiting_payment(self, request, queryset):
        self.add_status_note(
            request, queryset, 
            BookingStatus.WAITING_PAYMENT, 
            _("Rezervasiya statusu '{status}' olaraq dəyişdirildi. ({user} tərəfindən)")
        )
        self.message_user(request, _("Seçilmiş rezervasiyalar 'Ödəniş gözlənilir' kimi işarələndi"))
    
    @admin.action(description=_("Ləğv edilmiş kimi qeyd edin"))
    def mark_as_cancelled(self, request, queryset):
        self.add_status_note(
            request, queryset, 
            BookingStatus.CANCELLED, 
            _("Rezervasiya statusu '{status}' olaraq dəyişdirildi. ({user} tərəfindən)")
        )
        self.message_user(request, _("Seçilmiş rezervasiyalar ləğv edildi"))
        
    @admin.action(description=_("Tamamlanmış kimi qeyd edin"))
    def mark_as_completed(self, request, queryset):
        self.add_status_note(
            request, queryset, 
            BookingStatus.COMPLETED, 
            _("Rezervasiya statusu '{status}' olaraq dəyişdirildi. ({user} tərəfindən)")
        )
        self.message_user(request, _("Seçilmiş rezervasiyalar 'Tamamlandı' kimi işarələndi"))
    
    fieldsets = (
        ('Qiymət və Status', {
            'fields': (
                'price',
                'discounted_price',
                'discount_type',
                'discount_value',
                'total_discounted_price',
                'total_price',
                'currency',
                'status',
                'status_note',
                'status_changed_at',
                'total_days'            )
        }),
        ('Şəxsi məlumatlar', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Rezervasiya məlumatları', {
            'fields': (
                'booking_reference',
                'sanatorium',
                'room_type',
                'season',
                'check_in_date',
                'check_out_date',
                'adults',
                'children'
            )
        }),
        ('Müalicə məlumatları', {
            'fields': ('with_treatment', 'treatment_option')
        }),
        ('Xüsusi istəklər', {
            'fields': ('special_requests',),
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

