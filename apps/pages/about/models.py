from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField

class About(models.Model):
    banner_image = models.ImageField(upload_to='about/banner', verbose_name='Banner şəkili')
    banner_title = models.CharField(max_length=255, verbose_name='Banner başlığı')
    banner_description = models.TextField(verbose_name='Banner haqqında məlumat')
    
    content = RichTextUploadingField(verbose_name='Məlumat')

    reservation_image = models.ImageField(upload_to='about/reservation', verbose_name='Rezervasiya şəkili')
    reservation_title = models.CharField(max_length=255, verbose_name='Rezervasiya başlığı')
    reservation_description = models.TextField(verbose_name='Rezervasiya haqqında məlumat')


    def __str__(self):
        return 'Haqqımızda'

    class Meta:
        verbose_name = 'Haqqımızda səhifə'
        verbose_name_plural = 'Haqqımızda səhifə'


class History(models.Model):
    hero_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    hero_section_content = RichTextUploadingField(verbose_name='Haqqında məlumat')
    hero_section_image = models.ImageField(upload_to='about/history', verbose_name='Şəkil')

    introduction_title = models.CharField(max_length=255, verbose_name='Başlıq')
    introduction_content = RichTextUploadingField(verbose_name='Məlumat')

    timeline_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    timeline_section_description = RichTextUploadingField(verbose_name='Açıqlama')
    
    scientific_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    scientific_section_content = RichTextUploadingField(verbose_name='Məlumat')
    scientific_section_image = models.ImageField(upload_to='about/scientific', verbose_name='Şəkil')

    soviet_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    soviet_section_content = RichTextUploadingField(verbose_name='Məlumat')
    soviet_section_image = models.ImageField(upload_to='about/soviet', verbose_name='Şəkil')

    modern_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    modern_section_description = RichTextUploadingField(verbose_name='Açıqlama')

    def __str__(self):
        return "Tarix"

    
    class Meta:
        verbose_name = 'Tarix səhifə'
        verbose_name_plural = 'Tarix səhifə'


class TimelinePunkt(models.Model):
    section = models.ForeignKey(History, on_delete=models.CASCADE, related_name='timeline_punkts', verbose_name='Bölüm')
    year = models.CharField(max_length=50, verbose_name='Tarix')
    title = models.CharField(max_length=255, verbose_name='Başlığı')
    description = models.TextField(verbose_name='Haqqında məlumat')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                TimelinePunkt.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Tarixi ardıcıllıq'
        verbose_name_plural = 'Tarixi ardıcıllıqlar'
        ordering = ['priority']


class ModernPunkt(models.Model):    
    section = models.ForeignKey(History, on_delete=models.CASCADE, related_name='modern_punkts', verbose_name='Bölüm')
    icon = models.ImageField(upload_to='about/modern', verbose_name='Ikon')
    title = models.CharField(max_length=255, verbose_name='Başlığı')
    description = models.TextField(verbose_name='Haqqında məlumat')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                ModernPunkt.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Müasir dövr ardıcıllıq'
        verbose_name_plural = 'Müasir dövr ardıcıllıqlar'
        ordering = ['priority']



class TreatmentPage(models.Model):
    hero_title = models.CharField(max_length=255, verbose_name='Başlıq')
    hero_description = models.TextField(verbose_name='Haqqında məlumat')

    main_title = models.CharField(max_length=255, verbose_name='Başlıq')
    main_content = RichTextUploadingField(verbose_name='Məlumat')
    main_image = models.ImageField(upload_to='about/treatment', verbose_name='Şəkil')

    category_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    category_section_description = models.TextField(verbose_name='Haqqında məlumat')

    process_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    process_section_description = models.TextField(verbose_name='Haqqında məlumat')

    contact_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    contact_section_description = models.TextField(verbose_name='Haqqında məlumat')

    def __str__(self):
        return 'Müalicə olunan xəstəliklər'

    class Meta:
        verbose_name = 'Müalicə olunan xəstəliklər səhifə'
        verbose_name_plural = 'Müalicə olunan xəstəliklər səhifə'


class TreatmentCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Kateqoriya'
        verbose_name_plural = 'Müalicə olunan xəstəliklər səhifə | Müalicə kateqoriyaları'


class Treatment(models.Model):
    category = models.ForeignKey(TreatmentCategory, on_delete=models.CASCADE, related_name='treatments', verbose_name='Kateqoriya')
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    content = models.TextField()
    image = models.ImageField(upload_to='about/treatment', verbose_name='Şəkil')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Müalicə'
        verbose_name_plural = 'Müalicə olunan xəstəliklər səhifə | Müalicələr'


class TreatmentBenefit(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='benefits', verbose_name='Müalicə')
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                TreatmentBenefit.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Fayda'
        verbose_name_plural = 'Faydalar'
        ordering = ['priority']


class TreatmentProcess(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    content = models.TextField()
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                TreatmentProcess.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Müalicə prosesi'
        verbose_name_plural = 'Müalicə olunan xəstəliklər səhifə | Müalicə prosesləri'
        ordering = ['priority']



class Indication(models.Model):
    content = RichTextUploadingField(verbose_name='Məlumat')

    def __str__(self):
        return 'Naftalandan göstərişlər'

    class Meta:
        verbose_name = 'Naftalandan göstərişlər'
        verbose_name_plural = 'Naftalandan göstərişlər'
    

class Contraindications(models.Model):
    content = RichTextUploadingField(verbose_name='Məlumat')

    def __str__(self):
        return 'Əks göstərişlər'

    class Meta:
        verbose_name = 'Əks göstərişlər'
        verbose_name_plural = 'Əks göstərişlər'
