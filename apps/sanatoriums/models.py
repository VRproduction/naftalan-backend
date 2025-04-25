from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import date

from ckeditor_uploader.fields import RichTextUploadingField

from apps.core.models import Currency

class Location(models.Model):
    region = models.CharField(_("Ad"), max_length=256)
    country = models.CharField(_("Ölkə"), max_length=256)
    
    def __str__(self):
        return f"{self.region}, {self.country}"
    
    class Meta:
        verbose_name = _("Şəhərlər")
        verbose_name_plural = _("Şəhərlər")


class Season(models.Model):
    name = models.CharField(_("Mövsüm adı"), max_length=100)
    start_date = models.DateField(_("Başlanğıc tarixi"))
    end_date = models.DateField(_("Bitmə tarixi"))
    
    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%d.%m')} - {self.end_date.strftime('%d.%m')})"
    
    class Meta:
        verbose_name = _("Mövsüm")
        verbose_name_plural = _("Mövsümlər")
        ordering = ['start_date']
        
    def is_current(self):
        today = date.today()
        return self.start_date <= today <= self.end_date


class Sanatorium(models.Model):
    LOCATION_TYPE_CHOICES = (
        ('naftalan', _('Naftalan')),
        ('other_cities', _('Digər şəhərlər')),
    )   
    name = models.CharField(_("Ad"), max_length=512)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)
    location_type = models.CharField(_("Yerləşmə növü"), max_length = 100, choices = LOCATION_TYPE_CHOICES, null = True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='sanatoriums', verbose_name=_("Yerləşmə"))
    description = RichTextUploadingField(verbose_name=_('Haqqında'))
    short_description = models.TextField(_("Qısa təsvir"), blank=True)
    treatments = RichTextUploadingField(verbose_name=_('Müalicə imkanları'))
    rating = models.DecimalField(_("Reytinq"), max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    address = models.CharField(_("Ünvan"), max_length=255)
    map_iframe = models.TextField(_("Xəritə iframe"))
    is_active = models.BooleanField(_("Aktivdir"), default=True)
    in_home = models.BooleanField(_("Ana səhifədə görünsün?"), default = False)
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yenilənmə tarixi"), auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-rating', 'name']
        verbose_name = _("Sanatoriya")
        verbose_name_plural = _("Sanatoriyalar")


class SanatoriumImage(models.Model):
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.CASCADE, related_name='images', verbose_name=_("Sanatoriya"))
    image = models.ImageField(_("Şəkil"), upload_to='sanatoriums/')
    is_main = models.BooleanField(_("Əsas şəkil"), default=False)
    priority = models.IntegerField(_("Prioritet"), default=1)
    
    def __str__(self):
        return f"Image for {self.sanatorium.name}"
    
    class Meta:
        ordering = ['priority']
        verbose_name = _("Sanatoriya Şəkli")
        verbose_name_plural = _("Sanatoriya Şəkilləri")

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                SanatoriumImage.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)


class Facility(models.Model):
    name = models.CharField(_("Ad"), max_length=100)
    icon = models.FileField(_("İkon"), upload_to="facility", blank=True, null = True, help_text=_("İkon adı (İnterfeys üçün)"))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = _("Xidmətlər və imkanlar")
        verbose_name = _("Xidmət")


class SanatoriumFacility(models.Model):
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.CASCADE, related_name='sanatoiruim', verbose_name=_("Sanatorium"))
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, verbose_name=_("Xidmət"))
    
    def __str__(self):
        return f"{self.facility.name} at {self.sanatorium.name}"
    
    class Meta:
        verbose_name_plural = _("Sanatorium Obyektləri")
        verbose_name = _("Sanatorium Obyekti")
        unique_together = ('sanatorium', 'facility')


class TreatmentOption(models.Model):
    name = models.CharField(_("Müalicə növü"), max_length=255)
    description = models.TextField(_("Təsvir"), blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Müalicə növü")
        verbose_name_plural = _("Müalicə növləri")


class RoomType(models.Model):
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.CASCADE, related_name='room_types', verbose_name=_("Sanatorium"))
    name = models.CharField(_("Ad"), max_length=255)
    description = models.TextField(_("Təsvir"), blank=True)
    min_capacity = models.PositiveSmallIntegerField(_("Minimum tutum"), null=True, blank=True)
    max_capacity = models.PositiveSmallIntegerField(_("Maksimum tutum"), null=True, blank=True)
    max_extra_beds = models.PositiveSmallIntegerField(_("Maksimum əlavə çarpayı"), null=True, blank=True)
    size = models.PositiveIntegerField(_("Otaq ölçüsü (m²)"), blank=True, null=True)
    
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name = _("Otaq Növü")
        verbose_name_plural = _("Otaq Növləri")


