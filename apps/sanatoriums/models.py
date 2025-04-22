from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import nested_admin

from ckeditor_uploader.fields import RichTextUploadingField


class Location(models.Model):
    region = models.CharField(_("Ad"), max_length=256)
    country = models.CharField(_("Ölkə"), max_length=256)
    
    def __str__(self):
        return f"{self.region}, {self.country}"
    
    class Meta:
        verbose_name = _("Şəhərlər")
        verbose_name_plural = _("Şəhərlər")

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
    price = models.DecimalField(_("Qiymət"), max_digits=8, decimal_places=2, help_text=_("Gecə başına başlanğıc qiyməti"))
    address = models.CharField(_("Ünvan"), max_length=255)
    map_iframe = models.TextField(_("Xəritə iframe"))
    is_active = models.BooleanField(_("Aktivdir"), default=True)
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
    icon = models.CharField(_("İkon"), max_length=50, blank=True, help_text=_("İkon adı (İnterfeys üçün)"))
    
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




class RoomType(models.Model):
    sanatorium = models.ForeignKey(Sanatorium, on_delete=models.CASCADE, related_name='room_types', verbose_name=_("Sanatorium"))
    name = models.CharField(_("Ad"), max_length=255)
    
    def __str__(self):
        return f"{self.name} at {self.sanatorium.name}"
    
    class Meta:
        verbose_name = _("Otaq Növü")
        verbose_name_plural = _("Otaq Növləri")



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
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("İstifadəçi"))
    rating = models.PositiveSmallIntegerField(_("Reytinq"), validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField(_("Məzmun"))
    date = models.DateField(_("Tarix"), auto_now_add=True)
    is_published = models.BooleanField(_("Dərc olunub"), default=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.sanatorium.name}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = _("Rəy")
        verbose_name_plural = _("Rəylər")

