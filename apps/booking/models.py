from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.sanatoriums.models import Sanatorium, RoomType, Season, TreatmentOption, Currency

# Status choices for bookings
class BookingStatus(models.TextChoices):
    PENDING = 'pending', _('Gözləmədə')
    CONFIRMED = 'confirmed', _('Təsdiqlənib')
    CANCELLED = 'cancelled', _('Ləğv edilib')
    COMPLETED = 'completed', _('Tamamlanıb')

class Booking(models.Model):
    # Personal Information
    first_name = models.CharField(_("Ad"), max_length=100)
    last_name = models.CharField(_("Soyad"), max_length=100)
    email = models.EmailField(_("E-poçt"))
    phone = models.CharField(_("Telefon"), max_length=20)
    
    # Booking Details
    booking_reference = models.CharField(_("Rezervasiya nömrəsi"), max_length=10, unique=True)
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.PROTECT, related_name='bookings', verbose_name=_("Sanatorium"))
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name='bookings', verbose_name=_("Otaq növü"))
    season = models.ForeignKey(Season, on_delete=models.PROTECT, related_name='bookings', verbose_name=_("Mövsüm"), null=True, blank=True)
    check_in_date = models.DateField(_("Giriş tarixi"))
    check_out_date = models.DateField(_("Çıxış tarixi"))
    adults = models.PositiveSmallIntegerField(_("Böyük sayı"), validators=[MinValueValidator(1)])
    children = models.PositiveSmallIntegerField(_("Uşaq sayı"), default=0)
    
    # Special requests
    special_requests = models.TextField(_("Xüsusi istəklər"), blank=True)
    
    # Treatment options
    with_treatment = models.BooleanField(_("Müalicə ilə"), default=True)
    treatment_option = models.ForeignKey(TreatmentOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name=_("Müalicə növü"))

    # Booking status
    status = models.CharField(_("Status"), max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    
    # Price information 
    total_price = models.DecimalField(_("Ümumi məbləğ"), max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='bookings', verbose_name=_("Valyuta"))

    # Meta information
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yenilənmə tarixi"), auto_now=True)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.first_name} {self.last_name}"
    
    def days_of_stay(self):
        return (self.check_out_date - self.check_in_date).days
    
    class Meta:
        verbose_name = _("Rezervasiya")
        verbose_name_plural = _("Rezervasiyalar")
        ordering = ['-created_at']


class GuestDetail(models.Model):
    GENDER_CHOICES = (
        ('male', _('Kişi')),
        ('female', _('Qadın')),
    )
    
    AGE_CATEGORY_CHOICES = (
        ('adult', _('Böyük')),
        ('child', _('Uşaq')),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='guests', verbose_name=_("Rezervasiya"))
    first_name = models.CharField(_("Ad"), max_length=100)
    last_name = models.CharField(_("Soyad"), max_length=100)
    gender = models.CharField(_("Cinsiyyət"), max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(_("Doğum tarixi"))
    age_category = models.CharField(_("Yaş kateqoriyası"), max_length=10, choices=AGE_CATEGORY_CHOICES)
    is_main_guest = models.BooleanField(_("Əsas qonaq"), default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = _("Qonaq təfərrüatı")
        verbose_name_plural = _("Qonaq təfərrüatları")


class ExtraBedBooking(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='extra_beds', verbose_name=_("Rezervasiya"))
    quantity = models.PositiveSmallIntegerField(_("Miqdar"), default=1)
    for_adult = models.BooleanField(_("Böyük üçün"), default=False)
    with_treatment = models.BooleanField(_("Müalicə ilə"), default=False)
    treatment_option = models.ForeignKey(TreatmentOption, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Müalicə növü"))
    price_per_night = models.DecimalField(_("Gecə başına qiymət"), max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Extra bed for {self.booking.booking_reference}"
    
    class Meta:
        verbose_name = _("Əlavə çarpayı rezervasiyası")
        verbose_name_plural = _("Əlavə çarpayı rezervasiyaları")


class BookingNote(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notes', verbose_name=_("Rezervasiya"))
    note = models.TextField(_("Qeyd"))
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    
    def __str__(self):
        return f"Note for {self.booking.booking_reference}"
    
    class Meta:
        verbose_name = _("Rezervasiya qeydi")
        verbose_name_plural = _("Rezervasiya qeydləri")
        ordering = ['-created_at']