class RoomPrice(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='prices', verbose_name=_("Otaq növü"))
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name=_("Mövsüm"), null=True, blank=True)
    occupancy = models.PositiveSmallIntegerField(_("Nəfər sayı"), default=1)
    with_treatment = models.BooleanField(_("Müalicə ilə"), default=True)
    treatment_option = models.ForeignKey(TreatmentOption, on_delete=models.SET_NULL, null=True, blank=True, 
                                       verbose_name=_("Müalicə növü"))
    price = models.DecimalField(_("Qiymət"), max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Valyuta"), null=True)
    is_standard = models.BooleanField(_("Standart qiymət"), default=False, help_text=_("Seçildiyi təqdirdə, mövsüm olmadığı hallarda bu qiymət istifadə olunacaq"))
    
    def __str__(self):
        treatment_status = _("müalicə ilə") if self.with_treatment else _("müalicəsiz")
        season_text = self.season.name if self.season else _("Standart")
        return f"{self.room_type.name} - {self.occupancy} nəfər ({treatment_status}) - {season_text}"
    
    class Meta:
        verbose_name = _("Otaq qiyməti")
        verbose_name_plural = _("Otaq qiymətləri")
        unique_together = ('room_type', 'season', 'occupancy', 'with_treatment', 'treatment_option')


class AgeGroup(models.Model):
    name = models.CharField(_("Ad"), max_length=100)
    min_age = models.PositiveSmallIntegerField(_("Minimum yaş"))
    max_age = models.PositiveSmallIntegerField(_("Maksimum yaş"))
    
    def __str__(self):
        return f"{self.name} ({self.min_age}-{self.max_age} yaş)"
    
    class Meta:
        verbose_name = _("Yaş qrupu")
        verbose_name_plural = _("Yaş qrupları")
        ordering = ['min_age']


class ExtraBedPrice(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='extra_bed_prices', 
                                verbose_name=_("Otaq növü"))
    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, verbose_name=_("Yaş qrupu"))
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name=_("Mövsüm"), null=True, blank=True)
    is_standard = models.BooleanField(_("Standart qiymət"), default=True, help_text=_("Seçildiyi təqdirdə, mövsüm olmadığı hallarda bu qiymət istifadə olunacaq"))

    with_treatment = models.BooleanField(_("Müalicə ilə"), default=False)
    treatment_option = models.ForeignKey(TreatmentOption, on_delete=models.SET_NULL, null=True, blank=True, 
                                       verbose_name=_("Müalicə növü"))
    price = models.DecimalField(_("Qiymət"), max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("Valyuta"), null=True)
    
    def __str__(self):
        treatment_status = _("müalicə ilə") if self.with_treatment else _("müalicəsiz")
        season_text = self.season.name if self.season else _("Standart")
        return f"{self.room_type.name} - {self.age_group.name} ({treatment_status}) - {season_text}"
    
    class Meta:
        verbose_name = _("Əlavə çarpayı qiyməti")
        verbose_name_plural = _("Əlavə çarpayı qiymətləri")
        unique_together = ('room_type', 'season', 'age_group', 'with_treatment', 'treatment_option')


class RoomImage(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images', verbose_name=_("Otaq növü"))
    image = models.ImageField(_("Şəkil"), upload_to='rooms/')
    priority = models.IntegerField(_("Prioritet"), default=1)
    
    def __str__(self):
        return f"Image for {self.room_type.name}"
    
    class Meta:
        ordering = ['priority']
        verbose_name = _("Otaq Şəkli")
        verbose_name_plural = _("Otaq Şəkilləri")

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                RoomImage.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)


class Review(models.Model):
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.CASCADE, related_name='reviews', verbose_name=_("Sanatorium"))
    full_name = models.CharField(max_length=256)
    rating = models.PositiveSmallIntegerField(_("Reytinq"), validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField(_("Məzmun"))
    date = models.DateField(_("Tarix"), auto_now_add=True)
    is_published = models.BooleanField(_("Dərc olunub"), default=True)
    
    def __str__(self):
        return f"Review by {self.full_name} for {self.sanatorium.name}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = _("Rəy")
        verbose_name_plural = _("Rəylər")


class NaftalanSanatoriumsPage(models.Model):
    hero_section_title = models.CharField(_("Başlıq"), max_length=255)
    hero_section_description = models.TextField(_("Haqqında"))

    main_section_title = models.CharField(_("Başlıq"), max_length=255)
    main_section_description = RichTextUploadingField(_("Haqqında"))
    main_section_image = models.ImageField(_("Şəkil"), upload_to='sanatoriums/')

    sanatoriums_section_title = models.CharField(_("Başlıq"), max_length=255)
    sanatoriums_section_description = models.TextField(_("Haqqında"))

    contact_section_title = models.CharField(_("Başlıq"), max_length=255)
    contact_section_description = models.TextField(_("Haqqında"))

    def __str__(self):
        return "Naftalan Sanatoriyaları"


    class Meta:
        verbose_name = _("Naftalan Sanatoriyaları")
        verbose_name_plural = _("Naftalan Sanatoriyaları səhifəsi")


class OtherCitiesSanatoriumsPage(models.Model):
    hero_section_title = models.CharField(_("Başlıq"), max_length=255)
    hero_section_description = models.TextField(_("Haqqında"))

    main_section_title = models.CharField(_("Başlıq"), max_length=255)
    main_section_description = RichTextUploadingField(_("Haqqında"))
    main_section_image = models.ImageField(_("Şəkil"), upload_to='sanatoriums/')

    sanatoriums_section_title = models.CharField(_("Başlıq"), max_length=255)
    sanatoriums_section_description = models.TextField(_("Haqqında"))

    contact_section_title = models.CharField(_("Başlıq"), max_length=255)
    contact_section_description = models.TextField(_("Haqqında"))

    def __str__(self):
        return "Digər şəhərlərdəki sanatoriyalar"


    class Meta:
        verbose_name = _("Digər şəhərlərdəki sanatoriyalar")
        verbose_name_plural = _("Digər şəhərlərdəki sanatoriyalar səhifəsi")