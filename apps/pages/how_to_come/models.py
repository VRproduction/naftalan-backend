from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Hero(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Hero bölümü'
        verbose_name_plural = 'Hero bölümü'


class Location(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Haqqında məlumat')
    map_iframe = models.TextField(verbose_name='Map iframe')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Ünvan bölümü'
        verbose_name_plural = 'Ünvan bölümü'


class TransportOptionSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Haqqında məlumat')


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Nəqliyyat seçimləri bölümü'
        verbose_name_plural = 'Nəqliyyat seçimləri bölümü'


class TransportOption(models.Model):
    section = models.ForeignKey(TransportOptionSection, on_delete = models.PROTECT, related_name = 'options')
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = RichTextUploadingField(verbose_name='Məlumat')
    icon = models.ImageField(upload_to='transport-option')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Nəqliyyat seçimi'
        verbose_name_plural = 'Nəqliyyat seçimləri'


class VisaSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Bölüm haqqında Məlumat')
    content = RichTextUploadingField(verbose_name='Məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Viza məlumatı bölümü'
        verbose_name_plural = 'Viza məlumatı bölümü'