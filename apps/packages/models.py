from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from apps.sanatoriums.models import Sanatorium, RoomType, TreatmentOption, Season
from apps.core.models import Currency




class Package(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', _('Faiz')),
        ('fixed', _('Məbləğ')),
    ]

    name = models.CharField(_("Paket adı"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, null = True, blank = True)
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.CASCADE, related_name='packages', verbose_name=_("Sanatoriya"))
    
    # Package details
    duration = models.PositiveSmallIntegerField(_("Müddət (gün)"), default=7)
    discount_type = models.CharField(
        _("Endirim növü"),
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage'
    )
    discount_value = models.FloatField(
        _("Endirim dəyəri"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Faiz üçün 0-100 arası, məbləğ üçün 0 və ya daha böyük dəyər daxil edin")
    )
    is_active = models.BooleanField(_("Aktivdir"), default=True)
    is_featured = models.BooleanField(_("Seçilmiş"), default=False)

    # Price information
    original_price = models.FloatField(
        _("Orijinal qiymət"),
        validators=[MinValueValidator(0)],
        null = True
    )
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Valyuta"), null = True)
    occupancy = models.PositiveSmallIntegerField(_("Nəfər sayı"), default=2)

    in_home = models.BooleanField(default=True, verbose_name= _('Ana səhifədə görünsün?'))

    # Meta information
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yenilənmə tarixi"), auto_now=True)
    
    @property
    def discounted_price(self):
        if not self.original_price or not self.discount_value:
            return self.original_price

        if self.discount_type == 'percentage':
            if self.discount_value > 100:
                return self.original_price
            discount_amount = (self.original_price * self.discount_value) / 100
        else:  # fixed amount
            discount_amount = self.discount_value

        return max(0, self.original_price - discount_amount)

    def clean(self):
        super().clean()
        if self.discount_type == 'percentage' and self.discount_value > 100:
            raise ValidationError({
                'discount_value': _("Faiz 100-dən böyük ola bilməz")
            })
        
        if self.discounted_price > self.original_price:
            raise ValidationError({
                'discount_value': _("Endirimli qiymət orijinal qiymətdən böyük ola bilməz")
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        discount_info = ""
        if self.discount_value:
            if self.discount_type == 'percentage':
                discount_info = f" ({self.discount_value}% endirim)"
            else:
                discount_info = f" ({self.discount_value} {self.currency} endirim)"
        
        price_info = f"{self.discounted_price} {self.currency}"
        return f"{self.name} - {self.sanatorium.name} - {price_info}{discount_info}"
    
    class Meta:
        verbose_name = _("Paket")
        verbose_name_plural = _("Paketlər")
        ordering = ['-is_featured', '-created_at']


class PackageInclusion(models.Model):
    name = models.TextField(_("Təsvir"))
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='inclusions', verbose_name=_("Paket"))
    priority = models.PositiveIntegerField(_("Prioritet"), default=0)

    def __str__(self):
        return f"{self.name} - {self.package.name}"

    class Meta:
        verbose_name = _("Paketə daxil olan")
        verbose_name_plural = _("Paketə daxil olanlar")
        ordering = ['priority']
        unique_together = ['package', 'name']

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                PackageInclusion.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)


class PackageOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Gözləyir')),
        ('confirmed', _('Təsdiqlənib')),
        ('cancelled', _('Ləğv edilib')),
        ('completed', _('Tamamlanıb')),
    ]

    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name='orders', verbose_name=_("Paket"))
    first_name = models.CharField(_("Ad"), max_length=100)
    last_name = models.CharField(_("Soyad"), max_length=100)
    email = models.EmailField(_("E-poçt"))
    phone = models.CharField(_("Telefon"), max_length=20)
    check_in = models.DateField(_("Gəliş tarixi"))
    check_out = models.DateField(_("Gediş tarixi"))
    adults = models.PositiveSmallIntegerField(_("Böyüklər"), default=1)
    children = models.PositiveSmallIntegerField(_("Uşaqlar"), default=0)
    notes = models.TextField(_("Qeydlər"), blank=True, null=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_price = models.FloatField(_("Ümumi qiymət"))
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Valyuta"))
        
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yenilənmə tarixi"), auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.package.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Paket sifarişi")
        verbose_name_plural = _("Paket sifarişləri")
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.check_out <= self.check_in:
            raise ValidationError({
                'check_out': _("Gediş tarixi gəliş tarixindən sonra olmalıdır")
            })
        
        if self.adults + self.children > self.package.occupancy:
            raise ValidationError({
                'adults': _("Ümumi nəfər sayı paketin tutumundan çox ola bilməz"),
                'children': _("Ümumi nəfər sayı paketin tutumundan çox ola bilməz")
            })





